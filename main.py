import requests
import csv
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# === CONFIG ===
BASE_URL = "https://www.robotevents.com/api/v2"
BEARER_TOKEN = ""

# Configure session with retries
session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.robotevents.com/",
    "Origin": "https://www.robotevents.com"
}

# === FUNCTIONS ===

def make_request(url, params=None):
    try:
        response = session.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        
        # Check if we got a Cloudflare challenge
        if "cf-chl-bypass" in response.text.lower() or "enable javascript" in response.text.lower():
            raise requests.exceptions.RequestException("Cloudflare challenge detected")
            
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print(f"JSON decode error: {e}")
        return None

def get_team_id(team_number):
    if team_number == "1065A":
        return 153404
    if team_number == "1674A":
        return 180763
    if team_number == "2072C":
        return 169750
    if team_number == "3333W":
        return 123820
    if team_number == "3723A":
        return 129768
    if team_number == "10478S":
        return 128399

    params = {
        "grade[]": "High School",
        "program[]": 1
    }

    url = f"{BASE_URL}/teams?number={team_number}"
    data = make_request(url, params)
    
    if data:
        teams = data.get('data', [])
        if teams:
            return teams[0]['id']
        else:
            print(f"No team found with number {team_number}")
    return None

def get_team_matches(team_id, rounds):
    params = {
        "season[]": [190, 197],
        "round[]": rounds
    }
    
    url = f"{BASE_URL}/teams/{team_id}/matches"
    data = make_request(url, params)
    return data.get('data', []) if data else []

def get_team_awards(team_id):
    params = {
        "season[]": 190
    }
    
    url = f"{BASE_URL}/teams/{team_id}/awards"
    data = make_request(url, params)
    return data.get('data', []) if data else []

event_id2type = {}
def get_event_type(event_id):
    if event_id not in event_id2type:
        url = f"{BASE_URL}/events/{event_id}"
        data = make_request(url)
        if data:
            event_id2type[event_id] = data.get('level', 'Unknown')
        else:
            event_id2type[event_id] = 'Unknown'
    return event_id2type[event_id]

def save_matches_to_csv_and_md(matches, awards, team_number):
    # Process matches data
    for match in matches:
        if match.get('started') is None:
            match['started'] = match.get('scheduled')
    
    matches = sorted(matches, key=lambda x: (x['started'] is None, x['started']))
    
    # Prepare filenames
    filename_csv = f"{team_number}_matches.csv"
    filename_md = f"{team_number}_matches.md"

    # Writing to CSV
    with open(filename_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = [
            'Event Name', 'Event Type', 'Qualification', 'Match Name', 'Start Time',
            'Team Score', 'Opponent Score',
            'Winning Margin', 'Normalised Winning Margin', 'Verdict', 'Team Alliance', 'Winning Alliance',
            'Red Team 1', 'Red Team 2', 'Blue Team 1', 'Blue Team 2'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Writing to Markdown
        with open(filename_md, mode='w', encoding='utf-8') as md_file:
            md_file.write(f"# Match Results for Team {team_number}\n\n")
            md_file.write("| Event Name | Event Type | Qualification | Match Name | Start Time | Team Score | Opponent Score | Winning Margin | Normalised Winning Margin | Verdict | Team Alliance | Winning Alliance | Red Team 1 | Red Team 2 | Blue Team 1 | Blue Team 2 |\n")
            md_file.write("|------------|------------|---------------|------------|------------|------------|-----------------|----------------|---------------------------|---------|---------------|------------------|------------|------------|-------------|-------------|\n")

            for match in matches:
                # Extract match data
                event = match.get('event', {})
                event_name = event.get('name', 'Unknown').replace(",", "")
                event_type = get_event_type(event.get('id', -1))
                match_name = match.get('name', 'Unknown')
                
                # Find qualification from awards
                qualification = 'None'
                for award in awards:
                    award_event = award.get('event', {})
                    if award_event.get('name', '').replace(",", "") == event_name:
                        qualifications_list = award.get('qualifications', [])
                        qualification = qualifications_list[0] if qualifications_list else 'None'
                        break

                # Handle start time
                start_time = match.get('started') or match.get('scheduled') or 'TBD'
                
                # Process alliances
                alliances = match.get('alliances', [])
                red_teams = []
                blue_teams = []
                red_score = blue_score = None
                team_alliance = None

                for alliance in alliances:
                    color = alliance.get('color')
                    score = alliance.get('score')
                    teams = [team['team']['name'] for team in alliance.get('teams', [])]

                    if color == 'red':
                        red_teams = teams
                        red_score = score
                        if team_number in [t.split()[0] for t in teams]:  # Check if team number is in alliance
                            team_alliance = 'red'
                    elif color == 'blue':
                        blue_teams = teams
                        blue_score = score
                        if team_number in [t.split()[0] for t in teams]:  # Check if team number is in alliance
                            team_alliance = 'blue'

                # Calculate scores and margins
                if None in (red_score, blue_score, team_alliance):
                    team_score = opponent_score = margin = normalised_win_margin = 'N/A'
                    verdict = 'D'
                    winning_alliance = 'Unknown'
                else:
                    if team_alliance == 'red':
                        team_score = red_score
                        opponent_score = blue_score
                    else:
                        team_score = blue_score
                        opponent_score = red_score

                    margin = team_score - opponent_score
                    normalised_win_margin = margin / (team_score + opponent_score) if (team_score + opponent_score) != 0 else -1

                    if margin > 0:
                        winning_alliance = team_alliance
                        verdict = 'W'
                    elif margin < 0:
                        winning_alliance = 'blue' if team_alliance == 'red' else 'red'
                        verdict = 'L'
                    else:
                        winning_alliance = 'Tie'
                        verdict = 'D'

                # Ensure we have 2 teams per alliance
                red_teams.extend([''] * (2 - len(red_teams)))
                blue_teams.extend([''] * (2 - len(blue_teams)))

                # Write to CSV
                writer.writerow({
                    'Event Name': event_name,
                    'Event Type': event_type,
                    'Qualification': qualification,
                    'Match Name': match_name,
                    'Start Time': start_time,
                    'Team Score': team_score,
                    'Opponent Score': opponent_score,
                    'Winning Margin': margin,
                    'Normalised Winning Margin': normalised_win_margin,
                    'Verdict': verdict,
                    'Team Alliance': team_alliance or 'Unknown',
                    'Winning Alliance': winning_alliance,
                    'Red Team 1': red_teams[0] if len(red_teams) > 0 else '',
                    'Red Team 2': red_teams[1] if len(red_teams) > 1 else '',
                    'Blue Team 1': blue_teams[0] if len(blue_teams) > 0 else '',
                    'Blue Team 2': blue_teams[1] if len(blue_teams) > 1 else ''
                })

                # Write to Markdown
                md_file.write(f"| {event_name} | {event_type} | {qualification} | {match_name} | {start_time} | {team_score} | {opponent_score} | {margin} | {normalised_win_margin} | {verdict} | {team_alliance or 'Unknown'} | {winning_alliance} | {red_teams[0] if len(red_teams) > 0 else ''} | {red_teams[1] if len(red_teams) > 1 else ''} | {blue_teams[0] if len(blue_teams) > 0 else ''} | {blue_teams[1] if len(blue_teams) > 1 else ''} |\n")

    print(f"✅ Match results saved to {filename_csv} and {filename_md}")

def save_awards_to_csv_and_md(awards, team_number):
    filename_csv = f"{team_number}_awards.csv"
    filename_md = f"{team_number}_awards.md"

    with open(filename_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Event Name', 'Event Type', 'Title', 'Qualifications']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        with open(filename_md, mode='w', encoding='utf-8') as md_file:
            md_file.write(f"# Awards for Team {team_number}\n\n")
            md_file.write("| Event Name | Event Type | Title | Qualifications |\n")
            md_file.write("|------------|------------|-------|----------------|\n")

            for award in awards:
                event = award.get('event', {})
                event_name = event.get('name', 'Unknown').replace(",", "")
                event_type = get_event_type(event.get('id', -1))
                title = award.get('title', 'Unknown')
                qualifications = ";".join(award.get('qualifications', []))

                writer.writerow({
                    'Event Name': event_name,
                    'Event Type': event_type,
                    'Title': title,
                    'Qualifications': qualifications
                })

                md_file.write(f"| {event_name} | {event_type} | {title} | {qualifications} |\n")

    print(f"✅ Award results saved to {filename_csv} and {filename_md}")

failed = []

def main(team_number):
    print(f"\nFetching data for Team {team_number}...")
    
    # Check if files already exist
    if os.path.exists(f"{team_number}_matches.csv") and os.path.exists(f"{team_number}_awards.csv"):
        print("Data already exists for this team. Skipping...")
        return

    # Get team ID
    team_id = get_team_id(team_number)
    if not team_id:
        failed.append(team_number)
        print(f"Failed to retrieve team ID for {team_number}")
        return

    print(f"Found Team ID: {team_id}")
    event_id2type.clear()

    # Fetch data with rate limiting
    print("Fetching awards...")
    awards = get_team_awards(team_id)
    time.sleep(2)  # Rate limiting

    print("Fetching matches...")
    matches = []
    for round_num in range(2, 10):
        print(f"Fetching round {round_num} matches...")
        round_matches = get_team_matches(team_id, round_num)
        matches.extend(round_matches)
        time.sleep(1)  # Rate limiting

    # Save data
    if matches:
        save_matches_to_csv_and_md(matches, awards, team_number)
    else:
        failed.append(team_number)
        print(f"No matches found for team {team_number}")

    if awards:
        save_awards_to_csv_and_md(awards, team_number)
    else:
        failed.append(team_number)
        print(f"No awards found for team {team_number}")

if __name__ == "__main__":
    team_numbers = [
        # special handling
        

        # "39H", "94Z", "210Z", "321D", "360X", "603B", "719S", "839Z", "937X", "1011X",
        # "1065A", "1115E", "1229W", "1381P", "1674A", "1868A", "2011C", "2072C", "2150A", "2567C",
        # "2775V", "3131V", "3333W", "3723A", "3946S", "4148S", "4378A", "4828X", "5150J", "5864D",
        # "6121A", "6293X", "6741R", "7192F", "7447G", "7870Y", "8047F", "8349U", "8682C", "8889S",
        # "9065H", "9231A", "9784A", "10478S", "11442Y", "12478X", "14241A", "16099D", "16756B", "18031A",
        # "19122B", "20096G", "20605A", "23805S", "28828A", "30214A", "32792B", "35016Z", "36830B", "39599C",
        # "43272A", "45434S", "53999P", "55755A", "59001A", "62629X", "64783A", "66799G", "69403A", "71113X",
        # "74000M", "75503A", "77717F", "80001B", "81785K", "83149B", "86254B", "89250X", "93199G", "96504E",
        # "97673Z", "99040E", "99904W"
    ]

    for team_number in team_numbers:
        main(team_number)
        time.sleep(5)  # Delay between teams

    for x in failed:
        print(x)
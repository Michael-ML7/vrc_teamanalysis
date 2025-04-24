import requests
import csv
import os

# === CONFIG ===
BASE_URL = "https://www.robotevents.com/api/v2"
BEARER_TOKEN = ""

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Accept": "application/json"
}

# === FUNCTIONS ===

def get_team_id(team_number):
    url = f"{BASE_URL}/teams?number={team_number}"
    response = requests.get(url, headers=HEADERS)
    
    try:
        data = response.json()
    except ValueError:
        print(f"Error decoding JSON: {response.text}")
        return None

    if response.status_code == 200:
        teams = data.get('data', [])
        if len(teams) > 0:
            return teams[0]['id']
        else:
            print(f"No team found with number {team_number}.")
            return None
    else:
        print(f"Error fetching team ID: {response.status_code}")
        return None


def get_team_matches(team_id, rounds):
    # Include only 24-25 High Stakes season (season id 190)
    params = {
        "season[]": 190,
        "round[]": rounds
    }

    url = f"{BASE_URL}/teams/{team_id}/matches"
    response = requests.get(url, params=params, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    else:
        print(f"Error fetching matches: {response.status_code}")
        return []

def get_team_awards(team_id):
    # Include only 24-25 High Stakes season (season id 190)
    params = {
        "season[]": 190
    }

    url = f"{BASE_URL}/teams/{team_id}/awards"
    response = requests.get(url, params=params, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    else:
        print(f"Error fetching awards: {response.status_code}")
        return []

event_id2type = {}
def get_event_type(event_id):
    if event_id2type.get(event_id) == None:
        url = f"{BASE_URL}/events/{event_id}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            event_id2type[event_id] = data.get('level')
    return event_id2type.get(event_id, 'Unknown')


def save_matches_to_csv_and_md(matches, awards, team_number):
    for match in matches:
            if match.get('started') is None:
                match['started'] = match.get('scheduled')
    matches = sorted(matches, key=lambda x: (x['started'] is None, x['started']))
    
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
                event_name = match.get('event', {}).get('name', 'Unknown')
                event_name = event_name.replace(",", "") 
                event_type = get_event_type(match.get('event', {}).get('id', -1))
                match_name = match.get('name', 'Unknown')

                qualification = 'None'
                for award in awards:
                    if award.get('event', {}).get('name', '').replace(",", "") == event_name:
                        qualifications_list = award.get('qualifications', [])
                        qualification = qualifications_list[0] if qualifications_list else 'None'
                        break

                start_time = match.get('started', None)
                if not start_time:
                    start_time = match.get('scheduled', None)
                    if not start_time:
                        start_time = 'TBD'

                alliances = match.get('alliances', [])

                red_teams = []
                blue_teams = []
                red_score = blue_score = None
                team_alliance = None

                for alliance in alliances:
                    color = alliance.get('color')
                    score = alliance.get('score', None)
                    teams = [team['team']['name'] for team in alliance.get('teams', [])]

                    if color == 'red':
                        red_teams = teams
                        red_score = score
                        if team_number in red_teams:
                            team_alliance = 'red'
                    elif color == 'blue':
                        blue_teams = teams
                        blue_score = score
                        if team_number in blue_teams:
                            team_alliance = 'blue'

                if red_score is None or blue_score is None or team_alliance is None:
                    team_score = opponent_score = margin = normalised_win_margin = 'N/A'
                else:
                    if team_alliance == 'red':
                        team_score = red_score
                        opponent_score = blue_score
                    elif team_alliance == 'blue':
                        team_score = blue_score
                        opponent_score = red_score
                    else:
                        team_score = opponent_score = margin = 'Unknown'

                    margin = team_score - opponent_score

                    if team_score + opponent_score == 0:
                        normalised_win_margin = -1
                        continue
                    else:
                        normalised_win_margin = margin / (team_score + opponent_score)

                winning_alliance = 'Unknown'
                if margin > 0:
                    winning_alliance = team_alliance
                else:
                    if team_alliance == "red":
                        winning_alliance = "blue"
                    else:
                        winning_alliance = "red"

                verdict = 'D'
                if winning_alliance == team_alliance:
                    verdict = 'W'
                else:
                    verdict = 'L'

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
                    'Red Team 1': red_teams[0],
                    'Red Team 2': red_teams[1],
                    'Blue Team 1': blue_teams[0],
                    'Blue Team 2': blue_teams[1]
                })

                # Writing to Markdown
                md_file.write(f"| {event_name} | {event_type} | {qualification} | {match_name} | {start_time} | {team_score} | {opponent_score} | {margin} | {normalised_win_margin} | {verdict} | {team_alliance or 'Unknown'} | {winning_alliance} | {red_teams[0]} | {red_teams[1]} | {blue_teams[0]} | {blue_teams[1]} |\n")

    print(f"✅ Match results saved to {team_number}_matches.csv and {team_number}_matches.md")

def save_awards_to_csv_and_md(awards, team_number):
    filename_csv = f"{team_number}_awards.csv"
    filename_md = f"{team_number}_awards.md"

    with open(filename_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = [
            'Event Name', 'Event Type', 'Title', 'Qualifications'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Writing to Markdown
        with open(filename_md, mode='w', encoding='utf-8') as md_file:
            md_file.write(f"# Awards for Team {team_number}\n\n")
            md_file.write("| Event Name | Event Type | Title | Qualifications |\n")
            md_file.write("|------------|------------|-------|----------------|\n")

            for award in awards:
                event_name = award.get('event', {}).get('name', 'Unknown')
                event_name = event_name.replace(",", "")
                event_type = get_event_type(award.get('event', {}).get('id', -1))
                title = award.get('title', {'Fault'})
                qualifications = award.get('qualifications')

                writer.writerow({
                    'Event Name': event_name,
                    'Event Type': event_type,
                    'Title': title,
                    'Qualifications': ";".join(qualifications)
                })

                # Writing to Markdown
                md_file.write(f"| {event_name} | {event_type} | {title} | {';'.join(qualifications)} |\n")

    print(f"✅ Award results saved to {team_number}_awards.csv and {team_number}_awards.md")


# === MAIN ===

def main():
    team_number = input("Enter the team number (e.g., 86254B): ").strip().upper()
    team_id = get_team_id(team_number)

    if team_id:
        print(f"\nFetching data for Team {team_number} (ID: {team_id})...")

        # Fetch data
        awards = get_team_awards(team_id)
        matches = get_team_matches(team_id, 2)
        for i in range(3, 10):
            matches += get_team_matches(team_id, i)
        
        # Process team match data
        print("⚙ Match data")
        if os.path.exists(f"{team_number}_matches.csv"):
            os.remove(f"{team_number}_matches.csv")
        if matches:
            save_matches_to_csv_and_md(matches, awards, team_number)
        else:
            print("No matches found for team {team_number}")

        # Process team award data
        print("⚙ Award data")
        if os.path.exists(f"{team_number}_awards.csv"):
            os.remove(f"{team_number}_awards.csv")
        if awards:
            save_awards_to_csv_and_md(awards, team_number)
        else:
            print("No awards found for team {team_number}")
    else:
        print("Failed to retrieve team ID.")


if __name__ == "__main__":
    main()
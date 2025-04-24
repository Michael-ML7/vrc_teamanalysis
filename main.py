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

def save_matches_to_csv(matches, team_number):
    filename = f"{team_number}_matches.csv"

    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = [
            'Event Name', 'Event Type', 'Match Name', 'Start Time',
            'Team Score', 'Opponent Score',
            'Winning Margin', 'Normalised Winning Margin', 'Verdict', 'Team Alliance', 'Winning Alliance',
            'Red Team 1', 'Red Team 2', 'Blue Team 1', 'Blue Team 2'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()

        for match in matches:
            # Extract relevant match information
            event_name = match.get('event', {}).get('name', 'Unknown')
            event_name = event_name.replace(",", "") # removing the commas from the event name just for easier data analysis on Google Sheets
            event_type = get_event_type(match.get('event', {}).get('id', -1))
            match_name = match.get('name', 'Unknown')

            # Handle missing scheduled time
            start_time = match.get('started', None)
            if not start_time:
                start_time = match.get('scheduled', None) # If started does not exist then use scheduled time (approxmiately the same doesnt matter)
                if not start_time:
                    start_time = 'TBD'  # Set to 'TBD' if the start time is not available

            alliances = match.get('alliances', [])

            # Initialize variables for alliance teams and scores
            red_teams = []
            blue_teams = []
            red_score = blue_score = None
            team_alliance = None

            # Extract the teams and scores from alliances
            for alliance in alliances:
                color = alliance.get('color')
                score = alliance.get('score', None)
                teams = [team['team']['name'] for team in alliance.get('teams', [])]

                # Store teams based on alliance color
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

            # Handle missing scores or team alliance
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
                # Calculate the winning margin
                margin = team_score - opponent_score

                if team_score + opponent_score == 0:
                    normalised_win_margin = -1
                    continue
                else:
                    normalised_win_margin = margin / (team_score + opponent_score)

            # Identify the winning alliance
            winning_alliance = 'Unknown'
            if margin > 0:
                winning_alliance = team_alliance
            else:
                if team_alliance == "red":
                    winning_alliance = "blue"
                else:
                    winning_alliance = "red"

            # Debugging: Print out the match details for inspection
            # print(match_name)
            # print(f"Event: {event_name}, Match: {match_name}, Start: {start_time}")
            # print(f"Red Teams: {red_teams}, Blue Teams: {blue_teams}")
            # print(f"Red Score: {red_score}, Blue Score: {blue_score}")
            
            verdict = 'D'
            if winning_alliance == team_alliance:
                verdict = 'W'
            else:
                verdict = 'L'

            # Write the match details to the CSV
            writer.writerow({
                'Event Name': event_name,
                'Event Type': event_type,
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
    print(f"\n✅ Match results saved to {team_number}_matches.csv")


def save_awards_to_csv(awards, team_number):
    filename = f"{team_number}_awards.csv"

    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = [
            'Event Name', 'Event Type', 'Title', 'Qualifications'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()

        for award in awards:
            event_name = award.get('event', {}).get('name', 'Unknown')
            event_name = event_name.replace(",", "") # removing the commas from the event name just for easier data analysis on Google Sheets
            event_type = get_event_type(award.get('event', {}).get('id', -1))
            title = award.get('title', {'Fault'})
            qualifications = award.get('qualifications')

            # Write the match details to the CSV
            writer.writerow({
                'Event Name': event_name,
                'Event Type': event_type,
                'Title': title,
                'Qualifications': ";".join(qualifications)
            })
    print(f"\n✅ Match results saved to {team_number}_awards.csv")

# === MAIN ===

def main():
    team_number = input("Enter the team number (e.g., 86254B): ").strip().upper()
    team_id = get_team_id(team_number)

    if team_id:
        print(f"\nFetching data for Team {team_number} (ID: {team_id})...")
        
        # Process team match data
        # Include Qualification (2), Quarter-Finals (3), Semi-Finals (4), Finals (5)
        print("⚙ Match data")
        if os.path.exists(f"{team_number}_matches.csv"):
            os.remove(f"{team_number}_matches.csv")

        matches = get_team_matches(team_id, 2)
        for i in range(3,10):
            matches += get_team_matches(team_id, i)
        
        for match in matches:
            if match.get('started') is None:
                match['started'] = match.get('scheduled')
        matches = sorted(matches, key=lambda x: (x['started'] is None, x['started']))

        if matches:
            save_matches_to_csv(matches, team_number)
        else:
            print("No matches found for team {team_number}")

        # Process team award data
        print("⚙ Match data")
        if os.path.exists(f"{team_number}_awards.csv"):
            os.remove(f"{team_number}_awards.csv")
        awards = get_team_awards(team_id)
        if awards:
            save_awards_to_csv(awards, team_number)
    else:
        print("Failed to retrieve team ID.")


if __name__ == "__main__":
    main()

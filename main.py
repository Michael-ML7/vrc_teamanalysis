import requests
import csv
import os

# === CONFIG ===
BASE_URL = "https://www.robotevents.com/api/v2"
BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzIiwianRpIjoiZjg2YWZmYzZmNTMwZjg2NTIwMzljMmZjYTZkZjRiM2VjNmY3YTI2YzkwYzdmN2I3OWRiNzNhNWVkZTBkZmE1OTM0OGJlZmFhNTM1Yzg2MDUiLCJpYXQiOjE3NDUzNzkwMTguMzc2MDgsIm5iZiI6MTc0NTM3OTAxOC4zNzYwODE5LCJleHAiOjI2OTIwNjM4MTguMzcxNjA5Miwic3ViIjoiMTQ1ODYyIiwic2NvcGVzIjpbXX0.mb3L8qbIPapkvciF1waSk6qRTUH9FEOBuO3x-tJk0mUM5N4DD8URUTmnTPTV7FBPTMjYRp7lpE-7Lq_AdhORxJ2_bQKSHOJLHPanNKdvIptmqGID_omuGIP5V5R58TtCT1zX-lez24kUfFo-beEZVFklTMiCv8haOps-dmL7AK3itYM6KcE65f2UZ20TrDJ_xEo3eiTI8eONRp9_sjtcgiIpW5Xv-khELNV0KA39Gd_d5wn3CiRAzuSSyggbFzoQtFjw9S1jsaj7KxQmfPdCfa76HFVSmz67Y4-NDbI_mp4W7k3CsXKl0q-Owz0q_MI9vzSAQto1OwowRsYDFfJctgDjzXiutAGcHvGPVmPCpEuid9l9QzYobCyokCiVxmbdtshXcoAZtsWXpqsnp1atnJWaHVQjdzJSfx2Munsf_6fppsfCsf4sERUoXSrCmAWiLvc6bYHSwngKnYl8T4fGwdSud9eTcrLHu_yNjw1iU7_aMFHIQwcJWzj9A-dZfBgdrJrionY4v2U6b2Yr0t_6vsCerNx7eqI81S1lF6yWyHh4SqQk8s8gSu2BLRrtRd-wya7qXs6mPzoyk-Oju4QYcdPhzjZALFwsRyRqk7AcGgnzmsJnW0HaKxd6RGyv6hVNoz_E8txKquNXY4nRRvr6u0FjFYqEQ_d_uY1kvt8VwSk"  # <-- Replace this with your real token

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


def get_team_matches(team_id):
    # Include Qualification (2), Quarter-Finals (3), Semi-Finals (4), Finals (5)
    # Include only 24-25 High Stakes season (season id 190)
    params = {
        "season[]": 190,
        "round[]": [2, 3, 4, 5]
    }

    url = f"{BASE_URL}/teams/{team_id}/matches"
    response = requests.get(url, params=params, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    else:
        print(f"Error fetching matches: {response.status_code}")
        return []


def save_matches_to_csv(matches, team_number):
    filename = f"{team_number}_matches.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = [
            'Event Name', 'Match Name', 'Start Time',
            'Team Score', 'Opponent Score',
            'Winning Margin', 'Verdict', 'Team Alliance', 'Winning Alliance',
            'Red Team 1', 'Red Team 2', 'Blue Team 1', 'Blue Team 2'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for match in matches:
            # Extract relevant match information
            event_name = match.get('event', {}).get('name', 'Unknown')
            match_name = match.get('name', 'Unknown')

            # Handle missing scheduled time
            start_time = match.get('started', None)
            if not start_time:
                start_time = 'TBD'  # Set to 'TBD' if the start time is not available

            alliances = match.get('alliances', [])
            result = match.get('result', {})

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
                team_score = opponent_score = margin = 'N/A'
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
                'Match Name': match_name,
                'Start Time': start_time,
                'Team Score': team_score,
                'Opponent Score': opponent_score,
                'Winning Margin': margin,
                'Verdict': verdict,
                'Team Alliance': team_alliance or 'Unknown',
                'Winning Alliance': winning_alliance,
                'Red Team 1': red_teams[0],
                'Red Team 2': red_teams[1],
                'Blue Team 1': blue_teams[0],
                'Blue Team 2': blue_teams[1]
            })

    print(f"\n✅ Match results saved to {os.path.abspath(filename)}")


# === MAIN ===

def main():
    team_number = input("Enter the team number (e.g., 86254B): ").strip().upper()
    team_id = get_team_id(team_number)

    if team_id:
        print(f"\nFetching data for Team {team_number} (ID: {team_id})...")
        matches = get_team_matches(team_id)

        if matches:
            save_matches_to_csv(matches, team_number)
        else:
            print("No match data found.")
    else:
        print("Failed to retrieve team ID.")


if __name__ == "__main__":
    main()

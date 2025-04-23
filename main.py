import requests
import csv
import os

# === CONFIGURATION ===
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
    url = f"{BASE_URL}/teams/{team_id}/matches?round[]=2&round[]=3&round[]=4&round[]=5"
    response = requests.get(url, headers=HEADERS)

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
            'Event Name', 'Match Name', 'Scheduled Time',
            'Team Alliance', 'Team Score', 'Opponent Score',
            'Winning Margin', 'Winning Alliance',
            'Red Teams', 'Blue Teams'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for match in matches:
            # Extract relevant match information
            event_name = match.get('event', {}).get('name', 'Unknown')
            match_name = match.get('name', 'Unknown')
            print(match_name)

            # Handle missing scheduled time
            scheduled_time = match.get('scheduled', None)
            if not scheduled_time:
                scheduled_time = 'TBD'  # Set to 'TBD' if the scheduled time is not available

            # Skip matches that don't meet date criteria unless it's a final match (scheduled_time == 'TBD')
            if scheduled_time != 'TBD':
                year = scheduled_time[0:4]
                month = scheduled_time[5:7]
                if year < "2024":
                    continue
                if year == "2024" and month <= "05":
                    continue

            if "2023-2024" in event_name:
                continue  # Skip events from the 2023-2024 season

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
            # print(f"Event: {event_name}, Match: {match_name}, Scheduled: {scheduled_time}")
            # print(f"Red Teams: {red_teams}, Blue Teams: {blue_teams}")
            # print(f"Red Score: {red_score}, Blue Score: {blue_score}")

            # Write the match details to the CSV
            writer.writerow({
                'Event Name': event_name,
                'Match Name': match_name,
                'Scheduled Time': scheduled_time,
                'Team Alliance': team_alliance or 'Unknown',
                'Team Score': team_score,
                'Opponent Score': opponent_score,
                'Winning Margin': margin,
                'Winning Alliance': winning_alliance,
                'Red Teams': ', '.join(red_teams),
                'Blue Teams': ', '.join(blue_teams)
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
            # print(matches)
            # save_matches_to_csv(matches, team_number)
        else:
            print("No match data found.")
    else:
        print("Failed to retrieve team ID.")


if __name__ == "__main__":
    main()

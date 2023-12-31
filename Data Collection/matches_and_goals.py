import pyodbc
import requests
from datetime import datetime, timedelta

# Connect to the SQL Server database
server_name = 'VIETNT02'
database_name = 'EnglishPremierLeague'
trusted_connection = 'yes'
connection_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};Trusted_Connection={trusted_connection};'
conn = pyodbc.connect(connection_string)
if conn:
    print('Connected successfully')
cursor = conn.cursor()

# SQL queries for inserting match and goal data
insert_matches = '''
INSERT INTO dbo.matches
(match_id, home_team_id, away_team_id, home_team_scores, away_team_scores, stadium_id, kickoff, season, main_referee_id, attendance)
VALUES
(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''
insert_goals = '''
INSERT INTO dbo.goals
(goal_id, match_id, scorer_player_id, assist_player_id, time, scoring_team_id)
VALUES
(?, ?, ?, ?, ?, ?)
'''

# Disable constraints for bulk insert
cursor.execute("ALTER TABLE dbo.matches NOCHECK CONSTRAINT all")
cursor.execute("ALTER TABLE dbo.goals NOCHECK CONSTRAINT all")

# Components of the request
headers_requests = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.premierleague.com",
    "Referer": "https://www.premierleague.com/",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
}
url = f"https://footballapi.pulselive.com/football/fixtures"

# Defining a function to retrieve the list of match IDs
def match_id_list():
    # Payload for the initial request to get match IDs
    payload_id_list = {
        'comps': '1',
        'page': '0',
        'pageSize': '50',
        'sort': 'asc',
        'statuses': 'A,C',
        'altIds': 'true'
    }

    # Send the initial request to get the number of pages
    response = requests.get(url, headers=headers_requests, params=payload_id_list)
    r = response.json()
    pages = r['pageInfo']['numPages']

    id_list = list()

    # Iterate through each page to get match IDs
    for page in range(pages):
        ids = list()
        payload_id_list['page'] = page
        new_response = requests.get(url, headers=headers_requests, params=payload_id_list)
        new_r = new_response.json().get('content')
        for i in new_r:
            ids.append(int(i['id']))
        id_list.append(ids)
        print(ids)

    # Yield match IDs page by page
    for match_ids in id_list:
        yield match_ids


# Payload for individual match requests
payload_match = {"altIds": "true"}

# Maximum number of retries for HTTP requests
max_retries = 5

# Iterate through match IDs
for match_ids in match_id_list():
    print(f'Begin inserting (id: {match_ids[0]})')

    # Iterate through individual match IDs
    for match_id in match_ids:
        # Retry loop for handling HTTP request failures
        for retry in range(max_retries):
            try:
                match_response = requests.get(f'{url}/{match_id}',headers=headers_requests, params=payload_match)
                match_response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                if retry < max_retries - 1:
                    print(f"Retrying match id: {match_id}: ({retry + 1}/{max_retries})...")
                else:
                    print(f"Max retries reached. Skipping this request.")
                    break
        
        # Process the match data
        match_r = match_response.json()
        home_team_id = match_r['teams'][0]['team']['club']['id']
        away_team_id = match_r['teams'][1]['team']['club']['id']
        home_team_scores = match_r['teams'][0]['score']
        away_team_scores = match_r['teams'][1]['score']
        stadium_id = match_r['ground']['id']
        kickoff = datetime.fromtimestamp(match_r['kickoff']['millis'] / 1000) - timedelta(hours=7)
        kickoff = kickoff.strftime("%Y-%m-%d %H:%M:%S")
        season = match_r['gameweek']['compSeason']['label']
        main_referee_id = match_r['matchOfficials'][0]['id']

        # Check if attendance information is available
        if 'attendance' in match_r:
            attendance = match_r['attendance']
        else:
            attendance = None
        
        # Execute SQL query to insert match data
        cursor.execute(insert_matches, match_id, home_team_id, away_team_id, home_team_scores, away_team_scores, stadium_id, kickoff, season, main_referee_id, attendance)
        
        # Iterate through events in the match
        for event in match_r['events']:
            if event['type'] == 'G': # Process only goal events
                goal_id = event['id']
                scorer_player_id = event['personId']

                # Check if there is an assisting player
                if 'assistId' in event:
                    assist_player_id = event['assistId']
                else:
                    assist_player_id = None
                time = event['clock']['label'][:-2]
                scoring_team_id = event['teamId']

                # Execute SQL query to insert goal data
                cursor.execute(insert_goals, goal_id, match_id, scorer_player_id, assist_player_id, time, scoring_team_id)
        conn.commit()
    print(f'Complete inserting (id: {match_ids[-1]})')
conn.close()
import requests
import pyodbc

# Connect to the SQL Server database
server_name = 'VIETNT02'
database_name = 'EnglishPremierLeague'
trusted_connection = 'yes'
connection_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};Trusted_Connection={trusted_connection};'
conn = pyodbc.connect(connection_string)
if conn:
    print('Connected successfully')
cursor = conn.cursor()

# SQL query to insert team details into the 'dbo.teams' table
insert_query = '''
    INSERT INTO dbo.teams
    (team_id, team_name, founded_year, city, wins, draws, losses, total_red_cards, total_yellow_cards)
    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

headers = {
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

# SQL query to select distinct home_team_id from dbo.matches
cursor.execute('SELECT DISTINCT home_team_id FROM dbo.matches')
team_id_list = cursor.fetchall()

# Iterate through the team_id_list and fetch team details from the API
for i in team_id_list:
    team_id = i[0]
    print(f'team id: {team_id}')
    payload = {'comps': '1'}

    # API URLs for fetching team details
    url1 = f'https://footballapi.pulselive.com/football/clubs/{team_id}'
    url2 = f'https://footballapi.pulselive.com/football/stats/team/{team_id}'

    # HTTP requests to fetch data
    r1 = requests.get(url1, headers= headers)
    r2 = requests.get(url2, headers= headers, params= payload)
    response = r1.json()
    stats = r2.json().get('stats')

    # Extract team details from the responses
    team_name = response['name']
    founded_year = response['founded'] if 'founded' in response else None

    # Determine the city of the team
    if 'city' in response:
        city = response['city']
    elif 'city' in response['teams'][0]['grounds'][0]:
        city = response['teams'][0]['grounds'][0]['city']
    else:
        city = response['teams'][0]['grounds'][-1]['city']
    
    # Extract statistical information
    wins = int(next(filter(lambda x: x['name'] == 'wins', stats), None).get('value'))
    draws = int(next(filter(lambda x: x['name'] == 'draws', stats), None).get('value'))
    losses = int(next(filter(lambda x: x['name'] == 'losses', stats), None).get('value'))
    red = next(filter(lambda x: x['name'] == 'total_red_card', stats), None)
    if red is not None:
        total_red_cards = int(next(filter(lambda x: x['name'] == 'total_red_card', stats), None).get('value'))
    else:
        total_red_cards = 0
    total_yellow_cards = int(next(filter(lambda x: x['name'] == 'total_yel_card', stats), None).get('value'))
    
    # Execute the insert query with the extracted data
    cursor.execute(insert_query, team_id, team_name, founded_year, city, wins, draws, losses, total_red_cards, total_yellow_cards)
print('Insertion complete')

# Commit changes to the database and close the database connection
conn.commit()
conn.close()
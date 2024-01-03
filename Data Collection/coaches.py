import requests
import pyodbc
from bs4 import BeautifulSoup
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

# SQL query for inserting coach data
insert_query = '''
    INSERT INTO dbo.coaches
    (coach_id, first_name, last_name, country, birth, status, last_epl_team_id, matches, wins, draws, losses)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

# API endpoint for fetching coach data
url = f"https://footballapi.pulselive.com/football/teamofficials"
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

# Create a list to store all existing coach_id values
cursor.execute('SELECT coach_id FROM dbo.coaches')
existing_coach_ids = [row[0] for row in cursor.fetchall()]

# Pagination for the API request
page = 0

# Loop through paginated API responses
while True:
    payload = {
        'pageSize': '500',
        'comps': '1',
        'altIds': 'true',
        'type': 'manager',
        'compCodeForActivePlayer': 'EN_PR',
        'page': str(page)
    }
    r = requests.get(url, headers= headers, params= payload)
    response = r.json().get('content')
    
    # Break the loop if no more data is returned
    if not response:
        print("Insertion complete")
        break

    # Iterate through coach data and insert into the database
    for coach in response:
        coach_id = int(coach['id'])
        if coach_id in existing_coach_ids:
            print(f"Coach ID {coach_id} already exists. Skipping the loop.")
            continue
        first_name = coach['name']['first']
        last_name = coach['name']['last']
        country = coach['birth']['country']['country']
        birth = int(coach['birth']['date']['millis'])
        birth = datetime.utcfromtimestamp(0) + timedelta(milliseconds = birth)
        birth = birth.strftime("%Y-%m-%d")
        status = 'active' if coach['active'] else 'retired'
        last_epl_team_id = int(coach['currentTeam']['club']['id'])

        # Extract additional details from coach's page
        details = requests.get(url = f'https://www.premierleague.com/managers/{coach_id}')
        soup = BeautifulSoup(details.text, 'html.parser')
        target_section = soup.find_all('section', class_='player-overview__side-widget')
        stats = target_section[1].find_all('div', class_="player-overview__info")
        matches = int(stats[0].text)
        wins = int(stats[1].text)
        draws = int(stats[2].text)
        losses = int(stats[3].text)

        # Execute the SQL query to insert coach data
        cursor.execute(insert_query, coach_id, first_name, last_name, country, birth, status, last_epl_team_id, matches, wins, draws, losses)
    
    # Move to the next page of results
    page += 1

# Commit changes to the database and close the connection
conn.commit()
conn.close()
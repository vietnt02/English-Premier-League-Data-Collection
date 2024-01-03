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

# SQL query for inserting referee data
insert_query = 'INSERT dbo.referees (referee_id, first_name, last_name, debut_match_id, appearances, red_cards, yellow_cards) VALUES (?, ?, ?, ?, ?, ?, ?)'

# URL for fetching match officials data and headers for HTTP requests
url = f"https://footballapi.pulselive.com/football/matchofficials"
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

# Create a list to store all existing referee_id values
cursor.execute('SELECT referee_id FROM dbo.referees')
existing_referee_ids = [row[0] for row in cursor.fetchall()]

page = 0

# Infinite loop for paginated requests
while True:
    # Payload for the request to get match officials
    payload = {
        'comps': '1',
        'pageSize': '100',
        'altIds': 'true',
        'type': 'M',
        'page': str(page)
    }

    # Send the request to get match officials
    r = requests.get(url, headers=headers, params= payload)
    response = r.json().get('content')

    # Check if there is no more data
    if not response:
        print("Insertion complete")
        break

    # Iterate through each referee in the response
    for referee in response:
        referee_id = int(referee['id'])
        if referee_id in existing_referee_ids:
            print(f"Referee ID {referee_id} already exists. Skipping the loop.")
            continue
        first_name = referee['name']['first']
        last_name = referee['name']['last']
        debut_match_id = int(referee['debut']['id'])
        appearances = int(referee['appearances'])
        red_cards = int(referee['redCards'])
        yellow_cards = int(referee['yellowCards'])

        # Execute the SQL query to insert referee data
        cursor.execute(insert_query, referee_id, first_name, last_name, debut_match_id, appearances, red_cards, yellow_cards)
    # Move to the next page
    page += 1

# Commit changes to the database and close the database connection
conn.commit()
conn.close()
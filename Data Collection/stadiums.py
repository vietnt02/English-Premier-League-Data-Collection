import requests
import pyodbc
import pandas as pd

# Connect to the SQL Server database
server_name = 'VIETNT02'
database_name = 'EnglishPremierLeague'
trusted_connection = 'yes'
connection_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};Trusted_Connection={trusted_connection};'
conn = pyodbc.connect(connection_string)
if conn:
    print('Connected successfully')
cursor = conn.cursor()

# SQL query to insert stadium details into the 'dbo.stadiums' table
insert_query = 'INSERT INTO dbo.stadiums (stadium_id, stadium_name, city, capacity) VALUES (?, ?, ?, ?)'

# URL for fetching fixtures data and components for HTTP requests
url = f"https://footballapi.pulselive.com/football/fixtures"
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
payload = {"altIds": "true"}

# SQL query to select the first match_id for each unique stadium
select_query = '''
    SELECT
        subquery.match_id
    FROM
        (SELECT
            stadium_id
            , home_team_id
            , ROW_NUMBER() OVER (PARTITION BY stadium_id ORDER BY match_id) AS rank_match_id
            , match_id
        FROM
            dbo.matches) AS subquery
    WHERE
        rank_match_id = 1
'''

# Execute the select query
cursor.execute(select_query)
match_id_list = [row.match_id for row in cursor.fetchall()]

# Fetch stadium details using match_id
stadium_list1 = list()
for match_id in match_id_list:
    response = requests.get(f'{url}/{match_id}',headers=headers, params=payload)
    r = response.json().get('ground')
    stadium_name = r['name']
    city = r['city']
    stadium_id = r['id']
    stadium_list1.append([stadium_id, stadium_name, city])

# Create a DataFrame from the first set of stadium details
header_df = ['id', 'stadium_name', 'city']
df1 = pd.DataFrame(stadium_list1, columns=header_df)

# Payload for fetching team details
payload2 = {
    'pageSize': '100',
    'comps': '1',
    'altIds': 'true',
    'page': 0
}

url2 = f"https://footballapi.pulselive.com/football/teams"
response = requests.get(url2, headers=headers, params=payload2)
r = response.json().get('content')

# Fetch stadium details from teams
stadium_list2 = list()
for team in r:
    owner_team_id = team['club']['id']
    if owner_team_id == 22:
        continue
    for stadium in team['grounds']:
        stadium_name = stadium['name']
        if 'capacity' in stadium:
            capacity = int(stadium['capacity'])
        else:
            capacity = None
        stadium_list2.append([stadium_name,capacity])

# Create a DataFrame from the second set of stadium details
header_df2 = ['stadium_name', 'capacity']
df2 = pd.DataFrame(stadium_list2, columns=header_df2)

# Merge the two DataFrames on 'stadium_name' column
result_df = pd.merge(df1, df2, on='stadium_name', how='left')

# Iterate through rows of the resulting DataFrame and insert data into the 'dbo.stadiums' table
print('Start inserting')
for index, row in result_df.iterrows():
    stadium_id = row['id']
    stadium_name = row['stadium_name']
    city = row['city']
    if pd.isna(row['capacity']):
        capacity = None
    else:
        capacity = row['capacity']
    cursor.execute(insert_query, stadium_id, stadium_name, city, capacity)
print('Insertion complete')

# Commit changes to the database and close the database connection
conn.commit()
conn.close()
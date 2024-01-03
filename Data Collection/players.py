import requests
import pyodbc
from datetime import datetime, timedelta

# Connect to the SQL Server database
server_name = 'VIETNT02'
database_name = 'EnglishPremierLeague'
trusted_connection = 'yes'
connection_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};Trusted_Connection={trusted_connection};'
conn = pyodbc.connect(connection_string)
if conn:
    print('Connected to SQL Server database successfully')
cursor = conn.cursor()

# SQL query to insert player data into the database
insert_query = '''
    INSERT INTO	dbo.players
    (player_id,first_name,last_name,position,country,birth,appearances,clean_sheets,goals,assists,red_cards,yellow_cards)
    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

# Function to look up the country code
def countryLookup(code):
    country_dict = {'GB-ENG': 'England', 'GB-NIR': 'Northern Ireland', 'IE': 'Ireland', 'GB-SCT': 'Scotland', 'GB-WLS': 'Wales', 'AL': 'Albania', 'DZ': 'Algeria', 'AO': 'Angola', 'AQ': 'Antarctica', 'AG': 'Antigua and Barbuda', 'AR': 'Argentina', 'AM': 'Armenia', 'AU': 'Australia', 'AT': 'Austria', 'BS': 'Bahamas', 'BB': 'Barbados', 'BY': 'Belarus', 'BE': 'Belgium', 'BJ': 'Benin', 'BM': 'Bermuda', 'BO': 'Bolivia, Plurinational State of', 'BA': 'Bosnia and Herzegovina', 'BR': 'Brazil', 'BG': 'Bulgaria', 'BF': 'Burkina Faso', 'BI': 'Burundi', 'CM': 'Cameroon', 'CA': 'Canada', 'CV': 'Cape Verde', 'CL': 'Chile', 'CN': 'China', 'CO': 'Colombia', 'CG': 'Congo', 'CD': 'Congo, the Democratic Republic of the', 'CR': 'Costa Rica', 'CI': "Côte d'Ivoire", 'HR': 'Croatia', 'CW': 'Curaçao', 'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DK': 'Denmark', 'EC': 'Ecuador', 'EG': 'Egypt', 'EE': 'Estonia', 'FO': 'Faroe Islands', 'FI': 'Finland', 'FR': 'France', 'GA': 'Gabon', 'GI': 'Gibraltar', 'GM': 'Gambia', 'GE': 'Georgia', 'DE': 'Germany', 'GH': 'Ghana', 'GR': 'Greece', 'GD': 'Grenada', 'GN': 'Guinea', 'GY': 'Guyana', 'HN': 'Honduras', 'HU': 'Hungary', 'IS': 'Iceland', 'IR': 'Iran, Islamic Republic of', 'IL': 'Israel', 'IT': 'Italy', 'JM': 'Jamaica', 'JP': 'Japan', 'KE': 'Kenya', 'KR': 'Korea, Republic of', 'LV': 'Latvia', 'LR': 'Liberia', 'LT': 'Lithuania', 'MK': 'Macedonia, the Former Yugoslav Republic of', 'ML': 'Mali', 'MX': 'Mexico', 'ME': 'Montenegro', 'MS': 'Montserrat', 'MA': 'Morocco', 'NL': 'Netherlands', 'NZ': 'New Zealand', 'NG': 'Nigeria', 'NO': 'Norway', 'OM': 'Oman', 'PK': 'Pakistan', 'PS': 'Palestine, State of', 'PY': 'Paraguay', 'PE': 'Peru', 'PH': 'Philippines', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'RU': 'Russian Federation', 'KN': 'Saint Kitts and Nevis', 'SN': 'Senegal', 'RS': 'Serbia', 'SC': 'Seychelles', 'SL': 'Sierra Leone', 'SK': 'Slovakia', 'SI': 'Slovenia', 'ST': 'Sao Tome And Principe', 'ZA': 'South Africa', 'ES': 'Spain', 'SE': 'Sweden', 'CH': 'Switzerland', 'TG': 'Togo', 'TT': 'Trinidad and Tobago', 'TN': 'Tunisia', 'TR': 'Turkey', 'UA': 'Ukraine', 'US': 'United States', 'UY': 'Uruguay', 'VE': 'Venezuela, Bolivarian Republic of', 'ZM': 'Zambia', 'ZW': 'Zimbabwe'}
    return country_dict.get(code, code)
payload = {'comps': '1'}

# HTTP headers for the requests
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

# Payload for the player data request
payload_player = {
    'pageSize': '50',
    'compSeasons': '1',
    'altIds': 'true',
    'page': '0',
    'type': 'player',
    'id': '-1',
    'compSeasonId': '1'
}

# Function to retrieve a list of EPL seasons id
def seasons_list():
    url = 'https://footballapi.pulselive.com/football/competitions/1/compseasons'
    payload_season = {
        'page': '0',
        'pageSize': '100'
    }
    r = requests.get(url, headers= headers, params= payload_season)
    season_list = r.json().get('content')
    season_list = sorted(season_list, key= lambda x: x['id'])
    return season_list

url = 'https://footballapi.pulselive.com/football/players'

# Set to collect unique player IDs
all_player_ids = set()
print('Start collection set of player id')
for season_info in seasons_list():
    season = int(season_info['id'])
    payload_player['compSeasons'] = str(season)
    payload_player['compSeasonId'] = str(season)
    print(f'Season {season_info["label"]}: start')
    page = 0
    while True:
        payload_player['page'] = str(page)
        r = requests.get(url, headers= headers, params= payload_player)
        players = r.json().get('content')
        for player in players:
            all_player_ids.add(int(player['id']))
        page += 1
        if players == []:
            print(f'Season {season_info["label"]}: completed')
            break

cursor.execute('SELECT player_id FROM dbo.players')
existing_player_ids = [row[0] for row in cursor.fetchall()]
new_player_ids = list(all_player_ids.difference(set(existing_player_ids)))
new_player_ids.sort()
print('Completed collection set of player id')
print(f'Need to collect data of {len(new_player_ids)} players')

# Counter variable
i = 1

# Start collecting and inserting data into the database
print('Start inserting to database')
print(f'1st player: Start inserting')
for player_id in new_player_ids:
    url = f'https://footballapi.pulselive.com/football/stats/player/{player_id}'
    if i % 100 == 0:
        print(f'{i}th player: Start inserting')
    i += 1
    r = requests.get(url, headers= headers, params= payload)
    if r.text == '':
        player_id += 1
        continue
    player = r.json().get('entity')
    stats = r.json().get('stats')
    first_name = player['name']['first']
    last_name = player['name']['last']
    position = player['info']['positionInfo'] if 'positionInfo' in player['info'] else None
    if not player['nationalTeam']:
        country = None
    else:
        country = player['nationalTeam']['isoCode']
        country = countryLookup(country)
    if 'date' in player['birth']:
        birth = player['birth']['date']['millis']
        birth = datetime.utcfromtimestamp(0) + timedelta(milliseconds = birth)
        birth = birth.strftime("%Y-%m-%d")
    else:
        birth = None
    appearances_value = next(filter(lambda x: x['name'] == 'appearances', stats), {}).get('value')
    clean_sheets_value = next(filter(lambda x: x['name'] == 'clean_sheet', stats), {}).get('value')
    goals_value = next(filter(lambda x: x['name'] == 'goals', stats), {}).get('value')
    assists_value = next(filter(lambda x: x['name'] == 'goal_assist', stats), {}).get('value')
    red_cards_value = next(filter(lambda x: x['name'] == 'red_card', stats), {}).get('value')
    yellow_cards_value = next(filter(lambda x: x['name'] == 'yellow_card', stats), {}).get('value')
    
    # Handle None values and replace with 0
    appearances = int(appearances_value) if appearances_value is not None else 0
    clean_sheets = int(clean_sheets_value) if clean_sheets_value is not None else 0
    goals = int(goals_value) if goals_value is not None else 0
    assists = int(assists_value) if assists_value is not None else 0
    red_cards = int(red_cards_value) if red_cards_value is not None else 0
    yellow_cards = int(yellow_cards_value) if yellow_cards_value is not None else 0
    
    # Execute the SQL query to insert data into the database
    cursor.execute(insert_query, player_id,first_name,last_name,position,country,birth,appearances,clean_sheets,goals,assists,red_cards,yellow_cards)
    conn.commit()
print('Completed insertion')
conn.close()

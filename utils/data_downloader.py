import pandas as pd
import requests

def download_draft_combine_anthro_data(season="2024-25"):
    url = f'https://stats.nba.com/stats/draftcombineplayeranthro?LeagueID=00&SeasonYear={season}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Origin': 'https://www.nba.com',
        'Referer': 'https://www.nba.com/',
        'Accept': 'application/json, text/plain, */*',
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    headers = data['resultSets'][0]['headers']
    rows = data['resultSets'][0]['rowSet']
    df = pd.DataFrame(rows, columns=headers)

    return df

def download_draft_combine_drill_data(season="2024-25"):
    url = f'https://stats.nba.com/stats/draftcombinedrillresults?LeagueID=00&SeasonYear={season}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Origin': 'https://www.nba.com',
        'Referer': 'https://www.nba.com/',
        'Accept': 'application/json, text/plain, */*',
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()

    headers = data['resultSets'][0]['headers']
    rows = data['resultSets'][0]['rowSet']

    df = pd.DataFrame(rows, columns=headers)

    return df

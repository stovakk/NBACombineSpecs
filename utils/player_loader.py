import pandas as pd

def load_custom_players(path = "utah_players.csv"):
    df = pd.read_csv(path)
    return df
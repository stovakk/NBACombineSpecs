import pandas as pd

def load_custom_players(path = "Utah Players Anthro & Combine(Sheet1).csv"):
    df = pd.read_csv(path)
    return df
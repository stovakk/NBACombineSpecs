import pandas as pd

def load_custom_players(path = "Example of Roster Metrics.csv"):
    df = pd.read_csv(path)
    return df
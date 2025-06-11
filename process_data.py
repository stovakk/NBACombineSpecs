import pandas as pd
from utils.data_downloader import download_draft_combine_anthro_data, download_draft_combine_drill_data
from utils.data_cleaner import clean_and_merge
from components.distance_calculator import calculate_player_distances

# Download data
anthro_data_all = []
drill_data_all = []

for year in range(2000, 2025):
    season = f"{year}-{str(year+1)[2:]}"
    anthro_df = download_draft_combine_anthro_data(season=season)
    anthro_df['Season'] = season
    anthro_data_all.append(anthro_df)

    drill_df = download_draft_combine_drill_data(season=season)
    drill_df['Season'] = season
    drill_data_all.append(drill_df)

# Clean and merge data
merged_df = clean_and_merge(anthro_data_all, drill_data_all)

# Player of interest
player_of_interest = {
    'HEIGHT_WO_SHOES': 80,
    'WINGSPAN': 85,
    'STANDING_REACH': 108,
    'HAND_LENGTH': 8.25,
    'HAND_WIDTH': 8.75
}

# Calculate distances
working_df = calculate_player_distances(merged_df, player_of_interest)

print(working_df.head())

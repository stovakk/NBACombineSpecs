import pandas as pd

def clean_and_merge(anthro_data, drill_data):
    # Clean and select important columns
    combined_anthro = pd.concat(anthro_data, ignore_index=True)
    combined_anthro = combined_anthro[['PLAYER_NAME', 'Season', 'POSITION', 'HEIGHT_WO_SHOES', 'HEIGHT_WO_SHOES_FT_IN', 
                                       'WEIGHT', 'WINGSPAN', 'WINGSPAN_FT_IN', 'STANDING_REACH', 
                                       'STANDING_REACH_FT_IN', 'HAND_LENGTH', 'HAND_WIDTH']]

    combined_drill = pd.concat(drill_data, ignore_index=True)
    combined_drill = combined_drill[['PLAYER_NAME', 'Season', 'STANDING_VERTICAL_LEAP', 'MAX_VERTICAL_LEAP', 
                                     'LANE_AGILITY_TIME', 'MODIFIED_LANE_AGILITY_TIME', 'THREE_QUARTER_SPRINT', 'BENCH_PRESS']]

    # Merge and drop rows without height data
    merged_df = pd.merge(combined_anthro, combined_drill, on=["PLAYER_NAME", "Season"], how="inner")
    merged_df = merged_df.dropna(subset=['HEIGHT_WO_SHOES'])

    return merged_df

import pandas as pd
import numpy as np
import re

def clean_and_merge(anthro_data, drill_data):
    # Filter out empty DataFrames
    anthro_data = [df for df in anthro_data if not df.empty and not df.isna().all(axis=1).all()]
    drill_data = [df for df in drill_data if not df.empty and not df.isna().all(axis=1).all()]

    # Clean and select important columns
    combined_anthro = pd.concat(anthro_data, ignore_index=True)
    combined_anthro = combined_anthro[['PLAYER_NAME', 'Season', 'POSITION', 'HEIGHT_WO_SHOES', 
                                       'WEIGHT', 'WINGSPAN', 'STANDING_REACH', 'HAND_LENGTH', 'HAND_WIDTH']]

    combined_drill = pd.concat(drill_data, ignore_index=True)
    combined_drill = combined_drill[['PLAYER_NAME', 'Season', 'STANDING_VERTICAL_LEAP', 'MAX_VERTICAL_LEAP', 
                                     'LANE_AGILITY_TIME', 'MODIFIED_LANE_AGILITY_TIME', 'THREE_QUARTER_SPRINT', 'BENCH_PRESS']]

    # Convert height and reach from feet/inches to inches
    def convert_to_inches(value):
        if isinstance(value, str):
            matches = re.findall(r"(\d+)' (\d+\.?\d*)", value)
            if matches:
                feet, inches = map(float, matches[0])
                return feet * 12 + inches
        return np.nan

    numeric_anthro_cols = [
    'HEIGHT_WO_SHOES', 'WEIGHT', 'WINGSPAN', 'STANDING_REACH', 'HAND_LENGTH', 'HAND_WIDTH'
    ]

    numeric_drill_cols = [
        'STANDING_VERTICAL_LEAP', 'MAX_VERTICAL_LEAP',
        'LANE_AGILITY_TIME', 'MODIFIED_LANE_AGILITY_TIME',
        'THREE_QUARTER_SPRINT', 'BENCH_PRESS'
    ]


    for col in numeric_anthro_cols:
        combined_anthro[col] = pd.to_numeric(combined_anthro[col], errors='coerce')

    for col in numeric_drill_cols:
        combined_drill[col] = pd.to_numeric(combined_drill[col], errors='coerce')

    # Merge and drop rows without height data
    merged_df = pd.merge(combined_anthro, combined_drill, on=["PLAYER_NAME", "Season"], how="inner")
    merged_df = merged_df.dropna(subset=['HEIGHT_WO_SHOES', 'WINGSPAN', 'STANDING_REACH', 'HAND_LENGTH', 'HAND_WIDTH'])

    return merged_df

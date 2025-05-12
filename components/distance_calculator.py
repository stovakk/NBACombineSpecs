import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def calculate_player_distances(merged_df, player_of_interest):
    player_df = pd.DataFrame([player_of_interest])

    # Normalize the data
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(merged_df[['HEIGHT_WO_SHOES', 'WINGSPAN', 'STANDING_REACH', 'HAND_LENGTH', 'HAND_WIDTH']]),
                             columns=['HEIGHT_WO_SHOES', 'WINGSPAN', 'STANDING_REACH', 'HAND_LENGTH', 'HAND_WIDTH'])
    player_scaled = scaler.transform(player_df[['HEIGHT_WO_SHOES', 'WINGSPAN', 'STANDING_REACH', 'HAND_LENGTH', 'HAND_WIDTH']])

    def calculate_distance(row_scaled, player_scaled):
        diff = row_scaled - player_scaled
        valid_mask = ~np.isnan(diff)
        return np.sqrt(np.sum(diff[valid_mask]**2))

    distances = np.array([calculate_distance(df_scaled.iloc[i].values, player_scaled.flatten()) for i in range(df_scaled.shape[0])])

    # Add the distances to the original DataFrame
    working_df = merged_df.copy()
    working_df['Distance'] = distances
    working_df = working_df.sort_values(by='Distance', ascending=True).reset_index(drop=True)

    return working_df

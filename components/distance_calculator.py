import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def calculate_player_distances(merged_df, player_of_interest):
    # Select only the relevant columns for distance calculation
    features = ['HEIGHT_WO_SHOES', 'WINGSPAN', 'STANDING_REACH', 'HAND_LENGTH', 'HAND_WIDTH']
    
    # Normalize the data
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(merged_df[features]), columns=features)
    player_df = pd.DataFrame([player_of_interest])
    player_scaled = scaler.transform(player_df[features])

    # Calculate distances
    distances = np.sqrt(np.sum((df_scaled.values - player_scaled.flatten())**2, axis=1))

    # Add distances back to the original DataFrame
    results_df = merged_df[['PLAYER_NAME', 'Season']].copy()
    results_df['Distance'] = distances

    # Sort by distance
    results_df = results_df.sort_values(by='Distance', ascending=True).reset_index(drop=True)

    return results_df

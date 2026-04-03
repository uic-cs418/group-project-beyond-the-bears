import pandas as pd
import difflib

# Uses fuzzy matching to standardize names from base_df to match target_df
def standardize_player_names(base_df, target_df, name_col = 'Player', cutoff = 0.8):
    base_players = base_df[name_col].dropna().unique().astype(str)
    target_players = target_df[name_col].dropna().unique().astype(str)
    
    name_mapping = {}
    
    for name in base_players:
        # Look for the closest match in the target dataframe
        closest_match = difflib.get_close_matches(name, target_players, n=1, cutoff=cutoff)
        
        if closest_match:
            name_mapping[name] = closest_match[0]
        else:
            name_mapping[name] = name # Keep original if no close match is found
            
    # Apply the mapping to a copy of the dataframe
    df_updated = base_df.copy()
    df_updated[name_col] = df_updated[name_col].map(name_mapping).fillna(df_updated[name_col])
    
    return df_updated

# Pipeline function that executes the matching and merging of the two dataframes
def build_master_dataset(capology_df, sofascore_df):
    print("Standardizing Capology player names to match Sofascore...")
    capology_standardized = standardize_player_names(capology_df, sofascore_df)
    
    print("Executing Final Inner Merge...")
    final_df = pd.merge(capology_standardized, sofascore_df, on=['Season', 'Player'], how='inner')
    
    print("Merge Complete!")
    return final_df
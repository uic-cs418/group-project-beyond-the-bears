import pandas as pd
import ScraperFC as sfc
import time

# Cleans a single season's Capology DataFrame
# Automatically detects if it's using the new (18-col, 25-26 season) or old (8-col, previous seasons) schema
def clean_capology_df(df, season):
    # Detect schema based on the number of columns
    if df.shape[1] >= 15:
        # Detailed schema (e.g., 18 columns)
        columns_to_keep = [0, 3, 11, 13, 15]
    else:
        # Historical schema (e.g., 8 columns)
        columns_to_keep = [0, 2, 4, 5, 7]
        
    # Isolate the columns we want
    df = df.iloc[:, columns_to_keep]
    
    # Flatten the MultiIndex
    df.columns = df.columns.droplevel(0)
    
    # Standardize column names
    rename_dict = {
        'PLAYER': 'Player',
        'GROSS P/Y\n(EUR)': 'Salary (EUR)',
        'POS.': 'Position',
        'AGE': 'Age',
        'CLUB': 'Club',
    }
    df = df.rename(columns = rename_dict)
    
    # Clean the salary column (convert to string first to handle NaNs safely)
    df['Salary (EUR)'] = df['Salary (EUR)'].astype(str).str.replace(r'[€,\s]', '', regex = True).astype(float)
    
    # Add the season tracking column at the very front
    df.insert(0, 'Season', season)
    
    return df

# Scrapes salary data for a list of seasons and returns a concatenated dataframe
def scrape_capology_multiple_seasons(seasons, league = 'England Premier League', currency = 'eur', sleep_time = 10):
    # Initialize the scraper
    capology_scraper = sfc.Capology()
    all_seasons_data = []
    
    for season in seasons:
        print(f"Scraping data for the {season} season...")
        
        try:
            # Scrape the raw data
            raw_df = capology_scraper.scrape_salaries(year = season, league = league, currency = currency)
            
            # Clean it using our helper function
            clean_df = clean_capology_df(raw_df, season)
            
            # Append to our list
            all_seasons_data.append(clean_df)
            
            print(f"  -> Success! {len(clean_df)} players scraped.")
            
        except Exception as e:
            print(f"  -> Uh oh, something went wrong with {season}: {e}")
            
        # Pause before the next loop
        print(f"  -> Sleeping for {sleep_time} seconds...\n")
        time.sleep(sleep_time)
        
    # Concatenate everything together
    if len(all_seasons_data) > 0:
        master_df = pd.concat(all_seasons_data, ignore_index = True)
        print("Scraping complete! Master DataFrame created.")
        return master_df
    else:
        print("No data was successfully scraped.")
        return None

# Converts the season formating for the Sofascore API
def format_for_sofascore(capology_season):
    years = capology_season.split('-')
    return f"{years[0][-2:]}/{years[1]}"

# Cleans a single season's Sofascore DataFrame
def clean_sofascore_df(df, season_label):
    cols_to_drop = ['team', 'player id', 'team id']
    df = df.drop(columns = cols_to_drop, errors = 'ignore')

    # Fix future warning error (Ignore)
    df = df.dropna(axis=1, how='all')
    
    # Inserts the Sofascore-formatted season
    df.insert(0, 'Season', season_label) 
    
    return df

# Scrapes Sofascore player stats for a list of seasons and returns a concatenated dataframe
def scrape_sofascore_multiple_seasons(seasons, league = 'England Premier League', sleep_time = 15):
    # Initialize the scraper
    sofa = sfc.Sofascore()
    all_seasons_data = []
    
    for capology_season in seasons:
        # Translate the season string for the API
        sofa_season = format_for_sofascore(capology_season)
        print(f"Scraping Sofascore data for the {capology_season} season (API format: {sofa_season})...")
        
        try:
            # Fetch data using the translated 'sofa_season'
            raw_df = sofa.scrape_player_league_stats(year = sofa_season, league = league)
            
            # Clean data and add a season column
            clean_df = clean_sofascore_df(raw_df, capology_season)
            
            all_seasons_data.append(clean_df)
            print(f"  -> Success! {len(clean_df)} players scraped. Columns: {len(clean_df.columns)}")
            
        except Exception as e:
            print(f"  -> Uh oh, something went wrong with {capology_season}: {e}")
            
        print(f"  -> Sleeping for {sleep_time} seconds...\n")
        time.sleep(sleep_time)
        
    if len(all_seasons_data) > 0:
        master_df = pd.concat(all_seasons_data, ignore_index = True)
        master_df = master_df.dropna(axis = 1)
        master_df = master_df.rename(columns={'player': 'Player'})
        print("Scraping complete! Sofascore Master DataFrame created.")
        return master_df
    else:
        print("No data was successfully scraped.")
        return None
import pandas as pd
import json
import os
import numpy as np

# File names
INPUT_REVIEWS = 'reviews_met_topics.json'
INPUT_WEATHER = 'weather_data.csv'
OUTPUT_FILE = 'final_data_for_powerbi.json'

def merge_data():
    print("Starting integration with weather data...")

    # 1. Load reviews
    if not os.path.exists(INPUT_REVIEWS):
        print(f"ERROR: '{INPUT_REVIEWS}' not found.")
        return
        
    with open(INPUT_REVIEWS, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df_reviews = pd.DataFrame.from_records(data['reviews'])
    print(f"{len(df_reviews)} reviews loaded.")

    # 2. Load weather data
    if not os.path.exists(INPUT_WEATHER):
        print(f"ERROR: '{INPUT_WEATHER}' not found.")
        return
        
    df_weather = pd.read_csv(INPUT_WEATHER)
    print(f"{len(df_weather)} days of weather data loaded.")
    
    # DEBUG: Show found columns
    print(f"Weather columns found: {list(df_weather.columns)}")

    # 3. Clean and prepare for merge
    # Extract date from 'createTime' (YYYY-MM-DD)
    df_reviews['datum'] = df_reviews['createTime'].str[:10]
    
    # FIX 1: Check specifically for lowercase 'date' and rename to 'datum'
    if 'date' in df_weather.columns:
        df_weather = df_weather.rename(columns={'date': 'datum'})
    elif 'Date' in df_weather.columns:
        df_weather = df_weather.rename(columns={'Date': 'datum'})
        
    # Check if rename was successful
    if 'datum' not in df_weather.columns:
        print("ERROR: Could not find 'date' column in weather CSV.")
        return

    # Ensure date columns are strings for matching
    df_weather['datum'] = df_weather['datum'].astype(str)

    # 4. Merge on date
    print("Merging data based on date...")
    
    # FIX 2: Use the exact column names from your CSV file
    # We want: 'datum' + max temp + precipitation
    weather_cols_to_keep = ['datum']
    
    if 'temp_max_c' in df_weather.columns:
        weather_cols_to_keep.append('temp_max_c')
    if 'precip_amount_mm' in df_weather.columns:
        weather_cols_to_keep.append('precip_amount_mm')
    if 'temp_avg_c' in df_weather.columns:
        weather_cols_to_keep.append('temp_avg_c')

    # Merge!
    df_final = pd.merge(
        df_reviews, 
        df_weather[weather_cols_to_keep], 
        on='datum', 
        how='left'
    )
    
    # Remove temporary date column used for merging
    df_final = df_final.drop(columns=['datum'])
    
    print(f"Final DataFrame ready with {len(df_final.columns)} columns.")

    # 5. Save final file
    print(f"Saving to '{OUTPUT_FILE}'...")
    
    # Convert NaN to None (null) for Power BI compatibility
    df_final_for_json = df_final.replace({np.nan: None})
    output_data = {"reviews": df_final_for_json.to_dict('records')}
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nDone! '{OUTPUT_FILE}' is the final file for Power BI.")

if __name__ == "__main__":
    merge_data()
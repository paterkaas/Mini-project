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
    
    # Gebruik 'zinnen' in plaats van 'reviews'
    df_reviews = pd.DataFrame.from_records(data['zinnen']) 
    print(f"{len(df_reviews)} zinnen geladen voor integratie.")

    # 2. Load weather data
    if not os.path.exists(INPUT_WEATHER):
        print(f"ERROR: '{INPUT_WEATHER}' not found.")
        return
        
    df_weather = pd.read_csv(INPUT_WEATHER)
    print(f"{len(df_weather)} dagen weersgegevens geladen.")

    # 3. Voorbereiden voor merge
    # De datum in createTime is bijv. "2024-08-15T10:00:00Z", we pakken de eerste 10 tekens
    df_reviews['datum'] = df_reviews['createTime'].str[:10]
    
    # Kolomnaam in weer-bestand uniform maken
    if 'date' in df_weather.columns:
        df_weather = df_weather.rename(columns={'date': 'datum'})
    elif 'Date' in df_weather.columns:
        df_weather = df_weather.rename(columns={'Date': 'datum'})
        
    if 'datum' not in df_weather.columns:
        print("ERROR: Kon geen datum-kolom vinden in weather CSV.")
        return

    df_weather['datum'] = df_weather['datum'].astype(str)

    # 4. Mergen op datum
    print("Samenvoegen op basis van datum...")
    
    weather_cols_to_keep = ['datum']
    if 'temp_max_c' in df_weather.columns:
        weather_cols_to_keep.append('temp_max_c')
    if 'precip_amount_mm' in df_weather.columns:
        weather_cols_to_keep.append('precip_amount_mm')
    if 'temp_avg_c' in df_weather.columns:
        weather_cols_to_keep.append('temp_avg_c')

    df_final = pd.merge(
        df_reviews, 
        df_weather[weather_cols_to_keep], 
        on='datum', 
        how='left'
    )
    
    # Tijdelijke datum-kolom verwijderen
    df_final = df_final.drop(columns=['datum'])
    
    # 5. Opslaan
    print(f"Opslaan naar '{OUTPUT_FILE}'...")
    df_final_for_json = df_final.replace({np.nan: None})
    output_data = {"reviews": df_final_for_json.to_dict('records')}
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nSucces! '{OUTPUT_FILE}' is klaar voor Power BI.")

if __name__ == "__main__":
    merge_data()
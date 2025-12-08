import pandas as pd
import json
import os
import numpy as np

# Bestandsnamen
INPUT_REVIEWS = 'reviews_met_topics.json'
INPUT_WEATHER = 'weather_data.csv'
OUTPUT_FILE = 'final_data_for_powerbi.json' # Het definitieve bestand!

def merge_data():
    print("Starten met data-integratie met weerdata...")

    # 1. Laad de reviews
    if not os.path.exists(INPUT_REVIEWS):
        print(f"FOUT: '{INPUT_REVIEWS}' niet gevonden.")
        return
        
    with open(INPUT_REVIEWS, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df_reviews = pd.DataFrame.from_records(data['reviews'])
    print(f"{len(df_reviews)} reviews geladen.")

    # 2. Laad de weerdata
    if not os.path.exists(INPUT_WEATHER):
        print(f"FOUT: '{INPUT_WEATHER}' niet gevonden.")
        return
        
    df_weather = pd.read_csv(INPUT_WEATHER)
    print(f"{len(df_weather)} dagen weerdata geladen.")


    # 3. Opschonen en klaarmaken voor merge
    
    # Haal de datum uit de 'createTime' timestamp van de reviews
    # De tijdstempel is in formaat YYYY-MM-DDTHH:MM:SSZ
    df_reviews['datum'] = df_reviews['createTime'].str[:10] # pakt de eerste 10 karakters (YYYY-MM-DD)
    
    # We verwachten dat de weerdata een kolom 'Date' heeft (of pas dit hier aan)
    df_weather = df_weather.rename(columns={'Date': 'datum'})

    # Zorg dat de datum-kolommen hetzelfde datatype hebben (string)
    df_weather['datum'] = df_weather['datum'].astype(str)

    # 4. Merge de twee datasets op 'datum'
    # 'left' merge zorgt ervoor dat alle reviews behouden blijven
    print("Data aan het mergen op datum...")
    df_final = pd.merge(
        df_reviews, 
        df_weather[['datum', 'TMAX', 'PRCP', 'SNOW']], # Selecteer alleen relevante weer-kolommen
        on='datum', 
        how='left'
    )
    
    # Verwijder de tijdelijke 'datum' kolom
    df_final = df_final.drop(columns=['datum'])
    
    print(f"Definitief DataFrame klaar met {len(df_final.columns)} kolommen.")

    # 5. Opslaan van het definitieve bestand (met NaN -> null conversie voor Power BI)
    print(f"Opslaan naar '{OUTPUT_FILE}'...")
    
    # Converteer NaN naar None/null, wat essentieel is voor Power BI's JSON-import
    df_final_for_json = df_final.replace({np.nan: None})
    output_data = {"reviews": df_final_for_json.to_dict('records')}
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nKlaar! '{OUTPUT_FILE}' is het definitieve, complete bestand voor Power BI.")

if __name__ == "__main__":
    merge_data()
import pandas as pd
import io
import re
import os

INPUT_FILE = 'result.txt'
OUTPUT_FILE = 'weather_data.csv'

# 1. Definieer de kolomnaam-vertalingen
# Gebaseerd op de KNMI-beschrijvingen in het bestand
RENAME_MAP = {
    'TG': 'temp_avg_c',
    'TN': 'temp_min_c',
    'TX': 'temp_max_c',
    'DR': 'precip_duration_h',
    'RH': 'precip_amount_mm',
    'RHX': 'precip_max_hourly_mm'
}
# Kolommen die we moeten delen door 10
# (Allemaal behalve de ID's)
COLS_TO_CONVERT = ['TG', 'TN', 'TX', 'DR', 'RH', 'RHX']

def parse_knmi_data():
    """
    Leest het complexe KNMI-tekstbestand, schoont het op en slaat het op als CSV.
    """
    if not os.path.exists(INPUT_FILE):
        print(f"FOUT: '{INPUT_FILE}' niet gevonden.")
        print(f"Zorg dat '{INPUT_FILE}' in dezelfde map staat als het script.")
        return

    print(f"Starten met parsen van '{INPUT_FILE}'...")
    
    header_line = None
    data_lines = []

    # --- Stap 1: Lees het bestand en scheid data van commentaar ---
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            stripped_line = line.strip()
            
            # Check voor commentaar/header regels
            if stripped_line.startswith('#'):
                # Zoek de daadwerkelijke data-header
                if 'STN,YYYYMMDD' in stripped_line:
                    header_line = stripped_line.replace('#', '').strip()
                continue
            
            # Als het geen commentaar is, is het een (fragment van een) data-regel
            if stripped_line:
                data_lines.append(stripped_line)

    if not header_line:
        print("FOUT: Kon de header-regel ('# STN,YYYYMMDD,...') niet vinden in het bestand.")
        return

    # --- Stap 2: Repareer gebroken dataregels ---
    # Voeg alle data-fragmenten samen tot één lange string
    # Vervang newlines door spaties (voor het geval dat)
    full_data_string = " ".join(data_lines).replace('\n', ' ')
    
    # Split de string op basis van de '370,' stationcode
    # Dit zorgt ervoor dat elke dataregel correct begint
    # We gebruiken een 'positive lookahead' '(?=370,)' om te splitten *voor* de code
    processed_lines = re.split(r'(?=370,)', full_data_string)

    # Filter eventuele lege strings uit het resultaat
    clean_data_rows = [line.strip() for line in processed_lines if line.strip()]

    # --- Stap 3: Maak een "virtueel" CSV-bestand in het geheugen ---
    
    # Maak de header schoon (verwijder extra spaties)
    header = re.sub(r'\s*,\s*', ',', header_line)
    cols = header.split(',')
    
    csv_data_io = io.StringIO()
    csv_data_io.write(header + '\n') # Schrijf de schone header
    
    for line in clean_data_rows:
        # Maak de dataregel schoon (verwijder extra spaties)
        clean_line = re.sub(r'\s*,\s*', ',', line)
        csv_data_io.write(clean_line + '\n')
        
    # Spoel terug naar het begin van het virtuele bestand
    csv_data_io.seek(0)

    # --- Stap 4: Lees het virtuele bestand in met Pandas ---
    print("Data inlezen in pandas...")
    try:
        df = pd.read_csv(csv_data_io, sep=',')
    except Exception as e:
        print(f"FOUT: Er ging iets mis bij het inlezen van de data in pandas: {e}")
        return

    # --- Stap 5: Data opschonen en converteren ---
    print("Data opschonen (eenheden converteren, datums omzetten)...")
    
    # Converteer datumkolom
    df['YYYYMMDD'] = pd.to_datetime(df['YYYYMMDD'], format='%Y%m%d')
    df.rename(columns={'YYYYMMDD': 'date'}, inplace=True)
    
    # Converteer de meetwaarden
    for col in COLS_TO_CONVERT:
        if col in df.columns:
            # Converteer naar numeriek, fouten worden 'NaN' (Not a Number)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Speciale waarde: -1 (voor neerslag) betekent <0.05, we maken er 0 van
            df[col] = df[col].replace(-1, 0)
            
            # Converteer de eenheid (0.1 graden/mm/uur naar 1.0)
            df[col] = df[col] / 10.0
        
    # Hernoem kolommen naar duidelijke namen
    df.rename(columns=RENAME_MAP, inplace=True)
    
    # Verwijder kolommen die we niet hebben hernoemd (als die er zijn)
    # Dit ruimt eventuele lege kolommen op
    df = df[[col for col in df.columns if col in ['STN', 'date'] + list(RENAME_MAP.values())]]

    # --- Stap 6: Opslaan als schone CSV ---
    try:
        df.to_csv(OUTPUT_FILE, index=False, date_format='%Y-%m-%d')
        print("\n--- Voltooid ---")
        print(f"Succesvol {len(df)} dataregels verwerkt.")
        print(f"Schone data opgeslagen in: '{OUTPUT_FILE}'")
    except Exception as e:
        print(f"\nFOUT: Kon het CSV-bestand niet wegschrijven: {e}")


# --- Voer de functie uit als het script direct wordt gerund ---
# DEZE REGELS ZIJN ESSENTIEEL!
if __name__ == "__main__":
    parse_knmi_data()
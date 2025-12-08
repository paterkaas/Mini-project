import pandas as pd
import os

INPUT_FILE = 'weather_data.csv'

def analyze_weather_data():
    """
    Laadt de schone CSV met weerdata en print een samenvatting.
    """
    
    # --- 1. Controleer of het bestand bestaat ---
    if not os.path.exists(INPUT_FILE):
        print(f"FOUT: Bestand '{INPUT_FILE}' niet gevonden.")
        print("Heb je het 'parse_weather.py' script al succesvol gedraaid?")
        return

    print(f"--- Analyse van {INPUT_FILE} ---")

    # --- 2. Laad de data ---
    try:
        # We geven aan dat de 'date'-kolom als datum ingelezen moet worden
        df = pd.read_csv(INPUT_FILE, parse_dates=['date'])
    except Exception as e:
        print(f"FOUT: Kon het bestand '{INPUT_FILE}' niet inlezen. Error: {e}")
        return

    # --- 3. Basis-informatie ---
    print(f"\nData succesvol geladen.")
    print(f"Totaal aantal dagen met data: {len(df)}")
    
    # Datumbereik
    min_date = df['date'].min().strftime('%d-%m-%Y')
    max_date = df['date'].max().strftime('%d-%m-%Y')
    print(f"Datumbereik: van {min_date} tot {max_date}")
    
    # --- 4. Temperatuur Analyse ---
    print("\n🌡️ Temperatuur Analyse (in Graden Celsius)")
    
    # Gemiddelde
    avg_temp = df['temp_avg_c'].mean()
    print(f"  Gemiddelde temperatuur (hele periode): {avg_temp:.2f}°C")
    
    # Warmste dag (hoogste maximum)
    max_temp_val = df['temp_max_c'].max()
    max_temp_date = df.loc[df['temp_max_c'].idxmax()]['date'].strftime('%d-%m-%Y')
    print(f"  Warmste dag ooit gemeten: {max_temp_val}°C (op {max_temp_date})")

    # Koudste dag (laagste minimum)
    min_temp_val = df['temp_min_c'].min()
    min_temp_date = df.loc[df['temp_min_c'].idxmin()]['date'].strftime('%d-%m-%Y')
    print(f"  Koudste dag ooit gemeten: {min_temp_val}°C (op {min_temp_date})")

    # --- 5. Neerslag Analyse ---
    print("\n🌧️ Neerslag Analyse (in Millimeters)")
    
    # Totaal
    total_precip = df['precip_amount_mm'].sum()
    print(f"  Totale neerslag (hele periode): {total_precip:.1f} mm")
    
    # Natste dag
    wettest_day_val = df['precip_amount_mm'].max()
    wettest_day_date = df.loc[df['precip_amount_mm'].idxmax()]['date'].strftime('%d-%m-%Y')
    print(f"  Natste dag ooit gemeten: {wettest_day_val} mm (op {wettest_day_date})")
    
    # Aantal dagen zonder neerslag
    dry_days = len(df[df['precip_amount_mm'] == 0])
    print(f"  Aantal dagen zonder meetbare neerslag: {dry_days} dagen")

    # --- 6. Statistische Samenvatting ---
    print("\n--- Statistische Samenvatting ---")
    # .describe() geeft een mooi overzicht van alle numerieke kolommen
    # .round(2) rondt de getallen af op 2 decimalen
    print(df.describe().round(2))
    
    print("\n--- Eerste 5 rijen van de data ---")
    print(df.head())


# --- Voer de functie uit als het script direct wordt gerund ---
if __name__ == "__main__":
    analyze_weather_data()
import subprocess
import sys
import time
import os

def run_script(script_name):
    """
    Voert een Python-script uit en stopt de pijplijn als er een fout optreedt.
    """
    print(f"\n{'='*60}")
    print(f"STARTING: {script_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Gebruik de huidige Python-interpreter om het script aan te roepen
        result = subprocess.run([sys.executable, script_name], check=True)
        elapsed = time.time() - start_time
        print(f"DONE: {script_name} succesvol uitgevoerd in {elapsed:.1f} seconden.")
        
    except subprocess.CalledProcessError:
        print(f"\nERROR: Er is iets misgegaan tijdens het uitvoeren van '{script_name}'.")
        sys.exit(1)

def main():
    print("--- STARTING AUTOMATIC DATA PIELINE (INCL. HISTORISCHE VAKANTIES) ---")
    
    # Voer de standaard stappen uit
    run_script('clean_reviews.py')
    run_script('analyse_sentiment.py')
    run_script('analyse_topics.py')
    run_script('merge_with_weather.py')
    
    # --- NIEUW: VAKANTIEDATA TOEVOEGEN (2017-2025) ---
    # Deze stap moet ná de merge met het weer komen, omdat het de finale JSON verrijkt.
    run_script('add_holidays.py')

    # --- TUSSENBESTANDEN VERWIJDEREN ---
    print("\nOpschonen van tussenbestanden...")
    intermediate_files = [
        'cleaned_reviews.json', 
        'reviews_met_sentiment.json', 
        'reviews_met_topics.json'
    ]
    
    for file in intermediate_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Verwijderd: {file}")

    print("\n" + "="*60)
    print("SUCCES! De volledige dataset inclusief weer en vakanties is klaar.")
    print("Bestand: 'final_data_for_powerbi.json'")
    print("="*60)

if __name__ == "__main__":
    main()
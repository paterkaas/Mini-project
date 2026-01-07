import subprocess
import sys
import time
import os

def run_script(script_name):
    """
    Runs a Python script and stops the pipeline if an error occurs.
    """
    print(f"\n{'='*60}")
    print(f"STARTING: {script_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        elapsed = time.time() - start_time
        print(f"DONE: {script_name} successfully executed in {elapsed:.1f} seconds.")
        
    except subprocess.CalledProcessError:
        print(f"\nERROR: Something went wrong while executing '{script_name}'.")
        sys.exit(1)

def main():
    print("--- STARTING AUTOMATIC DATA PIPELINE ---")
    
    # Voer de stappen uit
    run_script('clean_reviews.py')
    run_script('analyse_sentiment.py')
    run_script('analyse_topics.py')
    run_script('merge_with_weather.py')

    # --- NIEUW: TUSSENBESTANDEN VERWIJDEREN ---
    print("\nCleaning up intermediate files...")
    intermediate_files = [
        'cleaned_reviews.json', 
        'reviews_met_sentiment.json', 
        'reviews_met_topics.json'
    ]
    
    for file in intermediate_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed: {file}")

    print("\n" + "="*60)
    print("SUCCESS! Only 'final_data_for_powerbi.json' remains.")
    print("="*60)

if __name__ == "__main__":
    main()
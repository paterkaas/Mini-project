import subprocess
import sys
import time

def run_script(script_name):
    """
    Runs a Python script and stops the pipeline if an error occurs.
    """
    print(f"\n{'='*60}")
    print(f"STARTING: {script_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Run the script
        result = subprocess.run([sys.executable, script_name], check=True)
        
        elapsed = time.time() - start_time
        print(f"DONE: {script_name} successfully executed in {elapsed:.1f} seconds.")
        
    except subprocess.CalledProcessError:
        print(f"\nERROR: Something went wrong while executing '{script_name}'.")
        print("The pipeline has stopped. Fix the error and try again.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\nERROR: Could not find file '{script_name}'.")
        print("Ensure you are in the correct folder and the filename is correct.")
        sys.exit(1)

def main():
    print("--- STARTING AUTOMATIC DATA PIPELINE ---")
    
    # STEP 1: Clean Data
    run_script('clean_reviews.py')

    # STEP 2: Sentiment Analysis
    run_script('analyse_sentiment.py')

    # STEP 3: Topic Modeling
    run_script('analyse_topics.py')

    # STEP 4: Enrich with Weather Data
    run_script('merge_with_weather.py')

    print("\n" + "="*60)
    print("SUCCESS! The full pipeline has completed.")
    print("You can now open 'final_data_for_powerbi.json' in Power BI.")
    print("="*60)

if __name__ == "__main__":
    main()
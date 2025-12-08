import json
import os

INPUT_FILE = 'terspegelt.json'
OUTPUT_FILE = 'cleaned_reviews.json'

# 1. Mapping to convert string ratings to numbers
RATING_MAP = {
    "FIVE": 5,
    "FOUR": 4,
    "THREE": 3,
    "TWO": 2,
    "ONE": 1
}

def clean_review_data():
    """
    Reads the combined JSON file, cleans the data,
    and saves it to a new file.
    """
    
    # --- 1. Load the file ---
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: File '{INPUT_FILE}' not found.")
        print("Please run 'combined_reviews.py' first.")
        return

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"ERROR: Could not read JSON from '{INPUT_FILE}'. Is the file corrupt?")
        return

    if 'reviews' not in data or not isinstance(data['reviews'], list):
        print(f"ERROR: '{INPUT_FILE}' does not have the expected structure (no 'reviews' list).")
        return

    original_count = len(data['reviews'])
    print(f"Starting cleaning process... {original_count} reviews found in '{INPUT_FILE}'.")

    # --- 2. Clean data ---
    cleaned_reviews_list = []
    processed_ids = set()  # Set to track duplicates
    skipped_count = 0
    duplicate_count = 0

    for review in data['reviews']:
        
        # 2a. Check for duplicates
        review_id_full = review.get('name')
        if not review_id_full:
            print("WARNING: Review found without 'name' (ID). Skipping.")
            skipped_count += 1
            continue
            
        if review_id_full in processed_ids:
            duplicate_count += 1
            continue  # This is a duplicate, skip
        processed_ids.add(review_id_full)

        # 2b. Convert rating
        rating_str = review.get('starRating')
        rating_int = RATING_MAP.get(rating_str)  # Returns 'None' if rating does not exist

        # 2c. Get reviewer name
        reviewer_name = review.get('reviewer', {}).get('displayName')

        # 2d. Filter: Skip reviews without rating or name
        if not rating_int or not reviewer_name:
            skipped_count += 1
            continue

        # 2e. Build the new, clean object
        cleaned_review = {
            "reviewId": review_id_full.split('/')[-1],  # A shorter, cleaner ID
            "reviewerName": reviewer_name,
            "rating": rating_int,
            "createTime": review.get('createTime'),
            "comment": review.get('comment'),  # Get review comment (if present)
            "replyComment": review.get('reviewReply', {}).get('comment') # Get reply (if present)
        }
        
        cleaned_reviews_list.append(cleaned_review)

    # --- 3. Save the result ---
    cleaned_data_output = {"reviews": cleaned_reviews_list}

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data_output, f, indent=2, ensure_ascii=False)
        
        print("\n--- Cleaning Completed ---")
        print(f"Total {original_count} reviews processed.")
        print(f"  {duplicate_count} duplicates removed.")
        print(f"  {skipped_count} reviews skipped (missing rating or name).")
        print(f"**{len(cleaned_reviews_list)} clean reviews** saved in '{OUTPUT_FILE}'.")

    except Exception as e:
        print(f"\nERROR: Could not write clean file '{OUTPUT_FILE}': {e}")

if __name__ == "__main__":
    clean_review_data()
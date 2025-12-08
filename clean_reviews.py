import json
import os

INPUT_FILE = 'combined_reviews.json'
OUTPUT_FILE = 'cleaned_reviews.json'

# 1. Mapping om string-ratings om te zetten naar getallen
RATING_MAP = {
    "FIVE": 5,
    "FOUR": 4,
    "THREE": 3,
    "TWO": 2,
    "ONE": 1
}

def clean_review_data():
    """
    Leest het gecombineerde JSON-bestand, schoont de data op, 
    en slaat het op in een nieuw bestand.
    """
    
    # --- 1. Inladen van het bestand ---
    if not os.path.exists(INPUT_FILE):
        print(f"FOUT: Bestand '{INPUT_FILE}' niet gevonden.")
        print("Voer eerst het script 'combineer_reviews.py' uit.")
        return

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"FOUT: Kon JSON niet lezen uit '{INPUT_FILE}'. Is het bestand corrupt?")
        return

    if 'reviews' not in data or not isinstance(data['reviews'], list):
        print(f"FOUT: '{INPUT_FILE}' heeft niet de verwachte structuur (geen 'reviews'-lijst).")
        return

    original_count = len(data['reviews'])
    print(f"Starten met opschonen... {original_count} reviews gevonden in '{INPUT_FILE}'.")

    # --- 2. Data opschonen ---
    cleaned_reviews_list = []
    processed_ids = set()  # Set om duplicaten bij te houden
    skipped_count = 0
    duplicate_count = 0

    for review in data['reviews']:
        
        # 2a. Check op duplicaten
        review_id_full = review.get('name')
        if not review_id_full:
            print("WAARSCHUWING: Review zonder 'name' (ID) gevonden. Wordt overgeslagen.")
            skipped_count += 1
            continue
            
        if review_id_full in processed_ids:
            duplicate_count += 1
            continue  # Dit is een duplicaat, sla over
        processed_ids.add(review_id_full)

        # 2b. Converteer rating
        rating_str = review.get('starRating')
        rating_int = RATING_MAP.get(rating_str)  # Geeft 'None' als de rating niet bestaat

        # 2c. Haal reviewer naam op (en 'plat' de structuur)
        reviewer_name = review.get('reviewer', {}).get('displayName')

        # 2d. Filter: Sla reviews zonder rating of naam over
        if not rating_int or not reviewer_name:
            skipped_count += 1
            continue

        # 2e. Bouw het nieuwe, schone object
        # We pakken alleen de velden die we willen houden
        cleaned_review = {
            "reviewId": review_id_full.split('/')[-1],  # Een kortere, schone ID
            "reviewerName": reviewer_name,
            "rating": rating_int,
            "createTime": review.get('createTime'),
            "comment": review.get('comment'),  # Pak het review-commentaar (indien aanwezig)
            "replyComment": review.get('reviewReply', {}).get('comment') # Pak het antwoord (indien aanwezig)
        }
        
        cleaned_reviews_list.append(cleaned_review)

    # --- 3. Opslaan van het resultaat ---
    
    # We slaan het op in dezelfde structuur als het origineel
    cleaned_data_output = {"reviews": cleaned_reviews_list}

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data_output, f, indent=2, ensure_ascii=False)
        
        print("\n--- Opschonen Voltooid ---")
        print(f"Totaal {original_count} reviews verwerkt.")
        print(f"  {duplicate_count} duplicaten verwijderd.")
        print(f"  {skipped_count} reviews overgeslagen (mistte rating of naam).")
        print(f"**{len(cleaned_reviews_list)} schone reviews** opgeslagen in '{OUTPUT_FILE}'.")

    except Exception as e:
        print(f"\nFOUT: Kon het schone bestand '{OUTPUT_FILE}' niet wegschrijven: {e}")

# --- Voer de functie uit als het script direct wordt gerund ---
if __name__ == "__main__":
    clean_review_data()
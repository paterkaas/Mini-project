import json
import pandas as pd
from transformers import pipeline
import os
import nltk
from nltk.tokenize import sent_tokenize

# Zorg dat de benodigde data voor zinssegmentatie aanwezig is
nltk.download('punkt')
nltk.download('punkt_tab')

INPUT_FILE = 'cleaned_reviews.json'
OUTPUT_FILE = 'reviews_met_sentiment.json'

def split_reviews_to_sentences(df):
    """Splitst volledige reviews op in losse zinnen met behoud van metadata."""
    zinnen_data = []
    print("Reviews opsplitsen in zinnen...")
    for _, row in df.iterrows():
        review_text = str(row['comment']) if row['comment'] else ""
        zinnen = sent_tokenize(review_text)
        for zin in zinnen:
            if len(zin.strip()) > 5:  # Filter zeer korte fragmenten
                zinnen_data.append({
                    'reviewId': row.get('reviewId'),
                    'zin_tekst': zin,
                    'originele_rating': row.get('rating'),
                    'createTime': row.get('createTime'),
                    'reviewerName': row.get('reviewerName')
                })
    return pd.DataFrame(zinnen_data)

def analyze_sentiment():
    print("Stap 1: Data laden...")
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: '{INPUT_FILE}' niet gevonden.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame.from_records(data['reviews'])
    
    # Filter reviews met tekst
    df_comments = df.dropna(subset=['comment']).copy()
    
    # Nieuw: Opsplitsen naar zinnen voor nauwkeuriger sentiment per aspect
    df_zinnen = split_reviews_to_sentences(df_comments)
    print(f"{len(df_zinnen)} zinnen gegenereerd uit {len(df_comments)} reviews.")

    print("Stap 2: Sentiment model laden...")
    model_name = "DTAI-KULeuven/robbert-v2-dutch-sentiment"
    sentiment_pipeline = pipeline("sentiment-analysis", model=model_name, tokenizer=model_name)

    print("Stap 3: Sentiment per zin analyseren...")
    zinnen_lijst = df_zinnen['zin_tekst'].tolist()
    
    # We analyseren de zinnen nu één voor één in een loop met een voortgangsbalk
    from tqdm import tqdm
    sentiments = []
    for zin in tqdm(zinnen_lijst, desc="Analyseren"):
        res = sentiment_pipeline(zin, truncation=True, max_length=512)
        sentiments.append(res[0])

    df_zinnen['sentiment_label'] = [s['label'] for s in sentiments]
    df_zinnen['sentiment_score'] = [s['score'] for s in sentiments]

    print(f"Stap 4: Resultaten opslaan naar '{OUTPUT_FILE}'...")
    output_data = {
        "metadata": {"total_sentences": len(df_zinnen)},
        "zinnen": df_zinnen.to_dict('records')
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print("Klaar!")

if __name__ == "__main__":
    analyze_sentiment()
import json
import pandas as pd
from transformers import pipeline
import os

INPUT_FILE = 'cleaned_reviews.json'
OUTPUT_FILE = 'reviews_met_sentiment.json'

# 1. Laad de schone data in een pandas DataFrame
print("Stap 1: Data laden...")
if not os.path.exists(INPUT_FILE):
    print(f"FOUT: '{INPUT_FILE}' niet gevonden. Heb je het clean-script al gedraaid?")
    exit()

try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Zet de lijst 'reviews' om in een DataFrame
    df = pd.DataFrame.from_records(data['reviews'])

    print(f"{len(df)} reviews geladen.")

except Exception as e:
    print(f"FOUT: Kon data niet laden. {e}")
    exit()


# 2. Filter op reviews die een commentaar hebben
df_comments = df.dropna(subset=['comment']).copy()
print(f"{len(df_comments)} reviews met commentaar gevonden om te analyseren.")

# 3. Laad het Nederlandse Sentiment Model
print("Stap 2: Sentiment-model laden (kan even duren)...")
model_name = "DTAI-KULeuven/robbert-v2-dutch-sentiment"
sentiment_pipeline = pipeline(
    "sentiment-analysis", 
    model=model_name, 
    tokenizer=model_name
)

# 4. Voer de sentiment-analyse uit
print("Stap 3: Sentiment aan het analyseren...")
comments_list = df_comments['comment'].tolist()

# FIX: 'truncation=True' voorkomt errors bij te lange reviews
sentiments = sentiment_pipeline(comments_list, truncation=True, max_length=512)

df_comments['sentiment_label'] = [s['label'] for s in sentiments]
df_comments['sentiment_score'] = [s['score'] for s in sentiments]

print("Analyse voltooid.")
# NIEUWE STAP 4.5: Model Validatie - Print een steekproef

print("\n--- Sentiment Validatie Steekproef (5 willekeurige resultaten) ---")
# Filter de geanalyseerde reviews en selecteer 5 willekeurige rijen
validation_sample = df_comments.sample(n=5, random_state=42) # Gebruik random_state voor reproduceerbaarheid

for index, row in validation_sample.iterrows():
    print(f"\nReview: {row['comment'][:150]}...") # Maximaal 150 tekens
    print(f" -> Label: {row['sentiment_label']}")
    print(f" -> Score: {row['sentiment_score']:.4f}")

# (De rest van het script gaat verder met opslaan...)

# 5. Voeg de sentiment-data samen met de originele data
df = df.join(df_comments[['sentiment_label', 'sentiment_score']])

# 6. Sla het verrijkte bestand op
print(f"Stap 4: Resultaten opslaan naar '{OUTPUT_FILE}'...")
output_data = {"reviews": df.to_dict('records')}

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"Klaar! '{OUTPUT_FILE}' is succesvol aangemaakt.")
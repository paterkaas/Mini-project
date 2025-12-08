import json
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import os
import numpy as np # Nodig om NaN correct te vervangen

INPUT_FILE = 'reviews_met_sentiment.json'
OUTPUT_FILE = 'reviews_met_topics.json' # Het definitieve bestand!

def analyze_topics():
    """
    Leest het bestand met sentiment, voegt topics toe, en slaat
    een Power BI-compatibel JSON-bestand op (zet NaN om naar null).
    """

    # --- 1. Laad de data met sentiment ---
    print("Stap 1: Data met sentiment laden...")
    if not os.path.exists(INPUT_FILE):
        print(f"FOUT: '{INPUT_FILE}' niet gevonden. Heb je 'analyseer_sentiment.py' al gedraaid?")
        return
        
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame.from_records(data['reviews'])
        print(f"{len(df)} reviews ingeladen.")
    except Exception as e:
        print(f"FOUT: Kon data niet laden. {e}")
        return

    # --- 2. Filter op reviews met commentaar (NEGEERT DE NaN WAARDEN) ---
    df_comments = df.dropna(subset=['comment']).copy()
    comments_list = df_comments['comment'].tolist()
    print(f"{len(comments_list)} commentaren gevonden om te clusteren (NaNs genegeerd).")

    if len(comments_list) == 0:
        print("Geen commentaren gevonden om te analyseren. Script stopt.")
        # We maken wel een leeg, maar geldig, bestand voor PowerBI
        df['topic_nr'] = np.nan 
    else:
        # --- 3. Stel het Topic Model in ---
        print("Stap 2: Modellen laden voor topic modeling...")
        sentence_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

        topic_model = BERTopic(
            embedding_model=sentence_model,
            language="multilingual",
            nr_topics="auto",
            verbose=True
        )

        # --- 4. Train het model en wijs topics toe ---
        print("Stap 3: Topics aan het trainen en toewijzen... (Dit kan even duren)")
        topics, probabilities = topic_model.fit_transform(comments_list)

        # Voeg de topic-nummers toe aan ons DataFrame
        df_comments['topic_nr'] = topics

        # --- 5. Bekijk de gevonden topics in de terminal ---
        print("\n--- Gevonden Topics (Top 5 woorden per topic) ---")
        top_topics = topic_model.get_topic_info()
        print(top_topics[top_topics.Topic != -1].head(10))
        print("--------------------------------------------------\n")

        # --- 6. Voeg de topic-data samen met de hoofdtabel ---
        # Reviews die geen topic-analyse hadden (omdat ze NaN waren) krijgen hier
        # automatisch ook 'NaN' voor 'topic_nr'.
        df = df.join(df_comments[['topic_nr']])

    # --- 7. Sla het definitieve bestand op (MET NaN -> null CONVERSIE) ---
    print(f"Stap 4: Definitief bestand opslaan naar '{OUTPUT_FILE}' (NaNs worden omgezet naar null)...")

    # Zet alle 'NaN' waarden (Not a Number) van pandas om naar 'None' (Python's versie van null)
    # Dit is de cruciale stap voor JSON-compatibiliteit.
    df_for_json = df.replace({np.nan: None})

    # Converteer het DataFrame naar de dictionary-structuur die Power BI verwacht
    output_data = {"reviews": df_for_json.to_dict('records')}
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            # json.dump() zal 'None' automatisch omzetten naar 'null' in het JSON-bestand.
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\nAlle analyses voltooid! '{OUTPUT_FILE}' is succesvol aangemaakt.")
        print("Dit bestand is nu 100% JSON-compatibel en kan door Power BI gelezen worden.")

    except Exception as e:
        print(f"\nFOUT bij het wegschrijven van de JSON: {e}")

# --- Voer de functie uit als het script direct wordt gerund ---
if __name__ == "__main__":
    analyze_topics()
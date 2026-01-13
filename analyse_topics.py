import json
import pandas as pd
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import os
import numpy as np

# Bestandsnamen
INPUT_FILE = 'reviews_met_sentiment.json'
OUTPUT_FILE = 'reviews_met_topics.json'

def analyze_topics():
    """
    Voert hiërarchische topic modeling uit op zinsniveau voor diepere inzichten.
    """

    # --- 1. Data laden (zinnen gegenereerd door analyse_sentiment.py) ---
    print("Stap 1: Sentiment-zinnen laden...")
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: '{INPUT_FILE}' niet gevonden. Run eerst 'analyse_sentiment.py'.")
        return
        
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # We gebruiken 'zinnen' omdat het sentiment-script nu op zinsniveau opslaat
        df_zinnen = pd.DataFrame(data['zinnen'])
        print(f"{len(df_zinnen)} zinnen geladen voor analyse.")
    except Exception as e:
        print(f"ERROR: Kon data niet laden. {e}")
        return

    # Pak de tekst van de zinnen voor de clustering
    zinnen_lijst = df_zinnen['zin_tekst'].astype(str).tolist()

    if len(zinnen_lijst) == 0:
        print("Geen tekst gevonden om te analyseren.")
        return

    # --- 2. BERTopic model configureren ---
    print("Stap 2: BERTopic model configureren...")
    
    # Uitgebreide stopwoorden om ruis in de topics te verminderen
    dutch_stop_words = [
        "de", "het", "een", "is", "en", "van", "te", "dat", "die", "op", "met", 
        "voor", "niet", "ook", "om", "als", "dan", "met", "google", "translated", 
        "by", "original", "review"
    ]
    
    vectorizer_model = CountVectorizer(stop_words=dutch_stop_words)

    # We gebruiken language="multilingual". BERTopic laadt intern de juiste 
    # sentence-transformers zonder dat we handmatige imports nodig hebben.
    topic_model = BERTopic(
        language="multilingual",
        vectorizer_model=vectorizer_model,
        nr_topics="20", # Zoekt zelf naar een optimaal aantal hoofd-topics
        verbose=True
    )

    # --- 3. Topics trainen op zinsniveau ---
    print("Stap 3: Topics trainen en toewijzen... (Dit kan even duren)")
    topics, probs = topic_model.fit_transform(zinnen_lijst)
    df_zinnen['topic_nr'] = topics

    # --- 4. Hiërarchische analyse voor sub-topics ---
    print("Stap 4: Sub-topic hiërarchie berekenen...")
    try:
        hierarchical_topics = topic_model.hierarchical_topics(zinnen_lijst)
        
        # Visualisaties opslaan voor de gebruiker
        print("Visualisaties genereren...")
        topic_model.visualize_topics().write_html("topic_overview.html")
        topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics).write_html("topic_hierarchy.html")
        print("Visualisaties opgeslagen als 'topic_overview.html' en 'topic_hierarchy.html'.")
    except Exception as e:
        print(f"Waarschuwing: Kon hiërarchie niet berekenen/opslaan: {e}")

    # --- 5. Topic namen toevoegen aan de dataframe ---
    # Haal de tekstuele namen van de topics op (bijv. "0_zwembad_water_lekker")
    topic_info = topic_model.get_topic_info()
    df_final = df_zinnen.merge(
        topic_info[['Topic', 'Name']], 
        left_on='topic_nr', 
        right_on='Topic', 
        how='left'
    ).drop(columns=['Topic']) # Dubbele kolom verwijderen

    # --- 6. Resultaten opslaan ---
    print(f"Stap 5: Resultaten opslaan naar '{OUTPUT_FILE}'...")
    
    # NaN vervangen door None voor JSON validiteit
    df_final = df_final.replace({np.nan: None})
    
    output_data = {
        "metadata": {
            "total_sentences": len(df_final),
            "topic_count": len(topic_info)
        },
        "zinnen": df_final.to_dict('records')
    }

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\nTopic analyse voltooid! '{OUTPUT_FILE}' is aangemaakt.")
    except Exception as e:
        print(f"ERROR bij schrijven JSON: {e}")

if __name__ == "__main__":
    analyze_topics()
import json
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer # Nieuw: Nodig voor de filter
import os
import numpy as np

INPUT_FILE = 'reviews_met_sentiment.json'
OUTPUT_FILE = 'reviews_met_topics.json'

def analyze_topics():
    """
    Reads the file with sentiment, adds topics, and saves
    a Power BI-compatible JSON file.
    """

    # --- 1. Load data with sentiment ---
    print("Step 1: Loading data with sentiment...")
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: '{INPUT_FILE}' not found. Have you run 'analyse_sentiment.py'?")
        return
        
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame.from_records(data['reviews'])
        print(f"{len(df)} reviews loaded.")
    except Exception as e:
        print(f"ERROR: Could not load data. {e}")
        return

    # --- 2. Filter for reviews with comments ---
    df_comments = df.dropna(subset=['comment']).copy()
    comments_list = df_comments['comment'].tolist()
    print(f"{len(comments_list)} comments found for clustering.")

    if len(comments_list) == 0:
        print("No comments found to analyze. Script stopping.")
        df['topic_nr'] = np.nan 
    else:
        # --- 3. Setup Topic Model with Stop Words ---
        print("Step 2: Loading models for topic modeling...")
        
        # A. Define the words we want to IGNORE (The "Stop Words")
        # These words often appear in translated reviews but have no meaning
        my_stop_words = [
            "google", "translated", "by", "original", "review", 
            "de", "het", "een", "is", "en", "van", "te", "dat", "die", # Dutch filler words
            "the", "and", "to", "of", "a", "in", "is", "for" # English filler words
        ]
        
        # B. Create a vectorizer that uses this list
        vectorizer_model = CountVectorizer(stop_words=my_stop_words)

        # C. Load the sentence transformer (the "brain")
        sentence_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

        # D. Create BERTopic with our custom filters
        topic_model = BERTopic(
            embedding_model=sentence_model,
            vectorizer_model=vectorizer_model, # Use our filter here!
            language="multilingual",
            nr_topics="auto",
            verbose=True
        )

        # --- 4. Train model and assign topics ---
        print("Step 3: Training topics and assigning... (This may take a while)")
        topics, probabilities = topic_model.fit_transform(comments_list)

        df_comments['topic_nr'] = topics

        # --- 5. View found topics ---
        print("\n--- Found Topics (Top 5 words per topic) ---")
        top_topics = topic_model.get_topic_info()
        # Print columns explicitly to avoid confusion
        print(top_topics[['Topic', 'Count', 'Name']].head(10))
        print("--------------------------------------------------\n")
        
        # --- 5.1 Validation: Save visualization ---
        print("Generating visualization...")
        try:
            fig = topic_model.visualize_topics()
            fig.write_html("bertopic_visualization.html")
            print("Visualization saved to 'bertopic_visualization.html'.")
        except Exception as e:
            print(f"Warning: Could not save visualization: {e}")

        # --- 6. Merge topic data ---
        df = df.join(df_comments[['topic_nr']])

    # --- 7. Save final file ---
    print(f"Step 4: Saving final file to '{OUTPUT_FILE}'...")

    # Convert NaN to None (null) for JSON compatibility
    df_for_json = df.replace({np.nan: None})

    output_data = {"reviews": df_for_json.to_dict('records')}
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\nAll analyses completed! '{OUTPUT_FILE}' created successfully.")

    except Exception as e:
        print(f"\nERROR writing JSON: {e}")

if __name__ == "__main__":
    analyze_topics()
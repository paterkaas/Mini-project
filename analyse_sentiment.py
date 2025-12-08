import json
import pandas as pd
from transformers import pipeline
import os

INPUT_FILE = 'cleaned_reviews.json'
OUTPUT_FILE = 'reviews_met_sentiment.json'

# 1. Load the clean data into a pandas DataFrame
print("Step 1: Loading data...")
if not os.path.exists(INPUT_FILE):
    print(f"ERROR: '{INPUT_FILE}' not found. Have you run the clean script?")
    exit()

try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame.from_records(data['reviews'])
    print(f"{len(df)} reviews loaded.")

except Exception as e:
    print(f"ERROR: Could not load data. {e}")
    exit()


# 2. Filter for reviews that have a comment
df_comments = df.dropna(subset=['comment']).copy()
print(f"{len(df_comments)} reviews with comments found for analysis.")

# 3. Load the Dutch Sentiment Model
print("Step 2: Loading sentiment model (this may take a while)...")
model_name = "DTAI-KULeuven/robbert-v2-dutch-sentiment"
sentiment_pipeline = pipeline(
    "sentiment-analysis", 
    model=model_name, 
    tokenizer=model_name
)

# 4. Perform sentiment analysis
print("Step 3: Analyzing sentiment...")
comments_list = df_comments['comment'].tolist()

# 'truncation=True' prevents errors with very long reviews
sentiments = sentiment_pipeline(comments_list, truncation=True, max_length=512)

df_comments['sentiment_label'] = [s['label'] for s in sentiments]
df_comments['sentiment_score'] = [s['score'] for s in sentiments]

# 4.5 Validation Step
print("\n--- Sentiment Validation Sample (5 random) ---")
try:
    validation_sample = df_comments.sample(n=5, random_state=42)
    for index, row in validation_sample.iterrows():
        print(f"Review: {str(row['comment'])[:100]}...")
        print(f" -> Label: {row['sentiment_label']} (Score: {row['sentiment_score']:.4f})")
except ValueError:
    print("Not enough data for validation sample.")

print("Analysis completed.")

# 5. Merge sentiment data with original data
df = df.join(df_comments[['sentiment_label', 'sentiment_score']])

# 6. Save the enriched file
print(f"Step 4: Saving results to '{OUTPUT_FILE}'...")
output_data = {"reviews": df.to_dict('records')}

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"Done! '{OUTPUT_FILE}' has been successfully created.")
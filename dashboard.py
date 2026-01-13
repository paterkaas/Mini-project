import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
st.set_page_config(page_title="TerSpegelt Management Dashboard", layout="wide")

st.title("📊 TerSpegelt Actionable Insights Dashboard")
st.markdown("Combined analysis of reviews, weather, and holiday periods (2017 - present).")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    file_path = 'final_data_for_powerbi.json'
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Data is stored under the 'reviews' key
    df = pd.DataFrame(data['reviews'])
    
    if 'createTime' in df.columns:
        df['createTime'] = pd.to_datetime(df['createTime'])
        df['date_only'] = df['createTime'].dt.date
        df['year'] = df['createTime'].dt.year
    return df

df = load_data()

if df is not None:
    # --- TRANSLATE DATA VALUES ---
    if 'periode_type' in df.columns:
        df['periode_type'] = df['periode_type'].replace({
            'Buiten vakantie': 'Off-season',
            'Vakantie': 'Holiday'
        })

    # --- CLEANING ---
    df = df[df['topic_nr'] != -1]

    # --- SIDEBAR: FILTERS ---
    st.sidebar.header("Dashboard Filters")
    
    years = sorted(df['year'].unique().tolist(), reverse=True)
    selected_years = st.sidebar.multiselect("Select Years", years, default=years[:2])

    periods = df['periode_type'].unique().tolist() if 'periode_type' in df.columns else []
    selected_periods = st.sidebar.multiselect("Select Holiday/Period", periods, default=periods)

    top_n = st.sidebar.slider("Number of top topics", 5, 20, 10)
    temp_df = df[df['year'].isin(selected_years)]
    top_topics = temp_df['Name'].value_counts().nlargest(top_n).index.tolist()
    selected_topics = st.sidebar.multiselect("Select Topics", sorted(df['Name'].unique()), default=top_topics)

    # --- APPLY FILTERS ---
    mask = (df['year'].isin(selected_years)) & (df['Name'].isin(selected_topics))
    if 'periode_type' in df.columns:
        mask &= (df['periode_type'].isin(selected_periods))
    
    df_filtered = df[mask].copy()

    # --- METRICS ---
    st.subheader(f"Status Overview ({', '.join(map(str, selected_years))})")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Number of sentences", len(df_filtered))
    with m2:
        neg_count = len(df_filtered[df_filtered['sentiment_label'] == 'Negative'])
        st.metric("Negative feedback", neg_count, delta_color="inverse")
    with m3:
        avg_score = df_filtered['sentiment_score'].mean()
        st.metric("Avg. Satisfaction", f"{avg_score:.2f}")
    with m4:
        if 'temp_max_c' in df_filtered.columns:
            st.metric("Avg. Max Temp", f"{df_filtered['temp_max_c'].mean():.1f}°C")

    # --- HOLIDAY & SENTIMENT ANALYSIS ---
    st.markdown("---")
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Sentiment per Topic")
        sent_per_topic = df_filtered.groupby(['Name', 'sentiment_label']).size().reset_index(name='Count')
        fig_sent_topic = px.bar(sent_per_topic, x='Count', y='Name', color='sentiment_label', 
                                orientation='h', barmode='stack',
                                color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#f1c40f', 'Negative': '#e74c3c'})
        st.plotly_chart(fig_sent_topic, use_container_width=True)

    with c2:
        st.subheader("Holiday vs. Off-season")
        if 'periode_type' in df_filtered.columns:
            period_dist = df_filtered.groupby(['periode_type', 'sentiment_label']).size().reset_index(name='n')
            fig_period = px.bar(period_dist, x='periode_type', y='n', color='sentiment_label', 
                                barmode='group', color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#f1c40f', 'Negative': '#e74c3c'})
            st.plotly_chart(fig_period, use_container_width=True)

    # --- WEATHER IMPACT ---
    st.markdown("---")
    st.subheader("🌤️ Weather Impact")
    w1, w2 = st.columns(2)

    with w1:
        st.markdown("**Rain intensity vs. Satisfaction**")
        if 'precip_amount_mm' in df_filtered.columns:
            df_rain = df_filtered[df_filtered['precip_amount_mm'] > 0]
            if not df_rain.empty:
                fig_rain = px.scatter(df_rain, x='precip_amount_mm', y='sentiment_score', 
                                      trendline="ols", labels={'precip_amount_mm': 'Precipitation (mm)'})
                st.plotly_chart(fig_rain, use_container_width=True)
            else:
                st.info("No rainy days in this selection.")

    with w2:
        st.markdown("**Temperature vs. Satisfaction**")
        if 'temp_max_c' in df_filtered.columns:
            temp_trend = df_filtered.groupby('date_only').agg({'temp_max_c': 'first', 'sentiment_score': 'mean'}).reset_index()
            fig_temp = px.scatter(temp_trend, x='temp_max_c', y='sentiment_score', trendline="ols",
                                  labels={'temp_max_c': 'Max Temp (°C)'})
            st.plotly_chart(fig_temp, use_container_width=True)

    # --- DEEP DIVE SECTION ---
    st.markdown("---")
    st.header("🔍 Deep Dive: Literal Reviews")
    
    # Wordcloud and Table logic for Negative feedback (Improvement Areas)
    st.subheader("🔴 Improvement Areas (Negative Feedback Focus)")
    df_neg = df_filtered[df_filtered['sentiment_label'] == 'Negative']

    if not df_neg.empty:
        d1, d2 = st.columns([1, 1])
        with d1:
            st.markdown("**Common themes in negative reviews**")
            custom_stopwords = set(STOPWORDS)
            custom_stopwords.update([
                "the", "in", "fur", "and", "sehr", "wir", "für", "mit", "und", "die", "een", "ist",
                "google", "translated", "by", "original", "review", "zo'n", "beetje",
                "de", "het", "en", "is", "dat", "op", "met", "voor", "niet", "ook", "om", "als", "dan", "te", "zijn",
                "was", "we", "er", "maar", "ik", "je", "deze", "die", "dit", "aan", "bij", "door", "naar", "over",
                "der", "das", "ein", "eine", "von", "zu", "was", "aber", "im", "dem", "nicht", "auch", "waren", "sind"
            ])
            text = " ".join(df_neg['zin_tekst'].astype(str))
            wordcloud = WordCloud(width=800, height=400, background_color='white', 
                                  colormap='Reds', stopwords=custom_stopwords, collocations=False).generate(text)
            fig_wc, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig_wc)

        with d2:
            st.markdown("**Top 5 Complaint Topics**")
            neg_topics = df_neg['Name'].value_counts().reset_index()
            neg_topics.columns = ['Topic', 'Count']
            st.table(neg_topics.head(5))
    else:
        st.success("No negative feedback found for this selection! 🎉")

    # --- NEW: FILTERABLE REVIEW TABLE ---
    st.markdown("---")
    st.subheader("📖 Read Literal Reviews")
    
    # Filters for the table
    col_sent, col_topic = st.columns(2)
    
    with col_sent:
        selected_sentiment = st.selectbox(
            "Filter by Sentiment:", 
            options=["All", "Positive", "Neutral", "Negative"],
            index=3  # Default to Negative as it was the original focus
        )
        
    with col_topic:
        # Get list of topics available for the selected sentiment to keep the filter relevant
        if selected_sentiment == "All":
            topic_options = sorted(df_filtered['Name'].unique().tolist())
        else:
            topic_options = sorted(df_filtered[df_filtered['sentiment_label'] == selected_sentiment]['Name'].unique().tolist())
        
        selected_review_topic = st.selectbox("Filter by Topic:", options=["All"] + topic_options)

    # Apply table filters
    df_table = df_filtered.copy()
    if selected_sentiment != "All":
        df_table = df_table[df_table['sentiment_label'] == selected_sentiment]
    if selected_review_topic != "All":
        df_table = df_table[df_table['Name'] == selected_review_topic]

    # Display the table
    if not df_table.empty:
        st.table(df_table[['Name', 'sentiment_label', 'zin_tekst', 'createTime']].rename(
            columns={
                'Name': 'Topic', 
                'sentiment_label': 'Sentiment',
                'zin_tekst': 'Review Text', 
                'createTime': 'Date'
            }
        ).sort_values(by='Date', ascending=False).head(20))
    else:
        st.info("No reviews match the selected filters.")

else:
    st.error("Data not found. Please ensure the full pipeline has been run.")
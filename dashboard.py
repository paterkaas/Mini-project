import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# --- CONFIGURATIE ---
st.set_page_config(page_title="TerSpegelt Management Dashboard", layout="wide")

st.title("📊 TerSpegelt Actionable Insights Dashboard")
st.markdown("Gecombineerde analyse van reviews, weer en vakantieperiodes (2017 - heden).")

# --- DATA LADEN ---
@st.cache_data
def load_data():
    file_path = 'final_data_for_powerbi.json'
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # De data staat onder de key 'reviews' in het eindbestand
    df = pd.DataFrame(data['reviews'])
    
    if 'createTime' in df.columns:
        df['createTime'] = pd.to_datetime(df['createTime'])
        df['datum_alleen'] = df['createTime'].dt.date
        df['jaar'] = df['createTime'].dt.year
    return df

df = load_data()

if df is not None:
    # --- OPSCHONING ---
    # Verwijder 'Topic -1' (ruis die nergens geplaatst kon worden)
    df = df[df['topic_nr'] != -1]

    # --- SIDEBAR: FILTERS ---
    st.sidebar.header("Dashboard Filters")
    
    # 1. Jaar Filter (Nieuw ivm data vanaf 2017)
    jaren = sorted(df['jaar'].unique().tolist(), reverse=True)
    selected_jaren = st.sidebar.multiselect("Selecteer Jaren", jaren, default=jaren[:2])

    # 2. Vakantie Filter
    periodes = df['periode_type'].unique().tolist() if 'periode_type' in df.columns else []
    selected_periodes = st.sidebar.multiselect("Selecteer Periode", periodes, default=periodes)

    # 3. Topic Filter
    top_n = st.sidebar.slider("Aantal top onderwerpen", 5, 20, 10)
    # Bepaal top topics op basis van de huidige selectie
    temp_df = df[df['jaar'].isin(selected_jaren)]
    top_topics = temp_df['Name'].value_counts().nlargest(top_n).index.tolist()
    selected_topics = st.sidebar.multiselect("Selecteer Onderwerpen", sorted(df['Name'].unique()), default=top_topics)

    # --- FILTER TOEPASSEN ---
    mask = (df['jaar'].isin(selected_jaren)) & (df['Name'].isin(selected_topics))
    if 'periode_type' in df.columns:
        mask &= (df['periode_type'].isin(selected_periodes))
    
    df_filtered = df[mask].copy()

    # --- METRICS ---
    st.subheader(f"Status Overzicht ({', '.join(map(str, selected_jaren))})")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Aantal zinnen", len(df_filtered))
    with m2:
        neg_count = len(df_filtered[df_filtered['sentiment_label'] == 'Negative'])
        st.metric("Negatieve feedback", neg_count, delta_color="inverse")
    with m3:
        avg_score = df_filtered['sentiment_score'].mean()
        st.metric("Gem. Tevredenheid", f"{avg_score:.2f}")
    with m4:
        if 'temp_max_c' in df_filtered.columns:
            st.metric("Gem. Max Temp", f"{df_filtered['temp_max_c'].mean():.1f}°C")

    # --- VAKANTIE & SENTIMENT ANALYSE ---
    st.markdown("---")
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Sentiment per Onderwerp")
        sent_per_topic = df_filtered.groupby(['Name', 'sentiment_label']).size().reset_index(name='Aantal')
        fig_sent_topic = px.bar(sent_per_topic, x='Aantal', y='Name', color='sentiment_label', 
                                orientation='h', barmode='stack',
                                color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#f1c40f', 'Negative': '#e74c3c'})
        st.plotly_chart(fig_sent_topic, use_container_width=True)

    with c2:
        st.subheader("Vakantie vs. Laagseizoen")
        if 'periode_type' in df_filtered.columns:
            # Verhouding sentiment per periode
            period_dist = df_filtered.groupby(['periode_type', 'sentiment_label']).size().reset_index(name='n')
            fig_period = px.bar(period_dist, x='periode_type', y='n', color='sentiment_label', 
                                barmode='group', color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#f1c40f', 'Negative': '#e74c3c'})
            st.plotly_chart(fig_period, use_container_width=True)

    # --- WEER-IMPACT ---
    st.markdown("---")
    st.subheader("🌤️ De invloed van het Weer")
    w1, w2 = st.columns(2)

    with w1:
        st.markdown("**Regen-intensiteit vs. Tevredenheid**")
        if 'precip_amount_mm' in df_filtered.columns:
            # Focus op dagen met regen
            df_rain = df_filtered[df_filtered['precip_amount_mm'] > 0]
            if not df_rain.empty:
                fig_rain = px.scatter(df_rain, x='precip_amount_mm', y='sentiment_score', 
                                      trendline="ols", labels={'precip_amount_mm': 'Neerslag (mm)'})
                st.plotly_chart(fig_rain, use_container_width=True)
            else:
                st.info("Geen regendagen in deze selectie.")

    with w2:
        st.markdown("**Temperatuur vs. Tevredenheid**")
        if 'temp_max_c' in df_filtered.columns:
            temp_trend = df_filtered.groupby('datum_alleen').agg({'temp_max_c': 'first', 'sentiment_score': 'mean'}).reset_index()
            fig_temp = px.scatter(temp_trend, x='temp_max_c', y='sentiment_score', trendline="ols",
                                  labels={'temp_max_c': 'Max Temp (°C)'})
            st.plotly_chart(fig_temp, use_container_width=True)

    # --- DE NEGATIEVE "DEEP DIVE" ---
    st.markdown("---")
    st.header("🔴 Verbeterpunten (Focus op negatieve feedback)")
    
    df_neg = df_filtered[df_filtered['sentiment_label'] == 'Negative']

    if not df_neg.empty:
        d1, d2 = st.columns([1, 1])
        
        with d1:
            st.markdown("**Wat wordt er letterlijk gezegd?**")
            # --- UITGEBREIDE STOPWOORDEN FILTER ---
            custom_stopwords = set(STOPWORDS)
            custom_stopwords.update([
                # Gebruikersverzoeken
                "the", "in", "fur", "and", "sehr", "wir", "für", "mit", "und", "die", "een", "ist",
                "google", "translated", "by", "original", "review", "zo'n", "beetje",
                # Nederlands
                "de", "het", "en", "is", "dat", "op", "met", "voor", "niet", "ook", "om", "als", "dan", "te", "zijn",
                "was", "we", "er", "maar", "ik", "je", "deze", "die", "dit", "aan", "bij", "door", "naar", "over",
                # Duits
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
            st.markdown("**Top 5 Klacht-onderwerpen**")
            neg_topics = df_neg['Name'].value_counts().reset_index()
            neg_topics.columns = ['Onderwerp', 'Aantal klachten']
            st.table(neg_topics.head(5))

        st.subheader("Lees de letterlijke klachten")
        sel_neg_topic = st.selectbox("Filter klachten op onderwerp:", ["Alle"] + neg_topics['Onderwerp'].tolist())
        
        display_neg = df_neg if sel_neg_topic == "Alle" else df_neg[df_neg['Name'] == sel_neg_topic]
        st.table(display_neg[['Name', 'zin_tekst', 'createTime']].sort_values(by='createTime', ascending=False).head(15))

    else:
        st.success("Geen negatieve feedback gevonden voor deze selectie! 🎉")

else:
    st.error("Data niet gevonden. Zorg dat de volledige pipeline gedraaid heeft.")
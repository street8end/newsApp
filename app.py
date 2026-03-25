import streamlit as st
import requests
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob

# --- СТИЛІ ---
st.set_page_config(page_title="Новини", layout="wide")

st.markdown("""
<style>
.big-title {
    font-size:40px;
    font-weight:bold;
}
.card {
    padding:15px;
    border-radius:15px;
    background-color:#1e1e1e;
    color:white;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">📊 Моніторинг новин</div>', unsafe_allow_html=True)

# --- API ---
if "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
else:
    api_key = st.text_input("Введи API ключ", type="password")

query = st.text_input("🔍 Пошук новин", "technology")

if st.button("🚀 Запустити аналіз"):

    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&language=en"
    response = requests.get(url).json()
    articles = response.get("articles", [])

    if not articles:
        st.warning("Немає новин")
    else:
        df = pd.DataFrame(articles)[["title", "publishedAt"]]
        df["publishedAt"] = pd.to_datetime(df["publishedAt"])

        # --- КАРТКИ ---
        col1, col2, col3 = st.columns(3)

        sentiments = df["title"].apply(lambda x: TextBlob(x).sentiment.polarity)
        positive = (sentiments > 0).sum()
        negative = (sentiments < 0).sum()

        col1.metric("📰 Новин", len(df))
        col2.metric("😊 Позитив", positive)
        col3.metric("😡 Негатив", negative)

        st.divider()

        # --- ГРАФІКИ ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("☁️ WordCloud")
            text = " ".join(df["title"])
            wc = WordCloud(background_color="black").generate(text)

            fig, ax = plt.subplots()
            ax.imshow(wc)
            ax.axis("off")
            st.pyplot(fig)

        with col2:
            st.subheader("📈 Активність")
            df["date"] = df["publishedAt"].dt.date
            activity = df.groupby("date").size()
            st.line_chart(activity)

        st.divider()

        # --- СПИСОК НОВИН ---
        st.subheader("📰 Останні новини")
        for i, row in df.iterrows():
            st.markdown(f"""
            <div class="card">
                {row['title']}
            </div>
            """, unsafe_allow_html=True)

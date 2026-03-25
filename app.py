import streamlit as st
import requests
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob

st.title("📊 Моніторинг новин")

# беремо ключ із secrets
api_key = st.secrets["API_KEY"]

query = st.text_input("Ключове слово", "technology")

if st.button("Пошук"):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&language=en"
    response = requests.get(url).json()

    articles = response.get("articles", [])

    if articles:
        df = pd.DataFrame(articles)[["title", "publishedAt"]]
        df["publishedAt"] = pd.to_datetime(df["publishedAt"])

        st.write(df)

        # WordCloud
        text = " ".join(df["title"])
        wc = WordCloud().generate(text)

        fig, ax = plt.subplots()
        ax.imshow(wc)
        ax.axis("off")
        st.pyplot(fig)

        # Активність
        df["date"] = df["publishedAt"].dt.date
        st.line_chart(df.groupby("date").size())

        # Тон
        df["sentiment"] = df["title"].apply(lambda x: TextBlob(x).sentiment.polarity)

        st.write({
            "positive": (df["sentiment"] > 0).sum(),
            "negative": (df["sentiment"] < 0).sum()
        })

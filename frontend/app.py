import os
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

API_BASE_URL = os.getenv("API_BASE_URL", "")


st.set_page_config(page_title="FinSentinel Dashboard", layout="wide")

st.title("FinSentinel Dashboard")
st.write("Track watchlist tickers and monitor financial sentiment trends.")

if not API_BASE_URL:
    st.error("API_BASE_URL is not set.")
    st.stop()

st.subheader("Add ticker to watchlist")

ticker_input = st.text_input("Enter ticker symbol", placeholder="e.g. TSLA")

if st.button("Add Ticker"):
    if not ticker_input.strip():
        st.warning("Please enter a ticker.")
    else:
        try:
            response = requests.post(
                f"{API_BASE_URL}/watchlist/add",
                json={"ticker": ticker_input.strip().upper()},
                timeout=30
            )
            data = response.json()

            if response.status_code == 200:
                st.success(f"Ticker added: {data['ticker']}")
            else:
                st.error(data.get("error", "Failed to add ticker"))
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

watchlist = []

st.subheader("Current watchlist")

try:
    response = requests.get(f"{API_BASE_URL}/watchlist", timeout=30)
    data = response.json()
    watchlist = data.get("watchlist", [])

    if watchlist:
        watchlist_df = pd.DataFrame(watchlist)
        st.dataframe(watchlist_df, use_container_width=True)
    else:
        st.info("No tickers in watchlist yet.")
except Exception as e:
    st.error(f"Error loading watchlist: {e}")

st.divider()

st.subheader("Ticker dashboard")

if watchlist:
    ticker_options = [item["ticker"] for item in watchlist]
    selected_ticker = st.selectbox("Select ticker", ticker_options)

    try:
        response = requests.get(
            f"{API_BASE_URL}/ticker-summary",
            params={"ticker": selected_ticker},
            timeout=30
        )
        summary = response.json()

        if response.status_code != 200:
            st.error(summary.get("error", "Failed to fetch ticker summary"))
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Sentiment", f"{summary.get('avg_sentiment', 0):.2f}")
            with col2:
                st.metric("Article Count", int(summary.get("article_count", 0)))

            trend = summary.get("trend", [])
            if trend:
                trend_df = pd.DataFrame(trend)

                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(trend_df["day"], trend_df["sentiment"], marker="o")
                ax.set_title(f"Recent Sentiment Trend: {selected_ticker}")
                ax.set_ylabel("Sentiment Score")
                ax.set_xlabel("Time")
                plt.xticks(rotation=45)

                st.pyplot(fig)
            else:
                st.info("No trend data available yet.")

            latest_articles = summary.get("latest_articles", [])
            st.subheader("Latest articles")

            if latest_articles:
                articles_df = pd.DataFrame(latest_articles)
                st.dataframe(articles_df, use_container_width=True)
            else:
                st.info("No articles available yet.")

    except Exception as e:
        st.error(f"Error loading ticker summary: {e}")
else:
    st.info("Add a ticker first to view the dashboard.")
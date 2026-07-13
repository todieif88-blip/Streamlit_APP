import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Global Top10 Market Cap Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("🌍 Global Market Cap TOP10 Stock Dashboard")
st.markdown("최근 1년간 글로벌 시가총액 Top10 기업의 주가를 비교합니다.")

# 글로벌 시가총액 Top10 (2025 기준)
stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Saudi Aramco": "2222.SR",
    "Broadcom": "AVGO",
    "TSMC": "TSM",
    "Berkshire Hathaway": "BRK-B"
}

selected = st.multiselect(
    "기업 선택",
    list(stocks.keys()),
    default=list(stocks.keys())
)

normalize = st.checkbox("100 기준으로 정규화", value=True)

end = datetime.today()
start = end - timedelta(days=365)

fig = go.Figure()

progress = st.progress(0)

for idx, company in enumerate(selected):

    ticker = stocks[company]

    df = yf.download(
        ticker,
        start=start,
        end=end,
        progress=False,
        auto_adjust=True
    )

    if len(df) == 0:
        continue

    price = df["Close"]

    if normalize:
        price = price / price.iloc[0] * 100

    fig.add_trace(
        go.Scatter(
            x=price.index,
            y=price,
            mode="lines",
            name=company,
            hovertemplate=
            "<b>%{fullData.name}</b><br>"
            "%{x|%Y-%m-%d}<br>"
            "%{y:.2f}<extra></extra>"
        )
    )

    progress.progress((idx+1)/len(selected))

ylabel = "Normalized Price (100=Start)" if normalize else "Price"

fig.update_layout(
    height=700,
    template="plotly_white",
    title="Global Top10 Stocks (Last 1 Year)",
    xaxis_title="Date",
    yaxis_title=ylabel,
    hovermode="x unified",
    legend_title="Company"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Ticker List")

ticker_df = pd.DataFrame(
    {
        "Company": stocks.keys(),
        "Ticker": stocks.values()
    }
)

st.dataframe(ticker_df, use_container_width=True)

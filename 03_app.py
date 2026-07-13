import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="🌍 Global Top10 Stocks",
    layout="wide"
)

st.title("🌍 글로벌 시가총액 Top10 주가 대시보드")
st.write("최근 1년간 주가 추이를 비교합니다.")

# 글로벌 시가총액 Top10 (미국 중심)
stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Broadcom": "AVGO",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK-B",
    "TSMC": "TSM"
}

selected = st.multiselect(
    "기업 선택",
    list(stocks.keys()),
    default=list(stocks.keys())
)

normalize = st.checkbox("100 기준 정규화", True)

fig = go.Figure()

progress = st.progress(0)

for i, company in enumerate(selected):

    ticker = stocks[company]

    try:
        df = yf.Ticker(ticker).history(
            period="1y",
            auto_adjust=True
        )

        if df.empty:
            st.warning(f"{company} 데이터를 가져오지 못했습니다.")
            continue

        price = df["Close"].dropna()

        if normalize:
            price = price / price.iloc[0] * 100

        fig.add_trace(
            go.Scatter(
                x=price.index,
                y=price.values,
                mode="lines",
                name=company
            )
        )

    except Exception as e:
        st.error(f"{company}: {e}")

    progress.progress((i + 1) / len(selected))

ylabel = "Normalized Price" if normalize else "Price (USD)"

fig.update_layout(
    title="최근 1년 주가",
    template="plotly_white",
    height=700,
    hovermode="x unified",
    xaxis_title="Date",
    yaxis_title=ylabel
)

st.plotly_chart(fig, use_container_width=True)

st.success("완료!")

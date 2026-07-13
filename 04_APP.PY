import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

st.set_page_config(
    page_title="서울시 공영주차장 정보",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울시 공영주차장 정보")

uploaded_file = st.file_uploader(
    "CSV 또는 Excel 파일을 업로드하세요.",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8")
        except:
            df = pd.read_csv(uploaded_file, encoding="cp949")
    else:
        df = pd.read_excel(uploaded_file)

    st.sidebar.header("검색")

    if "구" in df.columns:
        gu = st.sidebar.selectbox(
            "자치구 선택",
            ["전체"] + sorted(df["구"].dropna().unique().tolist())
        )

        if gu != "전체":
            df = df[df["구"] == gu]

    if "주차장명" in df.columns:
        keyword = st.sidebar.text_input("주차장명 검색")

        if keyword:
            df = df[df["주차장명"].str.contains(keyword, case=False, na=False)]

    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11
    )

    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():

        try:
            lat = float(row["위도"])
            lon = float(row["경도"])
        except:
            continue

        popup = f"""
        <b>{row.get('주차장명','')}</b><br><br>

        <b>주소</b><br>
        {row.get('주소','')}<br><br>

        <b>기본요금</b><br>
        {row.get('기본요금','')}<br><br>

        <b>추가요금</b><br>
        {row.get('추가요금','')}<br><br>

        <b>운영시간</b><br>
        {row.get('운영시간','')}<br><br>

        <b>전화번호</b><br>
        {row.get('전화번호','')}<br><br>

        <b>주차면수</b><br>
        {row.get('주차면수','')}
        """

        folium.Marker(
            location=[lat, lon],
            tooltip=row.get("주차장명", ""),
            popup=folium.Popup(popup, max_width=350),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(marker_cluster)

    st.subheader("🗺️ 주차장 위치")

    st_folium(
        m,
        width=None,
        height=600
    )

    st.subheader("📋 주차장 정보")

    st.dataframe(
        df,
        use_container_width=True
    )

else:
    st.info("서울시 공영주차장 CSV 또는 Excel 파일을 업로드하세요.")

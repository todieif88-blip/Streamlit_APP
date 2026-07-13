import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

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

    # 파일 읽기
    if uploaded_file.name.endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8")
        except:
            df = pd.read_csv(uploaded_file, encoding="cp949")
    else:
        df = pd.read_excel(uploaded_file)

    # 컬럼명 확인
    st.expander("데이터 컬럼 보기").write(df.columns.tolist())

    # 좌표 컬럼 자동 찾기
    lat_col = None
    lon_col = None

    for col in df.columns:
        c = col.strip().lower()

        if c in ["위도", "lat", "latitude", "y좌표", "y"]:
            lat_col = col

        if c in ["경도", "lng", "lon", "longitude", "x좌표", "x"]:
            lon_col = col

    if lat_col is None or lon_col is None:
        st.error("위도/경도 컬럼을 찾지 못했습니다.")
        st.stop()

    # 숫자로 변환
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")

    df = df.dropna(subset=[lat_col, lon_col])

    # 사이드바
    st.sidebar.header("검색")

    if "구" in df.columns:
        gu = st.sidebar.selectbox(
            "자치구",
            ["전체"] + sorted(df["구"].dropna().unique())
        )

        if gu != "전체":
            df = df[df["구"] == gu]

    if "주차장명" in df.columns:
        keyword = st.sidebar.text_input("주차장명 검색")

        if keyword:
            df = df[df["주차장명"].astype(str).str.contains(keyword, case=False)]

    # 지도 중심 자동 계산
    center_lat = df[lat_col].mean()
    center_lon = df[lon_col].mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12
    )

    marker_cluster = MarkerCluster().add_to(m)

    # 마커 생성
    for _, row in df.iterrows():

        popup = f"""
        <b>{row.get('주차장명','')}</b><br><br>

        주소 : {row.get('주소','')}<br>

        기본요금 : {row.get('기본요금','')}<br>

        추가요금 : {row.get('추가요금','')}<br>

        운영시간 : {row.get('운영시간','')}<br>

        전화번호 : {row.get('전화번호','')}<br>

        주차면수 : {row.get('주차면수','')}
        """

        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            tooltip=str(row.get("주차장명", "")),
            popup=folium.Popup(popup, max_width=350),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(marker_cluster)

    st.subheader("🗺️ 공영주차장 위치")

    st_folium(
        m,
        width=None,
        height=650
    )

    st.subheader("📋 주차장 정보")

    st.dataframe(
        df,
        use_container_width=True
    )

else:
    st.info("CSV 또는 Excel 파일을 업로드하세요.") 파일을 업로드하세요.")

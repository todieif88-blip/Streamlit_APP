"""
유튜브 댓글 분석기
- YouTube Data API v3 (REST) 사용
- Streamlit Cloud 배포 전제
실행: streamlit run app.py
"""

import re
import requests
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud
from collections import Counter
from datetime import datetime

# ----------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------
st.set_page_config(page_title="유튜브 댓글 분석기", page_icon="📺", layout="wide")

API_BASE = "https://www.googleapis.com/youtube/v3"

# Streamlit Cloud에서 packages.txt로 fonts-nanum을 설치하면 아래 경로에 폰트가 생깁니다.
# (로컬 macOS/Windows에서는 자동으로 대체 폰트를 사용합니다)
KOREAN_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # macOS
    "C:/Windows/Fonts/malgun.ttf",                  # Windows
]


def get_korean_font_path():
    for path in KOREAN_FONT_CANDIDATES:
        try:
            fm.FontProperties(fname=path)
            return path
        except Exception:
            continue
    return None


KOREAN_FONT_PATH = get_korean_font_path()
if KOREAN_FONT_PATH:
    try:
        fm.fontManager.addfont(KOREAN_FONT_PATH)
        plt.rcParams["font.family"] = fm.FontProperties(fname=KOREAN_FONT_PATH).get_name()
    except Exception:
        pass
plt.rcParams["axes.unicode_minus"] = False


# ----------------------------------------------------------------------
# 유틸 함수
# ----------------------------------------------------------------------
def extract_video_id(url: str) -> str | None:
    """다양한 형태의 유튜브 URL에서 video ID를 추출"""
    patterns = [
        r"(?:v=|/videos/|embed/|youtu\.be/|/shorts/)([0-9A-Za-z_-]{11})",
        r"^([0-9A-Za-z_-]{11})$",  # ID를 그냥 붙여넣은 경우
    ]
    url = url.strip()
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


@st.cache_data(show_spinner=False, ttl=600)
def fetch_video_info(api_key: str, video_id: str) -> dict:
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": api_key,
    }
    r = requests.get(f"{API_BASE}/videos", params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    if not data.get("items"):
        raise ValueError("영상을 찾을 수 없습니다. URL을 확인해주세요.")
    item = data["items"][0]
    return {
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "published_at": item["snippet"]["publishedAt"],
        "view_count": int(item["statistics"].get("viewCount", 0)),
        "like_count": int(item["statistics"].get("likeCount", 0)),
        "comment_count": int(item["statistics"].get("commentCount", 0)),
        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
    }


@st.cache_data(show_spinner=False, ttl=600)
def fetch_comments(api_key: str, video_id: str, max_results: int, order: str = "time") -> pd.DataFrame:
    """commentThreads.list를 페이지네이션하며 댓글 수집"""
    comments = []
    page_token = None

    while len(comments) < max_results:
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(100, max_results - len(comments)),
            "order": order,  # 'time' or 'relevance'
            "textFormat": "plainText",
            "key": api_key,
        }
        if page_token:
            params["pageToken"] = page_token

        r = requests.get(f"{API_BASE}/commentThreads", params=params, timeout=15)
        if r.status_code != 200:
            err = r.json().get("error", {}).get("message", r.text)
            raise RuntimeError(f"API 오류 ({r.status_code}): {err}")

        data = r.json()
        for item in data.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": top.get("authorDisplayName", ""),
                "text": top.get("textDisplay", ""),
                "like_count": top.get("likeCount", 0),
                "published_at": top.get("publishedAt", ""),
                "reply_count": item["snippet"].get("totalReplyCount", 0),
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    df = pd.DataFrame(comments)
    if not df.empty:
        df["published_at"] = pd.to_datetime(df["published_at"])
    return df


def clean_text_for_wordcloud(text: str) -> str:
    text = re.sub(r"http\S+|www\.\S+", " ", text)          # URL 제거
    text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", text)         # 특수문자/이모지 제거
    text = re.sub(r"\s+", " ", text).strip()
    return text


DEFAULT_STOPWORDS = {
    "그리고", "그런데", "그래서", "하지만", "이거", "저거", "정말", "진짜",
    "너무", "그냥", "이건", "저건", "이제", "우리", "제가", "그게", "이게",
    "합니다", "니다", "습니다", "인데", "이런", "저런", "그런", "것", "이",
    "가", "은", "는", "을", "를", "에", "의", "도", "로", "와", "과", "다",
    "고", "네", "요", "음", "아", "the", "and", "to", "of", "is", "in",
}


def build_wordcloud_freq(texts: list[str], extra_stopwords: set[str], min_len: int = 2) -> Counter:
    words = []
    stopwords = DEFAULT_STOPWORDS | extra_stopwords
    for t in texts:
        cleaned = clean_text_for_wordcloud(t)
        for w in cleaned.split():
            if len(w) >= min_len and w not in stopwords:
                words.append(w)
    return Counter(words)


# ----------------------------------------------------------------------
# 사이드바 - 입력
# ----------------------------------------------------------------------
st.sidebar.header("⚙️ 설정")

api_key = st.sidebar.text_input("YouTube Data API 키", type="password", help="Google Cloud Console에서 발급받은 YouTube Data API v3 키를 입력하세요.")
video_url = st.sidebar.text_input("유튜브 영상 링크", placeholder="https://www.youtube.com/watch?v=...")

max_comments = st.sidebar.slider("가져올 댓글 수", min_value=20, max_value=2000, value=200, step=20)
order = st.sidebar.selectbox("댓글 정렬 기준", options=["time", "relevance"], format_func=lambda x: "최신순" if x == "time" else "관련도순")

extra_stopwords_input = st.sidebar.text_input("워드클라우드 제외 단어 (쉼표로 구분)", placeholder="예: 영상, 구독")
extra_stopwords = {w.strip() for w in extra_stopwords_input.split(",") if w.strip()}

run = st.sidebar.button("🔍 분석 시작", type="primary", use_container_width=True)

st.title("📺 유튜브 댓글 분석기")
st.caption("영상 링크와 API 키를 입력하고 [분석 시작]을 눌러주세요.")

# ----------------------------------------------------------------------
# 메인 로직
# ----------------------------------------------------------------------
if run:
    if not api_key:
        st.error("API 키를 입력해주세요.")
        st.stop()
    if not video_url:
        st.error("유튜브 영상 링크를 입력해주세요.")
        st.stop()

    video_id = extract_video_id(video_url)
    if not video_id:
        st.error("영상 링크에서 video ID를 추출하지 못했습니다. URL을 확인해주세요.")
        st.stop()

    try:
        with st.spinner("영상 정보를 불러오는 중..."):
            info = fetch_video_info(api_key, video_id)
    except Exception as e:
        st.error(f"영상 정보를 불러오지 못했습니다: {e}")
        st.stop()

    # ---- 영상 표시 ----
    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.video(f"https://www.youtube.com/watch?v={video_id}")
    with col2:
        st.subheader(info["title"])
        st.write(f"채널: **{info['channel']}**")
        st.write(f"게시일: {pd.to_datetime(info['published_at']).strftime('%Y-%m-%d')}")
        m1, m2, m3 = st.columns(3)
        m1.metric("조회수", f"{info['view_count']:,}")
        m2.metric("좋아요", f"{info['like_count']:,}")
        m3.metric("전체 댓글 수", f"{info['comment_count']:,}")

    st.divider()

    # ---- 댓글 수집 ----
    try:
        with st.spinner(f"댓글 최대 {max_comments}개 수집 중..."):
            df = fetch_comments(api_key, video_id, max_comments, order=order)
    except Exception as e:
        st.error(f"댓글을 불러오지 못했습니다: {e}")
        st.stop()

    if df.empty:
        st.warning("댓글이 없거나, 댓글 기능이 비활성화된 영상입니다.")
        st.stop()

    st.success(f"댓글 {len(df):,}개 수집 완료!")

    tab1, tab2, tab3, tab4 = st.tabs(["⏱️ 시간대별 추이", "👍 댓글 반응도", "☁️ 워드클라우드", "📋 원본 데이터"])

    # ---- 탭1: 시간대별 추이 ----
    with tab1:
        st.subheader("날짜별 댓글 작성 추이")
        by_date = df.set_index("published_at").resample("D").size()
        fig1, ax1 = plt.subplots(figsize=(10, 3.5))
        ax1.plot(by_date.index, by_date.values, marker="o", markersize=3)
        ax1.set_xlabel("날짜")
        ax1.set_ylabel("댓글 수")
        ax1.grid(alpha=0.3)
        fig1.autofmt_xdate()
        st.pyplot(fig1)

        st.subheader("하루 중 시간대(0~23시)별 댓글 작성 분포")
        by_hour = df["published_at"].dt.hour.value_counts().reindex(range(24), fill_value=0)
        fig2, ax2 = plt.subplots(figsize=(10, 3.5))
        ax2.bar(by_hour.index, by_hour.values, color="#5B8FF9")
        ax2.set_xlabel("시간대 (시)")
        ax2.set_ylabel("댓글 수")
        ax2.set_xticks(range(0, 24, 1))
        ax2.grid(alpha=0.3, axis="y")
        st.pyplot(fig2)

    # ---- 탭2: 반응도 ----
    with tab2:
        st.subheader("좋아요 Top 10 댓글")
        top_liked = df.sort_values("like_count", ascending=False).head(10)
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        labels = [t[:20] + ("…" if len(t) > 20 else "") for t in top_liked["text"]]
        ax3.barh(labels[::-1], top_liked["like_count"][::-1], color="#F6BD16")
        ax3.set_xlabel("좋아요 수")
        st.pyplot(fig3)

        c1, c2, c3 = st.columns(3)
        c1.metric("평균 좋아요", f"{df['like_count'].mean():.1f}")
        c2.metric("평균 답글 수", f"{df['reply_count'].mean():.1f}")
        c3.metric("좋아요 0인 댓글 비율", f"{(df['like_count'] == 0).mean() * 100:.1f}%")

        st.subheader("좋아요 수 분포")
        fig4, ax4 = plt.subplots(figsize=(10, 3.5))
        ax4.hist(df["like_count"], bins=30, color="#5AD8A6")
        ax4.set_xlabel("좋아요 수")
        ax4.set_ylabel("댓글 개수")
        st.pyplot(fig4)

    # ---- 탭3: 워드클라우드 ----
    with tab3:
        st.subheader("댓글 워드클라우드")
        freq = build_wordcloud_freq(df["text"].tolist(), extra_stopwords)

        if not freq:
            st.warning("워드클라우드를 만들 단어가 충분하지 않습니다.")
        else:
            wc_kwargs = dict(
                width=1000,
                height=500,
                background_color="white",
                max_words=150,
                prefer_horizontal=0.9,
            )
            if KOREAN_FONT_PATH:
                wc_kwargs["font_path"] = KOREAN_FONT_PATH
            else:
                st.info("한글 폰트를 찾지 못했습니다. packages.txt에 fonts-nanum이 포함되어 있는지 확인해주세요.")

            wc = WordCloud(**wc_kwargs).generate_from_frequencies(freq)
            fig5, ax5 = plt.subplots(figsize=(12, 6))
            ax5.imshow(wc, interpolation="bilinear")
            ax5.axis("off")
            st.pyplot(fig5)

            st.subheader("빈도 Top 20 단어")
            top20 = pd.DataFrame(freq.most_common(20), columns=["단어", "빈도"])
            st.bar_chart(top20.set_index("단어"))

    # ---- 탭4: 원본 데이터 ----
    with tab4:
        st.dataframe(
            df[["author", "text", "like_count", "reply_count", "published_at"]]
            .sort_values("published_at", ascending=False),
            use_container_width=True,
            height=500,
        )
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("CSV로 다운로드", data=csv, file_name=f"comments_{video_id}.csv", mime="text/csv")

else:
    st.info("왼쪽 사이드바에 API 키와 영상 링크를 입력한 뒤 [분석 시작] 버튼을 눌러주세요.")

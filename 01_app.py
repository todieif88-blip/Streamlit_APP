import streamlit as st
import requests
from youtubesearchpython import VideosSearch

# -----------------------------
# 설정
# -----------------------------
st.set_page_config(
    page_title="오늘의 날씨 스타일 추천",
    page_icon="🌤️",
    layout="wide"
)

API_KEY = st.secrets["OPENWEATHER_API_KEY"]  # Streamlit Cloud Secrets 사용

# -----------------------------
# 날씨 조회 함수
# -----------------------------
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    return {
        "temp": data["main"]["temp"],
        "feel": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"],
        "weather": data["weather"][0]["description"]
    }


# -----------------------------
# 옷 추천
# -----------------------------
def recommend(temp):

    if temp >= 30:
        return {
            "comment":"🔥 매우 더운 날씨입니다.",
            "top":"반팔 티셔츠",
            "bottom":"반바지",
            "shoes":"샌들",
            "image":"https://images.unsplash.com/photo-1521572267360-ee0c2909d518"
        }

    elif temp >= 23:
        return {
            "comment":"😊 가볍게 입기 좋은 날씨입니다.",
            "top":"셔츠",
            "bottom":"청바지",
            "shoes":"운동화",
            "image":"https://images.unsplash.com/photo-1515886657613-9f3515b0c78f"
        }

    elif temp >= 17:
        return {
            "comment":"🍂 얇은 겉옷을 챙기세요.",
            "top":"맨투맨",
            "bottom":"긴바지",
            "shoes":"운동화",
            "image":"https://images.unsplash.com/photo-1496747611176-843222e1e57c"
        }

    elif temp >= 10:
        return {
            "comment":"🧥 자켓이 필요한 날씨입니다.",
            "top":"후드티",
            "bottom":"긴바지",
            "shoes":"운동화",
            "image":"https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
        }

    else:
        return {
            "comment":"❄️ 매우 춥습니다.",
            "top":"패딩",
            "bottom":"기모바지",
            "shoes":"부츠",
            "image":"https://images.unsplash.com/photo-1512436991641-6745cdb1723f"
        }


# -----------------------------
# 음악 추천
# -----------------------------
def music_keyword(weather):

    if "비" in weather:
        return "Rainy Jazz"

    elif "맑" in weather:
        return "Happy Morning"

    elif "눈" in weather:
        return "Winter Piano"

    elif "구름" in weather:
        return "Lofi Chill"

    else:
        return "Relax Music"


# -----------------------------
# 유튜브 검색
# -----------------------------
def youtube(keyword):

    search = VideosSearch(keyword, limit=1)
    result = search.result()

    if len(result["result"]) > 0:
        return result["result"][0]["link"]

    return None


# -----------------------------
# 화면
# -----------------------------
st.title("🌤️ 오늘의 날씨 스타일 추천")

city = st.text_input("도시를 입력하세요", "Seoul")

if st.button("추천 받기"):

    weather = get_weather(city)

    if weather is None:
        st.error("도시를 찾을 수 없습니다.")
        st.stop()

    clothes = recommend(weather["temp"])

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🌦️ 오늘의 날씨")

        st.metric("현재온도", f'{weather["temp"]:.1f}℃')
        st.metric("체감온도", f'{weather["feel"]:.1f}℃')
        st.metric("습도", f'{weather["humidity"]}%')
        st.metric("바람", f'{weather["wind"]} m/s')

        st.success(weather["weather"])

    with col2:

        st.subheader("👕 추천 코디")

        st.image(clothes["image"], use_container_width=True)

        st.write("### 상의")
        st.write(clothes["top"])

        st.write("### 하의")
        st.write(clothes["bottom"])

        st.write("### 신발")
        st.write(clothes["shoes"])

        st.info(clothes["comment"])

    st.divider()

    st.subheader("🎵 오늘의 추천 음악")

    keyword = music_keyword(weather["weather"])

    url = youtube(keyword)

    if url:
        st.video(url)

    st.divider()

    st.subheader("💬 오늘의 AI 코멘트")

    if weather["temp"] >= 28:
        st.write("🥤 시원한 음료와 함께 가볍게 외출하기 좋은 날입니다.")
    elif weather["temp"] >= 20:
        st.write("🚶 산책이나 데이트하기 좋은 날씨입니다.")
    elif weather["temp"] >= 10:
        st.write("🧥 아침저녁은 쌀쌀하니 겉옷을 챙기세요.")
    else:
        st.write("☕ 따뜻한 옷차림과 핫초코 한 잔이 잘 어울리는 날입니다.")

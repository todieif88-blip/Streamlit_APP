import random
import streamlit as st

st.set_page_config(page_title="한국 지역 카드 뒤집기 게임", page_icon="🗺️", layout="centered")

# ---------------------------------------------------------------------------
# 데이터
# ---------------------------------------------------------------------------
# 각 항목: 지역명 카드 + 대표 명소/축제 카드로 짝을 이룸
REGION_DATA = [
    {"region": "제주", "spot": "한라산", "icon": "⛰️", "blurb": "화산이 빚은 섬, 사계절 다른 얼굴을 보여주는 제주 한라산."},
    {"region": "경주", "spot": "불국사", "icon": "🏛️", "blurb": "천년 신라의 숨결이 살아있는 고도, 경주 불국사."},
    {"region": "부산", "spot": "해운대", "icon": "🏖️", "blurb": "탁 트인 바다와 도심이 만나는 부산 해운대."},
    {"region": "전주", "spot": "한옥마을", "icon": "🏘️", "blurb": "기와지붕이 이어지는 전통의 골목, 전주 한옥마을."},
    {"region": "강릉", "spot": "경포대", "icon": "🌊", "blurb": "동해의 일출과 호수를 함께 품은 강릉 경포대."},
    {"region": "안동", "spot": "하회마을", "icon": "🎭", "blurb": "탈춤과 종가 문화가 살아 숨쉬는 안동 하회마을."},
    {"region": "여수", "spot": "밤바다", "icon": "⚓", "blurb": "노랫말처럼 반짝이는 낭만의 도시, 여수 밤바다."},
    {"region": "통영", "spot": "케이블카", "icon": "🚡", "blurb": "한려수도를 한눈에, 통영 미륵산 케이블카."},
]

DIFFICULTY_OPTIONS = {
    "쉬움 (3x4, 6쌍)": 6,
    "보통 (4x4, 8쌍)": 8,
    "어려움 (5x4 중 일부, 8쌍 큰 보드)": 8,  # 데이터가 8쌍뿐이라 최대 8쌍
}

# ---------------------------------------------------------------------------
# 스타일 (관광공사 느낌의 청록/코랄 컬러 팔레트)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f4faf8 0%, #ffffff 100%);
    }
    div.stButton > button {
        width: 100%;
        aspect-ratio: 1 / 1;
        border-radius: 14px;
        border: 1px solid #d8ece5;
        font-size: 15px;
        font-weight: 600;
        white-space: pre-line;
        transition: transform 0.08s ease;
    }
    div.stButton > button:hover {
        transform: scale(1.03);
        border-color: #1D9E75;
    }
    .card-back button {
        background-color: #eef6f3 !important;
        color: #7f9e94 !important;
    }
    .stat-box {
        background-color: #eef6f3;
        border-radius: 12px;
        padding: 10px 16px;
        text-align: center;
        font-size: 14px;
        color: #0f6e56;
        font-weight: 600;
    }
    .win-banner {
        background-color: #e1f5ee;
        border: 1px solid #1D9E75;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        color: #085041;
        font-weight: 700;
        font-size: 17px;
        margin-top: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 게임 상태 초기화
# ---------------------------------------------------------------------------
def new_game(num_pairs: int):
    chosen = random.sample(REGION_DATA, num_pairs)
    cards = []
    for i, item in enumerate(chosen):
        cards.append({"pair_id": i, "label": item["region"], "icon": item["icon"], "matched": False})
        cards.append({"pair_id": i, "label": item["spot"], "icon": item["icon"], "matched": False})
    random.shuffle(cards)

    st.session_state.cards = cards
    st.session_state.flipped = []  # 현재 뒤집혀 있는 카드 인덱스 (최대 2개)
    st.session_state.tries = 0
    st.session_state.matched_pairs = 0
    st.session_state.total_pairs = num_pairs
    st.session_state.pending_clear = False  # 오답 확인 후 정리 대기 상태
    st.session_state.best_score = st.session_state.get("best_score")
    st.session_state.blurb_log = []


if "cards" not in st.session_state:
    st.session_state.difficulty_label = "보통 (4x4, 8쌍)"
    new_game(DIFFICULTY_OPTIONS[st.session_state.difficulty_label])

# ---------------------------------------------------------------------------
# 사이드바
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🗺️ 게임 설정")

    difficulty_label = st.selectbox(
        "난이도 선택",
        options=list(DIFFICULTY_OPTIONS.keys()),
        index=list(DIFFICULTY_OPTIONS.keys()).index(st.session_state.difficulty_label),
    )
    if difficulty_label != st.session_state.difficulty_label:
        st.session_state.difficulty_label = difficulty_label
        new_game(DIFFICULTY_OPTIONS[difficulty_label])
        st.rerun()

    if st.session_state.get("best_score"):
        st.markdown(f"🏆 **최고 기록:** {st.session_state.best_score}번 만에 완성")
    else:
        st.markdown("🏆 아직 기록이 없어요. 첫 완성에 도전해보세요!")

    st.divider()
    st.subheader("찾은 지역 소개")
    if st.session_state.blurb_log:
        for text in st.session_state.blurb_log:
            st.markdown(f"- {text}")
    else:
        st.caption("카드를 맞추면 이곳에 지역 소개가 나타나요.")

# ---------------------------------------------------------------------------
# 메인 화면
# ---------------------------------------------------------------------------
st.title("🗺️ 한국 지역 카드 뒤집기 게임")
st.caption("지역명과 대표 명소를 짝지어 맞혀보세요!")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown(f"<div class='stat-box'>시도 횟수<br>{st.session_state.tries}</div>", unsafe_allow_html=True)
with col_b:
    st.markdown(
        f"<div class='stat-box'>맞춘 쌍<br>{st.session_state.matched_pairs} / {st.session_state.total_pairs}</div>",
        unsafe_allow_html=True,
    )
with col_c:
    if st.button("🔄 다시 섞기", use_container_width=True):
        new_game(st.session_state.total_pairs)
        st.rerun()

st.write("")

# 오답 확인 후, 다음 클릭에서 카드 정리
if st.session_state.pending_clear:
    st.session_state.flipped = []
    st.session_state.pending_clear = False

num_cards = len(st.session_state.cards)
num_cols = 4
rows = (num_cards + num_cols - 1) // num_cols

card_idx = 0
for _ in range(rows):
    cols = st.columns(num_cols)
    for c in cols:
        if card_idx >= num_cards:
            break
        card = st.session_state.cards[card_idx]
        is_open = card["matched"] or card_idx in st.session_state.flipped

        with c:
            if is_open:
                label = f"{card['icon']}\n{card['label']}"
                disabled = True
            else:
                label = "❓"
                disabled = st.session_state.pending_clear

            if c.button(label, key=f"card_{card_idx}", disabled=disabled or card["matched"]):
                if st.session_state.pending_clear:
                    st.session_state.flipped = []
                    st.session_state.pending_clear = False

                if card_idx not in st.session_state.flipped and not card["matched"]:
                    st.session_state.flipped.append(card_idx)

                if len(st.session_state.flipped) == 2:
                    st.session_state.tries += 1
                    i1, i2 = st.session_state.flipped
                    c1, c2 = st.session_state.cards[i1], st.session_state.cards[i2]
                    if c1["pair_id"] == c2["pair_id"]:
                        c1["matched"] = True
                        c2["matched"] = True
                        st.session_state.matched_pairs += 1
                        match_item = next(
                            item for item in REGION_DATA if item["region"] == c1["label"] or item["region"] == c2["label"]
                        )
                        if match_item["blurb"] not in st.session_state.blurb_log:
                            st.session_state.blurb_log.append(match_item["blurb"])
                        st.session_state.flipped = []
                    else:
                        st.session_state.pending_clear = True

                st.rerun()
        card_idx += 1

st.write("")

if st.session_state.matched_pairs == st.session_state.total_pairs:
    st.markdown(
        f"<div class='win-banner'>🎉 모든 지역을 다 찾았어요! 총 {st.session_state.tries}번 만에 완성!</div>",
        unsafe_allow_html=True,
    )
    if not st.session_state.get("best_score") or st.session_state.tries < st.session_state.best_score:
        st.session_state.best_score = st.session_state.tries
        st.balloons()

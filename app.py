import streamlit as st
import google.generativeai as genai
import random
import time
from datetime import datetime

# --- 페이지 설정 ---
st.set_page_config(
    page_title="AI 메뉴 소믈리에",
    page_icon="🍽️",
    layout="centered"
)

# --- 스타일 커스텀 ---
st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; font-weight: bold; text-align: center; color: #FF4B4B; margin-bottom: 10px; }
    .sub-title { text-align: center; color: #666; margin-bottom: 30px; }
    .menu-card { padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #FF4B4B; }
    .winner-card { padding: 30px; background-color: #ffecec; border-radius: 15px; text-align: center; border: 2px solid #FF4B4B; }
    </style>
""", unsafe_allow_html=True)

# --- 1. 시크릿 키 설정 ---
# 로컬에서는 .streamlit/secrets.toml 파일을 사용하고,
# 배포 시에는 Streamlit Cloud의 Secrets 기능을 사용합니다.
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("API 키가 설정되지 않았습니다. Streamlit Secrets에 'GOOGLE_API_KEY'를 추가해주세요.")
    st.stop()

# --- 2. 시간 및 모델 설정 ---
# 1.5 Flash보다 똑똑한 1.5 Pro 모델 사용 (추론 능력 강화)
MODEL_NAME = "gemini-1.5-pro" 

def get_time_context():
    hour = datetime.now().hour
    if 5 <= hour < 11: return "아침", "🌅 상쾌한 아침"
    elif 11 <= hour < 16: return "점심", "☀️ 활기찬 점심"
    elif 16 <= hour < 22: return "저녁", "🌙 분위기 있는 저녁"
    else: return "야식", "🍺 출출한 밤 야식"

meal_type, time_greeting = get_time_context()

# --- 3. UI 구성 ---
st.markdown(f"<div class='main-title'>🍽️ {time_greeting} 추천</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Gemini AI가 당신의 상황에 딱 맞는 메뉴를 찾아드립니다.</div>", unsafe_allow_html=True)

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input("📍 현재 위치 (예: 강남역, 집, 부산)", placeholder="어디에 계신가요?")
        weather = st.selectbox("🌤️ 날씨", ["맑음", "비", "흐림", "눈", "더움", "추움", "미세먼지 심함"])
    with col2:
        mood = st.selectbox("😊 기분", ["신남", "우울", "스트레스 만땅", "평범", "배고픔", "다이어트 중", "술 고픔"])
        price = st.selectbox("💰 1인 예산", ["1만원 이하 (가성비)", "1~2만원 (적당히)", "2~5만원 (맛있는거)", "5만원 이상 (플렉스)", "상관없음"])
    
    submit_btn = st.form_submit_button("AI 메뉴 추천받기 (3가지 후보)")

# --- 4. 세션 상태 관리 (룰렛용) ---
if 'menu_candidates' not in st.session_state:
    st.session_state.menu_candidates = None

# --- 5. AI 추천 로직 ---
if submit_btn:
    if not location:
        st.warning("정확한 추천을 위해 위치를 입력해주세요!")
    else:
        with st.spinner(f"🧠 {MODEL_NAME}가 {location} 근처 맛집 트렌드와 메뉴를 분석 중입니다..."):
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                prompt = f"""
                당신은 메뉴 추천 전문가입니다. 사용자의 상황을 분석해 **3가지 서로 다른 스타일의 메뉴**를 추천해주세요.
                
                [사용자 정보]
                - 시간: {meal_type}
                - 위치: {location} (이 지역의 특색이나 맛집 트렌드 고려)
                - 날씨: {weather}
                - 기분: {mood}
                - 예산: {price}

                [요청사항]
                1. 3가지 추천 메뉴는 서로 겹치지 않는 스타일(예: 한식, 양식, 중식 등)로 구성하세요.
                2. 각 메뉴별로 추천 이유와 {location} 주변에서 먹기 좋은 팁을 한 줄로 적어주세요.
                3. 답변은 파이썬 리스트 형식으로 파싱할 수 있게 **반드시** 아래 형식(`|`로 구분)만 딱 출력하세요. 다른 말은 하지 마세요.
                
                형식: 메뉴명1:이유1|메뉴명2:이유2|메뉴명3:이유3
                """
                
                response = model.generate_content(prompt)
                
                # 응답 파싱
                raw_text = response.text.strip()
                candidates = []
                items = raw_text.split('|')
                for item in items:
                    if ':' in item:
                        name, reason = item.split(':', 1)
                        candidates.append({"name": name.strip(), "reason": reason.strip()})
                
                if len(candidates) >= 3:
                    st.session_state.menu_candidates = candidates[:3]
                else:
                    st.error("AI가 형식을 맞추지 못했습니다. 다시 시도해주세요.")
            
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# --- 6. 결과 화면 및 룰렛 ---
if st.session_state.menu_candidates:
    st.divider()
    st.subheader("📋 AI가 선정한 3가지 후보")
    
    cols = st.columns(3)
    for i, menu in enumerate(st.session_state.menu_candidates):
        with cols[i]:
            st.info(f"**후보 {i+1}**")
            st.markdown(f"### {menu['name']}")
            st.caption(menu['reason'])

    st.divider()
    st.markdown("### 🎲 결정장애 해결! 랜덤 룰렛 돌리기")
    
    if st.button("룰렛 START! 🎯", use_container_width=True):
        placeholder = st.empty()
        
        # 룰렛 애니메이션 효과
        for _ in range(15):
            picked = random.choice(st.session_state.menu_candidates)
            placeholder.markdown(f"<div class='winner-card'><h2>🎲 {picked['name']}...</h2></div>", unsafe_allow_html=True)
            time.sleep(0.1)
        
        # 최종 결과
        final_pick = random.choice(st.session_state.menu_candidates)
        placeholder.markdown(f"""
            <div class='winner-card'>
                <h1>👑 최종 선택: {final_pick['name']}</h1>
                <p>{final_pick['reason']}</p>
                <p>맛있는 식사 되세요!</p>
            </div>
        """, unsafe_allow_html=True)
        st.balloons()

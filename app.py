import streamlit as st
import google.generativeai as genai
import random
import time
from datetime import datetime

# --- 1. 페이지 및 스타일 설정 ---
st.set_page_config(
    page_title="결정의 신: AI 점메추/저메추", 
    page_icon="🍽️", 
    layout="centered"
)

st.markdown("""
    <style>
    /* 전체 폰트 및 배경 느낌 */
    .main-header { 
        text-align: center; 
        font-weight: 700;
        color: #FF4B4B; 
        margin-bottom: 10px; 
    }
    .sub-text {
        text-align: center;
        color: #6c757d;
        margin-bottom: 30px;
    }
    /* 메뉴 카드 스타일 */
    .menu-card { 
        padding: 20px; 
        border-radius: 12px; 
        margin-bottom: 15px; 
        background-color: white; 
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: 0.3s;
    }
    .menu-card:hover { 
        transform: translateY(-3px); 
        border-color: #FF4B4B;
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.2); 
    }
    /* 우승자 결과 박스 (그라데이션) */
    .winner-box {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white; 
        padding: 40px; 
        border-radius: 20px; 
        text-align: center;
        margin-top: 20px; 
        box-shadow: 0 10px 30px rgba(255, 75, 75, 0.4);
        animation: popUp 0.5s ease-out;
    }
    @keyframes popUp {
        0% { transform: scale(0.8); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    .winner-title { font-size: 1.2rem; opacity: 0.9; margin-bottom: 10px; }
    .winner-name { font-size: 3.5rem; font-weight: 800; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .winner-reason { font-size: 1.1rem; margin-top: 15px; font-weight: 300; }
    </style>
""", unsafe_allow_html=True)

# --- 2. API 키 및 모델 설정 ---
try:
    # Streamlit Cloud 배포 시 Secrets에서 가져옴
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("⚠️ API 키가 설정되지 않았습니다. .streamlit/secrets.toml을 확인하세요.")
    st.stop()

# ★★★ 요청하신 최신 고성능 모델 설정 ★★★
MODEL_NAME = "gemini-2.5-pro"

# --- 3. 시간대 자동 파악 로직 ---
def get_time_context():
    hour = datetime.now().hour
    if 5 <= hour < 11: return "아침", "🌅"
    elif 11 <= hour < 16: return "점심", "☀️"
    elif 16 <= hour < 22: return "저녁", "🌙"
    else: return "야식", "🍺"

time_txt, emoji = get_time_context()

# --- 4. 메인 UI 구성 ---
st.markdown(f"<h1 class='main-header'>{emoji} AI {time_txt} 메뉴 결정기</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-text'>Powered by <b>{MODEL_NAME}</b></div>", unsafe_allow_html=True)

# 세션 상태 초기화
if 'step' not in st.session_state: st.session_state.step = 0
if 'candidates' not in st.session_state: st.session_state.candidates = []

# 입력 폼 영역
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input("📍 위치 (동네/지역)", placeholder="예: 홍대, 성수동, 집")
        weather = st.selectbox("🌤️ 날씨", ["맑음", "비", "흐림", "눈", "미세먼지", "폭염", "한파"])
    with col2:
        mood = st.selectbox("😊 기분", ["신남", "피곤함", "우울", "스트레스 만땅", "배고픔", "다이어트", "술 땡김"])
        price = st.selectbox("💰 예산", ["가성비(저렴)", "적당함(보통)", "맛있는거(비쌈)", "가격상관없음(플렉스)"])

    # 버튼: 처음 시작하거나 다시 시작할 때
    btn_text = "AI에게 추천받기 🚀" if st.session_state.step == 0 else "조건 바꿔서 다시 받기 🔄"
    if st.button(btn_text, type="primary", use_container_width=True):
        st.session_state.step = 1
        st.session_state.candidates = [] # 초기화

# --- 5. [STEP 1] Gemini 2.5 Pro에게 메뉴 추천받기 ---
if st.session_state.step >= 1:
    # 아직 후보가 없으면 AI 호출
    if not st.session_state.candidates:
        with st.spinner(f"🧠 {MODEL_NAME}가 {location} 근처 트렌드와 당신의 기분을 분석 중..."):
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                
                # 프롬프트 엔지니어링
                prompt = f"""
                당신은 센스 있는 메뉴 추천 전문가입니다.
                
                [사용자 상황]
                - 시간: {time_txt}
                - 위치: {location} (이 지역의 분위기나 맛집 스타일을 고려할 것)
                - 날씨: {weather}
                - 기분: {mood}
                - 예산: {price}

                위 상황에 가장 적절한 **서로 다른 스타일의 메뉴 3가지**를 추천해주세요.
                
                [출력 형식]
                반드시 아래 포맷으로 3줄만 출력하세요. (설명은 짧고 매력적으로)
                메뉴명:추천이유
                메뉴명:추천이유
                메뉴명:추천이유
                """
                
                response = model.generate_content(prompt)
                
                # 결과 파싱
                lines = response.text.strip().split('\n')
                for line in lines:
                    if ':' in line:
                        name, reason = line.split(':', 1)
                        st.session_state.candidates.append({
                            'name': name.strip().replace("*", ""), 
                            'reason': reason.strip()
                        })
                
                # 파싱 결과가 3개 미만이면 재시도 유도
                if len(st.session_state.candidates) < 3:
                    st.warning("AI가 고민을 너무 많이 했나봐요. 다시 버튼을 눌러주세요!")
                    st.session_state.step = 0
                    
            except Exception as e:
                st.error(f"AI 호출 중 오류 발생: {e}")
                st.session_state.step = 0

    # 후보 리스트 출력
    if st.session_state.candidates:
        st.divider()
        st.markdown("### 📋 AI가 엄선한 3가지 후보")
        
        cols = st.columns(3)
        for i, item in enumerate(st.session_state.candidates):
            with cols[i]:
                st.markdown(f"""
                <div class='menu-card'>
                    <div style='font-size:1.2rem; font-weight:bold; color:#333;'>{i+1}. {item['name']}</div>
                    <div style='font-size:0.9rem; color:#666; margin-top:5px;'>{item['reason']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 룰렛 버튼
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if st.button("🎲 이 중에서 랜덤 결정! (룰렛 돌리기)", type="primary", use_container_width=True):
            st.session_state.step = 2

# --- 6. [STEP 2] 랜덤 룰렛 및 결과 발표 ---
if st.session_state.step == 2:
    st.divider()
    placeholder = st.empty()
    
    # 룰렛 애니메이션 효과 (빠르게 이름이 바뀜)
    candidate_names = [c['name'] for c in st.session_state.candidates]
    for _ in range(15): # 15번 깜빡임
        temp_pick = random.choice(candidate_names)
        placeholder.markdown(f"<h2 style='text-align:center; color:#ccc;'>🎲 {temp_pick}...</h2>", unsafe_allow_html=True)
        time.sleep(0.1) # 0.1초 간격
    
    # 최종 선택
    final_pick = random.choice(st.session_state.candidates)
    
    # 결과 화면 (그라데이션 박스)
    placeholder.markdown(f"""
        <div class='winner-box'>
            <div class='winner-title'>🎉 오늘의 {time_txt} 메뉴는 바로!</div>
            <div class='winner-name'>{final_pick['name']}</div>
            <div class='winner-reason'>"{final_pick['reason']}"</div>
            <div style='margin-top:20px; font-size:0.8rem; opacity:0.8;'>📍 {location} 근처에서 맛집을 찾아보세요!</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.balloons() # 축하 효과
    
    # 리셋 버튼
    if st.button("처음으로 돌아가기"):
        st.session_state.step = 0
        st.session_state.candidates = []
        st.rerun()

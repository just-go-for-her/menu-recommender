import streamlit as st
import random
import datetime
import pytz # 한국 시간 설정을 위한 라이브러리

# ---------------------------------------------------------
# 1. 데이터베이스 & 설정
# ---------------------------------------------------------
menu_db = [
    {"name": "뜨끈한 순대국/국밥", "price": 1, "tags": ["rain", "cold", "lunch", "soup", "alcohol"]},
    {"name": "편의점 도시락/라면", "price": 1, "tags": ["busy", "lunch"]},
    {"name": "매운 떡볶이", "price": 1, "tags": ["stress", "lunch", "dinner"]},
    {"name": "김치찌개/부대찌개", "price": 1, "tags": ["rain", "lunch", "soup"]},
    {"name": "햄버거/샌드위치", "price": 1, "tags": ["busy", "lunch", "greasy"]},
    
    {"name": "삼겹살 구이", "price": 2, "tags": ["dinner", "dust", "greasy", "alcohol"]},
    {"name": "파스타 & 피자", "price": 2, "tags": ["date", "lunch", "dinner"]},
    {"name": "마라탕", "price": 2, "tags": ["stress", "rain", "soup"]},
    {"name": "치킨 (치느님)", "price": 2, "tags": ["dinner", "beer", "sports"]},
    {"name": "해물파전 & 칼국수", "price": 2, "tags": ["rain", "soup", "alcohol"]},
    {"name": "족발/보쌈", "price": 2, "tags": ["dinner", "alcohol", "late"]},
    
    {"name": "고급 모듬회/참치", "price": 3, "tags": ["dinner", "alcohol", "fresh"]},
    {"name": "한우 소고기", "price": 3, "tags": ["dinner", "flex", "greasy"]},
    {"name": "호텔 뷔페", "price": 3, "tags": ["lunch", "dinner", "flex"]},
    {"name": "오마카세", "price": 3, "tags": ["dinner", "date", "fresh"]}
]

# ---------------------------------------------------------
# 2. 로직 함수
# ---------------------------------------------------------
def get_recommendations(budget_choice, time_tag, weather_input):
    candidates = []
    
    # 날씨 태그 변환
    weather_tags = []
    if "비" in weather_input: weather_tags.append("rain")
    if "눈" in weather_input or "추움" in weather_input: weather_tags.append("cold")
    if "더움" in weather_input: weather_tags.append("hot")
    if "스트레스" in weather_input: weather_tags.append("stress")

    for menu in menu_db:
        if menu["price"] == budget_choice:
            score = 0
            reason = "무난한 선택!"
            
            # 시간 가중치
            if time_tag in menu["tags"]: score += 10
            
            # 날씨/상황 가중치
            if "rain" in weather_tags and ("soup" in menu["tags"] or "rain" in menu["tags"]):
                score += 20
                reason = "☔ 비 오는 날엔 국물/전이 국룰!"
            if "stress" in weather_tags and "stress" in menu["tags"]:
                score += 20
                reason = "🔥 스트레스엔 매운맛으로 해소!"
            if "cold" in weather_tags and "soup" in menu["tags"]:
                score += 15
                reason = "❄️ 추운 날씨에 몸을 녹여줘요"
            if "alcohol" in menu["tags"] and time_tag == "dinner":
                score += 5 # 저녁 술안주 가산점

            score += random.randint(0, 5) # 랜덤 요소
            
            candidates.append({"name": menu["name"], "score": score, "reason": reason})
    
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:3]

# ---------------------------------------------------------
# 3. 화면 구성 (UI)
# ---------------------------------------------------------
st.set_page_config(page_title="너의 메뉴는?", page_icon="🍽️")

st.title("🍽️ AI 점메추/저메추 솔루션")
st.subheader("결정 장애 해결해 드립니다!")

# 1. 자동 시간 체크 (한국 시간)
KST = pytz.timezone('Asia/Seoul')
now = datetime.datetime.now(KST)
current_hour = now.hour

if 11 <= current_hour <= 14:
    time_tag = "lunch"
    time_msg = "점심"
elif 17 <= current_hour <= 20:
    time_tag = "dinner"
    time_msg = "저녁"
elif 21 <= current_hour <= 4:
    time_tag = "late"
    time_msg = "야식"
else:
    time_tag = "snack"
    time_msg = "간식"

st.info(f"🕒 현재 시간은 **[{time_msg}]** 타임으로 인식되었습니다.")

# 2. 사용자 입력
col1, col2 = st.columns(2)

with col1:
    weather_options = ["맑음/평범☀️", "비 옴☔", "눈/추움❄️", "더움/폭염🔥", "스트레스 만땅😡"]
    weather_input = st.selectbox("오늘 날씨나 기분은?", weather_options)

with col2:
    budget_map = {"텅장 지킴이 (1만원 ↓)": 1, "소확행 (1~2만원)": 2, "금융 치료 (2만원 ↑)": 3}
    budget_key = st.selectbox("지갑 사정은?", list(budget_map.keys()))
    budget_choice = budget_map[budget_key]

# 3. 결과 버튼
if st.button("👉 메뉴 추천받기 (Click)", use_container_width=True):
    with st.spinner('AI가 메뉴를 분석 중입니다...'):
        import time
        time.sleep(1) # 분석하는 척 (재미 요소)
        results = get_recommendations(budget_choice, time_tag, weather_input)
    
    st.divider()
    
    if results:
        # 1등 강조
        st.markdown(f"### 👑 오늘의 원픽: **{results[0]['name']}**")
        st.success(f"💡 {results[0]['reason']}")
        
        # 2,3등
        if len(results) > 1:
            st.markdown("#### 아쉬운 2등 & 3등")
            st.text(f"🥈 {results[1]['name']}")
            st.text(f"🥉 {results[2]['name']}")
    else:
        st.error("조건에 맞는 메뉴가 없어요 ㅠㅠ")

import streamlit as st
import pandas as pd
import numpy as np
import requests

# -----------------------------------------------------------------------------
# 0. Page Configuration & Custom Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="다문화 통계 조사 마이크로데이터 분석 플랫폼",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .card {
        background-color: #F8FAFC;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #2563EB;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. Helper Functions (API Key Load & Solar API Call)
# -----------------------------------------------------------------------------
def get_secret(key_name: str) -> str:
    """secrets.toml 또는 Streamlit Cloud Secrets에서 키 로드"""
    if key_name in st.secrets:
        return st.secrets[key_name]
    return ""

def ask_solar_api(data_text: str, user_query: str) -> str:
    """Upstage Solar API를 호출하여 입력 자료에 기반한 한국어 답변 생성"""
    solar_key = get_secret("SOLAR_API_KEY")
    if not solar_key:
        return "⚠️ `SOLAR_API_KEY`가 설정되어 있지 않습니다. Secrets에 API 키를 등록해주세요."

    system_prompt = f"""당신은 아래 제공된 다문화 관련 조사 자료만을 근거로 사용자의 질문에 정확하고 명확하게 한국어로 답변하는 전문 연구 보조 AI입니다.

[지침]
1. 반드시 제공된 [근거 자료] 내용을 기반으로만 답변하세요.
2. 자료에 명시되어 있지 않은 내용은 억지로 추측하지 말고 "제공된 자료에서 해당 내용을 찾을 수 없습니다."라고 안내하세요.
3. 한국어로 이해하기 쉽고 명확한 구조로 답변하세요.

[근거 자료]:
{data_text}"""

    url = "https://api.upstage.ai/v1/solar/chat/completions"
    headers = {
        "Authorization": f"Bearer {solar_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "solar-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"❌ Solar API 호출 오류 (코드: {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ API 연결 중 오류가 발생했습니다: {str(e)}"

# -----------------------------------------------------------------------------
# 2. Dummy Data Generators
# -----------------------------------------------------------------------------
@st.cache_data
def fetch_youth_panel_data():
    """1. 다문화청소년패널조사 마이크로데이터"""
    np.random.seed(42)
    n = 300
    return pd.DataFrame({
        "조사차수": np.random.choice([f"{i}차년도" for i in range(1, 6)], n),
        "지역": np.random.choice(["서울", "경기", "인천", "부산/경남", "대구/경북", "호남/충청/강원"], n),
        "청소년 성별": np.random.choice(["남성", "여성"], n),
        "정체성 형성 정도": np.random.choice(["높음", "보통", "낮음"], n, p=[0.5, 0.35, 0.15]),
        "학교적응도 (5점)": np.round(np.random.uniform(2.5, 5.0, n), 2),
        "한국어 능숙도 (5점)": np.round(np.random.uniform(3.0, 5.0, n), 2)
    })

@st.cache_data
def fetch_acceptability_data():
    """2. 국민 다문화수용성실태조사 마이크로데이터"""
    np.random.seed(101)
    n = 500
    return pd.DataFrame({
        "성별": np.random.choice(["남성", "여성"], n),
        "연령대": np.random.choice(["20대 이하", "30대", "40대", "50대", "60대 이상"], n),
        "지역": np.random.choice(["서울", "경기", "인천", "지방 광역시", "기타 시군"], n),
        "외국인 이웃 수용 여부": np.random.choice(["수용 가능", "조건부 수용", "수용 불가"], n, p=[0.6, 0.3, 0.1]),
        "진정한 한국인 인정 성향": np.random.choice(["혈통 중심", "문화/법적 거주 중심", "상관없음"], n, p=[0.3, 0.5, 0.2]),
        "외국 이주민 공직 출마 찬성": np.random.choice(["찬성", "중립", "반대"], n, p=[0.35, 0.35, 0.3]),
        "다문화 수용성 종합점수 (100점)": np.clip(np.round(np.random.normal(62, 12, n), 1), 0, 100)
    })

@st.cache_data
def fetch_family_survey_data():
    """3. 전국다문화가족실태조사 마이크로데이터"""
    np.random.seed(202)
    n = 400
    years = [2018, 2021, 2024]
    items = ["가구 월평균 소득(만원)", "자녀 양육 어려움 정도(5점)", "한국 생활 만족도(5점)", "차별 경험 비율(%)"]
    groups = ["결혼이민자", "귀화자", "다문화자녀", "배우자"]
    
    rows = []
    for i in range(1, n + 1):
        year = int(np.random.choice(years))
        item = np.random.choice(items)
        val = np.random.randint(150, 650) if item == "가구 월평균 소득(만원)" else np.round(np.random.uniform(2.0, 5.0), 1)
        rows.append({
            "실태조사연도": year,
            "실태조사대상 일련번호": f"ID-{year}-{i:04d}",
            "실태조사대상명": np.random.choice(groups),
            "실태조사항목명": item,
            "실태조사값": val,
            "데이터 기준 일자": f"{year}-12-31"
        })
    return pd.DataFrame(rows)

# -----------------------------------------------------------------------------
# 3. Sidebar Page Navigation
# -----------------------------------------------------------------------------
st.sidebar.title("📌 조사별 전용 페이지")

page = st.sidebar.radio(
    "이동할 페이지를 선택하세요:",
    [
        "1. 다문화청소년패널조사",
        "2. 국민 다문화수용성실태조사",
        "3. 전국다문화가족실태조사",
        "4. 3개 조사 종합 비교·분석"
    ]
)

# -----------------------------------------------------------------------------
# PAGE 1: 다문화청소년패널조사
# -----------------------------------------------------------------------------
if page == "1. 다문화청소년패널조사":
    st.markdown("<div class='main-header'>🌱 다문화청소년패널조사</div>", unsafe_allow_html=True)
    
    info_text = """다문화가정의 지속적인 증가라는 사회적 변화 속에서 다문화청소년의 성장과 발달 특성을 체계적으로 분석하기 위해 구축된 종단 조사 자료입니다. 본 조사는 다문화청소년과 그 보호자를 대상으로 개인적 특성, 다문화 관련 경험과 인식, 가정·학교·지역사회 등 환경 요인을 주요 변인으로 설정하여 반복적으로 조사합니다. 이를 통해 다문화청소년의 정체성 형성, 적응 과정, 발달 특성 및 생활 여건의 변화를 장기적으로 파악할 수 있으며, 다문화 정책 수립, 제도 개선, 학술 연구 및 통계 분석을 위한 핵심 기초 자료로 활용됩니다."""
    
    st.markdown(f"<div class='card'><b>조사 개요:</b><br>{info_text}</div>", unsafe_allow_html=True)

    df = fetch_youth_panel_data()

    col1, col2 = st.columns(2)
    with col1:
        wave_filter = st.multiselect("조사차수 선택", options=df["조사차수"].unique(), default=df["조사차수"].unique()[:2])
    with col2:
        region_filter = st.multiselect("지역 선택", options=df["지역"].unique(), default=df["지역"].unique())

    filtered_df = df[(df["조사차수"].isin(wave_filter)) & (df["지역"].isin(region_filter))]

    st.subheader("📈 주요 핵심 지표")
    m1, m2, m3 = st.columns(3)
    m1.metric("분석 대상 인원", f"{len(filtered_df):,} 명")
    m2.metric("평균 학교적응도", f"{filtered_df['학교적응도 (5점)'].mean():.2f} / 5.0")
    m3.metric("평균 한국어 능숙도", f"{filtered_df['한국어 능숙도 (5점)'].mean():.2f} / 5.0")

    c1, c2 = st.columns(2)
    with c1:
        st.write("**[정체성 형성 정도 분포]**")
        st.bar_chart(filtered_df["정체성 형성 정도"].value_counts())
    with c2:
        st.write("**[차수별 평균 학교적응도]**")
        st.line_chart(filtered_df.groupby("조사차수")["학교적응도 (5점)"].mean())

    with st.expander("📄 마이크로데이터 상세 조회"):
        st.dataframe(filtered_df, use_container_width=True)

    # Solar AI Q&A Section
    st.markdown("---")
    st.subheader("🤖 Solar AI 기반 자료 Q&A")
    user_q = st.text_input("위 조사 자료를 근거로 궁금한 점을 질문하세요:", placeholder="예: 다문화청소년패널조사의 주요 목적과 활용 방안은 무엇인가요?")
    
    if st.button("확인하기", key="btn_p1"):
        if user_q.strip():
            context = f"{info_text}\n\n[통계 요약 데이터]\n" + filtered_df.describe().to_string()
            with st.spinner("Solar AI가 자료를 바탕으로 답변을 분석 중입니다..."):
                answer = ask_solar_api(context, user_q)
            st.markdown("### 💬 AI 답변")
            st.write(answer)
        else:
            st.warning("질문을 입력해주세요.")

# -----------------------------------------------------------------------------
# PAGE 2: 국민 다문화수용성실태조사
# -----------------------------------------------------------------------------
elif page == "2. 국민 다문화수용성실태조사":
    st.markdown("<div class='main-header'>🌏 국민 다문화수용성실태조사</div>", unsafe_allow_html=True)

    info_text = """성별, 연령별, 지역별로 다문화 다양성 차원에 대한 응답, 외국인 거주에 대한 태도, 이웃으로 삼을 수 있는지의 여부, 진정한 한국인으로 인정 가능성에 대한 인식, 외국이주민의 공직 출마에 대한 인식 등의 통계조사 결과를 확인할 수 있습니다. 다문화에 대한 국민의 인식과 태도를 성별·연령·지역 등 다양한 특성별로 분석할 수 있어, 정책 대상별 맞춤형 사회통합 전략 수립에 활용됩니다. 또한 외국인에 대한 수용성 및 인식 변화 등을 파악하여 다문화 사회에 대한 이해 증진과 관련 제도 개선, 교육 및 홍보 자료 개발 등에 유익하게 활용될 수 있습니다."""

    st.markdown(f"<div class='card'><b>조사 개요:</b><br>{info_text}</div>", unsafe_allow_html=True)

    df = fetch_acceptability_data()

    col1, col2 = st.columns(2)
    with col1:
        age_filter = st.multiselect("연령대 선택", options=df["연령대"].unique(), default=df["연령대"].unique())
    with col2:
        region_filter = st.multiselect("지역 선택", options=df["지역"].unique(), default=df["지역"].unique())

    filtered_df = df[(df["연령대"].isin(age_filter)) & (df["지역"].isin(region_filter))]

    st.subheader("📈 다문화 수용성 핵심지표")
    m1, m2, m3 = st.columns(3)
    m1.metric("총 응답 샘플", f"{len(filtered_df):,} 명")
    m2.metric("평균 수용성 점수", f"{filtered_df['다문화 수용성 종합점수 (100점)'].mean():.1f} 점")
    m3.metric("이웃 수용 긍정 비율", f"{(filtered_df['외국인 이웃 수용 여부'] == '수용 가능').mean() * 100:.1f}%")

    st.subheader("📊 차원별 분석")
    t1, t2 = st.tabs(["연령대별 수용성 점수", "외국인 공직 출마 인식"])
    with t1:
        st.bar_chart(filtered_df.groupby("연령대")["다문화 수용성 종합점수 (100점)"].mean())
    with t2:
        st.bar_chart(pd.crosstab(filtered_df["성별"], filtered_df["외국 이주민 공직 출마 찬성"]))

    with st.expander("📄 마이크로데이터 상세 조회"):
        st.dataframe(filtered_df, use_container_width=True)

    # Solar AI Q&A Section
    st.markdown("---")
    st.subheader("🤖 Solar AI 기반 자료 Q&A")
    user_q = st.text_input("위 조사 자료를 근거로 궁금한 점을 질문하세요:", placeholder="예: 국민 다문화수용성 조사는 어떤 용도로 활용되나요?")
    
    if st.button("확인하기", key="btn_p2"):
        if user_q.strip():
            context = f"{info_text}\n\n[통계 요약 데이터]\n" + filtered_df.describe().to_string()
            with st.spinner("Solar AI가 자료를 바탕으로 답변을 분석 중입니다..."):
                answer = ask_solar_api(context, user_q)
            st.markdown("### 💬 AI 답변")
            st.write(answer)
        else:
            st.warning("질문을 입력해주세요.")

# -----------------------------------------------------------------------------
# PAGE 3: 전국다문화가족실태조사
# -----------------------------------------------------------------------------
elif page == "3. 전국다문화가족실태조사":
    st.markdown("<div class='main-header'>🏠 전국다문화가족실태조사</div>", unsafe_allow_html=True)

    info_text = """실태조사연도, 실태조사대상 일련번호, 실태조사대상명, 실태조사항목명, 실태조사값, 데이터 기준 일자 등의 내용을 확인할 수 있습니다. 조사 항목별 응답 데이터를 세분화된 수준에서 분석할 수 있습니다. 실태조사 대상별 일련번호와 항목명이 포함되어 있어, 특정 연도나 특정 그룹에 대한 비교·분석이 가능해 정책 기획의 정밀도를 높일 수 있습니다. 또한 실태조사값을 활용하여 데이터 기반의 인사이트 도출이 가능하며, 다문화 가족 정책의 개선과 현황 분석자료로도 활용될 수 있습니다."""

    st.markdown(f"<div class='card'><b>조사 개요:</b><br>{info_text}</div>", unsafe_allow_html=True)

    df = fetch_family_survey_data()

    col1, col2, col3 = st.columns(3)
    with col1:
        year_filter = st.multiselect("조사연도", options=df["실태조사연도"].unique(), default=df["실태조사연도"].unique())
    with col2:
        target_filter = st.multiselect("조사대상", options=df["실태조사대상명"].unique(), default=df["실태조사대상명"].unique())
    with col3:
        item_filter = st.selectbox("조사항목 선택", options=df["실태조사항목명"].unique())

    filtered_df = df[
        (df["실태조사연도"].isin(year_filter)) &
        (df["실태조사대상명"].isin(target_filter)) &
        (df["실태조사항목명"] == item_filter)
    ]

    st.subheader(f"📊 '{item_filter}' 세부 분석")
    if not filtered_df.empty:
        summary_df = filtered_df.groupby(["실태조사연도", "실태조사대상명"])["실태조사값"].mean().unstack()
        st.dataframe(summary_df.style.highlight_max(axis=0), use_container_width=True)
        st.bar_chart(summary_df)
    else:
        st.warning("선택 조건에 부합하는 데이터가 없습니다.")

    with st.expander("📄 마이크로데이터 상세 목록"):
        st.dataframe(filtered_df, use_container_width=True)

    # Solar AI Q&A Section
    st.markdown("---")
    st.subheader("🤖 Solar AI 기반 자료 Q&A")
    user_q = st.text_input("위 조사 자료를 근거로 궁금한 점을 질문하세요:", placeholder="예: 전국다문화가족실태조사의 주요 항목과 정책적 효과는 무엇인가요?")
    
    if st.button("확인하기", key="btn_p3"):
        if user_q.strip():
            context = f"{info_text}\n\n[선택 항목 데이터 요약]\n" + filtered_df.to_string()
            with st.spinner("Solar AI가 자료를 바탕으로 답변을 분석 중입니다..."):
                answer = ask_solar_api(context, user_q)
            st.markdown("### 💬 AI 답변")
            st.write(answer)
        else:
            st.warning("질문을 입력해주세요.")

# -----------------------------------------------------------------------------
# PAGE 4: 3개 조사 종합 비교·분석
# -----------------------------------------------------------------------------
else:
    st.markdown("<div class='main-header'>📊 3개 조사 통합 비교 및 인사이트</div>", unsafe_allow_html=True)
    st.write("3가지 다문화 실태 및 마이크로데이터 통합 정보입니다.")

    text1 = "1. 다문화청소년패널조사: 청소년과 보호자의 정체성 형성, 학교적응 및 환경 요인을 장기 파악하여 정책 기초자료로 활용."
    text2 = "2. 국민 다문화수용성실태조사: 성별·연령·지역별 외국인 이웃/거주 수용성 및 공직 출마 인식 분석을 통한 맞춤형 사회통합 전략 수립."
    text3 = "3. 전국다문화가족실태조사: 연도, 대상, 항목별 마이크로데이터 분석을 통해 정책 정밀도를 제고하고 다문화가족 현황 개선."

    combined_context = f"{text1}\n{text2}\n{text3}"

    st.markdown(f"""
    <div class='card'>
    <b>통합 개요:</b><br>
    • {text1}<br>
    • {text2}<br>
    • {text3}
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("🌱 **청소년패널조사**")
        st.write("청소년 발달 및 정체성 적응")
    with c2:
        st.info("🌏 **국민수용성조사**")
        st.write("사회적 수용성 및 인식 개선")
    with c3:
        st.info("🏠 **다문화가족실태**")
        st.write("가구 실태 및 세부 정책 정밀도")

    st.markdown("---")
    st.subheader("🤖 Solar AI 기반 3개 조사 통합 질의")
    user_q = st.text_input("3개 조사 전체를 바탕으로 종합 질의를 입력하세요:", placeholder="예: 3개 자료를 종합해서 볼 때, 정책적 시사점은 무엇인가요?")
    
    if st.button("확인하기", key="btn_p4"):
        if user_q.strip():
            with st.spinner("Solar AI가 3개 조사 자료를 종합 분석 중입니다..."):
                answer = ask_solar_api(combined_context, user_q)
            st.markdown("### 💬 AI 답변")
            st.write(answer)
        else:
            st.warning("질문을 입력해주세요.")

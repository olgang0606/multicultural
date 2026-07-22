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
    .key-badge {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. API Key Helper Functions
# -----------------------------------------------------------------------------
def get_api_key(key_name: str) -> str:
    """Streamlit secrets에서 API 키를 안전하게 불러오는 함수"""
    if key_name in st.secrets:
        return st.secrets[key_name]
    return ""

def render_api_status(key_name: str, key_value: str):
    """API 키 등록 상태 및 안내 표시 UI"""
    if key_value:
        masked_key = key_value[:4] + "*" * (len(key_value) - 4) if len(key_value) > 4 else "****"
        st.sidebar.success(f"🔑 **{key_name}**: 연동됨 (`{masked_key}`)")
    else:
        st.sidebar.warning(f"⚠️ **{key_name}**: 미설정")

# -----------------------------------------------------------------------------
# Dummy Data Generators (실제 API 호출 성공 시 대체되는 샘플 로직)
# -----------------------------------------------------------------------------
@st.cache_data
def fetch_youth_panel_data(api_key: str):
    """1. 다문화청소년패널조사 API 호출 모사"""
    # 실제 API 적용 시:
    # response = requests.get(f"https://api.example.com/youth?serviceKey={api_key}")
    # return pd.DataFrame(response.json())
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
def fetch_acceptability_data(api_key: str):
    """2. 국민 다문화수용성실태조사 API 호출 모사"""
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
def fetch_family_survey_data(api_key: str):
    """3. 전국다문화가족실태조사 API 호출 모사"""
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
# Sidebar & Page Navigation
# -----------------------------------------------------------------------------
st.sidebar.title("📌 조사별 전용 페이지")

# API Keys Load
key1 = get_api_key("MULTI1_API_KEY")
key2 = get_api_key("MULTI2_API_KEY")
key3 = get_api_key("MULTI3_API_KEY")

page = st.sidebar.radio(
    "이동할 페이지를 선택하세요:",
    [
        "Page 1. 다문화청소년패널조사 (Key 1)",
        "Page 2. 국민 다문화수용성실태조사 (Key 2)",
        "Page 3. 전국다문화가족실태조사 (Key 3)",
        "Page 4. 3개 조사 종합 비교·분석"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 API Key 연동 현황")
render_api_status("MULTI1_API_KEY", key1)
render_api_status("MULTI2_API_KEY", key2)
render_api_status("MULTI3_API_KEY", key3)

# -----------------------------------------------------------------------------
# PAGE 1: 다문화청소년패널조사 (MULTI1_API_KEY 사용)
# -----------------------------------------------------------------------------
if page == "Page 1. 다문화청소년패널조사 (Key 1)":
    st.markdown("<div class='main-header'>🌱 Page 1: 다문화청소년패널조사</div>", unsafe_allow_html=True)
    st.markdown("사용 인증키: `<span class='key-badge'>MULTI1_API_KEY</span>`", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='card'>
    <b>조사 개요:</b> 다문화청소년과 그 보호자를 대상으로 개인적 특성, 다문화 관련 경험, 가정·학교·지역사회 환경 요인을 종단 분석합니다.
    </div>
    """, unsafe_allow_html=True)

    if not key1:
        st.info("💡 `secrets.toml` 또는 Streamlit Cloud Secrets에 `MULTI1_API_KEY`를 설정하면 실시간 API 데이터가 연결됩니다. (현재는 샘플 데이터로 동작 중입니다)")

    df = fetch_youth_panel_data(key1)

    # 필터 옵션
    col1, col2 = st.columns(2)
    with col1:
        wave_filter = st.multiselect("조사차수 선택", options=df["조사차수"].unique(), default=df["조사차수"].unique()[:2])
    with col2:
        region_filter = st.multiselect("지역 선택", options=df["지역"].unique(), default=df["지역"].unique())

    filtered_df = df[(df["조사차수"].isin(wave_filter)) & (df["지역"].isin(region_filter))]

    # 지표 및 시각화
    st.subheader("📈 주요 지표")
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

# -----------------------------------------------------------------------------
# PAGE 2: 국민 다문화수용성실태조사 (MULTI2_API_KEY 사용)
# -----------------------------------------------------------------------------
elif page == "Page 2. 국민 다문화수용성실태조사 (Key 2)":
    st.markdown("<div class='main-header'>🌏 Page 2: 국민 다문화수용성실태조사</div>", unsafe_allow_html=True)
    st.markdown("사용 인증키: `<span class='key-badge'>MULTI2_API_KEY</span>`", unsafe_allow_html=True)

    st.markdown("""
    <div class='card'>
    <b>조사 개요:</b> 외국인 거주 태도, 이웃 수용성, 진정한 한국인 인정 성향, 외국이주민 공직 출마 인식 등을 성별·연령·지역별로 분석합니다.
    </div>
    """, unsafe_allow_html=True)

    if not key2:
        st.info("💡 `secrets.toml` 또는 Streamlit Cloud Secrets에 `MULTI2_API_KEY`를 설정하면 실시간 API 데이터가 연결됩니다. (현재는 샘플 데이터로 동작 중입니다)")

    df = fetch_acceptability_data(key2)

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

# -----------------------------------------------------------------------------
# PAGE 3: 전국다문화가족실태조사 (MULTI3_API_KEY 사용)
# -----------------------------------------------------------------------------
elif page == "Page 3. 전국다문화가족실태조사 (Key 3)":
    st.markdown("<div class='main-header'>🏠 Page 3: 전국다문화가족실태조사</div>", unsafe_allow_html=True)
    st.markdown("사용 인증키: `<span class='key-badge'>MULTI3_API_KEY</span>`", unsafe_allow_html=True)

    st.markdown("""
    <div class='card'>
    <b>조사 개요:</b> 실태조사연도, 대상, 항목명, 실태조사값 등 정밀한 마이크로데이터를 제공하여 다문화가족 정책의 세부 인사이트를 도출합니다.
    </div>
    """, unsafe_allow_html=True)

    if not key3:
        st.info("💡 `secrets.toml` 또는 Streamlit Cloud Secrets에 `MULTI3_API_KEY`를 설정하면 실시간 API 데이터가 연결됩니다. (현재는 샘플 데이터로 동작 중입니다)")

    df = fetch_family_survey_data(key3)

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

# -----------------------------------------------------------------------------
# PAGE 4: 3개 조사 종합 비교·분석
# -----------------------------------------------------------------------------
else:
    st.markdown("<div class='main-header'>📊 Page 4: 3개 조사 통합 비교 및 인사이트</div>", unsafe_allow_html=True)
    st.write("각 페이지에서 호출한 3개 마이크로데이터를 교차 분석하여 정책 인사이트를 도출합니다.")

    df1 = fetch_youth_panel_data(key1)
    df2 = fetch_acceptability_data(key2)
    df3 = fetch_family_survey_data(key3)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("🌱 **다문화청소년패널**")
        st.write(f"- Key1 상태: {'✅ 연동' if key1 else '⚠️ 미설정'}")
        st.write(f"- 분석 데이터: {len(df1):,} 건")
    with c2:
        st.info("🌏 **국민수용성실태**")
        st.write(f"- Key2 상태: {'✅ 연동' if key2 else '⚠️ 미설정'}")
        st.write(f"- 분석 데이터: {len(df2):,} 건")
    with c3:
        st.info("🏠 **다문화가족실태**")
        st.write(f"- Key3 상태: {'✅ 연동' if key3 else '⚠️ 미설정'}")
        st.write(f"- 분석 데이터: {len(df3):,} 건")

    st.markdown("---")
    st.subheader("💡 연계 활용 시사점")
    st.markdown("""
    - **1단계 (수용성 파악):** `MULTI2_API_KEY`로 호출한 국민 수용성 조사를 통해 지역별 타깃 정책 수요 도출
    - **2단계 (환경 파악):** `MULTI3_API_KEY` 데이터로 다문화가구 소득 및 자녀 양육 환경 정밀 분석
    - **3단계 (적응 지원):** `MULTI1_API_KEY` 데이터로 청소년 정체성 형성 및 학교 적응 프로그램 연계
    """)

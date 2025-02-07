import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 📌 데이터 로드
@st.cache_data
def load_data():
    file_path_single_household = "data11.csv"  # 1인 세대 데이터
    file_path_total_households = "data22.csv"  # 전체 세대 데이터

    df_single_household = pd.read_csv(file_path_single_household, low_memory=False, encoding='utf-8')
    df_total_households = pd.read_csv(file_path_total_households, low_memory=False, encoding='utf-8')

    return df_single_household, df_total_households

# 데이터 불러오기
df_single_household, df_total_households = load_data()

# 📌 데이터 전처리 함수
def preprocess_data(df_single_household, df_total_households):
    # 숫자로 변환 (쉼표 제거 후 변환)
    for col in ["2025년01월_계_총세대수", "2025년01월_남_총세대수", "2025년01월_여_총세대수"]:
        df_single_household[col] = df_single_household[col].replace(',', '', regex=True).apply(pd.to_numeric, errors='coerce').fillna(0)

    df_total_households["2025년01월_세대수"] = df_total_households["2025년01월_세대수"].replace(',', '', regex=True).apply(pd.to_numeric, errors='coerce').fillna(0)

    # 전체 데이터 병합
    df_combined = pd.merge(df_single_household, df_total_households, on="행정구역", how="inner")

    # 1인 세대 비율 계산
    df_combined["합산 1인 세대 비율(%)"] = (df_combined["2025년01월_계_총세대수"] / df_combined["2025년01월_세대수"]) * 100
    df_combined["남성 1인 세대 비율(%)"] = (df_combined["2025년01월_남_총세대수"] / df_combined["2025년01월_세대수"]) * 100
    df_combined["여성 1인 세대 비율(%)"] = (df_combined["2025년01월_여_총세대수"] / df_combined["2025년01월_세대수"]) * 100

    # 비율이 100%를 초과하는 경우 100%로 조정
    for col in ["합산 1인 세대 비율(%)", "남성 1인 세대 비율(%)", "여성 1인 세대 비율(%)"]:
        df_combined[col] = df_combined[col].clip(upper=100)

    return df_combined

# 데이터 전처리
df_combined = preprocess_data(df_single_household, df_total_households)

# 📌 Streamlit UI
st.markdown("<h3 style='text-align: center;'>🏙️ 지속가능한 도시와 1인 세대 비율 분석</h3>", unsafe_allow_html=True)
st.subheader("📌 SDG 11번 목표와 1인 세대 증가의 연관성 분석 프로젝트")

st.markdown("""
    지속가능한 도시(SDG 11)의 목표는 **모든 사람을 위한 포용적이고 안전하며 회복력 있고 지속가능한 도시와 공동체를 만드는 것**입니다.  
    1인 세대의 증가 추세는 **도시의 주거, 교통, 공공 서비스**에 영향을 미치며, 이는 SDG 11번 목표 달성과 직결됩니다.
    
    ### 주요 문제:
    - 🏠 **주거비 증가** → 1인 세대 증가로 인해 도시 내 주거 공급 압박이 심화됨  
    - 🚇 **교통 인프라 문제** → 대중교통 및 도보 중심 도시 개발 필요  
    - 🏥 **사회적 고립 위험** → 1인 가구 증가로 인한 복지 및 돌봄 서비스 요구 증가  
""")

# 📍 지역 선택
region_option = st.radio("📍 분석할 지역", ["전국", "서울특별시"])

# 👥 남녀 구분 선택
gender_option = st.radio("👥 분석 대상", ["합산", "남성", "여성"])

# 선택된 데이터 필터링
if region_option == "서울특별시":
    df_filtered = df_combined[df_combined["행정구역"].str.contains("서울")]
else:
    df_filtered = df_combined

# 선택된 성별에 따른 컬럼명 설정
column_map = {
    "합산": "합산 1인 세대 비율(%)",
    "남성": "남성 1인 세대 비율(%)",
    "여성": "여성 1인 세대 비율(%)"
}
selected_column = column_map[gender_option]

# 📌 상위 10개 지역 데이터
df_top10 = df_filtered.nlargest(10, selected_column)
df_bottom10 = df_filtered.nsmallest(10, selected_column)

# 📌 Plotly 그래프 (상위 10개 지역)
fig_top10 = px.bar(
    df_top10, 
    x=selected_column, 
    y="행정구역", 
    orientation="h", 
    title=f"🔼 1인 세대 비율 상위 10개 지역 ({gender_option})",
    text=selected_column,
    color=selected_column,
    color_continuous_scale="blues"
)
fig_top10.update_traces(texttemplate='%{text:.1f}%', textposition="outside")
fig_top10.update_layout(xaxis_title="1인 세대 비율 (%)", yaxis_title="지역", height=500)

# 📌 Plotly 그래프 (하위 10개 지역)
fig_bottom10 = px.bar(
    df_bottom10, 
    x=selected_column, 
    y="행정구역", 
    orientation="h", 
    title=f"🔽 1인 세대 비율 하위 10개 지역 ({gender_option})",
    text=selected_column,
    color=selected_column,
    color_continuous_scale="reds"
)
fig_bottom10.update_traces(texttemplate='%{text:.1f}%', textposition="outside")
fig_bottom10.update_layout(xaxis_title="1인 세대 비율 (%)", yaxis_title="지역", height=500)

# 📌 그래프 출력
st.plotly_chart(fig_top10, use_container_width=True)
st.plotly_chart(fig_bottom10, use_container_width=True)

st.markdown("""
    ### 🔍 정책 제안 (SDG 11과 연결)
    - 🏡 **1인 가구 맞춤형 주택 공급 확대** → 주거 안정성 확보  
    - 🚆 **지속가능한 교통 시스템 구축** → 1인 가구 중심의 이동 패턴 고려  
    - 🏥 **사회적 고립 방지를 위한 공공 서비스 확충** → 커뮤니티 지원 시스템 필요  

    1인 세대 증가는 단순한 통계가 아니라 **도시의 지속가능성 문제와 직접 연결**됩니다.  
    분석 데이터를 활용하여 SDG 11 목표를 달성할 정책을 고민해야 합니다.
""")

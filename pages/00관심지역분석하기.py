import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 📌 데이터 로드
@st.cache_data
def load_data():
    file_path_single_household = "data11.csv"  # 1인 세대 데이터
    file_path_total_households = "data22.csv"  # 전체 세대 데이터

    df_single_household = pd.read_csv(file_path_single_household, encoding='utf-8')
    df_total_households = pd.read_csv(file_path_total_households, encoding='utf-8')

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
st.title("📊 연령별 1인 세대 비율 분석 및 유사 지역 추천")

# 📍 지역 선택
region_option = st.radio("📍 지역 선택", ["전국", "서울특별시"])

# 👥 남녀 구분 선택
gender_option = st.radio("👥 분석 대상", ["합산", "남성", "여성"])

# 🎯 연령 선택
age_options = ["전체"] + [f"{i}세" for i in range(20, 80, 5)]
selected_age = st.selectbox("🎯 연령 선택", age_options)

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

# 🎯 연령대 필터링
if selected_age != "전체":
    age_col = f"2025년01월_{selected_age}_세대수"
    if age_col in df_filtered.columns:
        df_filtered = df_filtered[df_filtered[age_col] > 0]

# 📌 특정 지역 선택
selected_location = st.selectbox("🏙️ 비교할 지역 선택", df_filtered["행정구역"].unique())

# 선택된 지역의 1인 세대 비율 가져오기
selected_value = df_filtered[df_filtered["행정구역"] == selected_location][selected_column].values[0]

# 📌 유사한 지역 찾기 (차이가 적은 순으로 정렬)
df_filtered["비율 차이"] = np.abs(df_filtered[selected_column] - selected_value)
df_similar = df_filtered.sort_values("비율 차이").iloc[1:11]  # 본인 제외 10개 선택

# 📌 Plotly 그래프 (유사 지역)
fig_similar = px.bar(
    df_similar, 
    x=selected_column, 
    y="행정구역", 
    orientation="h", 
    title=f"🔍 {selected_location}과 가장 비슷한 1인 세대 비율 지역 10곳 ({gender_option})",
    text=selected_column,
    color=selected_column,
    color_continuous_scale="teal"
)
fig_similar.update_traces(texttemplate='%{text:.1f}%', textposition="outside")
fig_similar.update_layout(xaxis_title="1인 세대 비율 (%)", yaxis_title="지역", height=500)

# 📌 그래프 출력
st.plotly_chart(fig_similar, use_container_width=True)

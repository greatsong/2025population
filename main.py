import streamlit as st
import pandas as pd
import plotly.express as px

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

# 📌 데이터 전처리
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
st.title("📊전국 및 서울특별시 1인 가구 분석")

# 전국 / 서울 선택
region_option = st.radio("📍 지역 선택", ["전국", "서울특별시"])

# 남녀 구분 선택
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


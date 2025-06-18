import streamlit as st
import pandas as pd
import plotly.express as px

# 앱 제목
st.title("🔍 지역별 인구 현황 분석 대시보드")

# 데이터 로드 (실제 파일 경로로 수정 필요)
@st.cache_data
def load_data():
    df = pd.read_csv("data01.csv")
    # 컬럼명이 깨져 있을 경우 직접 지정
    df.columns = ["지역명"] + [f"인구_{i}" for i in range(1, 101)] + ["총인구"]
    return df

df = load_data()

# 사이드바에 지역 선택 필터 추가
st.sidebar.header("필터 설정")
selected_region = st.sidebar.selectbox("지역 선택", df["지역명"].unique())

# 선택한 지역 데이터 필터링
filtered_df = df[df["지역명"] == selected_region]

# 📈 인터랙티브 막대 그래프
st.subheader(f"{selected_region} 인구 분포")
fig_bar = px.bar(
    filtered_df,
    x=df.columns[1:-1],  # 인구 데이터 컬럼
    y="총인구",
    title=f"{selected_region} 인구 분포",
    labels={"x": "인구 카테고리", "y": "인구 수"},
    template="plotly_white"
)
st.plotly_chart(fig_bar, use_container_width=True)

# 📉 시계열 트렌드 라인 차트
st.subheader("인구 트렌드 (전체 지역 평균)")
fig_line = px.line(
    df,
    x=df.columns[1:-1],  # X축: 인구 카테고리
    y="총인구",
    title="지역별 인구 트렌드 비교",
    template="plotly_white"
)
st.plotly_chart(fig_line)

# 🌍 지역별 비교 (상위 10개 지역)
st.subheader("지역별 총인구 순위 (Top 10)")
top_regions = df.nlargest(10, "총인구")
fig_top = px.bar(
    top_regions,
    x="지역명",
    y="총인구",
    title="지역별 총인구 순위",
    template="plotly_white"
)
st.plotly_chart(fig_top)

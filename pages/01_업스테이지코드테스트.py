import streamlit as st
import pandas as pd
# 제목 설정
st.title("지역별 인구 현황 분석")

# 데이터 로드 (예시: CSV 파일)
# 실제 파일 경로로 수정 필요
df = pd.read_csv("data01.csv")

# 지역명과 총 인구 컬럼 선택 (예시)
regions = df.iloc[:, 0]  # 첫 번째 컬럼이 지역명이라고 가정
population = df.iloc[:, -1]  # 마지막 컬럼이 총 인구라고 가정

# 막대 그래프 생성
fig, ax = plt.subplots()
ax.barh(regions.head(10), population.head(10))  # 상위 10개 지역만 표시
ax.set_xlabel("인구 수")
ax.set_title("지역별 총 인구 (Top 10)")
plt.tight_layout()

# Streamlit에 그래프 표시
st.pyplot(fig)

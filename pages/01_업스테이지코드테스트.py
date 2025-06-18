import streamlit as st
import pandas as pd
import plotly.express as px

# 앱 제목
st.title("🔍 지역별 인구 현황 분석 대시보드")

# 데이터 로드 함수
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("202504_202504_연령별인구현황_남녀합계.csv", encoding='euc-kr')
        
        # 컬럼명 재설정 (실제 컬럼 수에 맞춰 조정)
        num_columns = len(df.columns)
        population_columns = [f"인구_{i}" for i in range(1, num_columns - 1)]
        df.columns = ["지역명"] + population_columns + ["총인구"]
        
        # 숫자 데이터 변환
        for col in population_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.fillna(0, inplace=True)
        
        return df, population_columns
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame(), []

# 데이터 로드
df, population_columns = load_data()

# 데이터 확인
if df.empty:
    st.stop()  # 데이터 없으면 실행 중단

# 데이터 타입 확인
if "총인구" not in df.columns:
    st.error("데이터에 '총인구' 컬럼이 없습니다.")
    st.stop()

# 총인구 컬럼을 숫자로 변환
df["총인구"] = pd.to_numeric(df["총인구"], errors='coerce')

# 사이드바 필터
st.sidebar.header("📊 필터 설정")
selected_region = st.sidebar.selectbox("지역 선택", df["지역명"].unique())

# 선택한 지역 데이터 추출
filtered_df = df[df["지역명"] == selected_region]

# 📉 시계열 트렌드 (전체 지역 평균)
st.subheader("🔄 인구 트렌드 (전체 지역 평균)")
if not population_columns:
    st.write("연령대 데이터가 없습니다.")
else:
    avg_population = df[population_columns].mean()
    fig_line = px.line(
        x=population_columns,
        y=avg_population,
        title="전체 지역 평균 인구 트렌드",
        labels={"x": "연령대", "y": "평균 인구 수"},
        template="plotly_white"
    )
    st.plotly_chart(fig_line)

# 🌍 지역별 총인구 비교 (상위 10개)
st.subheader("🏆 지역별 총인구 순위 (Top 10)")
top_regions = df.nlargest(10, "총인구")
fig_top = px.bar(
    top_regions,
    x="지역명",
    y="총인구",
    title="지역별 총인구 Top 10",
    template="plotly_white"
)
st.plotly_chart(fig_top)

# 📊 데이터 샘플 표시
st.subheader("📄 원본 데이터 샘플")
st.dataframe(df.head(10))

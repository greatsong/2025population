import streamlit as st
import pandas as pd
import plotly.express as px

# 앱 제목
st.title("🔍 지역별 인구 현황 분석 대시보드")

# 데이터 로드 함수
@st.cache_data
def load_data():
    try:
        # CSV 파일 경로 및 인코딩 지정
        file_path = "202504_202504_연령별인구현황_남녀합계.csv"
        df = pd.read_csv(file_path, encoding='euc-kr')

        # 컬럼 수에 맞게 이름 지정
        total_columns = df.shape[1]
        if total_columns < 3:
            st.error("CSV 데이터에 컬럼이 너무 적습니다. 형식을 확인해주세요.")
            return pd.DataFrame(), []

        population_columns = [f"인구_{i}" for i in range(1, total_columns - 1)]
        expected_columns = ["지역명"] + population_columns + ["총인구"]

        if len(expected_columns) != total_columns:
            st.error("컬럼 수가 예상과 맞지 않습니다. CSV 파일 형식을 확인해주세요.")
            return pd.DataFrame(), []

        df.columns = expected_columns

        # 숫자 데이터 전처리 (콤마 제거 후 숫자형으로 변환)
        for col in population_columns + ["총인구"]:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "", regex=False), errors='coerce')

        df.fillna(0, inplace=True)

        return df, population_columns

    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame(), []

# 데이터 로드
df, population_columns = load_data()

# 데이터 확인
if df.empty:
    st.stop()

# 사이드바 필터
st.sidebar.header("📊 필터 설정")
selected_region = st.sidebar.selectbox("지역 선택", df["지역명"].unique())

# 선택한 지역 데이터 추출
filtered_df = df[df["지역명"] == selected_region]

# 🔄 전체 평균 인구 트렌드 시각화
st.subheader("🔄 인구 트렌드 (전체 지역 평균)")
if population_columns:
    avg_population = df[population_columns].mean()
    avg_df = pd.DataFrame({
        "연령대": population_columns,
        "평균 인구 수": avg_population.values
    })
    fig_line = px.line(
        avg_df,
        x="연령대",
        y="평균 인구 수",
        title="전체 지역 평균 인구 트렌드",
        template="plotly_white"
    )
    st.plotly_chart(fig_line)
else:
    st.write("연령대 데이터가 없습니다.")

# 📍 선택 지역의 연령대별 인구
st.subheader(f"📍 {selected_region} 연령별 인구 분포")
if not filtered_df.empty:
    region_pop = filtered_df[population_columns].iloc[0]
    region_df = pd.DataFrame({
        "연령대": population_columns,
        "인구 수": region_pop.values
    })
    fig_local = px.bar(
        region_df,
        x="연령대",
        y="인구 수",
        title=f"{selected_region} 연령별 인구 분포",
        template="plotly_white"
    )
    st.plotly_chart(fig_local)

# 🏆 지역별 총인구 상위 10
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

# 📄 데이터 샘플
st.subheader("📄 원본 데이터 샘플 (상위 10개 지역)")
st.dataframe(df.head(10))

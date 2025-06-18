import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="지역별 인구 대시보드", layout="wide")
st.title("🔍 지역별 연령별 인구 현황 분석 대시보드")

# 데이터 로드 함수
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("202504_202504_연령별인구현황_남녀합계.csv", encoding='euc-kr')

        # 지역명 전처리
        df.rename(columns={"행정구역": "지역명"}, inplace=True)
        df["지역명"] = df["지역명"].str.replace(r"\(.*\)", "", regex=True).str.strip()

        # 총인구 컬럼
        total_col = "2025년04월_계_총인구수"
        df[total_col] = pd.to_numeric(df[total_col].astype(str).str.replace(",", "", regex=False), errors='coerce')

        # 연령대 컬럼 리스트 추출
        age_columns = [col for col in df.columns if "세" in col or "100세 이상" in col]
        for col in age_columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "", regex=False), errors='coerce')

        df.fillna(0, inplace=True)
        return df, total_col, age_columns
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame(), "", []

# 데이터 로드
df, total_col, age_columns = load_data()
if df.empty:
    st.stop()

# 사이드바 필터
st.sidebar.header("📊 필터 설정")
selected_region = st.sidebar.selectbox("지역 선택", df["지역명"].unique())

# 선택 지역 데이터
filtered_df = df[df["지역명"] == selected_region]

# 🔄 전체 지역 평균 인구 트렌드
st.subheader("📈 전체 지역 평균 연령대별 인구 분포")
avg_age_pop = df[age_columns].mean()
avg_df = pd.DataFrame({
    "연령대": age_columns,
    "평균 인구 수": avg_age_pop.values
})
fig_avg = px.line(avg_df, x="연령대", y="평균 인구 수",
                  title="전체 평균 연령대별 인구 분포",
                  template="plotly_white")
st.plotly_chart(fig_avg, use_container_width=True)

# 📍 선택한 지역의 연령 분포
st.subheader(f"📍 {selected_region} 연령대별 인구")
region_pop = filtered_df[age_columns].iloc[0]
region_df = pd.DataFrame({
    "연령대": age_columns,
    "인구 수": region_pop.values
})
fig_region = px.bar(region_df, x="연령대", y="인구 수",
                    title=f"{selected_region} 연령대별 인구 분포",
                    template="plotly_white")
st.plotly_chart(fig_region, use_container_width=True)

# 🏆 총인구 기준 Top 10 지역
st.subheader("🏆 총인구 기준 상위 10개 지역")
top10_df = df.nlargest(10, total_col)
fig_top10 = px.bar(top10_df, x="지역명", y=total_col,
                   title="총인구 상위 10개 지역",
                   template="plotly_white")
st.plotly_chart(fig_top10, use_container_width=True)

# 📄 원본 데이터 샘플
st.subheader("📄 원본 데이터 (상위 10개 행)")
st.dataframe(df.head(10))

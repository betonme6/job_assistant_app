import streamlit as st
from streamlit_echarts import st_echarts

def show(df):
    st.title("📊 招聘数据探索分析")

    # --- 筛选控件 ---
    city = st.sidebar.selectbox("📍 选择城市", ["全部"] + sorted(df["city"].dropna().unique().tolist()))
    job_keyword = st.sidebar.text_input("🔍 岗位关键词（可选）")
    salary_range = st.sidebar.slider("💰 最低薪资范围 (k)", 0, 100, (10, 50))
    chart_type = st.sidebar.selectbox("📊 图表类型", ["柱状图", "饼图"])

    # --- 数据预处理 ---
    df["min_salary"] = df["salary"].str.extract(r"(\d+)").astype(float)
    filtered = df[df["min_salary"].between(salary_range[0], salary_range[1])]

    if city != "全部":
        filtered = filtered[filtered["city"] == city]
    if job_keyword:
        filtered = filtered[filtered["positionName"].str.contains(job_keyword, case=False, na=False)]

    # --- 图表展示 ---
    st.subheader("📊 岗位分布图")

    data = filtered["positionName"].value_counts().head(10)
    x_data = list(map(str, data.index))
    y_data = list(map(int, data.values))

    if chart_type == "柱状图":
        option = {
            "xAxis": {"type": "category", "data": x_data},
            "yAxis": {"type": "value"},
            "series": [{"data": y_data, "type": "bar"}],
        }
    elif chart_type == "饼图":
        pie_data = [{"name": name, "value": value} for name, value in zip(x_data, y_data)]
        option = {
            "tooltip": {"trigger": "item"},
            "legend": {"orient": "vertical", "left": "left"},
            "series": [{
                "type": "pie",
                "radius": "60%",
                "data": pie_data
            }]
        }
    else:
        option = {}

    if option and x_data:
        st_echarts(option, height="400px")
    else:
        st.warning("⚠️ 暂无符合条件的数据用于绘图。")

    # --- 表格展示 ---
    st.subheader("📋 筛选后岗位详情（前 20 条）")
    show_cols = ["positionName", "companyFullName", "city", "salary", "workYear", "education"]
    if not filtered.empty:
        st.dataframe(filtered[show_cols].head(20).reset_index(drop=True))
    else:
        st.info("没有匹配的岗位，请调整筛选条件。")

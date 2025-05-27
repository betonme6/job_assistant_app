import streamlit as st
from utils.callback_functions import (
    cacu_skill_position_wordcount,
    cacu_postion_skill_wordcount,
    get_related_skills
)
from streamlit_echarts import st_echarts

def show(df):
    st.title("🧠 技能与岗位关联分析")

    query_mode = st.radio("请选择分析类型：", ["技能 → 岗位", "岗位 → 技能", "技能 → 技能"])
    keyword = st.text_input("请输入关键词（如 Python、算法工程师）")

    if keyword:
        if query_mode == "技能 → 岗位":
            result = cacu_skill_position_wordcount(df, keyword)
            st.markdown(result["text"])
            if "chart" in result:
                chart = result["chart"]
                option = {
                    "title": {"text": chart["title"]},
                    "xAxis": {"type": "category", "data": chart["x"]},
                    "yAxis": {"type": "value"},
                    "series": [{"data": chart["y"], "type": "bar"}],
                }
                st_echarts(option, height="400px")
            if "table" in result:
                st.subheader("📋 岗位推荐（前10条）")
                st.dataframe(result["table"].reset_index(drop=True))
            if "summary" in result:
                st.markdown("📝 **分析说明：**")
                st.write(result["summary"])

        elif query_mode == "岗位 → 技能":
            result = cacu_postion_skill_wordcount(df, keyword)
            st.markdown(result["text"])
            if "chart" in result:
                chart = result["chart"]
                option = {
                    "title": {"text": chart["title"]},
                    "xAxis": {"type": "category", "data": chart["x"]},
                    "yAxis": {"type": "value"},
                    "series": [{"data": chart["y"], "type": "bar"}],
                }
                st_echarts(option, height="400px")
            if "summary" in result:
                st.markdown("📝 **岗位说明：**")
                st.write(result["summary"])

        elif query_mode == "技能 → 技能":
            related = get_related_skills(df, keyword)
            st.markdown(f"📚 与 `{keyword}` 常同时出现的技能有：")
            st.write(", ".join(related))

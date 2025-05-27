import streamlit as st
from zhipuai import ZhipuAI
from streamlit_echarts import st_echarts
from utils.callback_functions import ask_glm
import pandas as pd

client = None

def show(df):
    global client
    st.title("🤖 智能招聘对话助手")

    columns = ["positionName", "companyFullName", "city", "salary", "workYear", "education"]

    # 左侧设置区
    key = st.sidebar.text_input("请输入 API Token:", type="password")
    temperature = st.sidebar.slider("temperature", 0.0, 1.5, 0.7)
    model = st.sidebar.selectbox("选择模型", ["glm"])
    chart_type = st.sidebar.selectbox("选择可视化展示类型", ["条形图", "饼图", "散点图", "表格"])

    # 聊天记录初始化
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.sidebar.button("清空聊天记录"):
        st.session_state.messages = []

    if key:
        client = ZhipuAI(api_key=key)
        st.sidebar.success("✅ API Token 已配置")

    # ✅ 显示历史消息记录
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            chart = msg.get("chart")
            chart_type_used = msg.get("chart_type", "条形图")

            if chart:
                # 根据每条记录的图表类型渲染
                if chart_type_used == "饼图":
                    pie_data = [{"name": name, "value": value} for name, value in zip(chart["x"], chart["y"])]
                    option = {
                        "title": {
                            "text": chart["title"],
                            "left": "center",
                            "top": "5%",
                            "textStyle": {"fontSize": 20, "fontWeight": "bold"}
                        },
                        "tooltip": {"trigger": "item"},
                        "legend": {"orient": "vertical", "left": "left"},
                        "series": [{
                            "name": chart["title"],
                            "type": "pie",
                            "radius": "60%",
                            "center": ["50%", "60%"],
                            "data": pie_data
                        }]
                    }
                elif chart_type_used == "散点图":
                    option = {
                        "title": {"text": chart["title"], "left": "center", "top": "5%"},
                        "xAxis": {"type": "category", "data": chart["x"]},
                        "yAxis": {"type": "value"},
                        "series": [{"data": chart["y"], "type": "scatter"}]
                    }
                else:  # 默认条形图
                    option = {
                        "title": {"text": chart["title"], "left": "center", "top": "5%"},
                        "xAxis": {"type": "category", "data": chart["x"]},
                        "yAxis": {"type": "value"},
                        "series": [{"data": chart["y"], "type": "bar"}]
                    }

                st_echarts(option, height="400px", key=f"chart_{i}")

            # ✅ 只有类型是“表格”时才显示
            if msg.get("table") is not None and msg.get("chart_type") == "表格":
                df_table = pd.DataFrame(msg["table"])
                st.dataframe(df_table)

            if msg.get("summary"):
                st.markdown("📝 **岗位说明：**")
                st.write(msg["summary"])

    # ✅ 用户输入问题
    prompt = st.chat_input("请输入您的问题...")
    if prompt and client:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI 正在思考中..."):
                full_response = ask_glm(client, prompt, df, chart_type, temperature)

                if isinstance(full_response, dict):
                    st.markdown(full_response["text"])

                    # 图表展示
                    if full_response.get("chart") and chart_type != "表格":
                        chart = full_response["chart"]

                        if chart_type == "饼图":
                            pie_data = [{"name": name, "value": value} for name, value in zip(chart["x"], chart["y"])]
                            option = {
                                "title": {"text": chart["title"], "left": "center", "top": "5%"},
                                "tooltip": {"trigger": "item"},
                                "legend": {"orient": "vertical", "left": "left"},
                                "series": [{
                                    "name": chart["title"],
                                    "type": "pie",
                                    "radius": "60%",
                                    "center": ["50%", "60%"],
                                    "data": pie_data
                                }]
                            }
                        elif chart_type == "散点图":
                            option = {
                                "title": {"text": chart["title"], "left": "center", "top": "5%"},
                                "xAxis": {"type": "category", "data": chart["x"]},
                                "yAxis": {"type": "value"},
                                "series": [{"data": chart["y"], "type": "scatter"}]
                            }
                        else:
                            option = {
                                "title": {"text": chart["title"], "left": "center", "top": "5%"},
                                "xAxis": {"type": "category", "data": chart["x"]},
                                "yAxis": {"type": "value"},
                                "series": [{"data": chart["y"], "type": "bar"}]
                            }

                        st_echarts(option, height="400px", key=f"live_chart_{len(st.session_state.messages)}")

                    # 表格展示
                    if chart_type == "表格" and full_response.get("table") is not None:
                        st.subheader("📋 岗位推荐结果（前10条）：")
                        st.dataframe(full_response["table"][columns].reset_index(drop=True))

                    if full_response.get("summary"):
                        st.markdown("📝 **岗位技能说明补充：**")
                        st.write(full_response["summary"])

                    # 保存表格数据
                    table_data = None
                    if isinstance(full_response.get("table"), pd.DataFrame):
                        table_data = full_response["table"][columns].to_dict(orient="records")

                    # ✅ 保存整条消息，包含当前 chart_type
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response["text"],
                        "chart": full_response.get("chart"),
                        "table": table_data,
                        "summary": full_response.get("summary"),
                        "chart_type": chart_type
                    })

                else:
                    st.markdown(full_response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response
                    })

import streamlit as st
from data_loader import load_data
from modules import explore, skill_analysis, llm_chat, auth  # ✅ 加入 explore 模块

st.set_page_config(page_title="职讯通 - 大学生招聘助手", layout="wide")

# 登录验证
auth.login()
if not auth.check_login():
    st.stop()

# 读取数据
df = load_data()

# 侧边栏导航
st.sidebar.title("📌 功能导航")
page = st.sidebar.selectbox(
    "选择你要使用的功能",
    ["数据可视化", "技能岗位分析", "AI招聘对话"]
)

# 页面调度
if page == "数据可视化":
    explore.show(df)  # ✅ 调用 explore 模块
elif page == "技能岗位分析":
    skill_analysis.show(df)
elif page == "AI招聘对话":
    llm_chat.show(df)

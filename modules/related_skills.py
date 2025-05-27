import streamlit as st
from collections import Counter

def show(df):
    st.title("🔁 技能关联分析")

    skill = st.text_input("请输入技能（如 java）：")
    if not skill:
        return

    all_skills = [s.lower() for sub in df['skill_list'] for s in sub if skill.lower() != s.lower()]
    top_skills = Counter(all_skills).most_common(10)
    st.write(f"与 `{skill}` 相关的推荐技能：")
    for s, count in top_skills:
        st.markdown(f"- {s}（共出现 {count} 次）")

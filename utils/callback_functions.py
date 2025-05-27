from collections import Counter

# ✅ 技能 → 技能 推荐（用于 skill_analysis.py）
def get_related_skills(df, skill, topn=10):
    all_skills = [
        s for sub in df['skill_list']
        if isinstance(sub, list) for s in sub
    ]
    filtered = [s.lower() for s in all_skills if s.lower() != skill.lower()]
    counter = Counter(filtered)
    top_related = [s for s, _ in counter.most_common(topn)]
    return top_related

# ✅ 技能 → 技能 推荐（用于 AI 对话）
def get_asso_skill(df, skill):
    all_skills = [s for sub in df['skill_list'] if isinstance(sub, list) for s in sub]
    counter = Counter([s.lower() for s in all_skills if s.lower() != skill.lower()])
    top_related = [s for s, _ in counter.most_common(10)]
    return f"💡 技能 {skill} 的推荐关联技术为：{', '.join(top_related)}"

# ✅ 技能 → 岗位 推荐 + 图表 + 表格 + 智能 summary
def cacu_skill_position_wordcount(df, skill, topn=5):
    matched = df[df['skill_list'].apply(lambda x: skill.lower() in [s.lower() for s in x] if isinstance(x, list) else False)]
    positions = matched['positionName'].value_counts().head(topn)

    text = f"🔍 掌握 {skill} 可以尝试的岗位包括：{', '.join(map(str, positions.index))}"

    chart_data = {
        "x": list(map(str, positions.index)),
        "y": list(map(int, positions.values)),
        "title": f"{skill} 技能对应岗位 Top {topn}"
    }

    table = matched[['positionName', 'companyFullName', 'city', 'salary', 'workYear', 'education']].head(10)

    top_roles = list(positions.index[:3])  # 取前3个岗位
    role_description = f"如 {', '.join(top_roles)} 等岗位"

    # 智能构造不同总结语句
    if "数据" in skill or "分析" in skill:
        summary = (
            f"{skill} 是数据驱动岗位中的核心技能，{role_description}需求持续增长。"
            "建议提升建模能力与项目经验，增强大数据处理与可视化能力。"
        )
    elif "前端" in skill or "html" in skill or "css" in skill:
        summary = (
            f"掌握 {skill} 可从事 {role_description}，建议结合 Vue、React 等现代前端框架深入学习，提升交互体验设计与组件复用能力。"
        )
    elif "java" in skill or "c++" in skill:
        summary = (
            f"{skill} 常用于后端或系统级开发，{role_description}对基础扎实者更为青睐。"
            "建议掌握常见框架如 Spring、MyBatis，并积累实战项目经验。"
        )
    elif "linux" in skill:
        summary = (
            f"具备 {skill} 能力通常适合从事 {role_description}，建议深入掌握 Shell 脚本、进程管理、网络配置等系统技能，提升工程实用性。"
        )
    else:
        summary = (
            f"掌握 {skill} 通常适合从事 {role_description} 等相关岗位。"
            "建议进一步提升项目经验和技术广度，提高求职竞争力。"
        )

    return {
        "text": text,
        "chart": chart_data,
        "table": table,
        "summary": summary
    }

# ✅ 岗位 → 技能 推荐 + 图表 + 总结
def cacu_postion_skill_wordcount(df, postionName, topn=10):
    matched = df[df['positionName'].str.contains(postionName, case=False, na=False)]
    skills = [s for sub in matched['skill_list'] if isinstance(sub, list) for s in sub]
    counter = Counter([s.lower() for s in skills])
    top_skills = counter.most_common(topn)

    text = f"🛠 `{postionName}` 岗位通常需要以下技能：{', '.join([s for s, _ in top_skills])}"

    chart_data = {
        "x": [str(s) for s, _ in top_skills],
        "y": [int(c) for _, c in top_skills],
        "title": f"{postionName} 岗位技能词频 Top {topn}"
    }

    if "嵌入式" in postionName:
        summary = (
            "嵌入式岗位要求熟练掌握 C/C++ 编程语言，理解 Linux 系统、单片机、通信接口如 SPI/I2C/UART，"
            "建议结合项目训练，提升软硬件协同能力。"
        )
    elif "算法" in postionName:
        summary = (
            "算法岗位常见技能包括 Python、C++、数学建模能力，推荐掌握常见机器学习框架如 PyTorch 或 TensorFlow。"
        )
    elif "前端" in postionName:
        summary = (
            "前端岗位应掌握 HTML/CSS/JavaScript，建议学习 Vue 或 React 等现代框架，同时提升交互体验设计能力。"
        )
    else:
        summary = f"岗位 `{postionName}` 技能需求如上，建议重点掌握技能频次较高的核心技术。"

    return {
        "text": text,
        "chart": chart_data,
        "summary": summary
    }

# ✅ AI 问答函数路由器
def ask_glm(client, prompt, df, chart_type, temperature):
    prompt_lower = prompt.lower()

    # 技能 → 技能推荐
    if "推荐" in prompt_lower and "技能" in prompt_lower:
        for skill in ["java", "python", "c++", "linux"]:
            if skill in prompt_lower:
                return get_asso_skill(df, skill)

    # 技能 → 岗位
    if any(kw in prompt_lower for kw in ["我会", "掌握", "学", "学习了", "能干什么", "能做什么", "可以从事"]):
        for skill in ["java", "python", "c++", "linux"]:
            if skill in prompt_lower:
                return cacu_skill_position_wordcount(df, skill)

    # 岗位 → 技能
    if "岗位" in prompt_lower and any(kw in prompt_lower for kw in ["需要什么技能", "要求", "要求掌握"]):
        for job in ["嵌入式", "算法", "前端", "java工程师"]:
            if job in prompt_lower:
                return cacu_postion_skill_wordcount(df, job)

    return f"🤖 暂未识别的问题：{prompt}"

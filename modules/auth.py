import streamlit as st
import pandas as pd
import hashlib
import os

USER_DATA_FILE = "data/users.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_DATA_FILE):
        return pd.read_csv(USER_DATA_FILE)
    else:
        return pd.DataFrame(columns=["username", "password_hash"])

def save_user(username, password_hash):
    df = load_users()
    new_row = pd.DataFrame([[username, password_hash]], columns=["username", "password_hash"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(USER_DATA_FILE, index=False)

def login():
    st.sidebar.subheader("🔐 用户登录 / 注册")
    choice = st.sidebar.radio("操作选项：", ["登录", "注册"])

    username = st.sidebar.text_input("用户名")
    password = st.sidebar.text_input("密码", type="password")

    if choice == "登录":
        if st.sidebar.button("登录"):
            df = load_users()
            user = df[df["username"] == username]
            if not user.empty and user.iloc[0]["password_hash"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.sidebar.success(f"欢迎回来，{username}！")
            else:
                st.sidebar.error("用户名或密码错误，请重试。")

    elif choice == "注册":
        if st.sidebar.button("注册"):
            df = load_users()
            if username in df["username"].values:
                st.sidebar.warning("⚠️ 用户名已存在，请换一个。")
            else:
                save_user(username, hash_password(password))
                st.sidebar.success("注册成功！请返回登录。")

def check_login():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("⚠️ 请先登录后再使用系统功能。")
        return False
    return True

import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file_path="data/招聘数据集(含技能列表）.csv"):
    df = pd.read_csv(file_path)
    if 'skill_list' in df.columns:
        df['skill_list'] = df['skill_list'].fillna("").apply(lambda x: x.split(","))
    return df

def get_unique_values(df, column_name):
    return sorted(df[column_name].dropna().unique())

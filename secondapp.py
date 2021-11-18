import streamlit as st
import pandas as pd
import numpy as np

st.title("FQ304大修数据展示")

f_path = "C:/Users/Dell/Documents/FQ304大修人员剂量明细.xlsx"

@st.cache
def get_data():
    data = pd.read_excel(
        f_path,
        
    )

    return data

data = get_data()

st.table(data)
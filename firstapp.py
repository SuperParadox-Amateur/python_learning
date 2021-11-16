import streamlit as st
import numpy as np
import pandas as pd

st.title("我的应用")

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=["a", "b", "c"]
)

st.line_chart(chart_data)

if st.checkbox("显示数据"):
    st.table(chart_data)
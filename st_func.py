#%%
import streamlit as st
import pandas as pd
#%%
# 确定数据源和数据类型
@st.cache
def get_data(file_path):
    data = pd.read_excel(
        file_path,
        sheet_name="数据源",
        usecols=[
            "人员编号",
            "姓名",
            "单位",
            "处室",
            "机组",
            "进入区域",
            "进入时间",
            "离开时间",
            "持续时间(h)",
            "EPD-γ剂量(mSv)"
        ],
        dtype={
            "人员编号": str,
            "进入时间": "datetime64",
            "离开时间": "datetime64"
        }
    )
    return data.sort_values("离开时间")

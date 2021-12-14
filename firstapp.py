#%%
import streamlit as st
import numpy as np
import pandas as pd
import datetime
from st_func import *

#%%
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

#%%
st.title("大修信息看板")

#%%
f_path = st.file_uploader("选择文件")


#%%
# 设置要筛选的数据源的日期范围
# 设定开始日期时间
first_dt = datetime.datetime.strptime(
    "2021/8/22 8:00:00",
    "%Y/%m/%d %H:%M:%S"
)
# 设定开始的日期

# 设定结束的日期时间
last_dt = datetime.datetime.strptime(
    "2021/9/19 11:46:00",
    "%Y/%m/%d %H:%M:%S"
)
# 设定结束的日期
over_date = last_dt.date() + datetime.timedelta(days = 1)

#%%
if f_path:
    # 获取数据
    data = get_data(f_path)

    # 选择日期
    selected_data = st.date_input(
        "选择日期",
        value=last_dt,
        min_value=first_dt.date(),
        max_value=last_dt.date()
    )

    next_selected_date = selected_data + datetime.timedelta(days=1)
    st.dataframe(data.query("离开时间<@next_selected_date"))


from datetime import date
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("展示")

@st.cache
def get_data():
    f_path = "C:/Users/DEll/Documents/FQ304大修人员剂量明细.xlsx"
    data = pd.read_excel(
        f_path,
        sheet_name="数据源",
        usecols=[
            "姓名",
            "人员编号",
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
            "人员编号": "str",
            "单位": "category",
            "处室": "category",
            "机组": "category",
            "进入区域": "category"
        }
    )
    data["进入时间"] = data["进入时间"].dt.date
    data["离开日期"] = data["离开时间"].dt.date
    return data

data = get_data()

# st.text(type(data["离开日期"]))

if st.checkbox("显示数据"):
    st.dataframe(data)

total_dose = pd.pivot_table(
    data= data,
    values=["EPD-γ剂量(mSv)", "人员编号"],
    index="离开日期",
    aggfunc={
        "EPD-γ剂量(mSv)": np.sum,
        "人员编号": np.count_nonzero
    },
    # margins=True
)

min_date = total_dose.index.min()
max_date = total_dose.index.max()

if max_date > date.today():
    default_date = date.today()
else:
    default_date = max_date

selected_date = st.date_input(
    "请选择日期",
    default_date,
    min_value=min_date,
    max_value=max_date)

fig = px.bar(
    total_dose.query("离开日期 <= @selected_date")["EPD-γ剂量(mSv)"])

st.plotly_chart(fig)

# st.area_chart(total_dose.query("离开日期 <= @selected_date")["EPD-γ剂量(mSv)"])

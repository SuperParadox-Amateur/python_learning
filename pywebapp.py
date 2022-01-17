from inspect import getcallargs
from os import getpid
from pandas.core.dtypes.missing import notnull
from pywebio import *
from pywebio.output import *
import datetime
import pandas as pd
import numpy as np
from pywebio.input import *
from pywebio import start_server
import plotly.express as px
from streamlit.elements import form


# 设定读取数据的函数
def get_data(file):
    data = pd.read_excel(
        file,
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
            "姓名": str,
            "人员编号": str,
            "单位": str,
            "处室": str,
            "机组": str,
            "进入区域": str,
            "进入时间": np.datetime64,
            "离开时间": np.datetime64,
            "持续时间(h)": float,
            "EPD-γ剂量(mSv)": float
        }
    )
    return data


# 设定获得相应数据透视表的函数
def get_pivot_data(df):

    # 获得每日个人剂量
    daily_person_dose = pd.pivot_table(
        df,
        index=[pd.Grouper(key="离开时间", freq="D"), "人员编号", "姓名", "单位", "处室"],
        values="EPD-γ剂量(mSv)",
        aggfunc="sum"
    ).reset_index().rename(columns={"EPD-γ剂量(mSv)": "每日剂量"})

    # 获得累计个人剂量
    total_person_dose = pd.pivot_table(
        df,
        index=["人员编号", "姓名", "单位", "处室"],
        values="EPD-γ剂量(mSv)",
        aggfunc="sum"
    ).reset_index().rename(columns={"EPD-γ剂量(mSv)": "累计剂量"})

    # 获得累计个人剂量分布
    total_person_dose_dist = pd.pivot_table(
        df,
        index=["人员编号", "姓名"],
        values="EPD-γ剂量(mSv)",
        aggfunc="sum"
    ).reset_index().rename(columns={"EPD-γ剂量(mSv)": "累计剂量"})

    # 获得每日信息
    daily_data = pd.pivot_table(
        df,
        index = pd.Grouper(key="离开时间", freq="D"),
        aggfunc={
            "EPD-γ剂量(mSv)": "sum",
            "持续时间(h)": "sum",
            "人员编号": "count"
        }
    ).reset_index().sort_values(by="离开时间")\
        .rename(columns={"EPD-γ剂量(mSv)": "每日剂量(mSv)", "持续时间(h)": "每日工时", "人员编号": "每日人次"})
    daily_data["累计剂量(mSv)"] = daily_data["每日剂量(mSv)"].cumsum()
    daily_data["累计工时"] = daily_data["每日工时"].cumsum()
    daily_data["累计人次"] = daily_data["每日人次"].cumsum()

    # 获得处室和单位剂量
    department_company_dose = pd.pivot_table(
        df,
        index=["处室", "单位"],
        values="EPD-γ剂量(mSv)",
        aggfunc="sum",
        margins=True,
        margins_name="总计"
    ).reset_index().rename(columns={"EPD-γ剂量(mSv)": "剂量"})

    # 获得每日单位信息
    daily_company_data = pd.pivot_table(
        df,
        index=[pd.Grouper(key="离开时间", freq="D"), "单位"],
        values=["EPD-γ剂量(mSv)", "持续时间(h)", "人员编号"],
        aggfunc="sum"
    ).reset_index()\
        .rename(columns={"EPD-γ剂量(mSv)": "日集体剂量(mSv)", "持续时间(h)": "每日工时", "人员编号": "每日人次"})
    
    # 获得累计单位信息
    total_company_data = pd.pivot_table(
        df,
        index="单位",
        values=["EPD-γ剂量(mSv)", "持续时间(h)", "人员编号"],
        aggfunc="sum"
    ).reset_index()\
        .rename(columns={"EPD-γ剂量(mSv)": "集体剂量(mSv)", "持续时间(h)": "集体工时", "人员编号": "集体人次"})

    return [
        daily_person_dose, 
        total_person_dose, 
        total_person_dose_dist, 
        daily_data, 
        department_company_dose,
        daily_company_data,
        total_company_data
        ]


# 设定获得前50人员的公司数量的函数
def get_company_top50(df):
    df_top_50_1 = pd.pivot_table(
        df,
        index="单位",
        aggfunc={"单位": "count"}
    ).rename(columns={"单位": "数量"}).reset_index().sort_values(by="数量", ascending=False)
    df_top_50_2 = [
        {"单位": "其他单位","数量": df_top_50_1["数量"].sum() - df_top_50_1.head(4)["数量"].sum()},
        {"单位": "总计","数量": df_top_50_1["数量"].sum()}
    ]
    df_top_50 = df_top_50_1.head(4).append(df_top_50_2, ignore_index=True)
    return df_top_50


# 设定获得人员剂量分布的函数
def dose_dist(df):
    cut_bins = [-np.infty, 0.5, 1.0, 2.0, 5.0, np.infty]
    bins_labels = ["0-0.5", "0.5-1.0", "1.0-2.0", "2.0-5.0", ">5.0"]
    dose_dist_df = pd.cut(df["累计剂量"], bins = cut_bins, labels = bins_labels)
    dose_dist_df = dose_dist_df.value_counts().reset_index()
    return dose_dist_df

def main():

    # 选择数据源文件和查询日期
    f_path = file_upload("请选择文件", accept=".xlsx")
    select_date = input("选择日期", type=DATE)

    if f_path and select_date:

        # 获得处理后的总数据透视表
        next_select_date = pd.to_datetime(select_date, format="%Y/%m/%d") + datetime.timedelta(days = 1)
        data= get_data(f_path["content"]).query("离开时间 < @next_select_date")
        pivoted_data = get_pivot_data(data)

        # 每日个人剂量前50
        daily_person_dose_50 = pivoted_data[0].query("离开时间.dt.date.astype('str') == @select_date")\
            .sort_values("每日剂量", ascending=False).head(50)
        daily_company_50 = get_company_top50(daily_person_dose_50)

        # 每日个人剂量第1和第50
        daily_person_dose_1and50 = pivoted_data[0].loc[[0,49],["单位", "每日剂量"]]
    
        # 累计个人剂量前50
        total_person_dose_50 = pivoted_data[1].sort_values("累计剂量", ascending=False).head(50)
        total_company_50 = get_company_top50(total_person_dose_50)

        # 累计个人剂量分布
        total_person_dose_dist = pivoted_data[2]
        total_dose_dist_df = dose_dist(total_person_dose_dist)
        daily_data = pivoted_data[3]

        # 测试输出
        put_html(daily_company_50.to_html(border=0))
        put_html(daily_person_dose_1and50.to_html(border=0))
        put_html(total_company_50.to_html(border=0))
        put_html(total_dose_dist_df.to_html(border=0))


if __name__ == "__main__":
    start_server(main, port=8080, debug=True, cdn = False)
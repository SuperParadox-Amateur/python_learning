#%%
import pandas as pd
import numpy as np
import datetime
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#%%
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

#%%
f_path = "C:/Users/Dell/Documents/data/FQ304大修人员剂量明细.xlsx"

#%%
@st.cache
# 确定数据源和数据类型
def get_data():
    data = pd.read_excel(
        f_path,
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

data = get_data()

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
person_dose_target = st.sidebar.number_input(
    "个人剂量目标",
    value = 3
    )
total_dose_target = st.sidebar.number_input(
    "集体累计剂量目标",
    value = 250
)

#%%
st.title("大修信息看板")


#%%
selected_date = st.date_input(
    "选择日期",
    value = last_dt,
    min_value = first_dt.date() + datetime.timedelta(days = 1),
    max_value = last_dt
)
next_selected_date = selected_date + datetime.timedelta(days=1)

#%%

#%%
# 求选定日期是星期几
week = [
    "星期一",
    "星期二",
    "星期三",
    "星期四",
    "星期五",
    "星期六",
    "星期日"
]

def get_date_info(date):
    week_name = week[selected_date.weekday()]
    return f"今天是**{selected_date: %Y年%m月%d日}**，**{week_name}**"

#%%
# 选择不同的日期输出不同的信息和大修进程信息
date_info = get_date_info(selected_date)

if selected_date < first_dt.date():
    duration_info = "大修未开始"
elif selected_date >= over_date:
    duration_info = "大修已结束"
else:
    duration_info = f"大修第**{(selected_date - first_dt.date()).days + 1}**天"

#%%
st.markdown(date_info)
st.markdown(duration_info)

#%%
# 求得之前人员每日的总和剂量、总和人次和总和工时
# 降序排序
# 重置index，方便查询
daily_person_sum_data = pd.pivot_table(
    data.query("离开时间 >= @first_dt and 离开时间 < @next_selected_date"),
    index=[
        # 将离开时间以日为单位分组
        pd.Grouper(key="离开时间", freq="D"),
        "人员编号",
        "姓名",
        "处室",
        "单位"
    ],
    aggfunc={
        "EPD-γ剂量(mSv)": np.sum,
        "人员编号": np.count_nonzero,
        "持续时间(h)": np.sum
    },
).rename(
    columns={
        "EPD-γ剂量(mSv)": "总和：剂量(mSv)",
        "人员编号": "总和：人次",
        "持续时间(h)": "总和：工时(h)"
    }
).sort_values(by = "总和：剂量(mSv)", ascending=False)\
    .sort_index(level = 0, sort_remaining=False)\
        .reset_index()

# 截止选定日期时，每日的总和剂量、总和人次和总和工时
# 降序排序
till_person_sum_data = pd.pivot_table(
    data.query("离开时间 >= @first_dt and 离开时间 < @next_selected_date"),
    index=[
        "人员编号",
        "姓名",
        "处室",
        "单位"
    ],
    aggfunc={
        "EPD-γ剂量(mSv)": np.sum,
        "人员编号": np.count_nonzero,
        "持续时间(h)": np.sum
    }
).rename(
    columns={
        "EPD-γ剂量(mSv)": "累计：剂量(mSv)",
        "人员编号": "累计：人次",
        "持续时间(h)": "累计：工时(h)"
    }
).sort_values(by="累计：剂量(mSv)", ascending=False).reset_index()

# 截止选定日期时，每日的剂量、人次和工时的总和累计
daily_sum_data = pd.pivot_table(
    data.query("离开时间 >= @first_dt and 离开时间 < @next_selected_date"),
    index=[pd.Grouper(key = "离开时间", freq = "D")],
    aggfunc={
        "EPD-γ剂量(mSv)": np.sum,
        "人员编号": np.count_nonzero,
        "持续时间(h)": np.sum
    }
).rename(
    columns={
        "EPD-γ剂量(mSv)": "总和：剂量(mSv)",
        "人员编号": "总和：人次",
        "持续时间(h)": "总和：工时(h)"
        }
    )

daily_sum_data["累计：剂量(mSv)"] = daily_sum_data["总和：剂量(mSv)"].cumsum()
daily_sum_data["累计：人次"] = daily_sum_data["总和：人次"].cumsum()
daily_sum_data["累计：工时(h)"] = daily_sum_data["总和：工时(h)"].cumsum()


#%%
# 分双栏展示今天最大个人剂量和最大个人累计剂量的信息
st.subheader("最大剂量信息")
dose_max_info_col1, till_dose_max_info_col2 = st.columns(2)
with dose_max_info_col1:
    # 今天最大个人剂量的信息
    this_day_dose_max_info = daily_person_sum_data.query("离开时间 < @next_selected_date").iloc[0]
    st.markdown(
        f'''
        今天（{selected_date:%Y年%m日%d日}）最大剂量人员信息\n
        人员编号：**{this_day_dose_max_info["人员编号"]}**\n
        姓名：**{this_day_dose_max_info["姓名"]}**\n
        处室：**{this_day_dose_max_info["处室"]}**\n
        单位：**{this_day_dose_max_info["单位"]}**
        '''
    )
with till_dose_max_info_col2:
    till_dose_max_info = till_person_sum_data.iloc[0]
    st.markdown(
        f'''
        截止今天（{selected_date:%Y年%m日%d日}）最大剂量人员信息\n
        人员编号：**{till_dose_max_info["人员编号"]}**\n
        姓名：**{till_dose_max_info["姓名"]}**\n
        处室：**{till_dose_max_info["处室"]}**\n
        单位：**{till_dose_max_info["单位"]}**
        '''
    )

#%%
# 剂量和目标
st.subheader("最大剂量和目标值")
# 分两栏显示最大个人剂量和集体累计剂量与目标值之间的关系
dose_target_col1, dose_target_col2 = st.columns(2)
# 截止选定日期时的最大剂量信息
with dose_target_col1:
    till_person_dose_max = till_person_sum_data.loc[0, "累计：剂量(mSv)"]
    st.markdown(f"截止今天最大个人剂量为 {till_person_dose_max:.3f} mSv")

    # 截止选定日期时的最大剂量与个人剂量目标的比值
    person_dose_target_rate = till_person_sum_data.loc[0, "累计：剂量(mSv)"] / person_dose_target
    st.markdown(f"截止今天最大剂量和目标剂量的比值为 {person_dose_target_rate:.2%}")

#%%
# 截止选定日期时的累计剂量信息
with dose_target_col2:
    till_dose_cumsum = daily_sum_data.loc[selected_date.strftime("%Y-%m-%d"), "累计：剂量(mSv)"]
    st.markdown(f"截止今天集体累计剂量为 {till_dose_cumsum:.3f} mSv")
    # 截止选定日期时的累计剂量与集体剂量目标的比值
    total_dose_target_rate = till_dose_cumsum/total_dose_target
    st.markdown(f"截止今天累计剂量和目标剂量的比值为 {total_dose_target_rate:.2%}")

#%%
# 今天的累计人次
till_visit_sum = daily_sum_data.loc[selected_date.strftime("%Y-%m-%d"),"累计：人次"]
st.markdown(f"截止今天累计人次为{till_visit_sum}")

#%%
st.subheader("今天个人总和剂量前10")

# 今天个人总和剂量前10
daily_person_dose_top10 = daily_person_sum_data.query(
    "离开时间 == @selected_date"
    ).head(10).loc[:,"人员编号":"总和：剂量(mSv)"]

st.table(daily_person_dose_top10.reset_index(drop=True))

#%%
# 查询截止到选定日期的剂量、人次和工时的信息
till_sum_data = daily_sum_data.query("离开时间 <= @next_selected_date")

#%%
# 创建水平并排的一对子图
collect_dose_fig = make_subplots(
    specs=[[
        {"secondary_y": True},
        {"secondary_y": True}
    ]],
    rows = 1,
    cols = 2,
    # 设置子图的标题
    subplot_titles=[
        "每日剂量和累计剂量",
        "每日人次和累计人次"
    ]
)

# 添加左子图，显示剂量信息
collect_dose_fig.add_trace(
    go.Bar(
        x = till_sum_data.index,
        y = till_sum_data["总和：剂量(mSv)"],
        name = "总和：剂量(mSv)",
        legendgroup = "group1",
        legendgrouptitle_text = "剂量"
    ),
    secondary_y=False,
    row=1,
    col=1
)
collect_dose_fig.add_trace(
    go.Scatter(
        x = till_sum_data.index,
        y = till_sum_data["累计：剂量(mSv)"],
        name = "累计：剂量(mSv)",
        mode = "lines",
        legendgroup = "group1",
        legendgrouptitle_text = "剂量"
    ),
    secondary_y=True,
    row = 1,
    col = 1
)

# 添加右子图，显示人次信息
collect_dose_fig.add_trace(
    go.Bar(
        x = till_sum_data.index,
        y = till_sum_data["总和：人次"],
        name = "总和：人次",
        legendgroup = "group2",
        legendgrouptitle_text = "人次"
    ),
    secondary_y=False,
    row=1,
    col=2
)
collect_dose_fig.add_trace(
    go.Scatter(
        x = till_sum_data.index,
        y = till_sum_data["累计：人次"],
        name = "累计：人次",
        mode = "lines",
        legendgroup = "group2",
        legendgrouptitle_text = "人次"
    ),
    secondary_y=True,
    row = 1,
    col = 2
)

# 设置x轴
collect_dose_fig.update_xaxes(
    tickformat = "%d日\n%Y年%m月",
    title_text = "日期"
)

# 设置左子图的y轴
collect_dose_fig.update_yaxes(
    title_text = "剂量(mSv)",
    secondary_y=False,
    row = 1,
    col = 1
)

# 设置右子图的y轴
collect_dose_fig.update_yaxes(
    title_text = "人次",
    secondary_y=False,
    row = 1,
    col = 2
)

# 设置整张图的信息
collect_dose_fig.update_layout(
    title_text = "每日的剂量和人次信息"
)

st.plotly_chart(collect_dose_fig, use_container_width=True)

#%%
# 累计剂量区间统计
points = [-np.infty, 0.5, 1, 2, 5, np.infty]
till_dose_interval = pd.cut(
    till_person_sum_data["累计：剂量(mSv)"],
    bins = points,
    labels=["0~0.5", "0.5~1", "1~2", "2~5", ">5"]
)

till_dose_dist = pd.value_counts(till_dose_interval).rename("人数")
# till_dose_dist = till_dose_dist[till_dose_dist != 0]
st.table(till_dose_dist)

#%%
# 绘制剂量区间分布的饼图
dose_dist_fig = go.Figure()

dose_dist_fig.add_trace(
    go.Pie(
        labels = till_dose_dist.index,
        values = till_dose_dist,
        textinfo = "value+percent"
    )
)

dose_dist_fig.update_layout(
    title_text = f"截止<b>{selected_date:%Y年%m月%d日}</b>人员剂量分布",
    legend_title = "剂量单位：mSv"
)

st.plotly_chart(dose_dist_fig, use_container_width=True)

#%%
till_department_dose = pd.pivot_table(
    daily_person_sum_data.query("离开时间 <= @next_selected_date"),
    values="总和：剂量(mSv)",
    index="处室",
    aggfunc=np.sum
).sort_values(by="总和：剂量(mSv)", ascending=False)

department_dose_fig = go.Figure()
department_dose_fig.add_trace(
    go.Bar(
        x = till_department_dose.index,
        y = till_department_dose["总和：剂量(mSv)"],
        text = till_department_dose["总和：剂量(mSv)"].round(decimals=3),
        textposition = "outside"
    )
)

st.plotly_chart(department_dose_fig, use_container_width=True)

#%%
this_day_comp_top50 =\
    daily_person_sum_data.query("离开时间 < @next_selected_date")\
        .head(50)["单位"].value_counts()[:4]

this_day_comp_top50 = this_day_comp_top50.append(
    pd.Series({"其他公司": 50 - this_day_comp_top50.sum()})
)

this_day_comp_fig = go.Figure()

this_day_comp_fig.add_trace(
    go.Pie(
        labels = this_day_comp_top50.index,
        values = this_day_comp_top50
    )
)

this_day_comp_fig.update_layout(
    title_text = f"今天（<b>{selected_date:%Y年%m月%d日}</b>）剂量前50的人员剂量的单位分布",
    legend_title = "数量"
)

st.plotly_chart(this_day_comp_fig, use_container_width=True)

#%%
till_comp_top50 =\
    daily_person_sum_data.query("离开时间 < @next_selected_date")\
        .head(50)["单位"].value_counts()[:4]

till_comp_top50 = till_comp_top50.append(
    pd.Series({"其他公司": 50 - till_comp_top50.sum()})
)

till_comp_fig = go.Figure()

till_comp_fig.add_trace(
    go.Pie(
        labels = till_comp_top50.index,
        values = till_comp_top50
    )
)

till_comp_fig.update_layout(
    title_text = f"截止今天（<b>{selected_date:%Y年%m月%d日%H时}</b>）剂量前50的人员剂量的单位分布",
    legend_title = "数量"
)

st.plotly_chart(till_comp_fig, use_container_width=True)

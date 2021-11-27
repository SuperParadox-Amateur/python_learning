#%%
import pandas as pd
import numpy as np
import datetime
#%%
f_path = "C:/Users/Dell/Documents/data/FQ304大修人员剂量明细.xlsx"
#%%
# 确定数据源和数据类型
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
#%%
# 设置要筛选的数据源的日期范围
# 设定起止日期时间
first_datetime = pd.to_datetime("2021/8/22 8:00")
last_datetime = pd.to_datetime("2021/9/19 11:46")
# 设置若在日期范围内，则以昨天为范围的终止日期，否则以截止日期范围的终止日期
now = datetime.datetime.now()
if now <= last_datetime:
    end_datetime = now - datetime.timedelta\
        (hours=now.hour, minutes=now.minute, seconds=now.second)
else:
    end_datetime = last_datetime
end_datetime
#%%
# 筛选日期范围内的数据
queried_data = data.query("离开时间 >= @first_datetime and 离开时间 <= @end_datetime")
queried_data.head()
#%%
# 透视汇总筛选的数据，以离开时间、人员编号、姓名、处室、单位为索引
# 统计每日每人的累计剂量、人次和工作时间
person_total_dose = pd.pivot_table(
    queried_data,
    # values=["EPD-γ剂量(mSv)", "人员编号", "持续时间(h)"],
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
    # margins=True, margins_name="总计"
)\
    # .stack(0).reset_index(0)
person_total_dose.head(10)
#%%
# 统计每日的累计剂量、人次和工作时间
day_total_data = queried_data.groupby(
    pd.Grouper(key="离开时间", freq="D"),
).agg(
    {"EPD-γ剂量(mSv)": np.sum,
    "人员编号": np.count_nonzero,
    "持续时间(h)": np.sum
}
)
day_total_data
#%%
# 每日剂量累加
day_total_dose = day_total_data["EPD-γ剂量(mSv)"].cumsum()
day_total_dose
#%%
# 选择某一日期
selected_date = pd.to_datetime("2021-9-1").strftime("%Y%m%d")
day_total_dose[selected_date]
#%%
# 每日人次累加
day_total_person = day_total_data["人员编号"].cumsum()
day_total_person
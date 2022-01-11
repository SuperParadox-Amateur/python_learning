# %%
import pandas as pd
import numpy as np
import random
import datetime

import plotly.express as px
import plotly.graph_objects as go



# %%
# 绘制子图
from plotly.subplots import make_subplots



# %%
# 时间
time_range = pd.date_range(start="2019/1/1", end="2021/12/31")
time_range



# %%
len(time_range)



# %%
# 水果
fruits = ["香蕉", "苹果", "葡萄", "橙子", "哈密瓜", "芭乐", "梨", "桃子"]
fruits_list = np.random.choice(fruits, size = len(time_range), replace=True)
fruits_list



# %%
# 客户
names = ["Mike", "John", "Tom", "xiaoming", "Jimmy", "Lym", "Michk"]
names_list = np.random.choice(names, size = len(time_range), replace=True)
names_list



# %%
# 生成订单数据
order = pd.DataFrame({
    "time": time_range,
    "fruit": fruits_list,
    "name": names_list,
    "kilogram": np.random.choice(list(range(50, 100)), size=len(time_range), replace=True)
})
order



# %%
# 水果信息
information = pd.DataFrame({
    "fruit": fruits,
    "price": [3.8, 8.9, 12.8, 6.8, 15.8, 4.9, 5.8, 7],
    "region": ["华南", "华北", "西北", "华中", "西北", "华南", "华北", "华中"]
})
information



# %%
# 数据合并
df = pd.merge(
    order,
    information,
    how="outer"
).sort_values("time").reset_index(drop=True)

df.head()



# %%
# 生成订单金额字段
df["amount"] = df["kilogram"] * df["price"]

df.head()



# %%
df1 = pd.pivot_table(
    df,
    index=pd.Grouper(key="time", freq="M"),
    values="kilogram",
    aggfunc=np.sum
).reset_index()

df1["time"] = df1["time"].dt.strftime("%Y-%m")

fig1 = px.bar(df1, x="time", y = "kilogram", color="kilogram")
fig1.update_layout(xaxis_tickangle = 45)
fig1.show()

# %%
# 2019-2021年销售额走势
df2 = pd.pivot_table(
    df,
    index=pd.Grouper(key="time", freq="M"),
    values="amount",
    aggfunc=np.sum
).reset_index()



# %%
fig2 = px.line(
    df2,
    x = "time",
    y = "amount",
    markers = True,
    hover_data={"time": "|%Y年%m月"}
)

fig2.update_layout(
    xaxis_tickformat = "%Y-%m",
    yaxis_tickformat = "0"
)
fig2.show()

# %%
# 年度销量、销售额和平均销售额

df3 = pd.pivot_table(
    df,
    index=pd.Grouper(key="time", freq="Y"),
    values=["kilogram", "amount"],
    aggfunc=np.sum
).reset_index()



# %%
df3["mean_amount"] = df3["amount"] / df3["kilogram"]
df3



# %%
# 水果年度销量占比

df4 = pd.pivot_table(
    df,
    index=[pd.Grouper(key="time", freq="Y"), "fruit"],
    values=["kilogram", "amount"],
    aggfunc=np.sum
).reset_index()

df4["time"] = df4["time"].dt.strftime("%Y")
df4

# %%
fig3 = make_subplots(
    rows=1, cols=3,
    subplot_titles=["2019年", "2020年", "2021年"],
    specs=[[{"type": "domain"}, {"type": "domain"}, {"type": "domain"}]]
)

years = df4["time"].unique().tolist()

for i, year in enumerate(years):
    name = df4[df4["time"] == year].fruit.tolist()
    value = df4[df4["time"] == year].kilogram.tolist()
    fig3.add_trace(
        go.Pie(
            labels = name,
            values = value
        ),
        row = 1, col = i + 1
    )

fig3.update_traces(
    textposition = "inside",
    textinfo = "percent+label",
    hole = 0.4,
    insidetextorientation = "radial",
    hoverinfo = "label+percent+name"
)

fig3.show()

# %%
for i, year in enumerate(years):
    df5 = df4[df4["time"] == year]
    fig4 = go.Figure(go.Treemap(
        labels = df5["fruit"].tolist(),
        parents = df5["time"].tolist(),
        values = df5["amount"].tolist(),
        textinfo = "label+value+percent root"
    ))
    fig4.show()

# %%
# 商品月度销量变化

df6 = pd.pivot_table(
    df,
    index=[pd.Grouper(key="time", freq="M"), "fruit"],
    values="amount",
    aggfunc=np.sum
).reset_index()

df6["time"] = df6["time"].dt.strftime("%Y-%m")
df6

# %%
fig5 = px.bar(
    df6,
    x = "time",
    y = "amount",
    color = "fruit",
    hover_data={"time": "|%Y年%m月"}
)
fig5.update_layout(
    xaxis_tickangle = 45,
    xaxis_tickformat = "%Y-%m",
    yaxis_tickformat = "0"
)

fig5.show()

# %%
# 不同地区的销量
df7 = pd.pivot_table(
    df,
    index=[pd.Grouper(key="time", freq="Y"), "region"],
    values="kilogram",
    aggfunc=np.sum
).reset_index()
df7["time"] = df7["time"].dt.strftime("%Y")


df7

# %%
fig6 = px.bar(
    df7,
    x = "region",
    y = "kilogram",
    color="region",
    facet_col="time",
    text = "kilogram"
)

fig6.show()

# %%
# 不同地区年度平均销售额
df8 = pd.pivot_table(
    df,
    index=[pd.Grouper(key="time", freq="Y"), "region"],
    values="amount",
    aggfunc=np.mean
).reset_index()

df8["time"] = df8["time"].dt.strftime("%Y")
df8["time"] = df8["time"].astype("int")
df8.style.background_gradient(cmap="Spectral_r")

# %%
# 用户订单量、金额对比
df9 = pd.pivot_table(
    df,
    index = "name",
    aggfunc={
        "time": "count",
        "amount": "sum"
    }
).reset_index()\
    .rename(columns = {"time": "order_number"})

df9.style.background_gradient(cmap="Spectral_r")

# %%
# 用户水果喜好
df10 = pd.pivot_table(
    df,
    index=["name", "fruit"],
    aggfunc={
        "time": "count",
        "amount": "sum" 
    }
).reset_index()\
    .rename(columns={"time": "number"})

df10.sort_values(["name", "number", "amount"], ascending=[True, False, False])
df10.style.bar(subset=["number", "amount"], color = "#a97fcf")

# %%
fig7 = px.bar(
    df10,
    x = "fruit", 
    y = "amount",
    facet_col="name",
    color = "number"
)

fig7.show()

# %%
# 用户分层——RFM模型
df11 = pd.pivot_table(
    df,
    index="name",
    aggfunc={
        "fruit": "count",
        "amount": "sum"
    }
).reset_index()\
    .rename(columns={"fruit": "F", "amount": "M"})

df11

# %%
now = datetime.datetime.now()
now

# %%
df["R"] = df["time"].apply(lambda x: (now - x).days)
df.sort_values(["name", "R"], ascending=[False, True])

# %%
df12 = pd.pivot_table(
    df,
    index="name",
    values="R",
    aggfunc="min"
).reset_index()

df12

# %%
df13 = pd.merge(df11, df12)
df13 = df13[["name", "F", "M", "R"]]
df13.style.background_gradient(cmap = "Spectral_r")

# %%
# 用户复购周期分析
# 每个用户的购买时间升序
df14 = df[["name", "time"]].sort_values(["name", "time"], ascending=[False, True])
df14

# %%
df15 = df14.groupby("name").shift(1).rename(columns={"time": "time1"})
df15

# %%
df16 = pd.concat([df14, df15], axis=1)
df16.dropna(inplace=True)
df16["timedelta"] = df16["time"] - df16["time1"]
df16["timedelta"] = df16["timedelta"].apply(lambda x: x.days)
df16

# %%
fig8 = px.bar(
    df16,
    x = "timedelta",
    y = "name",
    orientation="h",
    color = "timedelta",
    color_continuous_scale="spectral_r"
)
fig8.show()

# %%
df16.groupby("name")["timedelta"].agg(["count", "mean"])

# %%
fig9 = px.violin(
    df16,
    y = "timedelta",
    color="name"
)

fig9.show()



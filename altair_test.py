#%%
import streamlit as st
import altair as alt
from vega_datasets import data
#%%
# alt.renderers.enable("mimetype")
#%%
stocks = data.stocks()
#%%
fig1 = alt.Chart(stocks).mark_line(point = True).encode(
    x = "Date:T",
    y = "Price:Q",
    color = "symbol:N"
    # tooltip = ["Horsepower", "Miles_per_Gallon"]
).interactive()
#%%
st.altair_chart(fig1)
from pywebio import *
# from pywebio.output import *
import datetime
import pandas as pd
import numpy as np
from pywebio.input import URL
# from pywebio import start_server


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
            "人员编号": str,
            "进入时间": "datetime64",
            "离开时间": "datetime64"
        }
    )
    return data

def show_data():
    f_path = input.input("请选择文件：", type = URL)
    if f_path:
        # all_data = get_data(f_path)
        all_data = pd.read_csv(f_path)
        output.put_html(all_data.head(20).to_html(border=0))

# def show_data():
#     all_data = get_data(r"C:\Users\Dell\Documents\data\FQ304大修人员剂量明细.xlsx")
#     output.put_html(all_data.head(20).to_html(border=0))

# def dose_info_board():
#     start_dt = datetime.datetime.strptime("2021/8/22 8:00:00", "%Y/%m/%d %h:%M:%s")
#     end_dt = datetime.datetime.strptime("2021/9/19 11:46:00", "%Y/%m/%d %h:%M:%s")
#     # put_text(start_dt)
#     # put_text(end_dt)
#     f_path = file_upload("请选择文件")
#     if f_path:
#         all_data = get_data(f_path)
#         put_html(all_data.to_html())
#         selected_date = input("请选择日期", type = DATE)

if __name__ == "__main__":
    start_server(show_data, port=8080, debug=True, cdn = False)
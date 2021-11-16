from pywebio.input import *

age = input("How old are you?", type=NUMBER)

password = input("Input password.", type = PASSWORD)

gift = select("Which gift you want?", ["keyboard", "ipad"])

agree = checkbox("User Term", options=["I agree to term and conditions"])

answer = radio("Choose one", options=["A", "B", "C", "D"])

text = textarea("Text Area", rows=3, placeholder="Some text")

image = file_upload("Select a image: ", accept="image/*")
from pywebio import *

def main(): # PyWebIO application function
    name = input.input("what's your name")
    output.put_text("hello", name)


start_server(main, port=8080, debug=True)
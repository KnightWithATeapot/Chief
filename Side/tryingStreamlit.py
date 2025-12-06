import streamlit as st

st.title("Привет, Streamlit!")
name = st.text_input("Введите ваше имя:")
st.write("Привет,", name)

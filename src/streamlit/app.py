import streamlit as st
import requests
import time

API = "http://localhost:8000/api/generate_poem/"

st.set_page_config(page_title="Poetry Generator", page_icon="", layout="centered")

st.title("Vietnamese Poetry Generator")
st.markdown("Hãy nhập câu thơ đầu tiên và điều chỉnh tham số để tạo bài thơ bằng AI.")

prompt = st.text_input("✍️ Nhập câu thơ gợi ý đầu tiên:", "Em cười như nắng mai")

col1, col2 = st.columns(2)
with col1:
    temperature = st.slider("🔥 Temperature", 0.5, 1.5, 0.8, 0.05)
    top_k = st.slider("🔽 Top-K", 10, 100, 50, 10)
    repetition_penalty = st.slider("♻️ Repetition Penalty", 1.0, 2.0, 1.2, 0.1)
with col2:
    top_p = st.slider("🎯 Top-P (nucleus)", 0.5, 1.0, 0.95, 0.05)
    max_length = st.slider("📏 Độ dài tối đa", 20, 200, 50, 10)

if st.button("🚀 Tạo bài thơ"):
    with st.spinner("Đang tạo thơ..."):
        time.sleep(1)

        response = requests.post(API, json={
            "prompt": prompt,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "max_length": max_length,
            "repetition_penalty": repetition_penalty
        })
        poem = response.json()["poem"]

        st.session_state["output"] = poem

if "output" in st.session_state:
    st.markdown("### 📜 Bài thơ được tạo:")
    st.code(st.session_state["output"], language="markdown")
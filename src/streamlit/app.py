import streamlit as st
import requests  # Chỉ dùng nếu bạn thực sự gọi API
import time

st.set_page_config(page_title="🌸 Poetry Generator", page_icon="📜", layout="centered")

st.title("🌸 Vietnamese Poetry Generator")
st.markdown("Hãy nhập câu thơ đầu tiên và điều chỉnh tham số để tạo bài thơ bằng AI.")

# === Input từ người dùng ===
prompt = st.text_input("✍️ Nhập câu thơ gợi ý đầu tiên:", "Em cười như nắng mai")

col1, col2 = st.columns(2)
with col1:
    temperature = st.slider("🔥 Temperature", 0.5, 1.5, 0.8, 0.05)
    top_k = st.slider("🔽 Top-K", 10, 100, 50, 10)
    repetition_penalty = st.slider("♻️ Repetition Penalty", 1.0, 2.0, 1.2, 0.1)
with col2:
    top_p = st.slider("🎯 Top-P (nucleus)", 0.5, 1.0, 0.95, 0.05)
    max_length = st.slider("📏 Độ dài tối đa", 20, 200, 50, 10)

# === Gửi request ===
if st.button("🚀 Tạo bài thơ"):
    with st.spinner("Đang tạo thơ..."):
        # 🔁 Giả lập thời gian chờ API
        time.sleep(1)

        # 🎯 Thay bằng đoạn gửi HTTP request nếu có API thật:
        # response = requests.post("http://your-api.com/generate", json={
        #     "prompt": prompt,
        #     "temperature": temperature,
        #     "top_k": top_k,
        #     "top_p": top_p,
        #     "max_length": max_length,
        #     "repetition_penalty": repetition_penalty
        # })
        # poem = response.json()["poem"]

        # Giả lập output
        poem = f"""{prompt}
Nắng hồng vương má em  
Nhẹ rơi từng sợi nhớ  
Gió cuốn lùa tóc mềm  
Chiều trôi về bến mơ"""

        st.session_state["output"] = poem

# === Hiển thị kết quả ===
if "output" in st.session_state:
    st.markdown("### 📜 Bài thơ được tạo:")
    st.code(st.session_state["output"], language="markdown")

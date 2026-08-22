import streamlit as st
from src.chat import ChatManager

st.set_page_config(
    page_title="Yerel Yapay Zeka Asistanı",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Yerel Yapay Zeka Asistanı")
st.write("Belgeleriniz üzerinden soru sorabilirsiniz.")

# Modeli bir kez yükle
if "chat" not in st.session_state:
    st.session_state.chat = ChatManager()

# Kullanıcının sorusu
question = st.chat_input("Sorunuzu yazın...")

if question:

    # Kullanıcı mesajı
    st.chat_message("user").write(question)

    # Model cevabı
    answer = st.session_state.chat.ask(question)

    # Asistan cevabı
    st.chat_message("assistant").write(answer)
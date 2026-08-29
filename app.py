from pathlib import Path

import streamlit as st

from src.retriever import retrieve_top_k
from src.generator import Generator

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = str(PROJECT_ROOT / "rag_database.db")


st.set_page_config(
    page_title="Yerel Yapay Zeka Asistanı",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Yerel Yapay Zeka Asistanı")
st.write("Belgeleriniz üzerinden soru sorabilirsiniz.")


@st.cache_resource
def get_generator():
    return Generator(model_name="qwen2.5-0.5b", app_name="rag-app")


with st.sidebar:
    st.subheader("Durum")
    st.write("Model: Qwen 2.5 0.5B")
    st.write("Embedding: Qwen3 0.6B")
    st.write("Veritabanı: rag_database.db")

    if st.button("Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


question = st.chat_input("Sorunuzu yazın...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.write(question)

    with st.spinner("Yanıt hazırlanıyor..."):
        try:
            results = retrieve_top_k(question, DB_PATH, top_k=3)
        except Exception as e:
            st.error(f"Retriever hatası: {e}")
            st.stop()

        if not results:
            answer = "Bu bilgi belgelerde bulunamadı."
            source_text = None
        else:
            context = "\n\n".join(content for content, _score in results)

            try:
                generator = get_generator()
                st.write(context)
                answer = generator.generate_answer(question, context)
            except Exception as e:
                st.error(f"Generation hatası: {e}")
                st.stop()

            source_text = "\n".join(
                [f"{i+1}. skor: {score:.4f}" for i, (_content, score) in enumerate(results)]
            )

    st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.write(answer)

        if source_text:
            with st.expander("Kaynak bağlam parçaları"):
                st.text(source_text)
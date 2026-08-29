import streamlit as st
from pathlib import Path
from src.retriever import retrieve_top_k
from src.generator import Generator

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = str(PROJECT_ROOT / "rag_database.db")

st.set_page_config(
    page_title="Yerel Yapay Zeka Asistanı",
    layout="wide",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&display=swap');

    /* Arama çubuğunu ortala ve genişliğini ayarla */
    [data-testid="stChatInput"] {
        max-width: 800px !important;
        margin: 0 auto !important;
    }
    
    /* Tıklanınca çıkan kırmızı rengi zarif bir maviyle değiştir (Orijinal şekli bozulmadan) */
    [data-testid="stChatInput"] > div:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }

    /* Sohbet balonlarını (chat messages) daha modern, premium ve kart şeklinde yap */
    [data-testid="stChatMessage"] {
        background-color: var(--secondary-background-color);
        border-radius: 20px !important;
        padding: 15px 25px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
        border: 1px solid rgba(150, 150, 150, 0.1);
    }
    
    /* Avatarların etrafındaki çerçeveyi de daha şık yap */
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"], 
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
        border-radius: 50% !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sadece sohbet boşken Gemini tarzı tam ortalanmış karşılama ekranını göster
# Kaybolmama sorununu çözmek için st.empty() (boşaltılabilir alan) kullanıyoruz.
greeting_container = st.empty()

if "messages" not in st.session_state or not st.session_state.messages:
    greeting_container.markdown('''
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 65vh;">
            <h1 style="font-family: 'Dancing Script', 'Brush Script MT', cursive; font-size: 5.5rem; font-weight: 700; color: var(--text-color); margin-bottom: 5px; line-height: 1.1;">
                Merhaba, ben asistanınız.
            </h1>
            <h2 style="font-family: 'Dancing Script', 'Brush Script MT', cursive; font-size: 3rem; font-weight: 400; color: var(--text-color); opacity: 0.6; margin-top: 0;">
                Nasıl yardımcı olabilirim?
            </h2>
        </div>
    ''', unsafe_allow_html=True)

@st.cache_resource
def get_generator():
    return Generator(model_name="qwen2.5-1.5b", app_name="rag-app")


with st.sidebar:
    st.header("Sistem Durumu")
    
    st.markdown("""
    **Yapay Zeka Modeli**
    `Qwen 2.5 1.5B`
    
    **Arama Motoru (Embedding)**
    `Qwen3 0.6B`
    
    **Veritabanı**
    `rag_database.db`
    """)
    
    st.divider()

    if st.button("Sohbeti Temizle", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


question = st.chat_input("Sorunuzu yazın...")

if question:
    # Kullanıcı ilk soruyu sorduğu an "Merhaba" yazısını anında ekrandan sil!
    greeting_container.empty()
    
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.write(question)

    with st.spinner("Yanıt hazırlanıyor..."):
        try:
            results = retrieve_top_k(question, DB_PATH, top_k=5)
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
                #st.write(context)
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
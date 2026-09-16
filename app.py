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
    /* Google'dan çok modern ve teknolojik bir font çekiyoruz */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Tüm projenin fontunu bu modern fontla değiştiriyoruz */
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Arama çubuğunu ortala ve kenarlarını daha yuvarlak yap */
    [data-testid="stChatInput"] {
        max-width: 850px !important;
        margin: 0 auto !important;
        border-radius: 30px !important;
    }
    
    /* Arama çubuğuna tıklanınca mor/pembe neon bir parlama efekti ver */
    [data-testid="stChatInput"] > div:focus-within {
        border-color: #a855f7 !important;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.4) !important;
    }

    /* Sohbet balonlarını cam (glassmorphism) tasarımına çevir */
    [data-testid="stChatMessage"] {
        border-radius: 25px !important;
        padding: 20px 30px !important;
        margin-bottom: 25px !important;
        background: linear-gradient(145deg, rgba(35,35,35,0.7) 0%, rgba(20,20,20,0.7) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    
    /* Profil fotoğraflarının çerçevesi */
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"], 
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
        border-radius: 50% !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Karşılama Ekranı Konteyneri
greeting_container = st.empty()

if "messages" not in st.session_state or not st.session_state.messages:
    greeting_container.markdown('''
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 65vh;">
            <div style="background: rgba(255,255,255,0.05); padding: 10px 25px; border-radius: 50px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;">
                <span style="color: #a1a1aa; font-family: 'Outfit', sans-serif; font-size: 0.9rem; font-weight: 600; letter-spacing: 1px;">
                    ✨ 
                </span>
            </div>
            <h1 style="font-family: 'Outfit', sans-serif; font-size: 5rem; font-weight: 800; text-align: center; 
                       background: linear-gradient(90deg, #a855f7, #ec4899, #ef4444); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0; line-height: 1.2;">
                Özel Asistanınıza<br>Hoş Geldiniz
            </h1>
            <h2 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 300; color: #a1a1aa; margin-top: 15px; text-align: center;">
                Bugün size nasıl yardımcı olabilirim?
            </h2>
        </div>
    ''', unsafe_allow_html=True)

@st.cache_resource
def get_generator():
    return Generator(model_name="qwen2.5-1.5b", app_name="rag-app")

with st.sidebar:
    # Başlık
    st.markdown('''
        <h2 style="font-family: 'Outfit', sans-serif; font-size: 2rem; font-weight: 800; 
                   background: linear-gradient(90deg, #a855f7, #ec4899); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   margin-bottom: 25px; text-align: center;">
            Sistem Durumu
        </h2>
    ''', unsafe_allow_html=True)
    
    # Kutu tasarımları ve YENİ BUTON CSS'i
    st.markdown('''
        <style>
            .status-box {
                background: rgba(20, 20, 20, 0.4);
                border: 1px solid rgba(168, 85, 247, 0.2);
                border-radius: 15px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }
            .status-box:hover {
                border-color: #a855f7;
                box-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
                transform: translateY(-2px);
            }
            .status-title {
                color: #a1a1aa;
                font-family: 'Outfit', sans-serif;
                font-size: 0.85rem;
                font-weight: 600;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .status-value {
                background: rgba(16, 185, 129, 0.1); 
                color: #10b981; 
                font-family: monospace;
                padding: 6px 10px;
                border-radius: 8px;
                font-size: 0.95rem;
                display: inline-block;
                border: 1px solid rgba(16, 185, 129, 0.2);
            }
            
            /* SOHBETİ TEMİZLE BUTONU - SİBER TASARIM */
            [data-testid="stButton"] button {
                background: linear-gradient(90deg, #a855f7, #ec4899) !important;
                color: white !important;
                border: none !important;
                border-radius: 15px !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 600 !important;
                letter-spacing: 1px !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3) !important;
            }
            
            [data-testid="stButton"] button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(236, 72, 153, 0.5) !important;
                background: linear-gradient(90deg, #db2777, #dc2626) !important;
            }
        </style>
        
        <div class="status-box">
            <div class="status-title">🤖 Yapay Zeka Modeli</div>
            <div class="status-value">Qwen 2.5 1.5B</div>
        </div>
        
        <div class="status-box">
            <div class="status-title">🔍 Arama Motoru (Embedding)</div>
            <div class="status-value">Qwen3 0.6B</div>
        </div>
        
        <div class="status-box">
            <div class="status-title">🗄️ Veritabanı</div>
            <div class="status-value">rag_database.db</div>
        </div>
    ''', unsafe_allow_html=True)
    
    st.divider()

    # Butonun type="primary" kısmını kaldırdık ki kendi CSS'imizi özgürce kullanalım
    if st.button("Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("Sorunuzu yazın...")

if question:
    greeting_container.empty()
    
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.write(question)

    with st.spinner("Yanıt hazırlanıyor..."):
        try:
            # Modelin kafası karışmasın diye belge getirme sayısı 2 yapıldı
            results = retrieve_top_k(question, DB_PATH, top_k=2)
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
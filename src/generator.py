import os
import sys

# Try to import FoundryLocalSDK
try:
    from foundry_local_sdk import Configuration, FoundryLocalManager
except ImportError:
    FoundryLocalManager = None

def generate_answer(query: str, context: str, model_name: str = "qwen2.5-0.5b"):
    """
    Kullanıcının sorusunu ve veritabanından çekilen bağlamı (context) kullanarak
    LLM ile cevap üretir.
    """
    if FoundryLocalManager is None:
        raise RuntimeError("Foundry Local SDK yüklü değil.")
        
    try:
        FoundryLocalManager.initialize(Configuration(app_name="rag-app"))
    except Exception:
        pass
    manager = FoundryLocalManager.instance
    
    # Model'i çek ve indir
    model = manager.catalog.get_model(model_name)
    try:
        model.download(lambda p: print(f"\rLLM İndiriliyor {p:.0f}%", end="", flush=True))
    except Exception as e:
        print(f"\n[Uyarı] Model indirilirken ağ hatası oluştu (Azure sunucularına ulaşılamadı). Eğer model daha önce indirildiyse yüklemeye çalışılacak...")
    
    print("\nLLM modeli yükleniyor, cevap üretilecek...")
    try:
        model.load()
    except Exception as e:
        print(f"\n[Hata] Model yüklenemedi. Lütfen internet bağlantınızı kontrol edin. Detay: {e}")
        sys.exit(1)
    
    client = model.get_chat_client()
    
    # Prompt hazırlığı
    system_prompt = (
        "You are an intelligent assistant. You must answer the user's question ONLY "
        "using the information provided in the Context below. If the answer cannot be "
        "found in the Context, say 'I do not know'. Do not make up answers."
    )
    
    user_prompt = f"Context:\n{context}\n\nQuestion:\n{query}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    print("\n--- LLM CEVABI ---")
    
    # Streaming yapısı
    try:
        # OpenAI style
        for chunk in client.complete_streaming_chat(messages):
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
    except AttributeError:
        # Alternatif chat completion API ihtimaline karşı
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="", flush=True)
                
    print("\n------------------\n")
    model.unload()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    sys.path.append(project_root)
    
    # Retriever modülünü dahil et
    try:
        from src.retriever import retrieve_top_k
    except ImportError:
        print("Hata: retriever.py bulunamadı.")
        sys.exit(1)
        
    db_path = os.path.join(project_root, "rag_database.db")
    
    if not os.path.exists(db_path):
        print("Hata: rag_database.db bulunamadı! Önce vector_db.py dosyasını çalıştırın.")
        sys.exit(1)
        
    # Test Sorusu
    query = "What is Python and what is it used for?"
    
    # 1. Aşama: Veritabanından ilgili metinleri getir
    print(f"\nSoru: {query}")
    print("Veritabanından en alakalı bilgiler aranıyor...")
    results = retrieve_top_k(query, db_path, top_k=1)
    
    if not results:
        print("Veritabanında sonuç bulunamadı.")
        sys.exit(0)
        
    best_context = results[0][0]
    score = results[0][1]
    
    print(f"Bulunan Bağlam (Skor: {score:.4f}):\n{best_context}\n")
    
    # 2. Aşama: LLM'e Sor (Generation)
    generate_answer(query, best_context)

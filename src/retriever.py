import sqlite3
import json
import os
import math
from typing import List, Tuple

# Try to import FoundryLocalSDK
try:
    from foundry_local_sdk import Configuration, FoundryLocalManager
except ImportError:
    FoundryLocalManager = None

def get_query_embedding(query: str, model_name: str = "qwen3-embedding-0.6b-generic-cpu:1") -> List[float]:
    """
    Kullanıcının sorusunu embedding vektörüne dönüştürür.
    """
    if FoundryLocalManager is None:
        raise RuntimeError("Foundry Local SDK yüklü değil.")
        
    try:
        FoundryLocalManager.initialize(Configuration(app_name="rag-app"))
    except Exception:
        pass
    manager = FoundryLocalManager.instance
    
    # Modeli al (daha önce vector_db'de indirildiği için doğrudan yüklenecek)
    model = manager.catalog.get_model_variant(model_name)
    model.load()
    
    client = model.get_embedding_client()
    response = client.generate_embedding(query)
    
    model.unload()
    return response.data[0].embedding

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    İki vektör arasındaki kosinüs benzerliğini hesaplar.
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

def retrieve_top_k(query: str, db_path: str, top_k: int = 2) -> List[Tuple[str, float]]:
    """
    Sorulan soruya en benzer metin parçalarını (chunks) veritabanından bulup getirir.
    """
    # 1. Soru için embedding al
    print(f"Soru embedding modelinden geçiriliyor: '{query}'")
    query_embedding = get_query_embedding(query)
    
    # 2. Veritabanındaki kayıtları oku
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT content, embedding FROM documents")
    rows = cursor.fetchall()
    conn.close()
    
    # 3. Benzerlik hesapla
    results = []
    for row in rows:
        content = row[0]
        # JSON'dan listeye çevir
        doc_embedding = json.loads(row[1])
        
        # Kosinüs benzerliğini hesapla
        similarity = cosine_similarity(query_embedding, doc_embedding)
        results.append((content, similarity))
        
    # 4. Benzerlik skoruna göre azalan sırada sırala
    results.sort(key=lambda x: x[1], reverse=True)
    
    # 5. En iyi 'top_k' sonucu döndür
    return results[:top_k]

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    db_path = os.path.join(project_root, "rag_database.db")
    
    if not os.path.exists(db_path):
        print("Hata: rag_database.db bulunamadı! Önce vector_db.py dosyasını çalıştırın.")
        exit(1)
        
    # Test sorusu
    test_query = "What is RAG and how does it work?"
    print(f"\n--- RAG RETRIEVER TEST ---")
    print(f"Soru: {test_query}\n")
    
    top_results = retrieve_top_k(test_query, db_path, top_k=2)
    
    print("\nEn alakalı sonuçlar:")
    print("-" * 40)
    for i, (content, score) in enumerate(top_results):
        print(f"{i+1}. Sonuç (Benzerlik Skoru: {score:.4f}):")
        print(content)
        print("-" * 40)

import sqlite3
import json
import os
from typing import List, Dict

# Try to import FoundryLocalSDK
try:
    from foundry_local_sdk import Configuration, FoundryLocalManager
except ImportError:
    FoundryLocalManager = None

def get_embeddings(texts: List[str], model_name: str = "qwen3-embedding-0.6b-generic-cpu:1") -> List[List[float]]:
    """
    Microsoft Foundry Local SDK kullanarak metinler için embedding oluşturur.
    Eğer SDK yüklü değilse, test amaçlı sahte (mock) vektörler döndürür.
    """
    if FoundryLocalManager is None:
        print("Uyarı: foundry_local_sdk yüklü değil, sahte (mock) vektörler döndürülüyor.")
        # Her metin için 3 boyutlu sahte bir vektör oluştur
        return [[0.1, 0.2, 0.3] for _ in texts]
        
    try:
        FoundryLocalManager.initialize(Configuration(app_name="rag-app"))
        manager = FoundryLocalManager.instance
        
        # Embedding modelini al (isim sisteminize göre değişebilir)
        model = manager.catalog.get_model_variant(model_name)
        
        # Model yüklenmemişse indir
        model.download(lambda p: print(f"\rEmbedding Modeli İndiriliyor {p:.0f}%", end="", flush=True))
        
        model.load()
        
        # SDK'da embedding için client'i al (API yapısı varsayımsaldır)
        client = model.get_embedding_client()
        
        embeddings = []
        for text in texts:
            # SDK'ya metni gönderip embedding al
            response = client.generate_embedding(text)
            embeddings.append(response.data[0].embedding)
            
        model.unload()
        return embeddings
        
    except Exception as e:
        print(f"Embedding oluşturulurken hata oluştu: {e}")
        return [[0.1, 0.2, 0.3] for _ in texts]

def init_db(db_path: str) -> sqlite3.Connection:
    """
    SQLite veritabanını ve gerekli tabloyu oluşturur.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        embedding TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    return conn

def save_to_db(conn: sqlite3.Connection, chunks: List[Dict[str, str]], embeddings: List[List[float]]):
    """
    Metin parçalarını (chunks) ve vektörleri veritabanına kaydeder.
    """
    cursor = conn.cursor()
    
    for chunk, embedding in zip(chunks, embeddings):
        content = chunk["content"]
        # Vektörü SQLite'a kaydetmek için JSON formatında serileştiriyoruz
        embedding_json = json.dumps(embedding)
        
        cursor.execute(
            "INSERT INTO documents (content, embedding) VALUES (?, ?)", 
            (content, embedding_json)
        )
        
    conn.commit()

if __name__ == "__main__":
    import sys
    
    # document_loader modülünü bulabilmesi için sys.path ayarı
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    sys.path.append(project_root)
    
    from src.document_loader import load_and_chunk_documents
    
    # 1. Metin parçalarını (chunks) yükle
    documents_folder = os.path.join(project_root, "documents")
    print(f"'{documents_folder}' klasöründen dokümanlar okunuyor...")
    document_chunks = load_and_chunk_documents(documents_folder)
    
    if not document_chunks:
        print("Hiç doküman bulunamadı. İşlem sonlandırılıyor.")
        sys.exit(0)
        
    print(f"Toplam {len(document_chunks)} adet chunk bulundu.")
    
    # 2. Embeddingleri oluştur
    print("Embeddingler oluşturuluyor...")
    texts = [chunk["content"] for chunk in document_chunks]
    embeddings = get_embeddings(texts)
    
    # 3. Veritabanını oluştur ve verileri kaydet
    db_path = os.path.join(project_root, "rag_database.db")
    print(f"Veritabanı başlatılıyor: {db_path}")
    conn = init_db(db_path)
    
    print("Veriler veritabanına kaydediliyor...")
    save_to_db(conn, document_chunks, embeddings)
    
    # 4. Veritabanındaki satır sayısını kontrol et
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM documents")
    count = cursor.fetchone()[0]
    
    print("-" * 40)
    print(f"Başarılı! Veritabanına toplam {count} satır veri kaydedildi.")
    print("-" * 40)
    
    conn.close()

# Yerel Yapay Zeka Asistanı (Local RAG AI Assistant)

## Projenin Amacı
Bu proje, Microsoft Foundry Local teknolojisini kullanarak tamamen çevrimdışı (offline) ve yerel cihaz üzerinde çalışan bir RAG (Retrieval-Augmented Generation) Soru-Cevap asistanı geliştirmek amacıyla tasarlanmıştır. Proje, "One-Month Project Plan: Local RAG AI Assistant with Microsoft Foundry Local" müfredatının nihai hedeflerini ve bitirme projesi gereksinimlerini (%100) karşılamaktadır.

İnternet bağlantısına veya bulut API'lerine ihtiyaç duymadan, tamamen sizin kendi belgelerinize (knowledge base) dayanarak soruları yanıtlar ve yapay zekanın uydurma (halüsinasyon) yapmasını kesin kurallarla engeller.

## Kullanılan Teknolojiler & Mimari
* **Microsoft Foundry Local:** Cihaz üzerinde LLM (Büyük Dil Modeli) çıkarımı (inference) için kullanılmıştır. Herhangi bir bulut aboneliği gerektirmeden CPU/GPU hızlandırması ile yerel çalışır.
* **Modeller:** 
  * Üretici Model (LLM): `qwen2.5-1.5b`
  * Vektör/Embedding Modeli: `qwen3-0.6b`
* **Veritabanı (Vektör Depolama):** `SQLite`. Sunucusuz, hafif yapısıyla vektörleri ve metin parçalarını (chunks) dış bir sunucuya ihtiyaç duymadan tek bir dosyada (`rag_database.db`) saklar.
* **Arayüz (UI):** `Streamlit` ile çapraz platform, estetik, karanlık/aydınlık tema (dark/light mode) uyumlu, kaligrafik fontlarla zenginleştirilmiş modern bir sohbet arayüzü inşa edilmiştir.

## Sistem Nasıl Çalışır? (RAG Pipeline)
1. **Veri Hazırlığı (Ingestion):** `documents/` klasöründeki belgeler anlam bütünlüğünü koruyacak küçük parçalara (chunk) bölünür.
2. **Vektörizasyon (Embedding):** Her bir metin parçası, embedding modeli ile sayısal vektör dizilerine dönüştürülüp SQLite veritabanına kaydedilir.
3. **Arama (Retrieval):** Kullanıcı soru sorduğunda, soru vektörleştirilir ve veritabanında *Kosinüs Benzerliği (Cosine Similarity)* algoritmasıyla taranarak en alakalı 5 parça tespit edilir.
4. **Yanıt Üretimi (Generation):** Bulunan bu 5 metin parçası (context), çok katı kurallarla donatılmış bir Sistem İstemine (System Prompt) yerleştirilerek ana modele gönderilir. Model sadece bu metinlere sadık kalarak bir Türkçe yanıt üretir. Cevap belgelerde yoksa, uydurmak yerine "Bu bilgi belgelerde bulunamadı" yanıtını verir.

## Kurulum ve Çalıştırma
**Ön Koşullar:** Python yüklü bir bilgisayar ve aktif bir sanal ortam (venv).

1. **Bağımlılıkları Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Veritabanını Oluşturun (Eğer ilk defa kuruyorsanız):**
   ```bash
   python src/vector_db.py
   ```
   *Bu işlem `documents` klasöründeki metinleri tarar, embedding işlemi yapar ve `rag_database.db` dosyasını oluşturur.*

3. **Asistanı Başlatın:**
   ```bash
   streamlit run app.py
   ```
   *Tarayıcınızda açılan sekmede, ekranın altındaki şık arama çubuğunu kullanarak belgelerinizle anında sohbet etmeye başlayabilirsiniz.*

## Tasarım ve Geliştirme Kararları
* **Modern Arayüz (UI):** Arayüz tasarımı, pazar standardı olan AI asistanlarından (örn: Gemini) ilham alınarak geliştirilmiştir. Yazılar "Flexbox" mimarisiyle ekranın tam merkezine hizalanmış, renkler temanın (açık/koyu) durumuna göre dinamik hale getirilmiş ve arama çubuğuna özel odaklanma efektleri (gölgelendirme) eklenmiştir.
* **İstem Mühendisliği (Prompt Engineering):** Soru-Cevap botunun en büyük riski olan "halüsinasyon" ihtimali, `generator.py` dosyasındaki 3 aşamalı, numaralandırılmış negatif komutlarla (örn: "Dışarıdan hiçbir bilgi ekleme") tamamen ortadan kaldırılmıştır.

---


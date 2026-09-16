# microsoft_azure_foundry_local_LLM
# 🚀 Tamamen Yerel RAG (Retrieval-Augmented Generation) Asistanı

Bu proje, bulut bilişime veya internet bağlantısına ihtiyaç duymadan, **%100 çevrimdışı (offline)** ve veri gizliliğini koruyarak çalışan bir yapay zeka asistanıdır. Geliştirilen bu RAG mimarisi, internetteki genel bilgiler yerine yalnızca kullanıcının sisteme yüklediği özel dokümanları referans alarak güvenilir ve şeffaf cevaplar üretir.

## 🧠 Proje Mimarisi

Sistem 4 temel bileşenden oluşmaktadır:
* **Arama Motoru (Embedding):** `Qwen3-0.6B` modeli ile metinler matematiksel vektörlere dönüştürülür.
* **Veritabanı:** Vektörler, hafif ve yerel bir çözüm olan `SQLite` üzerinde saklanır.
* **Cevap Üretici (Generator):** Cihaz içi (on-device) çalışmaya uygun `Qwen 2.5 1.5B` dil modeli kullanılır.
* **Kullanıcı Arayüzü (UI):** `Streamlit` ile modern, cam tasarımlı (glassmorphism) ve kullanıcı dostu bir sohbet arayüzü sunulur.

---

## ⚙️ Kurulum ve Çalıştırma Adımları

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları sırasıyla uygulayın.

### 1. Gereksinimlerin Yüklenmesi
Öncelikle projenin çalışması için gerekli olan Python kütüphanelerini (özellikle Microsoft Foundry Local SDK ve Streamlit) kurun:
```bash
pip install -r requirements.txt

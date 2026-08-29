from foundry_local_sdk import Configuration, FoundryLocalManager


class Generator:
    def __init__(self, model_name: str = "qwen2.5-1.5b", app_name: str = "rag-app"):
        try:
            FoundryLocalManager.initialize(Configuration(app_name=app_name))
        except Exception:
            pass

        self.manager = FoundryLocalManager.instance
        self.model = self.manager.catalog.get_model(model_name)

        # ÖNEMLİ: modeli önce indir, sonra yükle
        try:
            self.model.download(
                lambda p: print(f"\rLLM modeli indiriliyor {p:.0f}%", end="", flush=True)
            )
            print()
        except Exception:
            # Model zaten indirilmiş olabilir
            pass

        self.model.load()
        self.client = self.model.get_chat_client()

    def generate_answer(self, query: str, context: str) -> str:
        system_prompt = (
            "Sen sadece sana verilen metinleri kullanarak cevap üreten bir asistansın.\n"
            "Lütfen aşağıdaki kurallara kesinlikle uy:\n"
            "1. Sadece metinlerdeki bilgileri kullan. Kendi genel bilgini asla ekleme.\n"
            "2. Eğer sorunun cevabı metinlerde varsa, o bilgiyle soruyu cevapla.\n"
            "3. Eğer metinlerde soruyla ilgili hiçbir bilgi yoksa, sadece şunu söyle: 'Bu bilgi belgelerde bulunamadı.'"
        )

        user_prompt = f"Bağlam:\n{context}\n\nSoru:\n{query}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = ""

        for chunk in self.client.complete_streaming_chat(messages):
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content
            if content:
                response += content

        return response.strip()

    def close(self):
        try:
            self.model.unload()
        except Exception:
            pass
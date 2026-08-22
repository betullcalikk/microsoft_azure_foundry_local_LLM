from foundry_local_sdk import Configuration, FoundryLocalManager


class ChatManager:
    def __init__(self):
        FoundryLocalManager.initialize(Configuration(app_name="my-app"))
        self.manager = FoundryLocalManager.instance

        self.model = self.manager.catalog.get_model("qwen2.5-0.5b")

        self.model.download(
            lambda p: print(f"\rDownloading {p:.0f}%", end="", flush=True)
        )
        print()

        self.model.load()

        self.client = self.model.get_chat_client()

    def ask(self, question):

        response = ""

        for chunk in self.client.complete_streaming_chat([
            {"role": "user", "content": question}
        ]):

            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                response += content

        return response

    def close(self):
        self.model.unload()
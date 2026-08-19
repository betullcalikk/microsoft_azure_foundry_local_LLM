from foundry_local_sdk import Configuration, FoundryLocalManager

def main():
    FoundryLocalManager.initialize(Configuration(app_name="my-app"))
    manager = FoundryLocalManager.instance

    model = manager.catalog.get_model("qwen2.5-0.5b")
    model.download(lambda p: print(f"\rDownloading {p:.0f}%", end="", flush=True))
    print()
    model.load()

    client = model.get_chat_client()

    for chunk in client.complete_streaming_chat([
        {"role": "user", "content": "Why is the sky blue?"}
    ]):
        if not chunk.choices:
            continue
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)

    print()
    model.unload()

if __name__ == "__main__":
    main()
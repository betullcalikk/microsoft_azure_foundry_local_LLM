from src.loader import load_documents


def main():

    loaded_docs = load_documents()

    if not loaded_docs:
        print("documents klasöründe .txt dosyası bulunamadı.")
        return

    for name, text in loaded_docs:
        print(f"\n{name}")
        print(text)


if __name__ == "__main__":
    main()
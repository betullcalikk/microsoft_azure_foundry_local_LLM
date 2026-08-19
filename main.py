from pathlib import Path

def load_documents(folder="documents"):
    docs = []
    folder_path = Path(folder)

    if not folder_path.exists():
        print(f"Klasör bulunamadı: {folder_path.resolve()}")
        return docs

    txt_files = list(folder_path.glob("*.txt"))
    print("Bulunan txt dosyaları:", [f.name for f in txt_files])

    for file_path in txt_files:
        text = file_path.read_text(encoding="utf-8")
        docs.append((file_path.name, text))

    return docs


def main():
    loaded_docs = load_documents()

    if not loaded_docs:
        print("documents klasöründe .txt dosyası bulunamadı.")
        return

    for name, text in loaded_docs:
        print(f"\n--- {name} ---")
        print(text)


if __name__ == "__main__":
    main()
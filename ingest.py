import re
from pathlib import Path

DOCS_DIR = Path("documents")


def clean_text(text: str) -> str:
    """Normalize whitespace; txt files are already clean of HTML/nav."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_documents(docs_dir: Path = DOCS_DIR) -> list[dict]:
    docs = []
    for file in sorted(docs_dir.glob("*.txt")):
        text = clean_text(file.read_text(encoding="utf-8"))
        docs.append({"source": file.name, "text": text})
    return docs


def chunk_documents(docs: list[dict]) -> list[dict]:
    """Split each document into paragraph chunks with title context."""
    chunks = []
    for doc in docs:
        paragraphs = [p.strip() for p in doc["text"].split("\n\n") if p.strip()]
        if not paragraphs:
            continue

        title = paragraphs[0]
        for idx, paragraph in enumerate(paragraphs):
            if idx == 0:
                chunk_text = paragraph
            else:
                chunk_text = f"{title}\n\n{paragraph}"

            chunks.append({
                "source": doc["source"],
                "chunk_index": idx,
                "text": chunk_text,
            })
    return chunks


if __name__ == "__main__":
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")

    all_chunks = chunk_documents(documents)
    print(f"Created {len(all_chunks)} chunks")

    print("\n--- Sample chunks (first 5) ---")
    for chunk in all_chunks[:5]:
        print(f"\nSOURCE: {chunk['source']} (chunk {chunk['chunk_index']})")
        print(chunk["text"][:250])
        if len(chunk["text"]) > 250:
            print("...")

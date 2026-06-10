"""Build or rebuild the ChromaDB vector index from documents/."""

from rag import RAGPipeline

if __name__ == "__main__":
    pipeline = RAGPipeline()
    count = pipeline.build_index(force=True)
    print(f"Indexed {count} chunks into ChromaDB.")

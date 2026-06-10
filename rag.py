import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

from ingest import chunk_documents, load_documents

load_dotenv()

CHROMA_PATH = "./chroma"
COLLECTION_NAME = "unofficial-guide"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"
TOP_K = 4


class RAGPipeline:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self._groq_client = None

    @property
    def groq_client(self) -> Groq:
        if self._groq_client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key or api_key == "your_key_here":
                raise ValueError(
                    "GROQ_API_KEY not set. Copy .env.example to .env and add your key."
                )
            self._groq_client = Groq(api_key=api_key)
        return self._groq_client

    def build_index(self, force: bool = False) -> int:
        if self.collection.count() > 0 and not force:
            return self.collection.count()

        docs = load_documents()
        chunks = chunk_documents(docs)
        if not chunks:
            raise ValueError("No chunks produced — check documents/ folder.")

        if force and self.collection.count() > 0:
            self.client.delete_collection(COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )

        texts = [c["text"] for c in chunks]
        embeddings = self.embedder.encode(texts, show_progress_bar=True).tolist()

        ids = [f"{c['source']}_{c['chunk_index']}" for c in chunks]
        metadatas = [
            {
                "source": c["source"],
                "chunk_index": c["chunk_index"],
            }
            for c in chunks
        ]

        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            end = i + batch_size
            self.collection.add(
                ids=ids[i:end],
                embeddings=embeddings[i:end],
                documents=texts[i:end],
                metadatas=metadatas[i:end],
            )

        return len(chunks)

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[dict]:
        query_embedding = self.embedder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        retrieved = []
        for doc, meta, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            retrieved.append({
                "text": doc,
                "source": meta["source"],
                "chunk_index": meta["chunk_index"],
                "distance": distance,
            })
        return retrieved

    def generate_answer(self, question: str, retrieved: list[dict]) -> str:
        if not retrieved:
            return "I don't have enough information on that."

        context_parts = []
        for i, chunk in enumerate(retrieved, 1):
            context_parts.append(
                f"[{i}] Source: {chunk['source']}\n{chunk['text']}"
            )
        context = "\n\n".join(context_parts)

        prompt = f"""You are The Unofficial Guide, a student knowledge assistant.

Answer the question using ONLY the information in the provided context documents.
Do NOT use outside knowledge or guess.
If the context does not contain enough information to answer, respond with exactly:
"I don't have enough information on that."
When you use information from a source, mention the professor or course and reference the source filename.

Context:
{context}

Question: {question}

Answer:"""

        response = self.groq_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()

    def ask(self, question: str) -> dict:
        retrieved = self.retrieve(question)
        answer = self.generate_answer(question, retrieved)
        sources = sorted({c["source"] for c in retrieved})
        return {
            "answer": answer,
            "sources": sources,
            "chunks": retrieved,
        }


_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
        _pipeline.build_index()
    return _pipeline


def ask(question: str) -> dict:
    return get_pipeline().ask(question)

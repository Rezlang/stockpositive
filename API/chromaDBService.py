from chromadb import PersistentClient
from typing import List, Dict
from LLMService import embed
import uuid
from utils import cos


class ChromaDBService:

    def __init__(self):
        self.chroma_client = PersistentClient(path="./chroma_db")

        self.collection = self.chroma_client.get_or_create_collection(
            name="rag_docs",
            metadata={
                "description": "RAG document storage",
                "embedding_dimension": 768
            },
            embedding_function=None
        )

        self.data_source_status = {}

    def set_source_enabled(self, source: str, enabled: bool):
        self.data_source_status[source] = enabled

    def get_enabled_sources(self) -> List[str]:
        return [s for s, enabled in self.data_source_status.items() if enabled]

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks

    def add_document(self, doc_text: str, source_name: str):
        chunks = self.chunk_text(doc_text)

        ids = []
        metadatas = []
        documents = []

        for chunk in chunks:
            ids.append(str(uuid.uuid4()))
            metadatas.append({"source": source_name})
            documents.append(chunk)

        embeds = embed(documents)

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeds
        )

        print(f"Inserted {len(chunks)} text chunks from source: {source_name}")

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        enabled_sources = self.get_enabled_sources()

        if not enabled_sources:
            print("No data sources enabled. Retrieval will return nothing.")
            return []

        query_embed = embed([query])[0]

        # raw vector search
        vector_results = self.collection.query(
            query_embeddings=[query_embed],
            n_results=top_k,
            include=["documents", "metadatas", "embeddings"]
        )

        retrieved_chunks = []
        for doc, meta, emb in zip(
            vector_results["documents"][0],
            vector_results["metadatas"][0],
            vector_results["embeddings"][0]
        ):
            if meta["source"] in enabled_sources:
                relevance = cos(emb, query_embed)
                retrieved_chunks.append({
                    "text": doc,
                    "source": meta["source"],
                    "embedding": emb,
                    "relevance": relevance
                })

        # sort by true semantic similarity
        retrieved_chunks.sort(key=lambda x: x["relevance"], reverse=True)

        return retrieved_chunks[:top_k]

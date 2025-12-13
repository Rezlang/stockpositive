import psycopg
import uuid
from typing import List, Optional, Tuple
from LLMService import embed
import numpy as np
import ast
import re

DB_NAME = "semantic_store"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = 5432

EMBEDDING_DIM = 768
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > chunk_size:
            chunks.append(' '.join(current_chunk))
            overlap_words = []
            if overlap > 0:
                all_words = ' '.join(current_chunk).split()
                overlap_words = all_words[-overlap:] if len(
                    all_words) >= overlap else all_words
            current_chunk = overlap_words + sentence.split()
            current_length = len(current_chunk)
        else:
            current_chunk.extend(sentence.split())
            current_length += sentence_length

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def init_db():
    with psycopg.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        autocommit=True
    ) as admin_conn:
        with admin_conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
            if not cur.fetchone():
                cur.execute(f"CREATE DATABASE {DB_NAME};")

    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY,
                    source TEXT NOT NULL UNIQUE,
                    full_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS chunks (
                    id UUID PRIMARY KEY,
                    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INT NOT NULL,
                    text TEXT NOT NULL,
                    embedding VECTOR({EMBEDDING_DIM}),
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(document_id, chunk_index)
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS chunks_embedding_idx
                ON chunks USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """)


def ingest_document(source: str, full_text: str) -> Optional[uuid.UUID]:
    chunks = chunk_text(full_text)
    doc_id = uuid.uuid4()

    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO documents (id, source, full_text)
                VALUES (%s, %s, %s)
                ON CONFLICT (source) DO NOTHING
                RETURNING id;
            """, (doc_id, source, full_text))

            row = cur.fetchone()
            if row is None:
                return None

            doc_id = row[0]

            chunk_embeddings = [np.array(e, dtype=np.float32)
                                for e in embed(chunks)]
            chunk_rows = [
                (uuid.uuid4(), doc_id, idx,
                 chunks[idx], chunk_embeddings[idx].tolist())
                for idx in range(len(chunks))
            ]

            cur.executemany("""
                INSERT INTO chunks (id, document_id, chunk_index, text, embedding)
                VALUES (%s, %s, %s, %s, %s);
            """, chunk_rows)

    return doc_id


def find_most_similar_chunk(query_text: str, top_k: int = 5) -> List[Tuple[str, str, float]]:
    query_embedding = np.array(embed([query_text])[0], dtype=np.float32)

    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.text, d.source, c.embedding
                FROM chunks c
                JOIN documents d ON c.document_id = d.id;
            """)
            results = []
            for text, source, emb in cur.fetchall():
                # Convert embedding string to numpy array
                if isinstance(emb, str):
                    emb_array = np.array(
                        ast.literal_eval(emb), dtype=np.float32)
                else:
                    emb_array = np.array(emb, dtype=np.float32)

                sim = cosine_similarity(query_embedding, emb_array)
                results.append((text, source, sim))

            results.sort(key=lambda x: x[2], reverse=True)
            return results[:top_k]


def get_document(doc_id: Optional[uuid.UUID] = None, source: Optional[str] = None) -> Optional[dict]:
    if doc_id is None and source is None:
        raise ValueError("Either doc_id or source must be provided")
    query_field = "id" if doc_id else "source"
    query_value = doc_id if doc_id else source

    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT id, source, full_text, created_at FROM documents WHERE {query_field} = %s;",
                (query_value,)
            )
            row = cur.fetchone()
            if row:
                return {"id": row[0], "source": row[1], "full_text": row[2], "created_at": row[3]}
    return None


if __name__ == "__main__":
    init_db()

    doc_id = ingest_document(
        source="Potter 1",
        full_text=open("potter.txt", "r", encoding="utf-8").read(),
    )

    if doc_id is None:
        print("Document already exists, skipping ingestion.")
    else:
        print("Ingested document:", doc_id)

    # Similarity search
    similar_chunks = find_most_similar_chunk(
        "pig tail")
    for text, source, sim in similar_chunks:
        print(
            f"Source: {source}, Similarity: {sim:.4f}, Chunk: {text}...\n")

    # Document lookup
    # doc_info = get_document(source="Potter 1")
    # print("Document info:", doc_info)

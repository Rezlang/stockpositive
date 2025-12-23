import psycopg
from psycopg.rows import dict_row

DB_NAME = "semantic_store"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = 5432

EMBEDDING_DIM = 768  # Gemini embedding dimension


def reset_db():
    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    ) as conn:
        with conn.cursor() as cur:
            # Drop tables if they exist
            cur.execute("DROP TABLE IF EXISTS chunks CASCADE;")
            cur.execute("DROP TABLE IF EXISTS documents CASCADE;")

            # Recreate tables
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            cur.execute(f"""
                CREATE TABLE documents (
                    id UUID PRIMARY KEY,
                    source TEXT NOT NULL UNIQUE,
                    full_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            cur.execute(f"""
                CREATE TABLE chunks (
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
                CREATE INDEX chunks_embedding_idx
                ON chunks USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """)

    print("Database reset: tables dropped and recreated.")


if __name__ == "__main__":
    reset_db()

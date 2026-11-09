import psycopg
from pgvector.psycopg import register_vector

from .config import DATABASE_URL, EMBED_DIM


def connect() -> psycopg.Connection:
    with psycopg.connect(DATABASE_URL, autocommit=True) as boot:
        boot.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn

def init_schema(conn: psycopg.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            id SERIAL PRIMARY KEY,
            source_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            paper_id INT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
            chunk_index INT NOT NULL,
            content TEXT NOT NULL,
            embedding vector({EMBED_DIM}) NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS chunks_embedding_idx
        ON chunks USING hnsw (embedding vector_cosine_ops)
        """
    )
    conn.commit()
from sentence_transformers import SentenceTransformer

from .config import EMBED_MODEL, QUERY_PREFIX
from .db import connect

_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def dense_search(query: str, k: int = 5) -> list[dict]:
    q = _get_model().encode(QUERY_PREFIX + query, normalize_embeddings=True)
    conn = connect()
    rows = conn.execute(
        """
        SELECT c.id, p.title, c.chunk_index, c.content,
               1 - (c.embedding <=> %s) AS score
        FROM chunks c JOIN papers p ON p.id = c.paper_id
        ORDER BY c.embedding <=> %s
        LIMIT %s
        """,
        (q, q, k),
    ).fetchall()
    conn.close()
    return [
        {"id": r[0], "title": r[1], "chunk_index": r[2],
         "content": r[3], "score": float(r[4])}
        for r in rows
    ]


if __name__ == "__main__":
    import sys

    question = " ".join(sys.argv[1:]) or "What is retrieval augmented generation?"
    for hit in dense_search(question):
        print(f"[{hit['score']:.3f}] {hit['title']} (chunk {hit['chunk_index']})")
        print(hit["content"][:300].replace("\n", " "), "...\n")
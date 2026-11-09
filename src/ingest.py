import json

import fitz
from sentence_transformers import SentenceTransformer

from .chunking import chunk_text, clean_text
from .config import CHUNK_OVERLAP, CHUNK_WORDS, EMBED_MODEL, PAPERS_DIR
from .db import connect, init_schema


def extract_text(pdf_path) -> str:
    with fitz.open(pdf_path) as doc:
        return "\n\n".join(page.get_text() for page in doc)


def load_title(pdf_path) -> str:
    meta = pdf_path.with_suffix(".json")
    if meta.exists():
        return json.loads(meta.read_text())["title"]
    return pdf_path.stem


def main() -> None:
    pdfs = sorted(PAPERS_DIR.glob("*.pdf"))
    if not pdfs:
        raise SystemExit("No PDFs found. Run: python -m src.download_papers")

    model = SentenceTransformer(EMBED_MODEL)
    conn = connect()
    init_schema(conn)

    for pdf in pdfs:
        source_id = pdf.stem
        exists = conn.execute(
            "SELECT 1 FROM papers WHERE source_id = %s", (source_id,)
        ).fetchone()
        if exists:
            continue

        text = clean_text(extract_text(pdf))
        chunks = chunk_text(text, CHUNK_WORDS, CHUNK_OVERLAP)
        if not chunks:
            continue

        vectors = model.encode(
            chunks, batch_size=32, normalize_embeddings=True, show_progress_bar=False
        )

        paper_id = conn.execute(
            "INSERT INTO papers (source_id, title) VALUES (%s, %s) RETURNING id",
            (source_id, load_title(pdf)),
        ).fetchone()[0]
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO chunks (paper_id, chunk_index, content, embedding) "
                "VALUES (%s, %s, %s, %s)",
                [(paper_id, i, c, v) for i, (c, v) in enumerate(zip(chunks, vectors))],
            )
        conn.commit()
        print(f"{source_id}: {len(chunks)} chunks")


if __name__ == "__main__":
    main()
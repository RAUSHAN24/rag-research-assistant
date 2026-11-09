import re


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"-\n(\w)", r"\1", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def chunk_text(text: str, chunk_words: int = 220, overlap: int = 40) -> list[str]:
    if overlap >= chunk_words:
        raise ValueError("overlap must be smaller than chunk_words")

    paragraphs = [p.replace("\n", " ").strip() for p in text.split("\n\n")]
    words: list[str] = []
    for p in paragraphs:
        if p:
            words.extend(p.split())

    chunks: list[str] = []
    step = chunk_words - overlap
    for start in range(0, len(words), step):
        window = words[start : start + chunk_words]
        if len(window) < overlap + 10 and chunks:
            break
        chunks.append(" ".join(window))
        if start + chunk_words >= len(words):
            break
    return chunks
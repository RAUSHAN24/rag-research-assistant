from src.chunking import chunk_text, clean_text


def test_clean_text_joins_hyphenated_breaks():
    assert "retrieval" in clean_text("retrie-\nval is useful")


def test_chunks_respect_size_and_overlap():
    text = " ".join(f"w{i}" for i in range(1000))
    chunks = chunk_text(text, chunk_words=100, overlap=20)
    assert all(len(c.split()) <= 100 for c in chunks)
    assert chunks[0].split()[-20:] == chunks[1].split()[:20]


def test_all_words_are_covered():
    text = " ".join(f"w{i}" for i in range(500))
    chunks = chunk_text(text, chunk_words=100, overlap=20)
    assert set(" ".join(chunks).split()) == set(text.split())
import json
import sys
import time

import arxiv
import requests

from .config import PAPERS_DIR


def main(query: str, max_results: int) -> None:
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    client = arxiv.Client(page_size=50, delay_seconds=3, num_retries=3)
    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
    )

    for result in client.results(search):
        paper_id = result.get_short_id().replace("/", "_")
        pdf_path = PAPERS_DIR / f"{paper_id}.pdf"
        if pdf_path.exists():
            continue

        print(f"downloading {paper_id}: {result.title}")
        response = requests.get(result.pdf_url, timeout=60)
        response.raise_for_status()
        pdf_path.write_bytes(response.content)

        meta = {"source_id": paper_id, "title": result.title}
        (PAPERS_DIR / f"{paper_id}.json").write_text(json.dumps(meta))
        time.sleep(3)


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "retrieval augmented generation"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    main(q, n)
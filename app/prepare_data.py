"""Docker build step: make sure the image has the scraped data, the search index and the embedding model.

The scraped data is not in the public repository, because Wasalt's llms.txt forbids redistributing it. So:
- Local builds and most hosts: put the scraper output in data/raw/ before `docker build`; the index is built here.
- Hugging Face Spaces (public repo): the data and the prebuilt index live in a PRIVATE dataset. The build reads it
  with the Space's HF_TOKEN secret (mounted at /run/secrets/HF_TOKEN) from the repo named by the DATA_REPO variable.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

from config import EMBED_MODEL, INDEX_DIR, MODEL_DIR, RAW_DIR, ROOT

SECRET_FILE = pathlib.Path("/run/secrets/HF_TOKEN")


def fetch_private_data(repo: str) -> None:
    from huggingface_hub import snapshot_download

    token = SECRET_FILE.read_text().strip() if SECRET_FILE.exists() else os.getenv("HF_TOKEN")
    if not token:
        sys.exit(f"DATA_REPO={repo} is set but no HF_TOKEN secret is available to read it.")
    snapshot_download(repo_id=repo, repo_type="dataset", token=token, local_dir=ROOT / "data",
                      allow_patterns=["raw/*.jsonl", "index/*"])
    print(f"fetched data from the private dataset {repo}", flush=True)


def main() -> None:
    if not any(RAW_DIR.glob("*.jsonl")):
        repo = os.getenv("DATA_REPO", "").strip()
        if not repo:
            sys.exit("No data: data/raw/ is empty and DATA_REPO is not set. Run the scrapers first (see README).")
        fetch_private_data(repo)

    if not (INDEX_DIR / "meta.json").exists():
        subprocess.run([sys.executable, str(ROOT / "app" / "build_index.py")], check=True)

    # the query-embedding model must be inside the image, so the container starts without downloading anything
    from fastembed import TextEmbedding

    TextEmbedding(EMBED_MODEL, cache_dir=str(MODEL_DIR))
    print("data, index and embedding model ready", flush=True)


if __name__ == "__main__":
    main()

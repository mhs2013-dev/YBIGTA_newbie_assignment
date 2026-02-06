"""Ingest embeddings into Pinecone vector index.

Batch upsert: 100 vectors per call.
Metadata: text truncated to 1000 chars (40KB limit).
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from pinecone import Pinecone
from tqdm import tqdm

load_dotenv()

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

BATCH_SIZE = 100
TEXT_LIMIT = 1000  # metadata text truncation


def ingest(progress_callback=None):
    """Batch upsert embeddings into Pinecone vector index.

    Args:
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        int: Number of vectors upserted.

    Hints:
        - Load embeddings from PROCESSED_DIR / "embeddings.npy"
        - Load IDs from PROCESSED_DIR / "embedding_ids.json"
        - Load texts from RAW_DIR / "corpus.jsonl" for metadata
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Upsert format: {"id": ..., "values": [...], "metadata": {"text": ...}}
        - Batch size: BATCH_SIZE (100), truncate text to TEXT_LIMIT (1000) chars
    """
    embeddings_path = PROCESSED_DIR / "embeddings.npy"
    ids_path = PROCESSED_DIR / "embedding_ids.json"
    corpus_path = RAW_DIR / "corpus.jsonl"

    if not embeddings_path.exists() or not ids_path.exists():
        raise FileNotFoundError("Embeddings or IDs not found. Run embedding step first.")
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus not found: {corpus_path}")

    embeddings = np.load(embeddings_path)
    ids = json.loads(ids_path.read_text())

    id_to_text: dict[str, str] = {}
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            id_to_text[doc["id"]] = doc["text"]

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX", "ragsession")
    index = pc.Index(index_name)

    total = len(ids)
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    batch_count = 0

    for start in tqdm(range(0, total, BATCH_SIZE), desc="Upserting to Pinecone"):
        end = min(start + BATCH_SIZE, total)
        vectors = []
        for i in range(start, end):
            doc_id = ids[i]
            text = id_to_text.get(doc_id, "")
            vectors.append(
                {
                    "id": doc_id,
                    "values": embeddings[i].tolist(),
                    "metadata": {"text": text[:TEXT_LIMIT]},
                }
            )
        index.upsert(vectors=vectors)

        batch_count += 1
        if progress_callback:
            progress_callback(batch_count, total_batches)

    return total


if __name__ == "__main__":
    ingest()

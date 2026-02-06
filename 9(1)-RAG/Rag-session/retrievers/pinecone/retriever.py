"""Vector retriever using Pinecone (cosine similarity)."""

import os

from dotenv import load_dotenv
from pinecone import Pinecone

from ingest.embedding import embed_query

load_dotenv()


def search(query: str, top_k: int = 10) -> list[dict]:
    """Vector cosine similarity search.

    Args:
        query: Search query string.
        top_k: Number of results to return.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Vector".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Use index.query(vector=..., top_k=..., include_metadata=True)
        - Text is in match["metadata"]["text"]
    """
    query_vector = embed_query(query)

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX", "ragsession")
    index = pc.Index(index_name)

    resp = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    matches = resp.get("matches", []) if isinstance(resp, dict) else resp.matches

    results = []
    for m in matches:
        if isinstance(m, dict):
            metadata = m.get("metadata") or {}
            results.append(
                {
                    "id": m.get("id"),
                    "text": metadata.get("text", ""),
                    "score": m.get("score", 0.0),
                    "method": "Vector",
                }
            )
        else:
            metadata = getattr(m, "metadata", {}) or {}
            results.append(
                {
                    "id": getattr(m, "id", None),
                    "text": metadata.get("text", ""),
                    "score": getattr(m, "score", 0.0),
                    "method": "Vector",
                }
            )

    return results

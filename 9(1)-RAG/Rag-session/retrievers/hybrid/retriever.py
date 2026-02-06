"""Hybrid retriever using Elasticsearch RRF (Reciprocal Rank Fusion).

Combines BM25 text search with dense vector kNN search.
Uses ES 8.14+ RRF support with rank_constant=60.
"""

import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from ingest.embedding import embed_query

load_dotenv()

INDEX_NAME = "wiki-hybrid"


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=30,
    )


def search(query: str, top_k: int = 10, candidate_size: int = 50) -> list[dict]:
    """RRF hybrid search combining BM25 + kNN.

    Args:
        query: Search query string.
        top_k: Number of results to return.
        candidate_size: Number of kNN candidates before RRF fusion.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Hybrid (RRF)".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Use get_es_client() and es.search() with "retriever" parameter
        - RRF retriever combines "standard" (BM25 match) + "knn" retrievers
        - kNN field: "embedding", rank_constant: 60
        - num_candidates = candidate_size * 2
    """
    query_vector = embed_query(query)

    es = get_es_client()
    retriever = {
        "rrf": {
            "retrievers": [
                {"standard": {"query": {"match": {"text": query}}}},
                {
                    "knn": {
                        "field": "embedding",
                        "query_vector": query_vector,
                        "k": candidate_size,
                        "num_candidates": candidate_size * 2,
                    }
                },
            ],
            "rank_constant": 60,
        }
    }

    resp = es.search(index=INDEX_NAME, body={"size": top_k, "retriever": retriever})
    hits = resp.get("hits", {}).get("hits", [])

    results = []
    for h in hits:
        src = h.get("_source", {})
        results.append(
            {
                "id": h.get("_id"),
                "text": src.get("text", ""),
                "score": h.get("_score", 0.0),
                "method": "Hybrid (RRF)",
            }
        )
    return results

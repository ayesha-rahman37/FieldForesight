
import os
import sys
from typing import Any, Dict, List, Optional

from sklearn.feature_extraction.text import HashingVectorizer

from app.services.rag_config import (
    RAG_CHROMA_DIR,
    RAG_COLLECTION_NAME,
    RAG_SIMILARITY_THRESHOLD,
    RAG_DEFAULT_TOP_K,
)

_CHROMA_CLIENT = None

_VECTOR_SIZE = 4096


# ============================================================
# VECTOR SEARCH CONFIGURATION
# ============================================================

def get_vectorizer():
    return HashingVectorizer(
        analyzer="char",
        ngram_range=(2, 5),
        n_features=_VECTOR_SIZE,
        alternate_sign=False,
        norm="l2",
        lowercase=True,
    )


# ============================================================
# CHROMA CLIENT
# ============================================================

def get_chroma_client():
    global _CHROMA_CLIENT

    if _CHROMA_CLIENT is None:
        import chromadb

        os.makedirs(RAG_CHROMA_DIR, exist_ok=True)

        _CHROMA_CLIENT = chromadb.PersistentClient(
            path=RAG_CHROMA_DIR
        )

    return _CHROMA_CLIENT


# ============================================================
# TEXT FORMATTING
# ============================================================

def format_query_for_model(query: str, model_name: str = "") -> str:
    return query.strip()


def format_passage_for_model(text: str, model_name: str = "") -> str:
    return text.strip()


# ============================================================
# METADATA NORMALIZATION
# ============================================================

def normalize_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Preserve available document metadata.
    Never invent missing document titles, pages, or sources.
    """

    if not isinstance(metadata, dict):
        metadata = {}

    normalized = {}

    # Possible metadata fields used by document ingestion.
    field_aliases = {
        "title": ["title", "document_title"],
        "source": ["source", "source_file", "filename", "file_name"],
        "page": ["page", "page_number", "page_num"],
        "section": ["section", "chapter", "heading"],
        "crop": ["crop"],
        "source_url": ["source_url", "url"],
        "chunk_id": ["chunk_id", "id"],
    }

    for output_key, possible_keys in field_aliases.items():

        value = None

        for key in possible_keys:
            candidate = metadata.get(key)

            if candidate is not None and str(candidate).strip():
                value = candidate
                break

        if value is not None:
            normalized[output_key] = value

    return normalized


# ============================================================
# CHUNK DEDUPLICATION
# ============================================================

def deduplicate_chunks(
    chunks: List[Dict[str, Any]],
    jaccard_threshold: float = 0.70,
) -> List[Dict[str, Any]]:

    unique = []
    seen = set()

    for chunk in chunks:

        clean = chunk.get("text", "").strip()

        if not clean or clean in seen:
            continue

        words = set(clean.split())

        duplicate = False

        for existing in unique:

            other = set(existing["text"].split())

            if not words or not other:
                continue

            similarity = len(words & other) / len(words | other)

            if similarity >= jaccard_threshold:
                duplicate = True
                break

        if not duplicate:
            seen.add(clean)
            unique.append(chunk)

    return unique


# ============================================================
# AGRONOMIC DOCUMENT RETRIEVAL
# ============================================================

def retrieve(
    query: str,
    crop: Optional[str] = None,
    k: int = RAG_DEFAULT_TOP_K,
) -> List[Dict[str, Any]]:

    if not query or not query.strip():
        return []

    try:

        client = get_chroma_client()

        collections = [
            collection.name
            for collection in client.list_collections()
        ]

        if RAG_COLLECTION_NAME not in collections:
            return []

        collection = client.get_collection(
            name=RAG_COLLECTION_NAME
        )

        count = collection.count()

        if count == 0:
            return []

        vectorizer = get_vectorizer()

        query_embedding = vectorizer.transform(
            [query.strip()]
        ).toarray()[0].tolist()

        # Optional crop filter.
        where_filter = None

        if crop and crop.strip():
            where_filter = {
                "crop": crop.strip().lower()
            }

        search_count = max(1, min(int(k), count))

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=search_count,
            where=where_filter,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        documents = results.get("documents", [[]])[0] or []
        metadatas = results.get("metadatas", [[]])[0] or []
        distances = results.get("distances", [[]])[0] or []

        retrieved = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):

            if not document:
                continue

            # Keep the existing scoring behavior.
            score = max(0.0, 1.0 - float(distance))

            if score < RAG_SIMILARITY_THRESHOLD:
                continue

            metadata = metadata or {}

            normalized_metadata = normalize_metadata(metadata)

            original_text = metadata.get("original_text")

            text = (
                original_text.strip()
                if isinstance(original_text, str) and original_text.strip()
                else document.strip()
            )

            if not text:
                continue

            chunk = {
                "text": text,
                "score": round(score, 4),
                "title": normalized_metadata.get("title"),
                "source": normalized_metadata.get("source"),
                "page": normalized_metadata.get("page"),
                "section": normalized_metadata.get("section"),
                "crop": normalized_metadata.get("crop"),
                "source_url": normalized_metadata.get("source_url"),
                "chunk_id": normalized_metadata.get("chunk_id"),
            }

            retrieved.append(chunk)

        return deduplicate_chunks(retrieved)

    except Exception as error:

        sys.stderr.write(
            f"[rag_service] Retrieval error: {error}\n"
        )

        return []

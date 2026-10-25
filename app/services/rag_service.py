"""
RAG Service: Semantic Chunking + Multilingual Sentence Embeddings + ChromaDB Vector Store.

Architecture:
- Embedding Model: Multilingual sentence-transformers (configured via RAG_EMBEDDING_MODEL).
  Loaded once as a lazy singleton at startup.
- Document Representation: Contextual header prepended before embedding.
- Vector DB: Local persistent ChromaDB instance storing chunk embeddings, text, and metadata.
- Retrieval: Stable interface `retrieve(query, crop, k)` returning [{text, title, section, score}].
"""

import os
import sys
from typing import Any, Dict, List, Optional

from app.services.rag_config import (
    RAG_EMBEDDING_MODEL,
    RAG_CHROMA_DIR,
    RAG_COLLECTION_NAME,
    RAG_SIMILARITY_THRESHOLD,
    RAG_DEFAULT_TOP_K,
)

# Lazy singleton holders
_EMBEDDING_MODEL = None
_CHROMA_CLIENT = None


def get_embedding_model():
    """
    Lazy singleton loader for the sentence-transformers multilingual embedding model.
    Loads once on first use and persists in memory.
    Prefers local cached files to prevent network head requests and allow offline execution.
    """
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Try loading from local HuggingFace cache first for instant offline execution
            try:
                _EMBEDDING_MODEL = SentenceTransformer(RAG_EMBEDDING_MODEL, local_files_only=True)
            except Exception:
                _EMBEDDING_MODEL = SentenceTransformer(RAG_EMBEDDING_MODEL, local_files_only=False)
        except Exception as e:
            sys.stderr.write(f"[rag_service] Error loading embedding model '{RAG_EMBEDDING_MODEL}': {e}\n")
            raise
    return _EMBEDDING_MODEL


def get_chroma_client():
    """
    Lazy singleton loader for persistent ChromaDB client.
    """
    global _CHROMA_CLIENT
    if _CHROMA_CLIENT is None:
        try:
            import chromadb
            os.makedirs(RAG_CHROMA_DIR, exist_ok=True)
            _CHROMA_CLIENT = chromadb.PersistentClient(path=RAG_CHROMA_DIR)
        except Exception as e:
            sys.stderr.write(f"[rag_service] Error initializing ChromaDB at '{RAG_CHROMA_DIR}': {e}\n")
            raise
    return _CHROMA_CLIENT


def format_query_for_model(query: str, model_name: str = RAG_EMBEDDING_MODEL) -> str:
    """
    Applies the model-specific prefix if required (e.g. e5 models require 'query: ').
    """
    q = query.strip()
    if "e5" in model_name.lower() and not q.startswith("query:"):
        return f"query: {q}"
    return q


def format_passage_for_model(text: str, model_name: str = RAG_EMBEDDING_MODEL) -> str:
    """
    Applies the model-specific prefix for documents (e.g. e5 models require 'passage: ').
    """
    t = text.strip()
    if "e5" in model_name.lower() and not t.startswith("passage:"):
        return f"passage: {t}"
    return t


def deduplicate_chunks(chunks: List[Dict[str, Any]], jaccard_threshold: float = 0.70) -> List[Dict[str, Any]]:
    """
    Semantic chunk deduplication: ensures overlapping or duplicate chunks are not sent
    multiple times to the LLM context, saving tokens and preventing repetition.
    """
    unique_chunks: List[Dict[str, Any]] = []
    seen_texts = set()

    for c in chunks:
        clean_text = c.get("text", "").strip()
        if not clean_text or clean_text in seen_texts:
            continue

        words_new = set(clean_text.split())
        is_duplicate = False

        for existing in unique_chunks:
            words_exist = set(existing.get("text", "").split())
            if not words_exist or not words_new:
                continue
            intersection = len(words_new.intersection(words_exist))
            union = len(words_new.union(words_exist))
            jaccard = intersection / union if union > 0 else 0.0

            if (
                c.get("title") == existing.get("title")
                and c.get("section") == existing.get("section")
            ) or jaccard >= jaccard_threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            seen_texts.add(clean_text)
            unique_chunks.append(c)

    return unique_chunks


def retrieve(
    query: str,
    crop: Optional[str] = None,
    k: int = RAG_DEFAULT_TOP_K,
) -> List[Dict[str, Any]]:
    """
    Retrieves top-K relevant guideline passages from ChromaDB vector store.

    Stable Signature:
        retrieve(query: str, crop: str | None, k: int = 4) -> [{ text, title, section, score }]

    Args:
        query: Farmer or system query in Bangla, English, or mixed.
        crop: Optional crop name filter (e.g. 'Rice', 'Wheat').
        k: Maximum number of chunks to return (default 4).

    Returns:
        List of dicts: [ { 'text': str, 'title': str, 'section': str, 'score': float } ]
        Returns [] if no relevant chunks match or vector collection is empty/missing.
    """
    if not query or not query.strip():
        return []

    try:
        client = get_chroma_client()
        # Check if collection exists
        existing_collections = [c.name for c in client.list_collections()]
        if RAG_COLLECTION_NAME not in existing_collections:
            sys.stderr.write(
                f"[rag_service] Warning: Collection '{RAG_COLLECTION_NAME}' does not exist in ChromaDB. "
                f"Returning empty results. Run 'python -m app.scripts.build_rag_index' to build it.\n"
            )
            return []

        collection = client.get_collection(name=RAG_COLLECTION_NAME)
        if collection.count() == 0:
            sys.stderr.write(
                f"[rag_service] Warning: Collection '{RAG_COLLECTION_NAME}' is empty. Returning empty results.\n"
            )
            return []

        # Load embedding model and encode query with proper prefix & L2 normalization
        model = get_embedding_model()
        formatted_query = format_query_for_model(query)
        query_embedding = model.encode(
            formatted_query,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        # Build metadata filter if crop is specified
        where_filter = None
        if crop and crop.strip():
            clean_crop = crop.strip().lower()
            where_filter = {"crop": clean_crop}

        # Query ChromaDB collection
        # Note: ChromaDB collection uses cosine distance.
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, collection.count()),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved: List[Dict[str, Any]] = []
        for doc_text, meta, distance in zip(documents, metadatas, distances):
            # ChromaDB cosine distance d = 1 - cosine_similarity
            similarity_score = max(0.0, 1.0 - float(distance))

            # Drop results below configured threshold
            if similarity_score < RAG_SIMILARITY_THRESHOLD:
                continue

            # Retrieve original clean text (without the contextual header)
            original_text = meta.get("original_text") or doc_text
            title = meta.get("title", "কৃষি গবেষণা নির্দেশিকা")
            section = meta.get("section", "সাধারণ গাইডলাইন")

            retrieved.append({
                "text": original_text,
                "title": title,
                "section": section,
                "score": round(similarity_score, 4),
            })

        return deduplicate_chunks(retrieved)

    except Exception as e:
        sys.stderr.write(f"[rag_service] Error during retrieval: {e}\n")
        return []


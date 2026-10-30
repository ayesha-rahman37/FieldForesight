
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Lightweight multilingual character n-gram retrieval (no PyTorch)
RAG_EMBEDDING_MODEL = "sklearn-hashing-char"

RAG_CHROMA_DIR = os.getenv(
    "RAG_CHROMA_DIR",
    str(BASE_DIR / "app" / "data" / "chroma")
)
RAG_COLLECTION_NAME = os.getenv("RAG_COLLECTION_NAME", "knowledge")

DOCS_KNOWLEDGE_DIR = os.getenv(
    "DOCS_KNOWLEDGE_DIR",
    str(BASE_DIR / "docs" / "knowledge")
)

# Threshold for character n-gram cosine similarity
RAG_SIMILARITY_THRESHOLD = float(
    os.getenv("RAG_SIMILARITY_THRESHOLD", "0.05")
)
RAG_DEFAULT_TOP_K = int(os.getenv("RAG_DEFAULT_TOP_K", "4"))

RAG_SEMANTIC_SIMILARITY_SPLIT = 0.70
RAG_CHUNK_MIN_TOKENS = 40
RAG_CHUNK_MAX_TOKENS = 250
RAG_CHUNK_OVERLAP_SENTENCES = 1

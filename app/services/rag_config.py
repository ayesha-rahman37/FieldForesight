"""
RAG Configuration Module
Defines hyperparameters and directory paths for:
semantic chunking + multilingual sentence embeddings + ChromaDB vector store.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Multilingual sentence-embedding model (Bangla supported)
# Default: intfloat/multilingual-e5-small (lightweight XLM-RoBERTa based, strong Bangla retrieval)
# Requires 'query: ' and 'passage: ' prefixes.
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "intfloat/multilingual-e5-small")

# Vector DB storage path
RAG_CHROMA_DIR = os.getenv("RAG_CHROMA_DIR", str(BASE_DIR / "app" / "data" / "chroma"))
RAG_COLLECTION_NAME = os.getenv("RAG_COLLECTION_NAME", "knowledge")

# Corpus path
DOCS_KNOWLEDGE_DIR = os.getenv("DOCS_KNOWLEDGE_DIR", str(BASE_DIR / "docs" / "knowledge"))

# Retrieval settings
# Minimum cosine similarity threshold (0.0 to 1.0) to drop low-relevance results
# For multilingual-e5-small, relevant documents score >= 0.82, while out-of-domain queries score < 0.80.
RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.82"))
RAG_DEFAULT_TOP_K = int(os.getenv("RAG_DEFAULT_TOP_K", "4"))

# Semantic Chunking Hyperparameters
# Adjacent sentence similarity drop threshold below which a new chunk begins
RAG_SEMANTIC_SIMILARITY_SPLIT = float(os.getenv("RAG_SEMANTIC_SIMILARITY_SPLIT", "0.70"))
# Minimum words/tokens per chunk before allowing a semantic split
RAG_CHUNK_MIN_TOKENS = int(os.getenv("RAG_CHUNK_MIN_TOKENS", "40"))
# Hard maximum words/tokens per chunk
RAG_CHUNK_MAX_TOKENS = int(os.getenv("RAG_CHUNK_MAX_TOKENS", "250"))
# Sentence overlap between consecutive chunks within the same section
RAG_CHUNK_OVERLAP_SENTENCES = int(os.getenv("RAG_CHUNK_OVERLAP_SENTENCES", "1"))


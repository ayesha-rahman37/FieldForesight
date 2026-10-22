"""
Idempotent RAG Index Builder
Builds the ChromaDB vector database from knowledge documents in docs/knowledge/*.md.

Usage:
    python -m app.scripts.build_rag_index

Methodology:
    1. Parse YAML frontmatter (crop, source, topic, title).
    2. Heading-based markdown structural splitting.
    3. Multilingual sentence-level splitting (handling Bangla danda '।' and punctuation).
    4. Variable semantic chunking via sentence embeddings cosine similarity drops.
    5. Contextual header prepended before embedding.
    6. Idempotent ChromaDB rebuild at app/data/chroma (collection 'knowledge').
"""

import re
import glob
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np

from app.services.rag_config import (
    DOCS_KNOWLEDGE_DIR,
    RAG_CHROMA_DIR,
    RAG_COLLECTION_NAME,
    RAG_EMBEDDING_MODEL,
    RAG_SEMANTIC_SIMILARITY_SPLIT,
    RAG_CHUNK_MIN_TOKENS,
    RAG_CHUNK_MAX_TOKENS,
    RAG_CHUNK_OVERLAP_SENTENCES,
)
from app.services.rag_service import (
    get_embedding_model,
    get_chroma_client,
    format_passage_for_model,
)


def parse_frontmatter_and_body(content: str) -> Tuple[Dict[str, str], str]:
    """
    Extracts YAML-like frontmatter between '---' markers and returns (metadata, body).
    """
    metadata: Dict[str, str] = {}
    body = content

    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    if match:
        raw_meta = match.group(1)
        body = match.group(2).strip()
        for line in raw_meta.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, val = line.split(":", 1)
                metadata[key.strip().lower()] = val.strip().strip('"').strip("'")

    return metadata, body


def split_into_sections(markdown_text: str) -> List[Tuple[str, str]]:
    """
    Splits markdown body by headings (#, ##, ###).
    Returns list of tuples: (heading_title, section_text).
    """
    lines = markdown_text.splitlines()
    sections: List[Tuple[str, str]] = []
    current_heading = "ভূমিকা ও সাধারণ নির্দেশিকা"
    current_lines: List[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            if current_lines:
                sec_text = "\n".join(current_lines).strip()
                if sec_text:
                    sections.append((current_heading, sec_text))
                current_lines = []
            current_heading = stripped.lstrip("#").strip()
        else:
            current_lines.append(line)

    if current_lines:
        sec_text = "\n".join(current_lines).strip()
        if sec_text:
            sections.append((current_heading, sec_text))

    return sections


def split_into_sentences(text: str) -> List[str]:
    """
    Splits text into sentences supporting Bangla danda '।', '.', '?', '!'.
    Preserves punctuation with the sentence.
    """
    raw_sentences = re.split(r"(?<=[।?!.\n])\s+", text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    return sentences


def semantic_chunk_section(
    sentences: List[str],
    model: Any,
) -> List[str]:
    """
    Performs variable semantic chunking inside a section based on cosine similarity
    between adjacent sentence embeddings, enforcing min/max token boundaries.
    """
    if not sentences:
        return []

    # If small section, return as single chunk
    total_words = sum(len(s.split()) for s in sentences)
    if total_words <= RAG_CHUNK_MIN_TOKENS or len(sentences) <= 2:
        return [" ".join(sentences)]

    # Embed individual sentences to detect semantic shifts
    formatted_sentences = [format_passage_for_model(s) for s in sentences]
    sentence_embeddings = model.encode(
        formatted_sentences,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    chunks: List[str] = []
    current_chunk = [sentences[0]]
    current_token_count = len(sentences[0].split())

    for i in range(1, len(sentences)):
        next_sent = sentences[i]
        next_tokens = len(next_sent.split())

        # Cosine similarity between sentence i-1 and sentence i
        sim = float(np.dot(sentence_embeddings[i - 1], sentence_embeddings[i]))

        # Condition to split:
        # 1. Topic shift (similarity drops below threshold) AND minimum chunk size reached
        # 2. Hard max token limit exceeded
        should_split = False
        if current_token_count >= RAG_CHUNK_MIN_TOKENS and sim < RAG_SEMANTIC_SIMILARITY_SPLIT:
            should_split = True
        elif (current_token_count + next_tokens) > RAG_CHUNK_MAX_TOKENS:
            should_split = True

        if should_split:
            chunks.append(" ".join(current_chunk))
            # 1-sentence overlap if configured
            if RAG_CHUNK_OVERLAP_SENTENCES > 0 and current_chunk:
                current_chunk = [current_chunk[-1], next_sent]
                current_token_count = len(current_chunk[0].split()) + next_tokens
            else:
                current_chunk = [next_sent]
                current_token_count = next_tokens
        else:
            current_chunk.append(next_sent)
            current_token_count += next_tokens

    if current_chunk:
        # Merge tiny trailing fragment if safe
        if chunks and current_token_count < RAG_CHUNK_MIN_TOKENS:
            last_chunk = chunks[-1]
            merged = last_chunk + " " + " ".join(current_chunk)
            if len(merged.split()) <= RAG_CHUNK_MAX_TOKENS:
                chunks[-1] = merged
            else:
                chunks.append(" ".join(current_chunk))
        else:
            chunks.append(" ".join(current_chunk))

    return chunks


def build_rag_index():
    """
    Reads all docs/knowledge/*.md files, chunks them semantically,
    and idempotently populates the ChromaDB 'knowledge' collection.
    """
    print("=" * 60)
    print("FieldForesight RAG Index Builder")
    print(f"Embedding Model: {RAG_EMBEDDING_MODEL}")
    print(f"ChromaDB Path  : {RAG_CHROMA_DIR}")
    print(f"Collection     : {RAG_COLLECTION_NAME}")
    print(f"Corpus Dir     : {DOCS_KNOWLEDGE_DIR}")
    print("=" * 60)

    knowledge_path = Path(DOCS_KNOWLEDGE_DIR)
    if not knowledge_path.exists():
        print(f"[!] Knowledge directory {DOCS_KNOWLEDGE_DIR} does not exist. Creating empty directory.")
        knowledge_path.mkdir(parents=True, exist_ok=True)
        return

    md_files = sorted(glob.glob(str(knowledge_path / "*.md")))
    if not md_files:
        print("[!] No .md files found in docs/knowledge/. Index remains empty.")
        return

    print(f"Found {len(md_files)} knowledge markdown document(s).")

    print("[*] Loading embedding model (lazy singleton)...")
    model = get_embedding_model()

    print("[*] Initializing ChromaDB persistent client...")
    client = get_chroma_client()

    # Idempotent: Rebuild collection from scratch
    existing_collections = [c.name for c in client.list_collections()]
    if RAG_COLLECTION_NAME in existing_collections:
        print(f"[*] Removing existing '{RAG_COLLECTION_NAME}' collection...")
        client.delete_collection(name=RAG_COLLECTION_NAME)

    collection = client.create_collection(
        name=RAG_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"[+] Created fresh collection '{RAG_COLLECTION_NAME}' (cosine space).")

    all_ids: List[str] = []
    all_documents: List[str] = []
    all_metadatas: List[Dict[str, Any]] = []
    all_embeddings_input: List[str] = []

    total_chunks = 0
    crop_counts: Dict[str, int] = {}

    for file_path in md_files:
        doc_id = Path(file_path).stem
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        meta, body = parse_frontmatter_and_body(content)
        crop = meta.get("crop", "General").strip()
        source = meta.get("source", "Department of Agricultural Extension (DAE)").strip()
        topic = meta.get("topic", "").strip()

        # Extract title from frontmatter or first H1
        title = meta.get("title", "")
        if not title:
            first_h1 = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
            if first_h1:
                title = first_h1.group(1).strip()
            else:
                title = topic or doc_id

        sections = split_into_sections(body)
        doc_chunk_idx = 0

        for heading, sec_text in sections:
            sentences = split_into_sentences(sec_text)
            chunks = semantic_chunk_section(sentences, model)

            for chunk in chunks:
                original_text = chunk.strip()
                if not original_text:
                    continue

                # Contextual header: Prepend before embedding
                header = f"Document: {title} | Section: {heading} | Crop: {crop}"
                prefixed_chunk = f"{header}\n\n{original_text}"

                # Model format (passage: prefix for e5)
                embedding_input = format_passage_for_model(prefixed_chunk)

                chunk_id = f"{doc_id}_{doc_chunk_idx:03d}"
                doc_chunk_idx += 1
                total_chunks += 1
                crop_counts[crop] = crop_counts.get(crop, 0) + 1

                all_ids.append(chunk_id)
                all_documents.append(prefixed_chunk)
                all_embeddings_input.append(embedding_input)
                all_metadatas.append({
                    "crop": crop.lower(),
                    "crop_display": crop,
                    "source": source,
                    "topic": topic,
                    "title": title,
                    "section": heading,
                    "doc_id": doc_id,
                    "original_text": original_text,
                })

    if all_ids:
        print(f"[*] Generating multilingual normalized embeddings for {len(all_ids)} chunks...")
        embeddings = model.encode(
            all_embeddings_input,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=16,
        ).tolist()

        print("[*] Adding chunks to ChromaDB...")
        collection.add(
            ids=all_ids,
            embeddings=embeddings,
            documents=all_documents,
            metadatas=all_metadatas,
        )

        print("\n" + "=" * 60)
        print("RAG Index Build Complete!")
        print(f"Total Chunks Indexed: {total_chunks}")
        print("Crop Distribution:")
        for c, count in sorted(crop_counts.items()):
            print(f"  - {c}: {count} chunk(s)")
        print(f"ChromaDB Storage: {RAG_CHROMA_DIR}")
        print("=" * 60)
    else:
        print("[!] No chunks generated from documents.")


if __name__ == "__main__":
    build_rag_index()


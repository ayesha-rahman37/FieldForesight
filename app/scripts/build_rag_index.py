
import re
import glob
from pathlib import Path
from typing import Dict, List, Tuple

from app.services.rag_config import (
    DOCS_KNOWLEDGE_DIR,
    RAG_CHROMA_DIR,
    RAG_COLLECTION_NAME,
)

from app.services.rag_service import (
    get_chroma_client,
    get_vectorizer,
)


def parse_frontmatter_and_body(
    content: str
) -> Tuple[Dict[str, str], str]:

    metadata = {}
    body = content

    match = re.match(
        r"^---\s*\n(.*?)\n---\s*\n(.*)$",
        content,
        re.DOTALL
    )

    if match:
        body = match.group(2).strip()

        for line in match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = (
                    value.strip().strip('"').strip("'")
                )

    return metadata, body


def split_into_sections(
    markdown_text: str
) -> List[Tuple[str, str]]:

    sections = []
    heading = "General"
    lines = []

    for line in markdown_text.splitlines():
        stripped = line.strip()

        if stripped.startswith("#"):
            if lines:
                sections.append(
                    (heading, "\n".join(lines).strip())
                )
                lines = []

            heading = stripped.lstrip("#").strip()

        else:
            lines.append(line)

    if lines:
        sections.append(
            (heading, "\n".join(lines).strip())
        )

    return sections


def split_into_chunks(text: str) -> List[str]:

    sentences = re.split(
        r"(?<=[।?!.\n])\s+",
        text
    )

    chunks = []
    current = []
    word_count = 0

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        words = len(sentence.split())

        if current and word_count + words > 180:
            chunks.append(" ".join(current))
            current = []
            word_count = 0

        current.append(sentence)
        word_count += words

    if current:
        chunks.append(" ".join(current))

    return chunks


def build_rag_index():

    print("=" * 55)
    print("FieldForesight Lightweight RAG Index Builder")
    print("=" * 55)

    knowledge_path = Path(DOCS_KNOWLEDGE_DIR)

    if not knowledge_path.exists():
        print("ERROR: Knowledge directory not found.")
        return

    files = sorted(
        glob.glob(str(knowledge_path / "*.md"))
    )

    if not files:
        print("ERROR: No markdown documents found.")
        return

    client = get_chroma_client()

    existing = [
        c.name for c in client.list_collections()
    ]

    if RAG_COLLECTION_NAME in existing:
        client.delete_collection(
            name=RAG_COLLECTION_NAME
        )

    collection = client.create_collection(
        name=RAG_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    vectorizer = get_vectorizer()

    ids = []
    documents = []
    metadatas = []

    for file_path in files:

        doc_id = Path(file_path).stem

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            content = file.read()

        meta, body = parse_frontmatter_and_body(content)

        crop = meta.get("crop", "General").strip()
        source = meta.get(
            "source",
            "Department of Agricultural Extension (DAE)"
        ).strip()

        title = meta.get(
            "title",
            meta.get("topic", doc_id)
        )

        sections = split_into_sections(body)

        chunk_number = 0

        for heading, section_text in sections:

            chunks = split_into_chunks(section_text)

            for chunk in chunks:

                if not chunk.strip():
                    continue

                header = (
                    f"Document: {title} | "
                    f"Section: {heading} | Crop: {crop}"
                )

                document = f"{header}\n\n{chunk}"

                ids.append(
                    f"{doc_id}_{chunk_number:03d}"
                )

                documents.append(document)

                metadatas.append({
                    "crop": crop.lower(),
                    "crop_display": crop,
                    "source": source,
                    "title": title,
                    "section": heading,
                    "doc_id": doc_id,
                    "original_text": chunk,
                })

                chunk_number += 1

    if not documents:
        print("ERROR: No chunks generated.")
        return

    print(f"Documents: {len(files)}")
    print(f"Chunks: {len(documents)}")
    print("Generating character n-gram embeddings...")

    embeddings = vectorizer.transform(
        documents
    ).toarray().tolist()

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print("=" * 55)
    print("RAG INDEX BUILD SUCCESSFUL")
    print("Indexed chunks:", collection.count())
    print("Collection:", RAG_COLLECTION_NAME)
    print("Storage:", RAG_CHROMA_DIR)
    print("=" * 55)


if __name__ == "__main__":
    build_rag_index()

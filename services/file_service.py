import os
import json


def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)

    return chunks


def process_files(repo_path, tree):
    documents = []

    for item in tree:
        if item["type"] != "file":
            continue

        full_path = os.path.join(repo_path, item["path"])
        content = read_file(full_path)

        if not content:
            continue

        chunks = chunk_text(content)

        for i, chunk in enumerate(chunks):
            documents.append({
                "path": item["path"],
                "chunk_id": i,
                "content": chunk
            })

    return documents


def save_chunks_to_json(documents, output_path="chunks.json"):
    """
    Save structured chunks for inspection
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    print(f"✅ Chunks saved to {output_path}")
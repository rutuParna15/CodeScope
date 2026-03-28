from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def embed_text(text):
    """
    Generate embedding for single text
    """
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_documents(documents):
    """
    documents = [
        {"content": "...", "path": "...", "chunk_id": 0}
    ]
    """
    texts = [doc["content"] for doc in documents]

    embeddings = model.encode(texts, normalize_embeddings=True)

    results = []

    for i, emb in enumerate(embeddings):
        results.append({
            "content": documents[i]["content"],
            "path": documents[i]["path"],
            "chunk_id": documents[i].get("chunk_id", None),
            "keywords": documents[i].get("keywords", []),
            "embedding": emb.tolist()
        })

    return results
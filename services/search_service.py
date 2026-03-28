import numpy as np
from services.embedding_service import embed_text


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

#bm25 keyword scoring
def keyword_score(query, doc):
    score = 0
    for word in query.lower().split():
        if word in doc["content"].lower():
            score += 1
        if word in doc.get("keywords", []):
            score += 2
    return score

def search(query, embedded_docs, top_k=5):
    """
    query: string
    embedded_docs: [
        {
            "content": "...",
            "path": "...",
            "embedding": [...]
        }
    ]
    """
    query_embedding = embed_text(query)

    results = []

    for doc in embedded_docs:
        sim = cosine_similarity(query_embedding, doc["embedding"])
        keyword = keyword_score(query, doc)
        score = sim + 0.2 * keyword # hybrid search
        
        results.append({
            "score": float(score),
            "content": doc["content"],
            "path": doc["path"]
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:top_k]
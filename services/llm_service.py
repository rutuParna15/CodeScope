from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query, docs):
    """
    docs = top retrieved chunks
    """

    context = "\n\n".join([
        f"[{doc['path']}]\n{doc['content'][:500]}"
        for doc in docs
    ])

    prompt = f"""
You are an expert codebase analysis assistant.

Your job is to analyze a repository and answer ONLY using the provided context.

---------------------
CONTEXT:
{context}
---------------------

QUESTION:
{query}

---------------------
STRICT RULES:

1. ONLY use the given context.
2. DO NOT use outside knowledge.
3. If the answer is not clearly present in the context, respond:
   "Not found in repo"
4. IGNORE unrelated or nonsensical queries (e.g. cooking, jokes, random topics).
5. Focus on:
   - Code logic
   - API flow
   - Authentication
   - Data flow
   - File relationships
6. Be precise and technical (no fluff).

---------------------
OUTPUT FORMAT (STRICT JSON):

Return ONLY valid JSON. No explanation outside JSON.

{{
  "status": "ok" | "not_found" | "irrelevant",
  "answer": "clear explanation of how the system works",
  "relevant_files": [
    {{
      "path": "file path",
      "reason": "why this file is relevant"
    }}
  ],
  "key_points": [
    "important point 1",
    "important point 2"
  ]
}}

---------------------

RULES FOR STATUS:
- "ok" → answer found in context
- "not_found" → context does not contain answer
- "irrelevant" → question unrelated to codebase

---------------------

IMPORTANT:
- Output MUST be valid JSON
- Do NOT include markdown
- Do NOT include backticks
- Do NOT include extra text
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",  
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content
from flask import Blueprint, request, render_template, session
from services.repo_service import clone_and_tree
from services.ast_chunker import process_files
from services.embedding_service import embed_documents
from services.search_service import search
from services.llm_service import generate_answer
import os, json, re

routes = Blueprint("routes", __name__)

embedded_docs_store = {}
tree_store = {}

DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"

def _build(d):
    """Normalise a dict that came from the LLM."""
    status = d.get("status", "ok")
    answer = d.get("answer", "")
    if isinstance(answer, str):
        answer = answer.strip()
        # answer field itself might be a nested JSON string — unwrap once
        try:
            inner = json.loads(answer)
            if isinstance(inner, dict):
                return _build(inner)
        except (json.JSONDecodeError, ValueError):
            pass
    return {
        "status": status,
        "answer": answer,
        "relevant_files": d.get("relevant_files", []),
        "key_points": d.get("key_points", []),
    }

def _plain(text):
    return {"status": "ok", "answer": text, "relevant_files": [], "key_points": []}

def normalize_answer(raw):
    # Already a dict
    if isinstance(raw, dict):
        return _build(raw)

    if not isinstance(raw, str):
        return _plain(str(raw))

    text = raw.strip()

    # Strip markdown code fences: ```json ... ``` or ``` ... ```
    fence = re.match(r'^```(?:json)?\s*([\s\S]*?)\s*```$', text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()

    # Direct parse
    try:
        return _build(json.loads(text))
    except (json.JSONDecodeError, ValueError):
        pass

    # JSON object buried anywhere in the string (e.g. "...\n{...}")
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return _build(json.loads(match.group()))
        except (json.JSONDecodeError, ValueError):
            pass

    # Give up — treat as plain text answer
    return _plain(text)


# ── Routes ────────────────────────────────────────────────────────────────────

@routes.route("/", methods=["GET"])
def home():
    session.setdefault("chat_history", [])
    return render_template("index.html")


@routes.route("/process", methods=["POST"])
def process():
    repo_url = request.form.get("repo_url")

    repo_path, tree = clone_and_tree(repo_url)
    documents = process_files(repo_path, tree)
    embedded_docs_store[repo_url] = embed_documents(documents)
    tree_store[repo_url] = tree

    session["chat_history"] = []
    session["current_repo"] = repo_url
    session.modified = True

    return render_template(
        "index.html",
        tree=tree,
        repo_url=repo_url,
        chat_history=[],
        debug_mode=DEBUG_MODE,
    )


@routes.route("/search", methods=["POST"])
def search_route():
    query = request.form.get("query")
    repo_url = request.form.get("repo_url")

    docs = search(query, embedded_docs_store.get(repo_url, []))
    raw_answer = generate_answer(query, docs)
    answer = normalize_answer(raw_answer)       # always a clean dict

    history = session.get("chat_history", [])
    history.append({"question": query, "answer": answer})
    session["chat_history"] = history
    session.modified = True

    return render_template(
        "index.html",
        answer=answer,
        results=docs if DEBUG_MODE else [],
        repo_url=repo_url,
        tree=tree_store.get(repo_url),
        chat_history=history,
        debug_mode=DEBUG_MODE,
    )


@routes.route("/clear", methods=["POST"])
def clear():
    session["chat_history"] = []
    session.modified = True
    repo_url = request.form.get("repo_url")
    return render_template(
        "index.html",
        repo_url=repo_url,
        tree=tree_store.get(repo_url),
        chat_history=[],
        debug_mode=DEBUG_MODE,
    )
from flask import Blueprint, request, render_template, session
from services.repo_service import clone_and_tree
from services.ast_chunker import process_files
from services.embedding_service import embed_documents
from services.search_service import search
from services.llm_service import generate_answer
import os

routes = Blueprint("routes", __name__)

# temporary in-memory storage
embedded_docs_store = {}
tree_store = {}

# Set DEBUG_MODE = True to show retrieved chunks, False to hide in production
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"

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

    # Reset chat history when a new repo is loaded
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
    answer = generate_answer(query, docs)

    # Append to session chat history
    history = session.get("chat_history", [])
    history.append({
        "question": query,
        "answer": answer,
    })
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
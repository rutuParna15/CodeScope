# Codescope

A lightweight codebase question-answering web app built with Flask.

## 🚀 Overview

`Codescope` lets you:
- Clone a GitHub repo by URL
- Build a file tree index
- Process text and Python AST into chunks
- Embed chunks with **SentenceTransformers** (`BAAI/bge-small-en-v1.5`)
- Perform vector + keyword hybrid search
- Use **Groq** LLM (`llama-4-scout-17b-16e-instruct`) for natural language answers
- Show conversational QA with history, relevant files, and key points

## ✨ Features

- GitHub repo cloning from user-provided URL
- Directory tree previews in sidebar
- Python AST extraction (functions/classes)
- Fallback chunking for non-Python files
- Semantic retrieval + local ranked search
- Chat interface with question history and clear button
- Debug mode (`DEBUG_MODE=true`) shows matched chunks

## 🛠️ Requirements

- Python 3.10+
- Create `.env`:
  - `SECRET_KEY` (required)
  - `DEBUG_MODE` (optional, `true`/`false`)
  - `GROQ_API_KEY` (required for LLM answer generation)

- Dependencies in `requirements.txt`

## 📦 Install

```bash
cd d:/Engineering/Projects/whereis
python -m pip install -r requirements.txt
```

## ▶️ Run

```bash
set SECRET_KEY=your_secret_key
set GROQ_API_KEY=your_groq_api_key
set DEBUG_MODE=false
python app.py
```

Open http://127.0.0.1:5000

## 🧠 Usage

1. Paste GitHub repo URL in left panel and click **Load repository**.
2. Wait for indexing (Clone → parse → chunk → embed).
3. Ask a query in the input bar (e.g. "How does authentication flow work?").
4. View answer + relevant files + key points.
5. Use Clear chat to reset conversation.

## 📁 Code structure

- `app.py` – Flask app bootstrap
- `routes.py` – HTTP endpoints: `/`, `/process`, `/search`, `/clear`
- `services/repo_service.py` – clone + tree builder
- `services/ast_chunker.py` – AST chunking and text fallback
- `services/embedding_service.py` – SentenceEmbeddings
- `services/search_service.py` – cosine + keyword hybrid ranking
- `services/llm_service.py` – Groq call w/ strict JSON output
- `templates/index.html` – UI + CSS + JS interface

## ⚙️ Environment Variables

- `SECRET_KEY`: Flask session key (required)
- `DEBUG_MODE`: `true` for debugging and chunk output
- `GROQ_API_KEY`: API key for Groq model endpoint

## 🧪 Notes

- Repo clones into `repos/<repo_name>` folder.
- Re-clone is skipped if valid `.git` exists.
- Search embeds are cached in memory for each repo URL.

## 🎥 Demo

https://github.com/user-attachments/assets/cef0961d-b22e-417f-81a3-f3f117deea2b


> **Note:** If the video doesn't play, you can view the [raw file here](demo.mp4).


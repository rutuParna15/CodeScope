import ast
import os


def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


# ---------- TEXT CHUNKING (fallback) ----------
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


# ---------- AST CHUNKING (Python only) ----------
def get_source_segment(source, node):
    lines = source.splitlines()
    start = node.lineno - 1
    end = node.end_lineno
    return "\n".join(lines[start:end])


def parse_python_file(file_path, relative_path):
    source = read_file(file_path)
    if not source:
        return []

    try:
        tree = ast.parse(source)
    except Exception:
        return []

    chunks = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            content = get_source_segment(source, node)

            chunks.append({
                "type": "function",
                "name": node.name,
                "path": relative_path,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "content": content
            })

        elif isinstance(node, ast.ClassDef):
            content = get_source_segment(source, node)

            chunks.append({
                "type": "class",
                "name": node.name,
                "path": relative_path,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "content": content
            })

    return chunks


# ---------- MAIN PIPELINE ----------
def process_files(repo_path, tree):
    documents = []

    for item in tree:
        if item["type"] != "file":
            continue

        full_path = os.path.join(repo_path, item["path"])
        content = read_file(full_path)

        if not content:
            continue

        # 🔥 Python → AST
        if item["path"].endswith(".py"):
            chunks = parse_python_file(full_path, item["path"])

            # fallback if AST fails
            if not chunks:
                text_chunks = chunk_text(content)
                for i, chunk in enumerate(text_chunks):
                    documents.append({
                        "type": "text",
                        "path": item["path"],
                        "chunk_id": i,
                        "content": chunk
                    })
            else:
                documents.extend(chunks)

        # 🔥 Non-Python → TEXT fallback
        else:
            text_chunks = chunk_text(content)
            for i, chunk in enumerate(text_chunks):
                documents.append({
                    "type": "text",
                    "path": item["path"],
                    "chunk_id": i,
                    "content": chunk
                })

    return documents
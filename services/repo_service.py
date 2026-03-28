from git import Repo
import os
import shutil


def is_valid_repo(path):
    """
    Check if folder is a valid git repo
    """
    return os.path.exists(os.path.join(path, ".git"))


def clone_and_tree(repo_url, clone_dir="repos"):
    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir)

    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    repo_path = os.path.join(clone_dir, repo_name)

    tree = []

    try:
        print("Repo path:", repo_path)

        # 🔥 Fix: check valid repo instead of just folder
        if not is_valid_repo(repo_path):
            if os.path.exists(repo_path):
                print("⚠️ Removing invalid repo folder...")
                shutil.rmtree(repo_path)

            print(f"Cloning: {repo_url}")
            Repo.clone_from(repo_url, repo_path)
        else:
            print("✅ Repo already exists, skipping clone")

        # 🔹 build tree
        for root, dirs, files in os.walk(repo_path):
            level = root.replace(repo_path, "").count(os.sep)

            tree.append({
                "type": "folder",
                "name": os.path.basename(root),
                "level": level,
                "path": os.path.relpath(root, repo_path)
            })

            for file in files:
                tree.append({
                    "type": "file",
                    "name": file,
                    "level": level + 1,
                    "path": os.path.relpath(os.path.join(root, file), repo_path)
                })

        return repo_path, tree

    except Exception as e:
        print("❌ CLONE ERROR:", str(e))
        return None, []
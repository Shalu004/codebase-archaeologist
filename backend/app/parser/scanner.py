import os
import hashlib
from typing import List, Dict, Any, Tuple
from app.core.config import settings

DEFAULT_IGNORE_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", "coverage", ".cache",
    "vendor", "__pycache__", ".venv", "venv", ".idea", ".vscode", "out",
    "target", ".turbo"
}

DEFAULT_IGNORE_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".mp4", ".webm", ".mov",
    ".zip", ".tar", ".gz", ".7z", ".rar", ".exe", ".dll", ".so", ".dylib",
    ".pyc", ".pyo", ".lock", ".woff", ".woff2", ".ttf", ".eot", ".db", ".sqlite"
}

ENTRY_POINT_FILENAMES = {
    "index.ts", "index.tsx", "index.js", "index.jsx", "main.ts", "main.tsx", "main.js",
    "App.tsx", "App.js", "server.ts", "server.js", "app.ts", "app.js", "main.py",
    "page.tsx", "page.js", "route.ts", "route.js"
}

class FileScanner:
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def is_ignored(self, rel_path: str, is_dir: bool = False) -> bool:
        parts = rel_path.replace("\\", "/").split("/")
        for part in parts:
            if is_dir and part in DEFAULT_IGNORE_DIRS:
                return True
            if part in DEFAULT_IGNORE_DIRS:
                return True

        if not is_dir:
            _, ext = os.path.splitext(rel_path)
            if ext.lower() in DEFAULT_IGNORE_EXTS:
                return True
            if rel_path.endswith("package-lock.json") or rel_path.endswith("yarn.lock") or rel_path.endswith("pnpm-lock.yaml"):
                return True
        return False

    def get_language(self, ext: str) -> str:
        ext = ext.lower()
        mapping = {
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".json": "json",
            ".py": "python",
            ".css": "css",
            ".html": "html",
            ".md": "markdown",
            ".prisma": "prisma",
            ".sql": "sql",
            ".yaml": "yaml",
            ".yml": "yaml",
        }
        return mapping.get(ext, "unknown")

    def scan(self) -> List[Dict[str, Any]]:
        scanned_files = []

        for root, dirs, files in os.walk(self.root_dir):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if not self.is_ignored(os.path.relpath(os.path.join(root, d), self.root_dir), is_dir=True)]

            for file_name in files:
                full_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(full_path, self.root_dir).replace("\\", "/")

                if self.is_ignored(rel_path, is_dir=False):
                    continue

                size_bytes = os.path.getsize(full_path)
                if size_bytes > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                    continue  # Skip huge files

                line_count = 0
                file_hash = ""
                content = ""
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        line_count = len(content.splitlines())
                        file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                except Exception:
                    pass

                _, ext = os.path.splitext(file_name)
                language = self.get_language(ext)
                is_entry_point = file_name in ENTRY_POINT_FILENAMES or "router" in file_name.lower()

                scanned_files.append({
                    "full_path": full_path,
                    "relative_path": rel_path,
                    "extension": ext,
                    "language": language,
                    "size_bytes": size_bytes,
                    "line_count": line_count,
                    "file_hash": file_hash,
                    "is_entry_point": is_entry_point,
                    "content": content
                })

        return scanned_files

    @staticmethod
    def build_file_tree(scanned_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tree_map = {}
        root_nodes = []

        for f in scanned_files:
            parts = f["relative_path"].split("/")
            current_path = ""
            for i, part in enumerate(parts):
                parent_path = current_path
                current_path = f"{current_path}/{part}" if current_path else part
                is_file = (i == len(parts) - 1)

                if current_path not in tree_map:
                    node = {
                        "id": current_path,
                        "name": part,
                        "path": current_path,
                        "type": "file" if is_file else "directory",
                        "size": f["size_bytes"] if is_file else 0,
                        "line_count": f["line_count"] if is_file else 0,
                        "language": f["language"] if is_file else None,
                        "children": [] if not is_file else None
                    }
                    tree_map[current_path] = node

                    if parent_path:
                        if parent_path in tree_map and tree_map[parent_path]["children"] is not None:
                            tree_map[parent_path]["children"].append(node)
                    else:
                        root_nodes.append(node)

        return root_nodes

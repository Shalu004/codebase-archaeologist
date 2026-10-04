import os
import git
from datetime import datetime
from typing import List, Dict, Any, Optional

class GitAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo: Optional[git.Repo] = None
        try:
            if os.path.exists(os.path.join(repo_path, ".git")):
                self.repo = git.Repo(repo_path)
        except Exception:
            self.repo = None

    def has_git(self) -> bool:
        return self.repo is not None

    def get_commit_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.repo:
            return []

        commits_data = []
        try:
            for commit in list(self.repo.iter_commits(max_count=limit)):
                # Extract changed files stats
                stats = commit.stats.files
                changed_files = []
                for fname, stat_info in stats.items():
                    changed_files.append({
                        "file_path": fname,
                        "insertions": stat_info.get("insertions", 0),
                        "deletions": stat_info.get("deletions", 0),
                        "lines": stat_info.get("lines", 0)
                    })

                commit_time = datetime.fromtimestamp(commit.committed_date)
                commits_data.append({
                    "commit_hash": commit.hexsha,
                    "author_name": commit.author.name,
                    "author_email": commit.author.email,
                    "message": commit.message.strip(),
                    "timestamp": commit_time.isoformat(),
                    "parents": [p.hexsha for p in commit.parents],
                    "changed_files": changed_files
                })
        except Exception:
            pass

        return commits_data

    def get_commit_diff(self, commit_hash: str) -> Dict[str, Any]:
        if not self.repo:
            return {"error": "Git repository metadata not available."}

        try:
            commit = self.repo.commit(commit_hash)
            parent = commit.parents[0] if commit.parents else git.NULL_TREE
            diffs = parent.diff(commit, create_patch=True)

            patch_data = []
            for d in diffs:
                patch_text = ""
                if d.diff:
                    patch_text = d.diff.decode("utf-8", errors="ignore")
                patch_data.append({
                    "a_path": d.a_path,
                    "b_path": d.b_path,
                    "change_type": d.change_type,
                    "patch": patch_text
                })

            return {
                "commit_hash": commit.hexsha,
                "author": commit.author.name,
                "message": commit.message.strip(),
                "timestamp": datetime.fromtimestamp(commit.committed_date).isoformat(),
                "diffs": patch_data
            }
        except Exception as e:
            return {"error": str(e)}

    def build_evolution_timeline(self, limit: int = 30) -> List[Dict[str, Any]]:
        commits = self.get_commit_history(limit=limit)
        if not commits:
            # Generate synthesized initial milestone for ZIP repos without git history
            return [
                {
                    "milestone_id": "m1",
                    "title": "Initial Repository Codebase Ingestion",
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "summary": "Full repository source snapshot imported and parsed into interactive knowledge map.",
                    "commit_hash": "HEAD",
                    "author": "Codebase Archaeologist",
                    "changed_files_count": 0
                }
            ]

        # Reverse chronological to chronological milestones
        timeline = []
        for i, c in enumerate(reversed(commits)):
            title = c["message"].split("\n")[0]
            timeline.append({
                "milestone_id": f"m{i+1}",
                "title": title[:80],
                "date": c["timestamp"].split("T")[0],
                "summary": c["message"],
                "commit_hash": c["commit_hash"],
                "author": c["author_name"],
                "changed_files_count": len(c["changed_files"])
            })

        return timeline

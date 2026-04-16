# app/storage/manager.py
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class StorageManager:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.recordings_dir = base_dir / "recordings"
        self.summaries_dir = base_dir / "summaries"
        self.clusters_dir = base_dir / "clusters"
        self.index_file = base_dir / "index.json"

    def init_dirs(self):
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        self.clusters_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_file.exists():
            self.index_file.write_text(json.dumps({"meetings": []}))

    def save_meeting(self, meeting: Dict):
        data = json.loads(self.index_file.read_text())
        data["meetings"].append(meeting)
        self.index_file.write_text(
            json.dumps(data, default=str, ensure_ascii=False, indent=2)
        )

    def list_meetings(self) -> List[Dict]:
        if not self.index_file.exists():
            return []
        data = json.loads(self.index_file.read_text())
        return data.get("meetings", [])

    def get_meeting(self, meeting_id: str) -> Optional[Dict]:
        meetings = self.list_meetings()
        for m in meetings:
            if m["id"] == meeting_id:
                return m
        return None

    def update_meeting(self, meeting_id: str, updates: Dict):
        data = json.loads(self.index_file.read_text())
        for i, m in enumerate(data["meetings"]):
            if m["id"] == meeting_id:
                data["meetings"][i].update(updates)
                break
        self.index_file.write_text(
            json.dumps(data, default=str, ensure_ascii=False, indent=2)
        )

    def save_summary(self, meeting_id: str, content: str) -> Path:
        path = self.summaries_dir / f"{meeting_id}.md"
        path.write_text(content, encoding="utf-8")
        return path

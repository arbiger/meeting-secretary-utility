# tests/test_storage.py
import json
import tempfile
from pathlib import Path
from app.storage.manager import StorageManager


def test_storage_manager_init(tmp_path):
    manager = StorageManager(base_dir=tmp_path)
    assert manager.index_file == tmp_path / "index.json"


def test_storage_manager_save_meeting(tmp_path):
    manager = StorageManager(base_dir=tmp_path)
    manager.init_dirs()
    manager.save_meeting(
        {
            "id": "2026-04-16_1400_test",
            "title": "Test Meeting",
            "date": "2026-04-16",
            "time": "14:00",
            "clusters": ["General"],
            "status": "completed",
        }
    )
    data = json.loads(manager.index_file.read_text())
    assert data["meetings"][0]["id"] == "2026-04-16_1400_test"


def test_storage_manager_list_meetings(tmp_path):
    manager = StorageManager(base_dir=tmp_path)
    manager.init_dirs()
    manager.save_meeting(
        {
            "id": "m1",
            "title": "A",
            "date": "2026-04-16",
            "time": "14:00",
            "clusters": [],
            "status": "completed",
        }
    )
    manager.save_meeting(
        {
            "id": "m2",
            "title": "B",
            "date": "2026-04-16",
            "time": "15:00",
            "clusters": [],
            "status": "completed",
        }
    )
    meetings = manager.list_meetings()
    assert len(meetings) == 2

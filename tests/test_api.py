# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_upload_recording_success(tmp_path, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "meetings_dir", tmp_path)
    from app.storage.manager import StorageManager

    manager = StorageManager(tmp_path)
    manager.init_dirs()

    files = {"file": ("test.m4a", b"fake audio data", "audio/m4a")}
    response = client.post("/api/recordings/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "meeting_id" in data
    assert data["status"] == "pending"


def test_list_meetings_empty(tmp_path, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "meetings_dir", tmp_path)
    response = client.get("/api/meetings")
    assert response.status_code == 200
    assert response.json() == []

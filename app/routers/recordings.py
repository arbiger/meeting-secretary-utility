# app/routers/recordings.py
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path

from app.storage.manager import StorageManager
from app.config import settings

router = APIRouter(prefix="/api/recordings", tags=["recordings"])


def get_storage() -> StorageManager:
    return StorageManager(settings.meetings_dir)


@router.post("/upload")
async def upload_recording(file: UploadFile = File(...)):
    """
    Upload audio file. Returns meeting_id for tracking.
    """
    storage = get_storage()
    storage.init_dirs()

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in [".m4a", ".mp3", ".wav", ".m4a"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    meeting_id = f"{datetime.now().strftime('%Y-%m-%d_%H%M')}_{uuid.uuid4().hex[:8]}"
    recording_path = storage.recordings_dir / f"{meeting_id}{ext}"

    with open(recording_path, "wb") as f:
        content = await file.read()
        f.write(content)

    meeting = {
        "id": meeting_id,
        "title": f"Recording_{meeting_id}",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "clusters": [],
        "recording_path": str(recording_path),
        "summary_path": "",
        "status": "pending",
        "created_at": datetime.now(),
    }
    storage.save_meeting(meeting)

    return {
        "meeting_id": meeting_id,
        "status": "pending",
        "recording_path": str(recording_path),
    }


@router.get("/{meeting_id}/download")
async def download_recording(meeting_id: str):
    """Download original audio file."""
    storage = get_storage()
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    recording_path = Path(meeting["recording_path"])
    if not recording_path.exists():
        raise HTTPException(status_code=404, detail="Recording file not found")

    return {"recording_path": str(recording_path)}

# app/routers/meetings.py
from fastapi import APIRouter, HTTPException
from typing import List
from pathlib import Path

from app.storage.manager import StorageManager
from app.config import settings

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


def get_storage() -> StorageManager:
    return StorageManager(settings.meetings_dir)


@router.get("")
async def list_meetings() -> List[dict]:
    """List all meetings."""
    storage = get_storage()
    return storage.list_meetings()


@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str):
    """Get meeting details."""
    storage = get_storage()
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    summary_path = meeting.get("summary_path")
    if summary_path and Path(summary_path).exists():
        meeting["summary_content"] = Path(summary_path).read_text(encoding="utf-8")
    else:
        meeting["summary_content"] = None

    return meeting


@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: str):
    """Delete meeting and associated files."""
    storage = get_storage()
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    recording_path = Path(meeting.get("recording_path", ""))
    if recording_path.exists():
        recording_path.unlink()

    summary_path = Path(meeting.get("summary_path", ""))
    if summary_path.exists():
        summary_path.unlink()

    data = storage.list_meetings()
    data = [m for m in data if m["id"] != meeting_id]
    storage.index_file.write_text(
        '{"meetings": '
        + __import__("json").dumps(data, default=str, ensure_ascii=False, indent=2)[13:]
    )

    return {"deleted": meeting_id}


@router.get("/clusters")
async def list_clusters():
    """List all clusters."""
    storage = get_storage()
    meetings = storage.list_meetings()
    clusters = set()
    for m in meetings:
        for c in m.get("clusters", []):
            clusters.add(c)
    return {"clusters": sorted(list(clusters))}

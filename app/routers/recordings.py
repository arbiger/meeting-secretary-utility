# app/routers/recordings.py
import os
import uuid
import asyncio
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
    Automatically triggers AI analysis after upload.
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

    asyncio.create_task(run_analysis(meeting_id))

    return {
        "meeting_id": meeting_id,
        "status": "pending",
        "recording_path": str(recording_path),
    }


async def run_analysis(meeting_id: str):
    """Background task to run AI analysis."""
    from app.services.transcriber import TranscriberService
    from app.services.analyzer import AnalyzerService
    import tempfile
    import shutil

    storage = get_storage()
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        return

    storage.update_meeting(meeting_id, {"status": "processing"})
    recording_path = meeting["recording_path"]

    temp_dir = Path(tempfile.mkdtemp())
    try:
        transcriber = TranscriberService()
        chunks = transcriber.chunk_audio(recording_path, temp_dir)
        if not chunks:
            storage.update_meeting(meeting_id, {"status": "failed"})
            return

        transcript = transcriber.transcribe_chunks(chunks)
        if not transcript.strip():
            storage.update_meeting(meeting_id, {"status": "failed"})
            return

        analyzer = AnalyzerService()
        result = analyzer.analyze(transcript)

        summary_path = storage.save_summary(meeting_id, result.markdown_content)

        clusters = [
            c.strip().replace(" ", "_").replace("/", "_") for c in result.clusters
        ]
        for cluster in clusters:
            cluster_path = storage.clusters_dir / cluster
            cluster_path.mkdir(exist_ok=True)
            symlink_path = cluster_path / f"{meeting_id}.md"
            if symlink_path.exists():
                symlink_path.unlink()
            os.symlink(os.path.relpath(summary_path, cluster_path), symlink_path)

        storage.update_meeting(
            meeting_id,
            {
                "title": result.title,
                "clusters": result.clusters,
                "summary_path": str(summary_path),
                "status": "completed",
            },
        )
    except Exception as e:
        storage.update_meeting(meeting_id, {"status": "failed"})
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


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

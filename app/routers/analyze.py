# app/routers/analyze.py
import tempfile
import shutil
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.storage.manager import StorageManager
from app.services.transcriber import TranscriberService
from app.services.analyzer import AnalyzerService
from app.config import settings

router = APIRouter(prefix="/internal", tags=["internal"])


def get_storage():
    return StorageManager(settings.meetings_dir)


@router.post("/analyze")
async def analyze_meeting(meeting_id: str):
    """
    Internal endpoint: analyze a recording and generate summary.
    """
    storage = get_storage()
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    storage.update_meeting(meeting_id, {"status": "processing"})

    recording_path = meeting["recording_path"]
    if not recording_path:
        raise HTTPException(status_code=400, detail="No recording path")

    temp_dir = Path(tempfile.mkdtemp())
    try:
        transcriber = TranscriberService()
        chunks = transcriber.chunk_audio(recording_path, temp_dir)
        if not chunks:
            storage.update_meeting(meeting_id, {"status": "failed"})
            raise HTTPException(status_code=500, detail="Audio conversion failed")

        transcript = transcriber.transcribe_chunks(chunks)
        if not transcript.strip():
            storage.update_meeting(meeting_id, {"status": "failed"})
            raise HTTPException(status_code=500, detail="Transcription returned empty")

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
            import os

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

        return {"meeting_id": meeting_id, "status": "completed", "title": result.title}

    except HTTPException:
        raise
    except Exception as e:
        storage.update_meeting(meeting_id, {"status": "failed"})
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# app/services/transcriber.py
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List
import requests

from app.config import settings


class TranscriberService:
    def __init__(self):
        self.asr_url = settings.asr_url
        self.asr_model = settings.asr_model

    def chunk_audio(self, input_path: Path, temp_dir: Path) -> List[Path]:
        """Convert audio to 16kHz WAV and split into 10-minute chunks."""
        temp_dir.mkdir(parents=True, exist_ok=True)
        try:
            cmd = [
                "/opt/homebrew/bin/ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-ar",
                "16000",
                "-ac",
                "1",
                "-acodec",
                "pcm_s16le",
                "-f",
                "segment",
                "-segment_time",
                "600",
                str(temp_dir / "chunk_%03d.wav"),
            ]
            subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            return sorted(list(temp_dir.glob("chunk_*.wav")))
        except Exception as e:
            print(f"Audio conversion failed: {e}")
            return []

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file via VibeVoice-ASR."""
        with open(audio_path, "rb") as f:
            files = {"file": ("chunk.wav", f, "audio/wav")}
            data = {
                "model": self.asr_model,
                "language": "zh",
            }
            response = requests.post(self.asr_url, files=files, data=data, timeout=600)
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list):
                return self._format_vibevoice_output(result)
            return result.get("text", "")

    def _format_vibevoice_output(self, segments: list) -> str:
        """Format VibeVoice-ASR output with speaker labels."""
        lines = []
        for seg in segments:
            speaker = seg.get("Speaker", 0)
            content = seg.get("Content", "")
            start = seg.get("Start", 0)
            end = seg.get("End", 0)
            if (
                content
                and not content.startswith("[")
                and content != "[Noise]"
                and content != "[Environmental Sounds]"
            ):
                lines.append(f"[{start:.1f}-{end:.1f}] Speaker {speaker}: {content}")
        return "\n".join(lines)

    def transcribe_chunks(self, chunks: List[Path]) -> str:
        """Transcribe multiple chunks and concatenate results."""
        transcript = ""
        for chunk in chunks:
            transcript += self.transcribe(chunk) + "\n"
        return transcript.strip()

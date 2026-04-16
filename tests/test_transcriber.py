# tests/test_transcriber.py
import pytest
from app.services.transcriber import TranscriberService


def test_transcriber_chunk_audio(tmp_path):
    service = TranscriberService()
    result = service.chunk_audio(tmp_path / "test.m4a", tmp_path)
    assert isinstance(result, list)

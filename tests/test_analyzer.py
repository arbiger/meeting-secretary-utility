# tests/test_analyzer.py
from app.services.analyzer import AnalyzerService
from app.models.meeting import AnalysisResult


def test_analyzer_format_prompt():
    service = AnalyzerService()
    prompt = service._build_prompt("Test transcript content")
    assert "transcript" in prompt
    assert len(prompt) > 100

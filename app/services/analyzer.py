# app/services/analyzer.py
import json
import requests

from app.config import settings
from app.models.meeting import AnalysisResult


class AnalyzerService:
    def __init__(self):
        self.llm_url = settings.llm_url
        self.llm_model = settings.llm_model

    def _build_prompt(self, transcript: str) -> str:
        return f"""You are an expert executive secretary. I will provide you with a meeting transcript.
Please perform the following tasks:
1. Identify participants based on context.
2. Provide a concise summary of discussions and decisions.
3. Extract TODOs with assignees.
4. Suggest 1 to 3 "Cluster Tags" for categorization (e.g., Marketing, Backend, Design).
5. Provide a short descriptive title.

Transcript:
{transcript}

Return the result as a JSON object:
{{
    "title": "...",
    "clusters": ["..."],
    "markdown_content": "# ...\\n\\n..."
}}
"""

    def analyze(self, transcript: str) -> AnalysisResult:
        """Analyze transcript via LLM and return structured result."""
        prompt = self._build_prompt(transcript)
        try:
            response = requests.post(
                self.llm_url,
                json={
                    "model": self.llm_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
                timeout=300,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            data = json.loads(content)
            return AnalysisResult(
                title=data.get("title", "Untitled"),
                clusters=data.get("clusters", []),
                markdown_content=data.get("markdown_content", ""),
            )
        except Exception as e:
            return AnalysisResult(
                title="Analysis Failed",
                clusters=["Unanalyzed"],
                markdown_content=f"# Analysis Error\n\n{str(e)}\n\n---\n\n## Transcript\n\n{transcript}",
            )

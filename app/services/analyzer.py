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
        return f"""你是一位專業的行政助理。我會提供你一段會議錄音逐字稿。
請執行以下任務：
1. 根據內容識別與會者身份。
2. 提供簡潔的討論摘要和決議。
3. 擷取待辦事項及其負責人。
4. 建議 1 到 3 個「分類標籤」用於分類（例如：行銷、後端、設計）。
5. 提供一個簡短描述性標題。

請用「繁體中文」回覆所有內容（包括標題、摘要、待辦事項等）。

逐字稿：
{transcript}

請回傳 JSON 格式：
{{
    "title": "...",
    "clusters": ["..."],
    "markdown_content": "# ...\n\n..."
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
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            data = json.loads(content)
            markdown = data.get("markdown_content", "")
            markdown_with_transcript = f"{markdown}\n\n---\n\n## 原始錄音文字 (Full Transcript)\n\n{transcript}"
            return AnalysisResult(
                title=data.get("title", "Untitled"),
                clusters=data.get("clusters", []),
                markdown_content=markdown_with_transcript,
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            return AnalysisResult(
                title="Analysis Failed",
                clusters=["Unanalyzed"],
                markdown_content=f"# Analysis Error\n\n{str(e)}\n\n---\n\n## Transcript\n\n{transcript}",
            )

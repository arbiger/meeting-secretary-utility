# mcp/server.py
# Note: This requires Python 3.10+ and fastmcp package
# Install with: pip install fastmcp
import requests
from pathlib import Path
from datetime import datetime

try:
    from mcp.server.fastmcp import FastMCP

    FASTAPI_URL = "http://127.0.0.1:6076"

    mcp = FastMCP("Meeting Secretary MCP")

    @mcp.tool()
    def list_meetings() -> str:
        """List all meetings."""
        try:
            response = requests.get(f"{FASTAPI_URL}/api/meetings", timeout=10)
            response.raise_for_status()
            meetings = response.json()
            if not meetings:
                return "No meetings found."
            return "\n".join(
                [f"- {m['date']} {m['time']} | {m['title']}" for m in meetings]
            )
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def get_summary(meeting_id: str) -> str:
        """Get summary content of a meeting."""
        try:
            response = requests.get(
                f"{FASTAPI_URL}/api/meetings/{meeting_id}", timeout=10
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("summary_content", "No summary")
            return content
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def analyze_meeting(filePath: str) -> str:
        """Analyze a meeting audio file."""
        try:
            from app.storage.manager import StorageManager
            from app.config import settings

            storage = StorageManager(settings.meetings_dir)
            storage.init_dirs()

            meeting_id = f"manual_{Path(filePath).stem}"
            ext = Path(filePath).suffix
            recording_path = storage.recordings_dir / f"{meeting_id}{ext}"
            import shutil

            shutil.copy(filePath, recording_path)

            meeting = {
                "id": meeting_id,
                "title": f"Manual_{meeting_id}",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M"),
                "clusters": [],
                "recording_path": str(recording_path),
                "summary_path": "",
                "status": "pending",
                "created_at": datetime.now(),
            }
            storage.save_meeting(meeting)

            response = requests.post(
                f"{FASTAPI_URL}/internal/analyze?meeting_id={meeting_id}", timeout=1
            )
            return f"Started analysis for {meeting_id}. Use get_summary('{meeting_id}') to check result."
        except Exception as e:
            return f"Error: {str(e)}"

    if __name__ == "__main__":
        mcp.run()

except ImportError:
    print("Error: fastmcp package required for MCP server")
    print("Install with: pip install fastmcp (requires Python 3.10+)")
    print("\nAlternative: Run FastAPI server and use HTTP tools directly")

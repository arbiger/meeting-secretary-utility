# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.routers import recordings, meetings, analyze
from app.config import settings
from app.storage.manager import StorageManager

app = FastAPI(title="Meeting Secretary Service")

app.include_router(recordings.router)
app.include_router(meetings.router)
app.include_router(analyze.router)

storage = StorageManager(settings.meetings_dir)
storage.init_dirs()

web_dir = Path(__file__).parent.parent / "web"
if web_dir.exists():
    app.mount("/web", StaticFiles(directory=str(web_dir)), name="web")

    @app.get("/")
    async def root():
        return FileResponse(str(web_dir / "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.port)

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class MeetingBase(BaseModel):
    title: str
    clusters: List[str] = []


class MeetingCreate(MeetingBase):
    pass


class Meeting(MeetingBase):
    id: str
    date: str
    time: str
    recording_path: str
    summary_path: str
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = datetime.now()


class MeetingResponse(BaseModel):
    id: str
    title: str
    date: str
    time: str
    clusters: List[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisResult(BaseModel):
    title: str
    clusters: List[str]
    markdown_content: str

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: Optional[str] = None
    tags: Optional[str] = None
    folder: Optional[str] = "General"

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AISummaryRequest(BaseModel):
    text: str

class AIFlashcardsRequest(BaseModel):
    text: str

class AISummaryResponse(BaseModel):
    summary: str

class AIFlashcardsResponse(BaseModel):
    flashcards: list[str]

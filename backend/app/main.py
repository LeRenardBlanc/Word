from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os
from . import crud, models, schemas, database, search, ai
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)
search.init_index()

from fastapi import APIRouter

app = FastAPI(title="Smart Note-taking App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

api_router = APIRouter()

@api_router.post("/notes/", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = crud.create_note(db=db, note=note)
    search.add_to_index(db_note.id, db_note.title, db_note.content or "")
    return db_note

@api_router.get("/notes/", response_model=List[schemas.Note])
def read_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notes = crud.get_notes(db, skip=skip, limit=limit)
    return notes

@api_router.get("/notes/{note_id}", response_model=schemas.Note)
def read_note(note_id: int, db: Session = Depends(get_db)):
    db_note = crud.get_note(db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

@api_router.put("/notes/{note_id}", response_model=schemas.Note)
def update_note(note_id: int, note: schemas.NoteUpdate, db: Session = Depends(get_db)):
    db_note = crud.update_note(db, note_id, note)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    search.update_index(db_note.id, db_note.title, db_note.content or "")
    return db_note

@api_router.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = crud.delete_note(db, note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"ok": True}

@api_router.get("/folders/")
def get_folders(db: Session = Depends(get_db)):
    # Crude way to get unique folders
    notes = crud.get_notes(db)
    folders = set(n.folder for n in notes if n.folder)
    return {"folders": list(folders)}

@api_router.get("/tags/")
def get_tags(db: Session = Depends(get_db)):
    notes = crud.get_notes(db)
    tags = set()
    for n in notes:
        if n.tags:
            for t in n.tags.split(','):
                tags.add(t.strip())
    return {"tags": list(tags)}

@api_router.get("/search/")
def search_notes(q: str):
    return search.search_index(q)

@api_router.post("/ai/summarize", response_model=schemas.AISummaryResponse)
def summarize(request: schemas.AISummaryRequest):
    summary = ai.summarize_text(request.text)
    return {"summary": summary}

@api_router.post("/ai/flashcards", response_model=schemas.AIFlashcardsResponse)
def flashcards(request: schemas.AIFlashcardsRequest):
    cards = ai.generate_flashcards(request.text)
    return {"flashcards": cards}

app.include_router(api_router, prefix="/api")
# Also include without prefix for direct backend usage during dev if needed, or better, stick to one.
# But existing tests might rely on no prefix.
# Let's see... `backend/tests/test_main.py` uses `/notes/`.
# So I should include it twice or update tests?
# Updating tests is better but duplicate router is easier for now to support both (though slightly messy).
# Actually, I'll just include it twice for compatibility with dev/test and prod build.
app.include_router(api_router)

# Mount static files (Frontend)
# We expect the frontend build to be in ../frontend/dist relative to this file
# But for the executable, we might place it differently.
# We'll check a few common locations.

frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
print(f"Frontend dist path: {os.path.abspath(frontend_dist)}")
if not os.path.exists(frontend_dist):
    # Try looking in current directory (for when running as executable if bundled there)
    frontend_dist = "frontend/dist"
    print(f"Frontend dist path (fallback): {os.path.abspath(frontend_dist)}")

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    # Catch-all for React Router
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
         # If it's an API call that 404s, return 404
         if request.url.path.startswith("/api") or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
             return JSONResponse(status_code=404, content={"detail": "Not found"})

         if os.path.exists(os.path.join(frontend_dist, "index.html")):
            return FileResponse(os.path.join(frontend_dist, "index.html"))
         return JSONResponse(status_code=404, content={"detail": "Not found"})

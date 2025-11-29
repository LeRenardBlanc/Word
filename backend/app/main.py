from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os
import time
from . import crud, models, schemas, database, search, ai, export
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

models.Base.metadata.create_all(bind=database.engine)
search.init_index()

app = FastAPI(title="Smart Note-taking App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

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
    search.delete_from_index(note_id)
    return {"ok": True}

@api_router.get("/notes/{note_id}/export")
def export_note(note_id: int, format: str = Query(..., regex="^(pdf|docx|txt|md)$"), db: Session = Depends(get_db)):
    db_note = crud.get_note(db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    try:
        if format == "pdf":
            file_path = export.export_to_pdf(db_note)
            media_type = "application/pdf"
            filename = f"{db_note.title}.pdf"
        elif format == "docx":
            file_path = export.export_to_docx(db_note)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"{db_note.title}.docx"
        elif format == "md":
            file_path = export.export_to_md(db_note)
            media_type = "text/markdown"
            filename = f"{db_note.title}.md"
        else: # txt
            file_path = export.export_to_txt(db_note)
            media_type = "text/plain"
            filename = f"{db_note.title}.txt"
            
        return FileResponse(file_path, media_type=media_type, filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

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

# --- AI Endpoints ---

@api_router.post("/ai/summarize", response_model=schemas.AISummaryResponse)
def summarize(request: schemas.AISummaryRequest):
    summary = ai.summarize_text(request.text)
    return {"summary": summary}

@api_router.post("/ai/flashcards", response_model=schemas.AIFlashcardsResponse)
def flashcards(request: schemas.AIFlashcardsRequest):
    cards = ai.generate_flashcards(request.text)
    return {"flashcards": cards}

@api_router.post("/ai/autocorrect", response_model=schemas.AIAutocorrectResponse)
def autocorrect(request: schemas.AIAutocorrectRequest):
    corrected = ai.autocorrect_text(request.text)
    return {"corrected_text": corrected}

@api_router.post("/ai/autocomplete", response_model=schemas.AIAutocompleteResponse)
def autocomplete(request: schemas.AIAutocompleteRequest):
    if request.smart:
        # Use LLM for sentence completion
        completion = ai.smart_completion(request.text)
        return {"suggestions": [], "completion": completion}
    else:
        # Use Spellchecker for word completion
        suggestions = ai.autocomplete_text(request.text)
        return {"suggestions": suggestions, "completion": None}

@api_router.post("/ai/abbreviations", response_model=schemas.AIAbbreviationResponse)
def abbreviations(request: schemas.AIAbbreviationRequest):
    abbrs = ai.detect_abbreviations(request.text)
    return {"abbreviations": abbrs}

app.include_router(api_router, prefix="/api")
app.include_router(api_router)

# Mount static files (Frontend)
frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if not os.path.exists(frontend_dist):
    frontend_dist = "frontend/dist"

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
         if request.url.path.startswith("/api") or request.url.path.startswith("/docs"):
             return JSONResponse(status_code=404, content={"detail": "Not found"})
         if os.path.exists(os.path.join(frontend_dist, "index.html")):
            return FileResponse(os.path.join(frontend_dist, "index.html"))
         return JSONResponse(status_code=404, content={"detail": "Not found"})
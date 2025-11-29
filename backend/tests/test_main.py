from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/notes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_note():
    response = client.post(
        "/notes/",
        json={"title": "Test Note", "content": "Test Content", "folder": "Test Folder"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Test Content"
    assert "id" in data

def test_ai_summary():
    response = client.post(
        "/ai/summarize",
        json={"text": "Sentence one. Sentence two. Sentence three. Sentence four."},
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data

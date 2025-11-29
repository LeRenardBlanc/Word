import uvicorn
import os
import sys

# Add backend directory to path so imports work
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

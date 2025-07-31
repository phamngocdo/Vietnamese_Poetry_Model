import uvicorn
from pathlib import Path
from fastapi import FastAPI

from gpt2_poetry import GPT2Poetry
from routes import model_router


SRC_DIR = Path(__file__).resolve().parent.parent

port = 8000

app = FastAPI()
app.include_router(model_router, prefix="/api", tags=["Poetry Generation"])

def start():
    model = GPT2Poetry()
    print("GPT2Poetry model initialized successfully.")
    uvicorn.run(
        app,
        host="localhost",
        port=port
    )

if __name__ == "__main__":
    start()
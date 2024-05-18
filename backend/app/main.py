from fastapi import FastAPI
from app.routers import memes

app = FastAPI()

app.include_router(memes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Meme Generator API"}

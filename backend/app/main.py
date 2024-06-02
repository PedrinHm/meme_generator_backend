from fastapi import FastAPI
from app.routers import memes, image_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(memes.router)
app.include_router(image_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Meme Generator API"}

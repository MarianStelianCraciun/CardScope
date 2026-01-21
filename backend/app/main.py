from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import models
from .api import cards

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CardScope API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your phone's IP or frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cards.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to CardScope API"}

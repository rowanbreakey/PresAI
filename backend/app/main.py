from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import random

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class dataBatch(BaseModel):
    frames: List[str]
    audio: str

@app.post("/api/process-batch")
async def process_batch(batch: dataBatch):
    # Placeholders to be replaced with actual logic later.
    eye_contact_score = "good"
    gesture_score = "excellent"
    pacing = "fast"
    filler_word_count = str(random.random())
    tip = "slow down a little for better pacing and fewer filler words!"

    return {
        "status": "success",
        "eyeContact" : eye_contact_score, 
        "gestures": gesture_score,
        "pacing": pacing, 
        "fillerWords" : filler_word_count,
        "tip" : tip
    }
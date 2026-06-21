from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Any
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import audio
import cv2 
import numpy as np

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

def do_video_analysis(frame_batch):
    data_by_frame = []

    base_options = python.BaseOptions(model_asset_path='holistic_landmarker.task')

    options = vision.HolisticLandmarkerOptions(
        base_options = base_options,
        output_face_blendshapes = True,
        output_hand_landmarks = True
    )

    with vision.HolisticLandmarker.create_from_options(options) as landmarker:
        for frame in frame_batch:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

            result = landmarker.detect(mp_frame)

            frame_data: dict[str, Any] = {
                "right_wrist" : None, 
                "left_wrist" : None, 
                "right_eye" : None
            }

            if result.right_hand_landmarks:
                wrist = result.right_hand_landmarks[0][0]
                frame_data["right_wrist"] = (wrist.x, wrist.y, wrist.z)

            if result.left_hand_landmarks:
                wrist = result.left_hand_landmarks[0][0]
                frame_data["left_wrist"] = (wrist.x, wrist.y, wrist.z)

            if result.face_landmarks:
                eye_center = result.face_landmarks[0][468]
                frame_data["right_eye"] = (eye_center.x, eye_center.y, eye_center.z)

            data_by_frame.append(frame_data)

    # now all the data is in the data_by_frame list so I just need to do some math and stuff to tell when the wrists are moving and where the eyes are looking at




@app.post("/api/process-batch")
async def process_batch(batch: dataBatch):
    do_video_analysis(batch.frames)

    eye_contact_score = "good"
    gesture_score = "excellent"
    pacing = "fast"
    filler_word_count = "1"
    tip = "slow down a little for better pacing and fewer filler words!"

    return {
        "status": "success",
        "eyeContact" : eye_contact_score, 
        "gestures": gesture_score,
        "pacing": pacing, 
        "fillerWords" : filler_word_count,
        "tip" : tip
    }
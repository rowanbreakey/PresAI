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
import math

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
    # good start just need to clean up my math portion a little so that it also checks to make sure everything exists and isnt none.
    # use some if statements and set to 0.0 otherwise to appear as no movement.
    # could also try doing something where if the landmarks arent detected it prompts the user to go back onscreen?
    data_by_frame = []

    base_options = python.BaseOptions(model_asset_path='holistic_landmarker.task')

    options = vision.HolisticLandmarkerOptions(
        base_options = base_options,
        refine_landmarks = True,
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

            if result.right_hand_landmarks and len(result.right_hand_landmarks) > 0:
                wrist = result.right_hand_landmarks[0][0]
                frame_data["right_wrist"] = (wrist.x, wrist.y)

            if result.left_hand_landmarks and len(result.left_hand_landmarks) > 0:
                wrist = result.left_hand_landmarks[0][0]
                frame_data["left_wrist"] = (wrist.x, wrist.y)

            if result.face_landmarks and len(result.face_landmarks) > 0:
                nose = result.face_landmarks[0][1]
                eye_center = result.face_landmarks[0][468]

                if nose and eye_center:
                    frame_data["left_eye"] = [eye_center.x-nose.x, eye_center.y-nose.y]

            data_by_frame.append(frame_data)

    velos_by_frame = []

    for i in range(1, len(data_by_frame)):
        dx_right_wrist = data_by_frame[i]["right_wrist"][0] - data_by_frame[i-1]["right_wrist"][0]
        dy_right_wrist = data_by_frame[i]["right_wrist"][1] - data_by_frame[i-1]["right_wrist"][1]
        right_wrist_step = round(math.sqrt(dx_right_wrist**2 + dy_right_wrist**2), 4)

        dx_left_wrist = data_by_frame[i]["left_wrist"][0] - data_by_frame[i-1]["left_wrist"][0]
        dy_left_wrist = data_by_frame[i]["left_wrist"][1] - data_by_frame[i-1]["left_wrist"][1]
        left_wrist_step = round(math.sqrt(dx_left_wrist**2 + dy_left_wrist**2), 4)

        dx_left_eye = data_by_frame[i]["left_eye"][0] - data_by_frame[i-1]["left_eye"][0]
        dy_left_eye = data_by_frame[i]["left_eye"][1] - data_by_frame[i-1]["left_eye"][1]
        left_eye_step = round(math.sqrt(dx_left_eye**2 + dy_left_eye**2), 4)

        velos_by_frame.append((right_wrist_step, left_wrist_step, left_eye_step))
    
    return velos_by_frame

    
def do_audio_analysis(audio_batch):
    return audio_batch

@app.post("/api/process-batch")
async def process_batch(batch: dataBatch):
    video_data = do_video_analysis(batch.frames)
    audio_data = do_audio_analysis(batch.audio)

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
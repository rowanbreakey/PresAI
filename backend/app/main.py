from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Any, Optional
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import base64
import numpy as np
import math
import json
import os
from pydub import AudioSegment
import io
from faster_whisper import WhisperModel
import ctypes
from supabase import create_client, Client
from pydantic_settings import BaseSettings, SettingsConfigDict
from gotrue.errors import AuthApiError

os.environ["GLOG_minloglevel"] = "2"

ffmpeg_bin = r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin"
os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]

app = FastAPI()

FFMPEG_DIR = r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin"

os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ["PATH"]

os.environ["FFMPEG_BINARY"] = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
os.environ["FFPROBE_BINARY"] = os.path.join(FFMPEG_DIR, "ffprobe.exe")

AudioSegment.converter = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(FFMPEG_DIR, "ffprobe.exe")

ctypes.WinDLL(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin\cublas64_12.dll")

model = WhisperModel("base", device="cuda", compute_type="float16")

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

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings() # pyright: ignore[reportCallIssue]

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

def get_supabase() -> Client:
    print(settings.SUPABASE_URL)
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def decode_base64_frames(base64_string: str):
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]

    img_bytes = base64.b64decode(base64_string)

    array = np.frombuffer(img_bytes, dtype=np.uint8)
    frame = cv2.imdecode(array, cv2.IMREAD_COLOR)

    return frame

def do_video_analysis(frame_batch):
    # could also try doing something where if the landmarks arent detected it prompts the user to go back onscreen?
    data_by_frame = []

    BaseOptions = mp.tasks.BaseOptions
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "holistic_landmarker.task")

    options = vision.HolisticLandmarkerOptions(
        base_options = BaseOptions(model_asset_path=model_path),
        output_face_blendshapes = True
    )

    with vision.HolisticLandmarker.create_from_options(options) as landmarker:
        for frame in frame_batch:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

            result = landmarker.detect(mp_frame)

            frame_data: dict[str, Any] = {
                "right_wrist" : None, 
                "left_wrist" : None, 
                "left_eye" : None
            }

            if result.right_hand_landmarks and len(result.right_hand_landmarks) > 0:
                wrist = result.right_hand_landmarks[0]
                frame_data["right_wrist"] = (wrist.x, wrist.y)

            if result.left_hand_landmarks and len(result.left_hand_landmarks) > 0:
                wrist = result.left_hand_landmarks[0]
                frame_data["left_wrist"] = (wrist.x, wrist.y)

            if result.face_landmarks and len(result.face_landmarks) > 0:
                nose = result.face_landmarks[1]
                eye_center = result.face_landmarks[468]

                if nose and eye_center:
                    frame_data["left_eye"] = [eye_center.x-nose.x, eye_center.y-nose.y]

            data_by_frame.append(frame_data)

    velos_by_frame = []

    for i in range(1, len(data_by_frame)):
        if data_by_frame[i]["right_wrist"] and data_by_frame[i-1]["right_wrist"]:
            dx_right_wrist = data_by_frame[i]["right_wrist"][0] - data_by_frame[i-1]["right_wrist"][0]
            dy_right_wrist = data_by_frame[i]["right_wrist"][1] - data_by_frame[i-1]["right_wrist"][1]
            right_wrist_step = round(math.sqrt(dx_right_wrist**2 + dy_right_wrist**2), 4)
        else:
            right_wrist_step = 0

        if data_by_frame[i]["left_wrist"] and data_by_frame[i-1]["left_wrist"]:
            dx_left_wrist = data_by_frame[i]["left_wrist"][0] - data_by_frame[i-1]["left_wrist"][0]
            dy_left_wrist = data_by_frame[i]["left_wrist"][1] - data_by_frame[i-1]["left_wrist"][1]
            left_wrist_step = round(math.sqrt(dx_left_wrist**2 + dy_left_wrist**2), 4)
        else:
            left_wrist_step = 0

        if data_by_frame[i]["left_eye"] and data_by_frame[i-1]["left_eye"]:
            dx_left_eye = data_by_frame[i]["left_eye"][0] - data_by_frame[i-1]["left_eye"][0]
            dy_left_eye = data_by_frame[i]["left_eye"][1] - data_by_frame[i-1]["left_eye"][1]
            left_eye_step = round(math.sqrt(dx_left_eye**2 + dy_left_eye**2), 4)
        else:
            left_eye_step = 0

        velos_by_frame.append((right_wrist_step, left_wrist_step, left_eye_step))
    print(velos_by_frame)
    return velos_by_frame

    
def do_audio_analysis(audio_batch):
    segments, info = model.transcribe(audio_batch, beam_size=1, vad_filter=True, language="en")

    transcription = []

    for segment in segments:
        transcription.append(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
    
    return transcription

@app.post("/auth/signup")
def sign_in(payload: SignUpRequest, supabase: Client = Depends(get_supabase)):
    try:
        signup_data = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password
        })

        return {
            "message": "User successfully registered",
            "user": signup_data.user,
            "session_active": signup_data.session is not None
        }

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An error occurred during signup. {e}"
        )


@app.post("/api/process-batch")
async def process_batch(frames : str = Form(...), audio : Optional[UploadFile] = File(None)):
    frame_list = json.loads(frames)
    decoded_frames = []
    for frame in frame_list:
        decoded_frames.append(decode_base64_frames(frame))
    
    video_data = do_video_analysis(decoded_frames)

    if audio:
        webm_bytes = await audio.read()

        audio_segment = AudioSegment.from_file(io.BytesIO(webm_bytes), format="webm")

        audio_segment.export("temp_audio.wav", format="wav")
    
        audio_data = do_audio_analysis("temp_audio.wav")

        if os.path.exists("temp_audio.wav"):
            os.remove("temp_audio.wav")
    else:
        audio_data = "Audio data could not be retreived"

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
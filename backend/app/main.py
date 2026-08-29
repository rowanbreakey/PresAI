from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status, Response, Cookie
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
from supabase.lib.client_options import ClientOptions
from pydantic_settings import BaseSettings, SettingsConfigDict
from gotrue.errors import AuthApiError
from google import genai
from google.genai import types
from typing import List, Dict, cast

os.environ["GLOG_minloglevel"] = "2"

ffmpeg_bin = r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin"
os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]

app = FastAPI()

FFMPEG_DIR = r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin"

os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ["PATH"]

os.environ["FFMPEG_BINARY"] = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
os.environ["FFPROBE_BINARY"] = os.path.join(FFMPEG_DIR, "ffprobe.exe")

AudioSegment.converter = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(FFMPEG_DIR, "ffprobe.exe") # type: ignore

ctypes.WinDLL(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin\cublas64_12.dll")

model = WhisperModel("base", device="cuda", compute_type="float16")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
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
    SUPABASE_SERVICE_ROLE_KEY: str
    GEMINI_API_KEY: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings() # pyright: ignore[reportCallIssue]

client = genai.Client(api_key=settings.GEMINI_API_KEY)

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

class AIResponseQuick(BaseModel):
    """You are responsible for analysing data from a users presentation and giving them helpful feedback on how to improve
    
    You are given: 
    - A transcript taken from the last 5 seconds of the users speech. Keep in mind this transcript my not be perfect so if the words do not make sense act as though no transcript is provided
    - A 2D list containing the velocities of the eye and wrist landmarks from the users camera feed. The format of this list is [right_wrist, left_wrist, eye].
    """

    eye_contact: str = Field(description='Return: "Excellent", "Good", "Ok" or "Poor" based on how much the users eyes are scanning their audience (velocity of eye landmark)')
    pacing: str = Field(description='Return: "Excellent", "Good", "Ok" or "Poor" based on how fast the user is speaking (# of words in transcript) keep in mind this is a presentation and not a conversation')
    filler_word_count: int = Field(description='Return the number of filler words in the users speech. Filler words include but are not limited to "um", "like" and excessive use of "very"')
    gesture_use: str = Field(description='Return: "Excellent", "Good", "Ok" or "Poor" based on how much the user is gesticulating (wrist landmark velocities)')
    quick_tip: str = Field(description='Return a short one sentence tip to help the user improve. This should coincide with feedback from the other analysis categories.')

class AIResponseOverall(BaseModel):
    """You are responsible for giving feedback to a user based on data aquired from a presentation they gave

    You are given:
    - a full transcript of everything they said in their presentation (note that this may be innacurate and so dont give feedback on the coherence of content)
    - a list of scores given based on the quality of the users gestures throughout the presentation
    - a list of scores given based on the level of eye contact the user maintained with their audience
    - a list of scores based on the pacing of the users speech throughout their presentation
    
    Scores were taken roughly every 5 seconds throuhgout the users presentation

    IF THE ABOVE ARE NOT PROVIDED, GIVE A SCORE OF 0 AND FEEDBACK containing what data was missing/insufficient.
    """

    overall_score: int = Field(description='Return: an integer from 1-100 based on the overall quality of the users presentation.')
    feedback_paragraph: str = Field(description='Return: a quick paraphraph (2-5 sentences) detailing how the user could improve their presentation. some potential talking points include but are not limited to pacing, gestures, eye contact, number of filler words, etc. ')

def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_service_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

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
    return velos_by_frame

    
def do_audio_analysis(audio_batch):
    segments, info = model.transcribe(audio_batch, beam_size=1, vad_filter=True, language="en")

    transcription = []

    for segment in segments:
        transcription.append(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
    
    return transcription

def get_response_dict(parsed_data) -> dict:
    if isinstance(parsed_data, BaseModel):
        return parsed_data.model_dump()
    if isinstance(parsed_data, dict):
        return parsed_data
    return {}

@app.post("/auth/signup")
def sign_up(payload: SignUpRequest, supabase: Client = Depends(get_supabase)):
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
    
@app.post("/auth/signin")
def sign_in(payload: SignUpRequest, response: Response, supabase: Client = Depends(get_supabase)):
    try:
        signin_data = supabase.auth.sign_in_with_password({
            "email" : payload.email,
            "password" : payload.password
        })

        session = signin_data.session
        if not session or not signin_data.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        access_token = session.access_token
        refresh_token = session.refresh_token

        IS_PROD = os.getenv("ENV") == "production"
        response.set_cookie(
            key="supabase_access_token",
            value=access_token,
            httponly=True, 
            secure=IS_PROD, 
            samesite="none" if IS_PROD else "lax", 
            max_age=3600
        )

        response.set_cookie(
            key="supabase_refresh_token",
            value=refresh_token,
            httponly=True, 
            secure=IS_PROD, 
            samesite="none" if IS_PROD else "lax", 
            max_age=3600
        )

        return {"status" : "success", "user" : signin_data.user.id}
        
    except HTTPException as e:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = f"Login unsuccessful: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"An error ocurred: {e}"
        )

@app.post("/api/process-batch")
async def process_batch(frames : str = Form(...), audio : Optional[UploadFile] = File(None), supabase_access_token : str = Cookie(None), supabase : Client = Depends(get_service_supabase)):
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
        audio_data = ""

    print(audio_data)
    ai_response_raw = client.models.generate_content(
        model="gemini-3.5-flash", 
        contents=f"TRANSCRIPT: {audio_data}, LANDMARK VELOCITIES: {video_data}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json", 
            response_schema=AIResponseQuick,
        ),
    )


    data = get_response_dict(ai_response_raw.parsed)
    data["success"] = "success"

    transcript = ""

    for chunk in audio_data:
        split_up = chunk.split("]")
        print(split_up)
        transcript += split_up[1]
    data["transcript"] = transcript

    try:
        user_response = supabase.auth.get_user(supabase_access_token)
        if user_response:
            user = user_response.user
            id = user.id
            supabase.table("active_session_data").insert({"user_id":id, "data": data}).execute()
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return data

@app.get("/api/get-feedback")
async def get_feedback(supabase_access_token : str = Cookie(None), supabase : Client = Depends(get_service_supabase)):
    try:
        user_response = supabase.auth.get_user(supabase_access_token)
        if user_response:
            user = user_response.user
            id = user.id
            response = supabase.table("active_session_data").select("data").eq("user_id", id).execute()
            all_data = cast(List[Dict], response.data)

            transcript = ""
            gestures = []
            eye_contact = []
            pacing = []
            for data in all_data:
                transcript += data["data"]["transcript"]
                gestures.append(data["data"]["gesture_use"])
                eye_contact.append(data["data"]["eye_contact"])
                pacing.append(data["data"]["pacing"])

            ai_response_raw = client.models.generate_content(
                model="gemini-3.5-flash", 
                contents=f"TRANSCRIPT: {transcript}, GESTURE RATINGS: {gestures}, EYE CONTACT RATINGS: {eye_contact}, PACING: {pacing}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", 
                    response_schema=AIResponseOverall,
                ),
            )

            data = get_response_dict(ai_response_raw.parsed)
            print("should have pritned data")
            return data
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Something went wrong while retreiving your data")

@app.delete("/api/delete-old-feedback")
async def delete_old_feedback(supabase_access_token : str = Cookie(None), supabase : Client = Depends(get_service_supabase)):
    try:
        user_response = supabase.auth.get_user(supabase_access_token)
        if user_response:
            user = user_response.user
            id = user.id
            supabase.table("active_session_data").delete().eq("user_id", id).execute()
    except Exception as e:
        raise HTTPException(status_code=401, detail="Something went wrong while retreiving your data")
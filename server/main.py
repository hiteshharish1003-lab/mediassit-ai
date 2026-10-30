# server/main.py
import os
import logging
import uuid
import json
import shutil
from typing import Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from utils.llm_parser import parse_jpg_to_structured
from utils.chatbot_utils import answer_query

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
SUMMARY_DIR = BASE_DIR / "summaries"

UPLOAD_DIR.mkdir(exist_ok=True)
SUMMARY_DIR.mkdir(exist_ok=True)

app = FastAPI(title="MediAssist AI Backend")
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store the latest result for dashboard/chatbot use
LATEST_RESULT: dict[str, Any] | None = None


@app.get("/")
def root():
    return {"message": "MediAssist AI backend running (LLM-enhanced mode)."}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload PDF/Image → OCR → LLM Parser → Risk Detection → Summary
    Returns FULL structured medical output.
    """
    global LATEST_RESULT

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image of your prescription (JPG, PNG, or WEBP).")

    # Create unique filename so multiple uploads don't overwrite
    unique_id = uuid.uuid4().hex
    suffix = Path(file.filename or "prescription.jpg").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
        raise HTTPException(status_code=400, detail="Supported formats: JPG, PNG, WEBP, BMP.")
    filename = f"{unique_id}{suffix}"
    file_path = UPLOAD_DIR / filename

    # Save upload
    contents = await file.read()
    if len(contents) > 12 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be smaller than 12 MB.")
    with open(file_path, "wb") as buffer:
        buffer.write(contents)
    try:
        llm_result = parse_jpg_to_structured(filename)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Prescription analysis failed")
        status_code = getattr(exc, "status_code", None)
        if status_code == 401:
            detail = "Groq rejected the API key. Check GROQ_API_KEY in server/.env, save it, and restart the backend."
        elif status_code == 403:
            detail = "Groq denied access to the configured vision model. Check model access for this API key/project."
        elif status_code == 429:
            detail = "Groq rate limit or usage quota reached. Check your Groq usage limits and try again later."
        elif status_code == 400:
            detail = "Groq rejected the image analysis request. Check the backend terminal for its error details."
        elif exc.__class__.__name__ in {"APIConnectionError", "APITimeoutError"}:
            detail = "Could not connect to Groq. Check your internet connection and try again."
        else:
            detail = f"Prescription analysis failed ({exc.__class__.__name__}). Check the backend terminal for details."
        raise HTTPException(status_code=502, detail=detail) from exc
    LATEST_RESULT = llm_result
    return llm_result


@app.get("/latest/")
def get_latest():
    """
    Dashboard fetches this endpoint to load latest LLM structured result.
    """
    if LATEST_RESULT is None:
        return None
    return LATEST_RESULT


@app.post("/chat/")
def chat_endpoint(payload: dict):
    """
    AI Chatbot endpoint.
    Uses latest LLM structured result as context if none provided.
    """
    q = payload.get("query", "")
    if not q:
        raise HTTPException(status_code=400, detail="Missing 'query'.")

    global LATEST_RESULT
    context = payload.get("context")
    # Use a short, human-readable summary as chatbot context to avoid raw JSON snippets
    if not context and LATEST_RESULT:
        # prefer LATEST_RESULT.summary, fallback to a short medications list
        if isinstance(LATEST_RESULT, dict):
            context = json.dumps(LATEST_RESULT, ensure_ascii=False)
        else:
            context = ""

    answer = answer_query(q, context or "", payload.get("history", []))
    return {"response": answer}

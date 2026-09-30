import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, UploadFile  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from starlette.concurrency import run_in_threadpool  # noqa: E402

from .ai_service import score_with_gemini  # noqa: E402
from .extractors import extract_docx, extract_image, extract_pdf  # noqa: E402
from .schemas import ScoreResult  # noqa: E402

app = FastAPI(title="ATS Resume Scorer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_BYTES = 5 * 1024 * 1024
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
IMAGE_MIMES = {"image/png", "image/jpeg"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/score-resume", response_model=ScoreResult)
async def score_resume(
    file: UploadFile = File(...),
    job_description: str = Form(""),
):
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file.")
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File too large (max 5 MB).")

    name = (file.filename or "").lower()
    mime = file.content_type or ""

    try:
        # PyMuPDF / python-docx are blocking, so run them in a threadpool
        if name.endswith(".pdf") or mime == "application/pdf":
            extracted = await run_in_threadpool(extract_pdf, data)
        elif name.endswith(".docx") or mime == DOCX_MIME:
            extracted = await run_in_threadpool(extract_docx, data)
        elif mime in IMAGE_MIMES or name.endswith((".png", ".jpg", ".jpeg")):
            img_mime = "image/png" if name.endswith(".png") else "image/jpeg"
            extracted = extract_image(data, img_mime)
        else:
            raise HTTPException(415, "Upload a PDF, DOCX, PNG or JPG.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            422, "Could not read this file. Is it corrupted or password-protected?"
        )

    try:
        return await score_with_gemini(extracted, job_description)
    except Exception as e:
        raise HTTPException(502, f"AI analysis failed: {e}")

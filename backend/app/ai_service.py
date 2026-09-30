import json
import os
from functools import lru_cache

from google import genai
from google.genai import types

from .extractors import Extracted
from .schemas import ScoreResult

SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) analyst and technical recruiter.
Evaluate the resume and return ONLY JSON matching the given schema.

SCORING RUBRIC (total 100):
- Keyword relevance: 35  (vs. job description if given; otherwise vs. standard keywords for the role the resume targets)
- ATS formatting/parsability: 25  (tables, multi-column layouts, text in headers/footers, images/graphics, icons, unusual fonts, missing standard section headings)
- Content impact: 25  (quantified achievements, strong action verbs, clarity, no fluff)
- Structure & completeness: 15  (contact info, summary, skills, experience, education, projects, consistent dates)

RULES:
- Be strict and consistent; do not inflate scores. Most resumes score 55-80.
- keyword_match.matched: only keywords actually present in the resume.
- keyword_match.missing: important keywords from the JD (or the inferred target role) that are absent. Max 15 each, most important first.
- Use the provided EXTRACTION METADATA as evidence for formatting_issues (e.g. tables_detected > 0, column_count > 1, text_in_header_footer = true).
- If an image is provided, also judge visual layout, font legibility and contrast.
- Each formatting issue needs a concrete fix.
- recommendations: 5-8 specific, actionable bullets. Reference actual content from the resume where possible.
- Never invent experience the candidate does not have."""


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to backend/.env")
    return genai.Client(api_key=key)


def _build_user_text(ex: Extracted, jd: str) -> str:
    return f"""EXTRACTION METADATA:
{json.dumps(ex.meta, indent=2)}

JOB DESCRIPTION:
{jd.strip() or "Not provided. Infer the target role from the resume and score against general expectations for it."}

RESUME TEXT:
{ex.text or "(No extractable text. Analyse the attached image(s) instead.)"}"""


async def score_with_gemini(ex: Extracted, jd: str) -> ScoreResult:
    parts = [types.Part.from_text(text=_build_user_text(ex, jd))]
    for img_bytes, mime in ex.images:
        parts.append(types.Part.from_bytes(data=img_bytes, mime_type=mime))

    resp = await get_client().aio.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=[types.Content(role="user", parts=parts)],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=ScoreResult,
            temperature=0.2,
        ),
    )
    result = resp.parsed or ScoreResult.model_validate_json(resp.text)
    result.ats_score = max(0, min(100, result.ats_score))
    return result

# AI-Based ATS-Friendly Resume Scorer

FastAPI + React + Gemini. Upload a resume (PDF / DOCX / PNG / JPG), optionally paste a job description,
and get an ATS score, keyword match, formatting check and actionable recommendations.

## Flow
React (drag & drop) -> POST /score-resume -> FastAPI (PyMuPDF / python-docx / raw image bytes) -> Gemini (structured JSON) -> React

## Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then put your GEMINI_API_KEY inside
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

## Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
App: http://localhost:5173

## Push to GitHub
```bash
git init && git branch -M main
git remote add origin https://github.com/<your-username>/CV-ATS-FRIENDLY.git
git pull origin main --allow-unrelated-histories   # only if the repo already has commits
git add . && git commit -m "feat: AI ATS resume scorer"
git push -u origin main
```
Never commit `.env`. Only `.env.example` goes to GitHub.

## Note
The score is an AI estimate, not a guarantee of how a specific ATS will parse your resume.

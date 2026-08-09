# DevOpsMentor AI v0.1

Personal AI-powered DevOps interview coach.

## First vertical slice

- Choose a topic and difficulty.
- Start an adaptive interview.
- Answer questions.
- Receive rubric-based AI evaluation.
- Get a follow-up question.
- Finish with a performance report.
- Store sessions locally in SQLite.

## Stack

- Python 3.11+
- FastAPI
- SQLite + SQLAlchemy
- OpenAI Python SDK / Responses API
- HTML/CSS/JavaScript frontend served by FastAPI

## Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add OPENAI_API_KEY to .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

If no API key is configured, deterministic demo mode lets you test the full interview flow.

## Next milestones

1. Expand the DevOps knowledge base.
2. Improve adaptive scoring.
3. Add production incident simulations.
4. Add persistent skill profiles.
5. Add RAG/vector retrieval.
6. Add a richer Next.js UI.

from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .schemas import StartInterviewRequest, StartInterviewResponse, AnswerRequest, AnswerResponse, SessionReport
from .interview_engine import start_session, answer_current, report

Base.metadata.create_all(bind=engine)
app = FastAPI(title="DevOpsMentor AI", version="0.1.0")

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "devopsmentor-ai"}

@app.post("/api/interviews", response_model=StartInterviewResponse)
def create_interview(payload: StartInterviewRequest, db: Session = Depends(get_db)):
    session, question = start_session(db, payload.topic, payload.difficulty)
    return {"session_id": session.id, "question_number": session.question_number,
            "total_questions": session.total_questions, "question": question}

@app.post("/api/interviews/{session_id}/answer", response_model=AnswerResponse)
def submit_answer(session_id: int, payload: AnswerRequest, db: Session = Depends(get_db)):
    try:
        result, next_question, session = answer_current(db, session_id, payload.answer)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"evaluation": result["evaluation"], "score": result["score"],
            "next_question": next_question, "question_number": session.question_number,
            "total_questions": session.total_questions, "completed": session.status == "completed"}

@app.get("/api/interviews/{session_id}/report", response_model=SessionReport)
def get_report(session_id: int, db: Session = Depends(get_db)):
    try:
        return report(db, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

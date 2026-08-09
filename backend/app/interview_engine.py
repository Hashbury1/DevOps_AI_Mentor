from sqlalchemy.orm import Session
from .models import InterviewSession, InterviewTurn
from .question_bank import get_questions
from .ai import evaluate_answer, generate_next_question

def start_session(db: Session, topic: str, difficulty: str):
    questions = get_questions(topic)
    session = InterviewSession(topic=topic, difficulty=difficulty,
                               question_number=1, total_questions=min(8, len(questions)))
    db.add(session)
    db.commit()
    db.refresh(session)
    db.add(InterviewTurn(session_id=session.id, question=questions[0]["question"]))
    db.commit()
    return session, questions[0]["question"]

def answer_current(db: Session, session_id: int, answer: str):
    session = db.get(InterviewSession, session_id)
    if not session or session.status != "active":
        raise ValueError("Interview session not found or already completed.")

    turns = db.query(InterviewTurn).filter(InterviewTurn.session_id == session_id).order_by(InterviewTurn.id).all()
    current = turns[-1]
    questions = get_questions(session.topic)
    base = questions[min(len(turns)-1, len(questions)-1)]

    result = evaluate_answer(current.question, base["rubric"], answer)
    current.answer = answer
    current.evaluation = result["evaluation"]
    current.score = result["score"]

    completed = len(turns) >= session.total_questions
    next_question = None

    if completed:
        session.status = "completed"
        session.score = round(sum(t.score or 0 for t in turns) / len(turns), 1)
    else:
        next_question = generate_next_question(session.topic, session.difficulty,
                                               result["follow_up_focus"], current.question)
        session.question_number += 1
        db.add(InterviewTurn(session_id=session_id, question=next_question))

    db.commit()
    return result, next_question, session

def report(db: Session, session_id: int):
    session = db.get(InterviewSession, session_id)
    if not session:
        raise ValueError("Session not found.")
    turns = db.query(InterviewTurn).filter(
        InterviewTurn.session_id == session_id,
        InterviewTurn.score.is_not(None)
    ).all()
    return {
        "session_id": session.id,
        "topic": session.topic,
        "difficulty": session.difficulty,
        "score": session.score,
        "status": session.status,
        "strengths": [t.question[:80] for t in turns if (t.score or 0) >= 80][:3],
        "weaknesses": [t.question[:80] for t in turns if (t.score or 0) < 60][:3],
        "recommendation": "Review weak concepts, then repeat the interview at a higher difficulty.",
    }

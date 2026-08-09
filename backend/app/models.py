from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic: Mapped[str] = mapped_column(String(100))
    difficulty: Mapped[str] = mapped_column(String(30))
    question_number: Mapped[int] = mapped_column(Integer, default=1)
    total_questions: Mapped[int] = mapped_column(Integer, default=8)
    score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class InterviewTurn(Base):
    __tablename__ = "interview_turns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluation: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)

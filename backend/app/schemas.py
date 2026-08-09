from pydantic import BaseModel, Field

class StartInterviewRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=100)
    difficulty: str = Field(default="intermediate", min_length=1, max_length=30)

class StartInterviewResponse(BaseModel):
    session_id: int
    question_number: int
    total_questions: int
    question: str

class AnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=10000)

class AnswerResponse(BaseModel):
    evaluation: str
    score: float
    next_question: str | None
    question_number: int
    total_questions: int
    completed: bool

class SessionReport(BaseModel):
    session_id: int
    topic: str
    difficulty: str
    score: float
    status: str
    strengths: list[str]
    weaknesses: list[str]
    recommendation: str

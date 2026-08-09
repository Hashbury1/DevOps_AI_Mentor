import json
from openai import OpenAI
from .config import settings

def evaluate_answer(question: str, rubric: list[str], answer: str) -> dict:
    if not settings.openai_api_key:
        return demo_evaluation(rubric, answer)

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = f"""
Evaluate this DevOps interview answer.

Question:
{question}

Required concepts:
{json.dumps(rubric)}

Candidate answer:
{answer}

Return ONLY JSON:
{{
  "score": number,
  "evaluation": "specific feedback",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "follow_up_focus": "one concept to probe next"
}}

Score 0-100. Reward correct reasoning, troubleshooting methodology,
evidence gathering, technical accuracy, sequencing, and tradeoffs.
"""
    response = client.responses.create(
        model=settings.openai_model,
        instructions="You are a rigorous but constructive Senior DevOps interviewer.",
        input=prompt,
        text={"format": {"type": "json_object"}},
    )
    return json.loads(response.output_text)

def generate_next_question(topic: str, difficulty: str, focus: str, previous_question: str) -> str:
    if not settings.openai_api_key:
        return f"Follow-up: What specific evidence would you collect to prove or disprove your {focus} hypothesis?"

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = f"""
Generate ONE DevOps interview follow-up question.
Topic: {topic}
Difficulty: {difficulty}
Focus: {focus}
Previous question: {previous_question}
Test reasoning, not memorization. Return only the question.
"""
    response = client.responses.create(
        model=settings.openai_model,
        instructions="You are a Senior DevOps interviewer.",
        input=prompt,
    )
    return response.output_text.strip()

def demo_evaluation(rubric: list[str], answer: str) -> dict:
    text = answer.lower()
    hits = sum(1 for item in rubric if item.lower() in text)
    score = round(hits / max(len(rubric), 1) * 100, 1)
    strengths = [x for x in rubric if x.lower() in text][:3]
    weaknesses = [x for x in rubric if x.lower() not in text][:3]
    focus = weaknesses[0] if weaknesses else "evidence and verification"
    return {
        "score": score,
        "evaluation": f"Demo evaluation: covered {hits}/{len(rubric)} rubric concepts. Focus next on {focus}.",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "follow_up_focus": focus,
    }

# DevOpsMentor AI

## Phase 3 — Stateful Incident Engine

This version replaces the simple evidence buttons with a natural-language investigation loop.

### What is implemented

- Incident state
- Evidence tracking
- Action tracking
- Hypothesis recording
- Mitigation state
- Natural-language investigation endpoint
- Final diagnosis submission
- Incident investigation UI

### Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Open:

http://127.0.0.1:8001/incident.html

### Try this investigation

Do not simply request everything in order. Think like an interview candidate.

For example:

> I'll first check the ALB metrics and target response time.

Then investigate based on what you see.

The next milestone is the AI evaluation layer, which will judge the investigation process rather than only the final answer.

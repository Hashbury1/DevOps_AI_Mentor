# DevOpsMentor AI v0.5

Phase 3 Evaluation Engine.

Run:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Open http://127.0.0.1:8001/incident.html

The evaluator scores triage, evidence gathering, hypotheses, AWS reasoning,
prioritization, mitigation, root cause and prevention.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .incident_engine import INCIDENT, IncidentState, new_state, interpret_request

router = APIRouter(prefix="/api/incidents", tags=["incidents"])
STATES: dict[str, IncidentState] = {}

class InvestigateRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

class DiagnosisRequest(BaseModel):
    diagnosis: str = Field(min_length=10, max_length=5000)

@router.post("/start")
def start():
    state = new_state()
    STATES[state.incident_id] = state
    return {
        "incident_id": INCIDENT["id"],
        "title": INCIDENT["title"],
        "severity": INCIDENT["severity"],
        "briefing": INCIDENT["briefing"],
        "state": state.stage,
    }

@router.get("/{incident_id}/state")
def get_state(incident_id: str):
    state = STATES.get(incident_id)
    if not state:
        raise HTTPException(404, "Incident has not been started.")
    return {
        "incident_id": state.incident_id,
        "stage": state.stage,
        "evidence_seen": state.evidence_seen,
        "hypotheses": state.hypotheses,
        "actions": state.actions,
        "mitigation_status": state.mitigation_status,
        "diagnosis": state.diagnosis,
    }

@router.post("/{incident_id}/investigate")
def investigate(incident_id: str, payload: InvestigateRequest):
    state = STATES.get(incident_id)
    if not state:
        raise HTTPException(404, "Incident has not been started.")

    result, evidence = interpret_request(payload.message, state)
    return {
        "response": result,
        "evidence_type": evidence,
        "state": {
            "evidence_seen": state.evidence_seen,
            "hypotheses": state.hypotheses,
            "actions_count": len(state.actions),
            "mitigation_status": state.mitigation_status,
        },
    }

@router.post("/{incident_id}/diagnosis")
def diagnosis(incident_id: str, payload: DiagnosisRequest):
    state = STATES.get(incident_id)
    if not state:
        raise HTTPException(404, "Incident has not been started.")
    state.diagnosis = payload.diagnosis
    state.stage = "diagnosis_submitted"
    return {
        "status": "captured",
        "message": (
            "Diagnosis captured. The next engine will score your reasoning against "
            "the incident evidence, root cause, mitigation and prevention criteria."
        ),
    }

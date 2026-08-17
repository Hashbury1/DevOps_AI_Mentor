from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .incident_engine import INCIDENT, IncidentState, new_state, interpret_request
from .evaluation_engine import evaluate

router = APIRouter(prefix="/api/incidents", tags=["incidents"])
STATES = {}

class InvestigateRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

class DiagnosisRequest(BaseModel):
    diagnosis: str = Field(min_length=10, max_length=5000)

@router.post("/start")
def start():
    s = new_state(); STATES[s.incident_id] = s
    return {"incident_id":INCIDENT["id"],"title":INCIDENT["title"],"severity":INCIDENT["severity"],
            "briefing":INCIDENT["briefing"],"state":s.stage}

@router.get("/{incident_id}/state")
def state(incident_id:str):
    s=STATES.get(incident_id)
    if not s: raise HTTPException(404,"Incident has not been started.")
    return {"incident_id":s.incident_id,"stage":s.stage,"evidence_seen":s.evidence_seen,
            "hypotheses":s.hypotheses,"actions":s.actions,
            "mitigation_status":s.mitigation_status,"diagnosis":s.diagnosis}

@router.post("/{incident_id}/investigate")
def investigate(incident_id:str,payload:InvestigateRequest):
    s=STATES.get(incident_id)
    if not s: raise HTTPException(404,"Incident has not been started.")
    result,key=interpret_request(payload.message,s)
    return {"response":result,"evidence_type":key,
            "state":{"evidence_seen":s.evidence_seen,"hypotheses":s.hypotheses,
                     "actions_count":len(s.actions),"mitigation_status":s.mitigation_status}}

@router.post("/{incident_id}/diagnosis")
def diagnosis(incident_id:str,payload:DiagnosisRequest):
    s=STATES.get(incident_id)
    if not s: raise HTTPException(404,"Incident has not been started.")
    s.diagnosis=payload.diagnosis; s.stage="diagnosis_submitted"
    return evaluate(s)
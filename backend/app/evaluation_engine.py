from .incident_engine import INCIDENT

WEIGHTS = {
    "initial_triage": 10, "evidence_gathering": 20, "hypothesis_quality": 15,
    "aws_reasoning": 15, "prioritization": 10, "mitigation": 10,
    "root_cause": 10, "prevention": 10,
}

def has(text, words):
    text = text.lower()
    return any(w in text for w in words)

def evaluate(state):
    evidence = set(state.evidence_seen)
    actions = " ".join(state.actions)
    diagnosis = state.diagnosis or ""
    combined = f"{actions} {diagnosis}"

    scores = {}
    scores["initial_triage"] = min(10, (4 if "alb" in evidence else 0) +
                                   (2 if "health" in evidence else 0) +
                                   (4 if "logs" in evidence else 0))

    pts = {"alb":3,"health":2,"logs":5,"rds":4,"deployment":4,"flow":1,"routes":1,"sg":1}
    scores["evidence_gathering"] = min(20, sum(pts[k] for k in evidence))

    h = 0
    if state.hypotheses: h += 5
    if has(combined, ["database","rds","connection pool","connection exhaustion"]): h += 5
    if has(combined, ["deployment","2.8.0","release"]): h += 3
    if has(combined, ["network","vpc","routing","security group"]): h += 2
    scores["hypothesis_quality"] = min(15,h)

    a = 0
    if "alb" in evidence and has(combined,["target","application"]): a += 4
    if "flow" in evidence and has(combined,["accept","network","networking"]): a += 4
    if "rds" in evidence and has(combined,["connection","database"]): a += 4
    if has(combined,["health check","health checks"]): a += 3
    scores["aws_reasoning"] = min(15,a)

    p = min(7, len(evidence.intersection({"alb","logs","rds","deployment"}))*2)
    if "logs" in evidence and "rds" in evidence: p += 2
    if len(evidence.intersection({"routes","sg"})) >= 2 and len(evidence.intersection({"alb","logs","rds","deployment"})) <= 1: p -= 3
    scores["prioritization"] = max(0,min(10,p))

    scores["mitigation"] = 10 if state.mitigation_status == "completed" else 0

    r = 0
    if has(diagnosis,["database","rds","connection pool","connection exhaustion"]): r += 4
    if has(diagnosis,["2.8.0","deployment","release"]): r += 3
    if has(diagnosis,["504","timeout","latency"]): r += 1
    if has(diagnosis,["regression","database access","order-query","query"]): r += 2
    scores["root_cause"] = min(10,r)

    pr = 0
    if has(diagnosis,["monitor","alert","connection pool","connection"]): pr += 3
    if has(diagnosis,["load test","load-test","testing"]): pr += 2
    if has(diagnosis,["rollback","deployment","canary","threshold"]): pr += 3
    if has(diagnosis,["review","fix","database access"]): pr += 2
    scores["prevention"] = min(10,pr)

    feedback=[]
    if scores["prioritization"] < 6: feedback.append("You spent too much attention on lower-probability infrastructure paths.")
    if "rds" not in evidence: feedback.append("You did not inspect RDS/database saturation directly.")
    if "deployment" not in evidence: feedback.append("You did not inspect the recent deployment.")
    if scores["root_cause"] < 7: feedback.append("Your diagnosis did not clearly connect the deployment to database connection-pool exhaustion.")
    if scores["prevention"] < 7: feedback.append("Your prevention plan needs concrete monitoring, testing, and deployment safeguards.")
    if state.mitigation_status != "completed": feedback.append("You did not complete a mitigation action.")

    strengths=[]
    if "alb" in evidence: strengths.append("You checked load-balancer and target behavior.")
    if "logs" in evidence: strengths.append("You used application logs to move beyond infrastructure symptoms.")
    if "flow" in evidence: strengths.append("You gathered network evidence instead of assuming a VPC failure.")
    if "deployment" in evidence: strengths.append("You correlated the incident with a recent production change.")
    if has(diagnosis,["database","connection pool","rds"]): strengths.append("Your diagnosis recognized database connection saturation.")

    return {
        "overall_score": sum(scores.values()), "scores": scores,
        "strengths": strengths, "improvement_areas": feedback,
        "expected_root_cause": INCIDENT["root_cause"],
        "prevention_points": INCIDENT["prevention_points"],
        "summary": "The score evaluates both your investigation process and your final diagnosis."
    }
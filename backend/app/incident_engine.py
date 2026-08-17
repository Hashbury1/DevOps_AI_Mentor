from dataclasses import dataclass, field


@dataclass
class IncidentState:
    incident_id: str
    stage: str = "investigating"
    evidence_seen: list[str] = field(default_factory=list)
    hypotheses: list[dict] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    mitigation_status: str = "not_started"
    diagnosis: str = ""


INCIDENT = {
    "id": "aws-vpc-001",
    "title": "Production API Intermittent 504s",
    "severity": "SEV-2",

    "briefing": (
        "At 02:13 UTC, the production API began returning intermittent "
        "504 errors. Error rate increased from 0.2% to 18%. CPU and "
        "memory are normal. Database connections are increasing. "
        "A deployment completed 17 minutes before the alert. "
        "You are the on-call DevOps engineer."
    ),

    "root_cause": (
        "The api 2.8.0 deployment introduced a database-access "
        "regression that caused database connection-pool exhaustion. "
        "The application became slow and requests eventually timed "
        "out at the load balancer."
    ),

    "prevention_points": [
        "Review and correct the database access-layer change.",
        "Add database connection-pool saturation monitoring.",
        "Add deployment rollback thresholds.",
        "Load-test the new order-query path before production rollout.",
    ],
}


EVIDENCE = {
    "alb": """ALB metrics — last 30 minutes

RequestCount: normal
HTTPCode_ELB_5XX_Count: normal
HTTPCode_Target_5XX_Count: increased from 0.1% to 2.4%
TargetResponseTime p95: increased from 180ms to 4.8s
HealthyHostCount: 6/6

The ALB itself appears healthy while target response latency has increased.""",

    "health": """Target health

Healthy: 6
Unhealthy: 0

All targets pass the configured health check.
A passing health check does not prove the application is healthy
for real traffic.""",

    "logs": """Application logs — 02:10–02:16 UTC

02:13:04 WARN route=/orders db_wait=3210ms
02:13:07 WARN route=/orders db_wait=4180ms
02:13:09 ERROR route=/orders error="database connection pool exhausted"
02:13:10 ERROR route=/orders error="database connection pool exhausted"
02:14:02 WARN active_db_connections=498 max_connections=500

The errors began shortly after the deployment.""",

    "flow": """VPC Flow Logs

Application subnet -> RDS subnet: ACCEPT
No significant REJECT records during the incident window.
NAT Gateway traffic is normal.

A basic networking/security filtering failure is less likely.""",

    "routes": """Private application subnet route table

10.0.0.0/16 -> local
0.0.0.0/0 -> nat-0abc123

RDS subnet route table

10.0.0.0/16 -> local

Expected local routing exists between application and RDS.""",

    "sg": """Security groups

ALB SG -> application SG: TCP/443 allowed
Application SG -> RDS SG: TCP/5432 allowed
RDS SG source: application SG

No recent security-group changes detected.""",

    "deployment": """Deployment record

02:04 UTC — api-prod deployment started
02:08 UTC — deployment completed
02:13 UTC — error rate begins rising

Version: api 2.7.3 -> 2.8.0

Change summary:
- modified database access layer
- introduced new order-query code
- no infrastructure changes""",

    "rds": """RDS metrics

Database CPU: 41%
Database free memory: normal
Database connections: 498 / 500
Database connection attempts: sharply increased
Read/write latency: mildly elevated

The database is close to its connection limit.""",
}


def new_state():
    return IncidentState(incident_id=INCIDENT["id"])


def evidence_key(text: str):
    text = text.lower()

    mappings = [
        (["alb", "load balancer"], "alb"),
        (["target health", "target status", "health check"], "health"),
        (["application logs", "app logs", "logs"], "logs"),
        (["flow logs", "vpc flow", "network flow"], "flow"),
        (["route table", "routing", "routes"], "routes"),
        (["security group", "security groups", "sg"], "sg"),
        (["deployment", "deploy", "release"], "deployment"),
        (["rds", "database metrics", "db metrics",
          "database connections"], "rds"),
    ]

    for phrases, key in mappings:
        if any(phrase in text for phrase in phrases):
            return key

    return None


def interpret_request(text: str, state: IncidentState):

    key = evidence_key(text)

    if key:

        if key not in state.evidence_seen:
            state.evidence_seen.append(key)

        state.actions.append(text)

        return EVIDENCE[key], key

    text_lower = text.lower()

    if any(
        word in text_lower
        for word in ["rollback", "roll back", "revert"]
    ):

        state.actions.append(text)
        state.mitigation_status = "completed"

        return (
            "Rollback requested. Version 2.7.3 is being restored. "
            "For this simulation, error rate is returning toward normal. "
            "Continue with root-cause analysis and explain why the "
            "rollback was justified.",
            "rollback",
        )

    if any(
        word in text_lower
        for word in [
            "hypothesis",
            "i think",
            "i suspect",
            "likely cause",
        ]
    ):

        state.actions.append(text)

        state.hypotheses.append({
            "statement": text,
            "confidence": None,
        })

        return (
            "Hypothesis recorded. Continue gathering evidence and "
            "tell me what signal would increase or decrease your "
            "confidence.",
            "hypothesis",
        )

    state.actions.append(text)

    return (
        "Make the investigation request concrete. Try ALB metrics, "
        "target health, application logs, VPC Flow Logs, route tables, "
        "security groups, RDS metrics, or deployment history.",
        "unknown",
    )

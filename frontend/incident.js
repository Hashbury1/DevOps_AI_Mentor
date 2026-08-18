let incidentId = null;

const $ = (id) => document.getElementById(id);

function showError(message) {
    const box = $("error");

    if (!box) {
        alert(message);
        return;
    }

    box.textContent = message;
    box.classList.remove("hidden");
}

function clearError() {
    const box = $("error");

    if (box) {
        box.textContent = "";
        box.classList.add("hidden");
    }
}

function addMessage(type, text) {
    const chat = $("chat");

    const message = document.createElement("div");
    message.className = "message " + type;

    const label = document.createElement("strong");
    label.textContent = type === "ai" ? "DevOpsMentor" : "You";

    const content = document.createElement("p");
    content.textContent = String(text ?? "");

    message.appendChild(label);
    message.appendChild(content);

    chat.appendChild(message);
}

async function api(url, options = {}) {

    const response = await fetch(url, options);

    let data;

    try {
        data = await response.json();
    } catch (error) {
        throw new Error("The server returned invalid JSON.");
    }

    if (!response.ok) {
        throw new Error(
            data.detail ||
            data.message ||
            "API request failed."
        );
    }

    return data;
}


async function startIncident() {

    try {

        const data = await api(
            "/api/incidents/start",
            {
                method: "POST"
            }
        );

        incidentId = data.incident_id;

        $("briefing").innerHTML = "";

        const title = document.createElement("h2");
        title.textContent = data.title;

        const severity = document.createElement("p");
        severity.textContent = "Severity: " + data.severity;

        const briefing = document.createElement("p");
        briefing.textContent = data.briefing;

        $("briefing").appendChild(title);
        $("briefing").appendChild(severity);
        $("briefing").appendChild(briefing);

        addMessage(
            "ai",
            "You are now the on-call DevOps engineer. Begin your investigation."
        );

        await refreshState();

    } catch (error) {

        showError(
            "Could not start incident: " + error.message
        );
    }
}


async function refreshState() {

    if (!incidentId) {
        return;
    }

    const data = await api(
        "/api/incidents/" +
        incidentId +
        "/state"
    );

    renderState(data);
}


function renderState(data) {

    const state = $("state");

    state.innerHTML = "";

    addStateRow(
        state,
        "Stage",
        data.stage
    );

    addStateRow(
        state,
        "Evidence",
        data.evidence_seen.length
            ? data.evidence_seen.join(", ")
            : "None yet"
    );

    addStateRow(
        state,
        "Actions",
        data.actions_count
    );

    addStateRow(
        state,
        "Mitigation",
        data.mitigation_status
    );

    addStateRow(
        state,
        "Hypotheses",
        data.hypotheses.length
    );
}


function addStateRow(parent, label, value) {

    const row = document.createElement("p");

    const strong = document.createElement("strong");

    strong.textContent = label + ": ";

    row.appendChild(strong);

    row.appendChild(
        document.createTextNode(
            String(value ?? "")
        )
    );

    parent.appendChild(row);
}


$("investigateForm").addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();

        clearError();

        const message =
            $("message").value.trim();

        if (!message) {
            return;
        }

        if (!incidentId) {
            showError("Incident has not started.");
            return;
        }

        addMessage(
            "user",
            message
        );

        $("message").value = "";

        try {

            const data = await api(
                "/api/incidents/" +
                incidentId +
                "/investigate",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );

            addMessage(
                "ai",
                data.response
            );

            await refreshState();

        } catch (error) {

            showError(
                "Investigation failed: " +
                error.message
            );
        }
    }
);


$("submitDiagnosis").addEventListener(
    "click",
    async function() {

        clearError();

        const diagnosis =
            $("diagnosis").value.trim();

        if (!incidentId) {

            showError(
                "Incident has not started."
            );

            return;
        }

        if (diagnosis.length < 10) {

            showError(
                "Please provide a proper diagnosis."
            );

            return;
        }

        try {

            const data = await api(
                "/api/incidents/" +
                incidentId +
                "/diagnosis",

                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        diagnosis: diagnosis
                    })
                }
            );

            console.log(
                "Evaluation received:",
                data
            );

            renderEvaluation(data);

            await refreshState();

        } catch (error) {

            showError(
                "Evaluation failed: " +
                error.message
            );
        }
    }
);


function renderEvaluation(data) {

    const evaluation =
        $("evaluation");

    evaluation.innerHTML = "";

    evaluation.classList.remove(
        "hidden"
    );


    // SCORE

    const eyebrow =
        document.createElement("p");

    eyebrow.className = "eyebrow";

    eyebrow.textContent =
        "INCIDENT EVALUATION";


    const heading =
        document.createElement("h2");

    heading.textContent =
        "Overall Score: " +
        String(data.overall_score ?? 0) +
        "/100";


    evaluation.appendChild(
        eyebrow
    );

    evaluation.appendChild(
        heading
    );


    // SCORES

    const scoreTitle =
        document.createElement("h3");

    scoreTitle.textContent =
        "Performance Breakdown";

    evaluation.appendChild(
        scoreTitle
    );


    const scores =
        document.createElement("div");

    scores.className = "scores";


    const labels = {

        initial_triage:
            "Initial Triage",

        evidence_gathering:
            "Evidence Gathering",

        hypothesis_quality:
            "Hypothesis Quality",

        aws_reasoning:
            "AWS Reasoning",

        prioritization:
            "Investigation Prioritization",

        mitigation:
            "Mitigation",

        root_cause:
            "Root Cause Analysis",

        prevention:
            "Prevention"
    };


    Object.entries(
        data.scores || {}
    ).forEach(
        ([key, value]) => {

            const row =
                document.createElement("div");

            row.className = "score";


            const name =
                document.createElement("span");

            name.textContent =
                labels[key] || key;


            const number =
                document.createElement("strong");

            number.textContent =
                String(value ?? 0);


            row.appendChild(name);

            row.appendChild(number);

            scores.appendChild(row);
        }
    );


    evaluation.appendChild(
        scores
    );


    // STRENGTHS

    addEvaluationList(
        evaluation,
        "What You Did Well",
        data.strengths
    );


    // IMPROVEMENTS

    addEvaluationList(
        evaluation,
        "Areas To Improve",
        data.improvement_areas
    );


    // ROOT CAUSE

    const rootTitle =
        document.createElement("h3");

    rootTitle.textContent =
        "Expected Root Cause";

    evaluation.appendChild(
        rootTitle
    );


    const root =
        document.createElement("p");

    root.textContent =
        data.expected_root_cause ||
        "No root cause returned.";

    evaluation.appendChild(
        root
    );


    // PREVENTION

    addEvaluationList(
        evaluation,
        "Prevention Points",
        data.prevention_points
    );


    evaluation.scrollIntoView({
        behavior: "smooth"
    });
}


function addEvaluationList(
    parent,
    title,
    items
) {

    const heading =
        document.createElement("h3");

    heading.textContent =
        title;

    parent.appendChild(
        heading
    );


    const list =
        document.createElement("ul");


    if (
        !Array.isArray(items) ||
        items.length === 0
    ) {

        const item =
            document.createElement("li");

        item.textContent =
            "None identified.";

        list.appendChild(
            item
        );

    } else {

        items.forEach(
            function(text) {

                const item =
                    document.createElement("li");

                item.textContent =
                    String(text ?? "");

                list.appendChild(
                    item
                );
            }
        );
    }


    parent.appendChild(
        list
    );
}


startIncident();
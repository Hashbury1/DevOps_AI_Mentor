let incidentId = null;
const $ = id => document.getElementById(id);
const esc = x => String(x).replace(/[&<>"']/g, c => ({
  "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
}[c]));

function add(role, text) {
  const div = document.createElement("div");
  div.className = "message " + role;
  div.innerHTML = `<strong>${role === "ai" ? "DevOpsMentor" : "You"}</strong><p>${esc(text)}</p>`;
  $("chat").appendChild(div);
  div.scrollIntoView({behavior:"smooth"});
}

function renderState(s) {
  $("state").innerHTML = `
    <p><b>Stage:</b> ${esc(s.stage)}</p>
    <p><b>Evidence:</b> ${s.evidence_seen.length ? esc(s.evidence_seen.join(", ")) : "None yet"}</p>
    <p><b>Actions:</b> ${s.actions.length}</p>
    <p><b>Mitigation:</b> ${esc(s.mitigation_status)}</p>
    <p><b>Hypotheses:</b> ${s.hypotheses.length}</p>
  `;
}

async function start() {
  const r = await fetch("/api/incidents/start", {method:"POST"});
  const d = await r.json();
  incidentId = d.incident_id;
  $("briefing").innerHTML =
    `<b>${esc(d.severity)}</b><h2>${esc(d.title)}</h2><p>${esc(d.briefing)}</p>` +
    `<p><strong>Your job:</strong> investigate, form hypotheses, mitigate safely, then provide an RCA.</p>`;
  add("ai", "You are now on call. What is your first investigation step?");
  await refreshState();
}

async function refreshState() {
  const r = await fetch(`/api/incidents/${incidentId}/state`);
  const s = await r.json();
  renderState(s);
}

$("form").onsubmit = async e => {
  e.preventDefault();
  const message = $("message").value.trim();
  if (!message) return;
  add("user", message);
  $("message").value = "";

  const r = await fetch(`/api/incidents/${incidentId}/investigate`, {
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify({message})
  });
  const d = await r.json();
  add("ai", d.response);
  renderState(d.state);
};

$("submitDiagnosis").onclick = async () => {
  const diagnosis = $("diagnosis").value.trim();
  if (!diagnosis) return;
  const r = await fetch(`/api/incidents/${incidentId}/diagnosis`, {
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify({diagnosis})
  });
  const d = await r.json();
  $("diagnosisResult").innerHTML = `<div class="notice">${esc(d.message)}</div>`;
  await refreshState();
};

start();

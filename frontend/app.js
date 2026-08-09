let sessionId=null;
const $=id=>document.getElementById(id);
function esc(v){return v.replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));}
function msg(role,text){const d=document.createElement("div");d.className="message "+role;
d.innerHTML=`<div class="role">${role==="ai"?"AI Mentor":"You"}</div><div>${esc(text)}</div>`;
$("chat").appendChild(d);d.scrollIntoView({behavior:"smooth"});}
$("start").onclick=async()=>{
const r=await fetch("/api/interviews",{method:"POST",headers:{"Content-Type":"application/json"},
body:JSON.stringify({topic:$("topic").value,difficulty:$("difficulty").value})});const d=await r.json();
sessionId=d.session_id;$("setup").classList.add("hidden");$("interview").classList.remove("hidden");
$("chat").innerHTML="";$("progress").textContent=`Question 1/${d.total_questions}`;msg("ai",d.question);};
$("answerForm").onsubmit=async e=>{e.preventDefault();const a=$("answer").value.trim();if(!a)return;
msg("user",a);$("answer").value="";
const r=await fetch(`/api/interviews/${sessionId}/answer`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({answer:a})});
const d=await r.json();$("liveScore").textContent=`Latest score: ${d.score}%`;msg("ai",`${d.evaluation}\n\nScore: ${d.score}%`);
if(d.completed){$("answerForm").classList.add("hidden");$("progress").textContent="Interview complete";showReport();}
else{$("progress").textContent=`Question ${d.question_number}/${d.total_questions}`;msg("ai",d.next_question);}};
async function showReport(){const r=await fetch(`/api/interviews/${sessionId}/report`);const d=await r.json();
$("report").classList.remove("hidden");$("report").innerHTML=`<p class="eyebrow">INTERVIEW REPORT</p><h2>${d.score}%</h2>
<p><strong>Topic:</strong> ${esc(d.topic)}</p><p><strong>Difficulty:</strong> ${esc(d.difficulty)}</p>
<h3>Recommendation</h3><p>${esc(d.recommendation)}</p><button onclick="location.reload()">Start another interview</button>`;}

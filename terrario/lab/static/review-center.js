const $ = (selector) => document.querySelector(selector);
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[char]));
let session;

async function v1(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (options.method && options.method !== "GET") headers["X-CSRF-Token"] = session.csrf_token;
  const response = await fetch(`/api/v1/${path}`, { ...options, headers });
  const payload = await response.json();
  if (!response.ok) throw new Error(`${payload.error?.code || "REQUEST_FAILED"} · ${payload.error?.message || response.statusText}`);
  return payload.data;
}

async function legacyPost(path, body) {
  const response = await fetch(`/api/${path}`, { method:"POST", headers:{ "Content-Type":"application/json" }, body:JSON.stringify(body) });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "REQUEST_FAILED");
  return payload;
}

async function legacyGet(path) {
  const response = await fetch(`/api/${path}`);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "REQUEST_FAILED");
  return payload;
}

function reviewCard(review) {
  const pending = !review.latest_decision;
  const hash = review.artifact_hash || "HASH_UNAVAILABLE";
  const card = document.createElement("article");
  card.className = `review ${pending ? "pending" : "decided"}`;
  card.innerHTML = `<div class="facts"><div class="fact"><small>Solicitud</small><code>${escapeHtml(review.review_id)}</code></div><div class="fact"><small>Tipo</small><strong>${escapeHtml(review.review_kind)}</strong></div><div class="fact"><small>Estado</small><strong>${pending ? "PENDIENTE" : escapeHtml(review.latest_decision)}</strong></div><div class="fact"><small>Versión exacta</small><code>${escapeHtml(review.artifact_version_id)}</code></div><div class="fact"><small>Hash científico</small><code>${escapeHtml(hash)}</code></div></div><p style="margin:10px 0 0"><strong>Solicitud:</strong> ${escapeHtml(review.reason)}</p>`;
  if (!pending) return card;
  if (review.review_kind !== "EXPERIMENT_DESIGN") {
    card.insertAdjacentHTML("beforeend", `<p class="warning">La revisión de preregistro se completa en el panel Preregistros, donde se muestran sus warnings y ceremonia de lock.</p>`);
    return card;
  }
  const ceremony = `REVIEW ${hash.slice(0, 12)}`;
  card.insertAdjacentHTML("beforeend", `<label>Decisión<select><option value="APPROVE_FOR_EXPERIMENT_DESIGN">Aprobar diseño para experimento</option><option value="REQUEST_CHANGES">Solicitar cambios</option><option value="REJECT">Rechazar</option></select></label><label>Razón humana<textarea required placeholder="Explica qué revisaste y por qué tomas esta decisión."></textarea></label><label id="approvalCeremony">Para aprobar, escriba <code>${escapeHtml(ceremony)}</code><input autocomplete="off" spellcheck="false"></label><button disabled>Registrar decisión auditada</button><p class="status" aria-live="polite"></p>`);
  const [select, reason, confirmation, ceremonyLabel, button, result] = [card.querySelector("select"), card.querySelector("textarea"), card.querySelector("input"), card.querySelector("#approvalCeremony"), card.querySelector("button"), card.querySelector("[aria-live]")];
  const canSubmit = () => !!reason.value.trim() && (select.value !== "APPROVE_FOR_EXPERIMENT_DESIGN" || confirmation.value === ceremony);
  const refresh = () => { ceremonyLabel.hidden = select.value !== "APPROVE_FOR_EXPERIMENT_DESIGN"; button.disabled = !canSubmit(); };
  reason.addEventListener("input", refresh); confirmation.addEventListener("input", refresh); select.addEventListener("change", refresh); refresh();
  button.onclick = async () => {
    button.disabled = true; result.textContent = "Registrando decisión…";
    try {
      const decision = await v1(`review-requests/${encodeURIComponent(review.review_id)}/decisions`, { method:"POST", body:JSON.stringify({ artifact_hash:hash, decision:select.value, reason:reason.value.trim() }) });
      result.className = "good"; result.textContent = `Decisión ${decision.decision_id} registrada. No se ejecutó ciencia.`;
      await loadReviews();
    } catch (error) { result.className = "error"; result.textContent = error.message; button.disabled = false; }
  };
  return card;
}

async function loadReviews() {
  const target = $("#reviews");
  try {
    const { items } = await v1("review-requests");
    const pending = items.filter((item) => !item.latest_decision).reverse();
    const decided = items.filter((item) => item.latest_decision).reverse();
    target.replaceChildren();
    const heading = document.createElement("h3");
    heading.textContent = pending.length ? `${pending.length} revisión(es) pendiente(s)` : "No hay revisiones pendientes";
    target.append(heading, ...(pending.map(reviewCard)));
    if (decided.length) {
      const history = document.createElement("details");
      history.innerHTML = `<summary>${decided.length} revisión(es) ya decidida(s) · historial</summary>`;
      history.append(...decided.map(reviewCard));
      target.append(history);
    }
    if (!items.length) target.insertAdjacentText("beforeend", "No hay solicitudes de revisión locales.");
  } catch (error) { target.className = "error"; target.textContent = error.message; }
}

async function checkD2() {
  const output = $("#d2Result"); output.className = "status"; output.textContent = "Validando contrato y fixture D2…";
  const request = { world_id:"D2", draft_id:"d2-review-center-check", purpose:"Human-facing D2 validation only; no persistence or execution.", dimensions:[10,10], action_availability:["MOVE","PUSH","CONSUME","INSPECT","NOOP"], seed:42 };
  try {
    const [validation, fixture] = await Promise.all([legacyPost("worlds/validate", request), legacyGet("studio/d2/visual-fixture")]);
    if (!validation.valid || fixture.agent_executed || fixture.evidence_graph_writes !== 0 || fixture.scientific_result_writes !== 0 || !fixture.frames?.length) throw new Error("D2 did not satisfy its read-only validation contract");
    output.className = "good"; output.textContent = `D2 válido · ${validation.findings.length} hallazgos · fixture ${fixture.fixture_id} · ${fixture.frames.length} frames · sin agente, evidencia ni resultados.`;
  } catch (error) { output.className = "error"; output.textContent = error.message; }
}

async function boot() {
  try {
    session = await v1("session");
    const health = await v1("health");
    $("#health").innerHTML = `<p class="good"><strong>${escapeHtml(health.status)}</strong> · base ${escapeHtml(health.database)}</p><p class="status">Migraciones: ${escapeHtml(health.migrations?.status || "checked")}. Ejecución científica: ${escapeHtml(String(health.scientific_execution))}.</p>`;
    await loadReviews();
  } catch (error) { $("#health").className = "error"; $("#health").textContent = error.message; }
}

$("#checkD2").onclick = checkD2;
boot();

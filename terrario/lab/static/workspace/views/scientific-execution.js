/** Raw-artifact execution panel.  It deliberately cannot publish evidence. */
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
const short = (value, size = 12) => (value ? `${String(value).slice(0, size)}…` : "—");

/**
 * Command legality mirrors `execution/service.py`. The server remains the only
 * authority; the panel simply stops offering a transition it knows is illegal,
 * so a disabled control is a statement about the protocol, not a UI opinion.
 */
const COMMAND_STATES = {
  START: ["READY"],
  PAUSE: ["RUNNING"],
  RESUME: ["PAUSED"],
  CANCEL: ["REQUESTED", "VALIDATING", "AUTHORIZED", "PLANNED", "READY", "RUNNING", "PAUSED", "PAUSING"],
};
const NEXT_STEP = {
  REQUESTED: "Cree una autorización explícita para este root.",
  VALIDATING: "La autorización se está validando contra el root.",
  AUTHORIZED: "Falta sellar el plan de ejecución.",
  PLANNED: "El plan está sellado; espere READY.",
  READY: "Puede iniciar. START consume la autorización.",
  RUNNING: "Observe en World2D Scientific; no modifique el protocolo.",
  PAUSING: "Pausa solicitada; se confirma en una frontera segura.",
  PAUSED: "Reanude o cancele según el protocolo.",
  COMPLETED: "Verifique integridad. COMPLETED no es evidencia confirmatoria.",
  RECOVERY_REQUIRED: "Expiró el lease o se interrumpió el estado: use recuperación explícita.",
  FAILED: "Estado terminal. Conserve el registro y diagnostique antes de rediseñar.",
  CANCELLED: "Estado terminal por cancelación explícita.",
  ABORTED: "Estado terminal. Conserve la razón registrada.",
};

export class ScientificExecutionPanel {
  constructor(api, { onError } = {}) { this.api = api; this.onError = onError || (() => {}); this.container = null; this.execution = null; }
  render(container) {
    this.container = container;
    container.innerHTML = `<section class="scientific-execution" aria-label="Scientific execution"><header><strong>SCIENTIFIC EXECUTION</strong> <span class="ws-mode-badge pinned">RAW ARTIFACTS · NOT EVIDENCE</span></header>
      <p>Requires an exact locked preregistration root and a human authorization. Locking is not execution authorization.</p>
      <div id="seSummary" class="se-summary" role="status" aria-live="polite">Sin ejecución seleccionada. Empiece por un root de preregistro bloqueado.</div>
      <label>Locked root <input id="seRoot" autocomplete="off" size="68" spellcheck="false" placeholder="64 caracteres hexadecimales del root bloqueado" aria-describedby="seRootHint" aria-label="Exact preregistration root"></label>
      <p id="seRootHint" class="se-hint">64 hex. Se obtiene al bloquear un preregistro en <a href="/?view=preregistrations" target="_blank" rel="noopener">Lab · Preregistros</a>; no es un identificador que se pueda escribir de memoria.</p>
      <button id="seRequest">Request</button>
      <fieldset><legend>Explicit authorization</legend><label>Mode <select id="seMode"><option>ONE_EXECUTION</option><option>N_EXECUTIONS</option><option>REPLICATION_SERIES</option><option>UNTIL_EXPIRY</option></select></label><label>Maximum <input id="seCount" type="number" min="1" value="1"></label><label>Reason <input id="seReason" value="local scientific execution"></label><button id="seAuthorize">Authorize selected root</button></fieldset>
      <div role="toolbar" aria-label="Scientific execution controls"><button data-command="START" disabled>Start</button><button data-command="PAUSE" disabled>Pause at safe boundary</button><button data-command="RESUME" disabled>Resume</button><button data-command="CANCEL" disabled>Cancel</button><button id="seVerify" disabled>Verify integrity</button></div>
      <details id="seDetails"><summary>Registro completo de la ejecución · identidad y procedencia</summary><pre id="seStatus" aria-live="polite">No scientific execution selected.</pre></details></section>`;
    container.querySelector("#seRequest").onclick = () => this.request();
    container.querySelector("#seAuthorize").onclick = () => this.authorize();
    container.querySelectorAll("[data-command]").forEach((button) => { button.onclick = () => this.command(button.dataset.command); });
    container.querySelector("#seVerify").onclick = () => this.verify();
    container.querySelector("#seRoot").oninput = () => this._validateRootField();
    void this.refresh();
  }
  async request() { try { this.execution = await this.api.requestScientificExecution(this._root()); this._show(); } catch (error) { this._error(error); } }
  async authorize() { try { const root = this._root(), mode = this.container.querySelector("#seMode").value, count = Number(this.container.querySelector("#seCount").value); const auth = await this.api.authorizeScientificExecution({ preregistration_root_hash: root, scope_type: mode, max_execution_count: mode === "ONE_EXECUTION" ? 1 : count, reason: this.container.querySelector("#seReason").value, resource_ceiling: { cpu_cores: 1, gpu_devices: [], memory_bytes: 1073741824, disk_bytes: 1073741824, max_processes: 1, wall_clock_seconds: 3600 }, ...(mode === "REPLICATION_SERIES" ? { replication_group_id: `local-${root.slice(0, 12)}` } : {}), ...(mode === "UNTIL_EXPIRY" ? { expires_at: new Date(Date.now() + 86400000).toISOString() } : {}) }); if (!this.execution) this.execution = await this.api.requestScientificExecution(root); this.execution = await this.api.bindScientificAuthorization(this.execution.execution_id, auth.authorization_id, this.execution.revision); this.execution = await this.api.sealScientificPlan(this.execution.execution_id, this.execution.revision); this._show(); } catch (error) { this._error(error); } }
  async command(command) { if (!this.execution) return; try { this.execution = await this.api.scientificCommand(this.execution.execution_id, command, crypto.randomUUID(), this.execution.revision); if (command === "START" || command === "RESUME") this.execution = await this.api.dispatchScientificExecution(this.execution.execution_id); this._show(); } catch (error) { this._error(error); } }
  async verify() { if (!this.execution) return; try { const report = await this.api.verifyScientificExecution(this.execution.execution_id); this.container.querySelector("#seDetails").open = true; this.container.querySelector("#seStatus").textContent = JSON.stringify({ execution: this.execution, verification: report }, null, 2); } catch (error) { this._error(error); } }
  async refresh() { try { const rows = await this.api.scientificExecutions(); if ((rows.items || []).length) { this.execution = rows.items.at(-1); this._show(); } } catch { /* execution service may be absent during an older saved workspace */ } }
  _root() { const root = this.container.querySelector("#seRoot").value.trim(); if (!/^[a-f0-9]{64}$/.test(root)) throw new Error("An exact 64-character preregistration root is required."); return root; }
  /** Says what is wrong with the typed root while it is being typed, not after a failed request. */
  _validateRootField() {
    const input = this.container.querySelector("#seRoot"), hint = this.container.querySelector("#seRootHint"), value = input.value.trim();
    if (!value) { input.removeAttribute("aria-invalid"); hint.className = "se-hint"; hint.dataset.state = ""; return; }
    const valid = /^[a-f0-9]{64}$/.test(value);
    input.setAttribute("aria-invalid", valid ? "false" : "true");
    hint.className = valid ? "se-hint ok" : "se-hint warn";
    hint.dataset.state = valid ? "ROOT_SHAPE_OK" : `${value.length}/64 caracteres hex`;
  }
  _show() {
    if (!this.execution) return;
    const execution = this.execution, state = String(execution.state || "");
    // L0/L1: what this is, where it is, and what the protocol allows next.
    this.container.querySelector("#seSummary").innerHTML = `<span class="se-state se-state-${esc(state.toLowerCase())}">${esc(state)}</span>`
      + `<span>execution <code>${esc(short(execution.execution_id, 16))}</code></span>`
      + `<span>root <code>${esc(short(execution.preregistration_root_hash, 16))}</code></span>`
      + `<span>revision ${esc(execution.revision)}</span>`
      + `<span>plan <code>${esc(short(execution.plan_hash))}</code></span>`
      + `<em>${esc(NEXT_STEP[state] || "Estado sin guía registrada; consulte el registro completo.")}</em>`;
    for (const button of this.container.querySelectorAll("[data-command]")) {
      const legal = (COMMAND_STATES[button.dataset.command] || []).includes(state);
      button.disabled = !legal;
      button.title = legal ? "" : `${button.dataset.command} no es legal en estado ${state}`;
    }
    this.container.querySelector("#seVerify").disabled = false;
    this.container.querySelector("#seStatus").textContent = JSON.stringify(execution, null, 2);
  }
  _error(error) { this.onError("SCIENTIFIC_EXECUTION_ERROR", error.message, "Scientific Execution"); }
}

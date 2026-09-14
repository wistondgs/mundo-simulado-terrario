/**
 * Typed API client for the workspace. The frontend never touches SQLite
 * directly; it only calls these typed endpoints. Mutating scientific operations
 * require an explicit endpoint and carry the session CSRF token.
 */

const JSON_HEADERS = { "Content-Type": "application/json" };

export class ApiError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export class ApiClient {
  /**
   * @param {string} base - base URL (default "")
   */
  constructor(base = "") {
    this.base = base;
    this.csrfToken = null;
    this.sessionId = null;
  }

  async _fetch(path, options = {}) {
    const response = await fetch(`${this.base}${path}`, options);
    let body = null;
    try { body = await response.json(); } catch { body = null; }
    if (!response.ok) {
      const err = (body && body.error) || {};
      throw new ApiError(response.status, err.code || "REQUEST_FAILED",
                         err.message || response.statusText);
    }
    return body;
  }

  async get(path) {
    const body = await this._fetch(path);
    return body && body.data !== undefined ? body.data : body;
  }

  async post(path, payload, { mutation = false } = {}) {
    const headers = { ...JSON_HEADERS };
    // The backend authorizes every non-GET with the session CSRF token; send it
    // once initialized so read queries and mutations alike are accepted.
    if (this.csrfToken) headers["X-CSRF-Token"] = this.csrfToken;
    const body = await this._fetch(path, {
      method: "POST", headers, body: JSON.stringify(payload ?? {}),
    });
    return body && body.data !== undefined ? body.data : body;
  }

  /** Initialize the session (CSRF + session id) from the governance API. */
  async initSession() {
    const session = await this.get("/api/v1/session");
    this.sessionId = session.session_id || null;
    this.csrfToken = session.csrf_token || null;
    return session;
  }

  // ---- cross-graph ----
  crossGraphStatus() { return this.get("/api/v1/cross-graph"); }
  resolve(ref) { return this.post("/api/v1/cross-graph/resolve", ref); }
  graphSlice(ref, opts = {}) {
    return this.post("/api/v1/cross-graph/graph-slice", { ref, ...opts });
  }
  neighborhood(ref, opts = {}) {
    return this.post("/api/v1/cross-graph/traverse/neighborhood", { ref, ...opts });
  }
  typedPath(startRef, pattern, opts = {}) {
    return this.post("/api/v1/cross-graph/traverse/typed-path",
                     { start_ref: startRef, pattern, ...opts });
  }
  shortestPath(startRef, endRef, opts = {}) {
    return this.post("/api/v1/cross-graph/traverse/shortest-path",
                     { start_ref: startRef, end_ref: endRef, ...opts });
  }
  provenance(ref) { return this.post("/api/v1/cross-graph/provenance", { ref }); }
  lineage(ref, opts = {}) { return this.post("/api/v1/cross-graph/lineage", { ref, ...opts }); }
  history(ref) { return this.post("/api/v1/cross-graph/history", { ref }); }
  traceBreaks() { return this.get("/api/v1/cross-graph/trace-breaks"); }
  snapshots() { return this.get("/api/v1/cross-graph/snapshots"); }
  snapshotDiff(left, right) {
    return this.post("/api/v1/cross-graph/snapshots/diff",
                     { left_snapshot_id: left, right_snapshot_id: right });
  }
  verifyCrossGraph() { return this.get("/api/v1/cross-graph/verify"); }
  saveComposition(payload) {
    return this.post("/api/v1/cross-graph/compositions", payload, { mutation: true });
  }
  getComposition(id) { return this.get(`/api/v1/cross-graph/compositions/${encodeURIComponent(id)}`); }

  // ---- reference graph ----
  referenceGraphStatus() { return this.get("/api/v1/reference-graph"); }
  references() { return this.get("/api/v1/reference-graph/references"); }
  reference(id) { return this.get(`/api/v1/reference-graph/references/${encodeURIComponent(id)}`); }
  referenceClaims(id) {
    return this.get(`/api/v1/reference-graph/references/${encodeURIComponent(id)}/claims`);
  }
  referenceProtocol(id) {
    return this.get(`/api/v1/reference-graph/references/${encodeURIComponent(id)}/protocol`);
  }
  referenceProvenance(id) {
    return this.get(`/api/v1/reference-graph/references/${encodeURIComponent(id)}/provenance`);
  }
  findReferences(query) { return this.post("/api/v1/reference-graph/references/find", query); }
  findByConstruct(construct) {
    return this.post("/api/v1/reference-graph/find/by-construct", { construct });
  }
  searchClaims(text) { return this.post("/api/v1/reference-graph/claims/search", { text }); }
  projection(filters) { return this.post("/api/v1/reference-graph/projection", filters); }

  // ---- operational hypergraph (read-only architecture, never evidence) ----
  operationalHypergraph() { return this.get("/api/operational-hypergraph"); }

  // ---- world / scenario (legacy lab API) ----
  worldDefinition(worldId) { return this.get(`/api/worlds/${encodeURIComponent(worldId)}`); }
  worldPreview(worldId, seed) {
    return this.get(`/api/worlds/${encodeURIComponent(worldId)}/preview?seed=${seed}`);
  }
  runAgentView(runId, step) {
    return this.get(`/api/runs/${encodeURIComponent(runId)}/agent-view?step=${step}`);
  }
  runObserverView(runId, step) {
    return this.get(`/api/runs/${encodeURIComponent(runId)}/observer-view?step=${step}`);
  }

  // ---- scientific execution (raw artifacts only; never EvidenceGraph) ----
  scientificExecutions() { return this.get("/api/v1/scientific-executions"); }
  scientificExecution(id) { return this.get(`/api/v1/scientific-executions/${encodeURIComponent(id)}`); }
  requestScientificExecution(preregistration_root_hash) {
    return this.post("/api/v1/scientific-executions", { preregistration_root_hash }, { mutation: true });
  }
  authorizeScientificExecution(payload) { return this.post("/api/v1/execution-authorizations", payload, { mutation: true }); }
  bindScientificAuthorization(id, authorization_id, expected_revision) {
    return this.post(`/api/v1/scientific-executions/${encodeURIComponent(id)}/bind-authorization`, { authorization_id, expected_revision }, { mutation: true });
  }
  sealScientificPlan(id, expected_revision) {
    return this.post(`/api/v1/scientific-executions/${encodeURIComponent(id)}/plan`, { expected_revision }, { mutation: true });
  }
  scientificCommand(id, command, command_id, expected_revision) {
    return this.post(`/api/v1/scientific-executions/${encodeURIComponent(id)}/commands`, { command, command_id, expected_revision }, { mutation: true });
  }
  verifyScientificExecution(id) { return this.get(`/api/v1/scientific-executions/${encodeURIComponent(id)}/verify`); }
  scientificPlayback(id, trialId, attemptId, after = -1) {
    return this.get(`/api/v1/scientific-executions/${encodeURIComponent(id)}/trials/${encodeURIComponent(trialId)}/frames?attempt_id=${encodeURIComponent(attemptId)}&after_sequence=${after}`);
  }
}

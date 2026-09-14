/** Read-only junction view for the operational (not theory) hypergraph. */
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

export class OperationalHypergraphPanel {
  constructor(api, { onError } = {}) {
    this.api = api; this.onError = onError || (() => {}); this.edges = []; this.container = null;
  }

  render(container) {
    this.container = container;
    container.innerHTML = `<div id="operationalHypergraph" aria-live="polite">Loading operational hypergraph…</div>`;
    this.load();
  }

  async load() {
    try {
      const response = await this.api.operationalHypergraph();
      this.edges = response.hyperedges || [];
      this._draw(this.edges[0]);
    } catch (error) {
      this.onError("DOMAIN_UNAVAILABLE", error.message, "operational hypergraph");
      const target = this.container?.querySelector("#operationalHypergraph");
      if (target) target.textContent = "Operational hypergraph unavailable.";
    }
  }

  _draw(edge) {
    const target = this.container?.querySelector("#operationalHypergraph");
    if (!target || !edge) return;
    target.innerHTML = `
      <div style="display:flex;gap:6px;align-items:center;margin-bottom:8px">
        <label for="opHyperedge" style="font-size:12px">Relation</label>
        <select id="opHyperedge" style="min-width:0;flex:1">${this.edges.map((item) =>
          `<option value="${escapeHtml(item.edge_id)}"${item.edge_id === edge.edge_id ? " selected" : ""}>${escapeHtml(item.edge_id)} — ${escapeHtml(item.label)}</option>`).join("")}</select>
      </div>
      <div style="font-size:11px;color:var(--ws-muted);margin-bottom:8px">${escapeHtml(edge.output_classification)} · ${escapeHtml(edge.schema_version)}</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:6px;align-items:center">
        ${edge.members.map((member) => `<div style="border:1px solid var(--ws-border);border-radius:5px;padding:6px;background:var(--ws-panel-bg,#fff)">
          <strong style="display:block;font-size:11px">${escapeHtml(member.role)}</strong>
          <span style="font-size:10px;color:var(--ws-muted)">${escapeHtml(member.node_type)}${member.causal ? " · causal" : " · observational"}</span>
        </div>`).join("")}
      </div>
      <div style="margin:10px auto;padding:8px;border:2px solid #7a4d8a;border-radius:50%;max-width:210px;text-align:center;font-size:12px;background:#f5edf8">
        <strong>⬢ ${escapeHtml(edge.edge_id)}</strong><br>${escapeHtml(edge.output)}
      </div>
      <p style="font-size:12px;line-height:1.35;margin:8px 0">${escapeHtml(edge.semantics)}</p>
      <p style="font-size:11px;color:var(--ws-muted);margin:0">No EvidenceGraph output · read-only architecture</p>`;
    target.querySelector("#opHyperedge").onchange = (event) =>
      this._draw(this.edges.find((item) => item.edge_id === event.target.value));
  }
}

/**
 * Inspector + Provenance panel. Shows the selected object's detail and offers
 * provenance drilldown: Why is this here? Where did it come from? Who asserted
 * it? Which source / version / snapshot / rule? Was it reviewed? Claim type
 * classification is never hidden.
 */
import { CLAIM_TYPE_LABEL, DOMAIN_VISUAL } from "../core/contracts.js";

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function kv(entries) {
  return `<dl class="ws-kv">${entries.map(([k, v]) =>
    `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(v ?? "—")}</dd>`).join("")}</dl>`;
}

export class InspectorPanel {
  constructor(api, { onError } = {}) {
    this.api = api;
    this.onError = onError || (() => {});
    this.container = null;
  }

  render(container) {
    this.container = container;
    container.innerHTML = `<p style="color:var(--ws-muted)">Select an object to inspect it.</p>`;
  }

  async inspect(key) {
    if (!this.container) return;
    const [domain, entity_type, ...rest] = key.split(":");
    const entity_id = rest.join(":");
    const visual = DOMAIN_VISUAL[domain] || DOMAIN_VISUAL.ONTOLOGY;
    this.container.innerHTML = `
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
        <span style="font-size:20px;color:${visual.color}">${visual.icon}</span>
        <div><strong>${escapeHtml(entity_id)}</strong>
        <div style="font-size:11px;color:var(--ws-muted)">${escapeHtml(domain)} · ${escapeHtml(entity_type)}</div></div>
      </div>
      <div id="inspectorBody">Loading…</div>
      <div class="ws-section-title">Provenance</div>
      <div id="inspectorProvenance">—</div>`;
    try {
      if (domain === "REFERENCE") {
        await this._inspectReference(entity_id);
      } else {
        document.getElementById("inspectorBody").innerHTML = kv([
          ["Domain", domain], ["Type", entity_type], ["ID", entity_id]]);
      }
      await this.showProvenance(key);
    } catch (error) {
      this.onError("DOMAIN_UNAVAILABLE", error.message, key);
    }
  }

  async _inspectReference(referenceId) {
    const [record, claims, protocol, provenance] = await Promise.all([
      this.api.reference(referenceId).catch(() => null),
      this.api.referenceClaims(referenceId).catch(() => ({ items: [] })),
      this.api.referenceProtocol(referenceId).catch(() => null),
      this.api.referenceProvenance(referenceId).catch(() => null),
    ]);
    const body = document.getElementById("inspectorBody");
    if (!body) return;
    const claimItems = (claims.items || []);
    body.innerHTML = `
      ${record ? kv([
        ["Reference", record.reference_id],
        ["Type", record.reference_type],
        ["Status", record.status],
        ["Discipline", record.discipline],
        ["Verification", record.verification_status],
      ]) : ""}
      ${record && record.constructs ? `<div class="ws-section-title">Constructs</div>
        <div>${record.constructs.map((c) => `<span class="ws-tag">${escapeHtml(c)}</span>`).join("")}</div>` : ""}
      ${record && record.experimental_paradigms ? `<div class="ws-section-title">Paradigms</div>
        <div>${record.experimental_paradigms.map((p) => `<span class="ws-tag">${escapeHtml(p)}</span>`).join("")}</div>` : ""}
      ${protocol && Object.keys(protocol).length ? `<div class="ws-section-title">Protocol</div>
        ${kv(Object.entries(protocol).slice(0, 8))}` : ""}
      <div class="ws-section-title">Source claims (${claimItems.length})</div>
      ${claimItems.map((claim) => `
        <div style="border-left:3px solid var(--ws-border);padding:4px 8px;margin:4px 0">
          <span class="ws-tag candidate">${escapeHtml(CLAIM_TYPE_LABEL[claim.claim_type] || claim.claim_type)}</span>
          <div style="font-size:12px;margin-top:2px">${escapeHtml(claim.claim_text)}</div>
          <small style="color:var(--ws-muted)">${escapeHtml(claim.extraction_method || "")} · ${escapeHtml(claim.verification_status || "")}</small>
        </div>`).join("") || "<p>None recorded.</p>"}`;
  }

  async showProvenance(key) {
    const [domain, entity_type, ...rest] = key.split(":");
    const entity_id = rest.join(":");
    const target = document.getElementById("inspectorProvenance");
    if (!target) return;
    try {
      const prov = await this.api.provenance({ domain, entity_type, entity_id });
      const resolution = prov.resolution || {};
      target.innerHTML = `
        ${kv([
          ["Endpoint", resolution.status || "—"],
          ["Content hash", resolution.content_hash ? `${String(resolution.content_hash).slice(0, 16)}…` : "—"],
        ])}
        ${prov.domain_provenance && Object.keys(prov.domain_provenance).length ?
          `<div class="ws-section-title">Domain provenance</div>${kv(Object.entries(prov.domain_provenance).slice(0, 6))}` : ""}
        ${(prov.cross_links || []).length ? `<div class="ws-section-title">Cross-links</div>
          ${prov.cross_links.map((l) => `<div style="font-size:11px;margin:3px 0">
            <span class="ws-tag">${escapeHtml(l.relation_type)}</span> ${escapeHtml(l.provenance || "")}
            <br><small style="color:var(--ws-muted)">by ${escapeHtml(l.created_by || "")} · ${escapeHtml(l.created_at || "")}</small>
          </div>`).join("")}` : "<p>No cross-links.</p>"}`;
    } catch (error) {
      target.innerHTML = `<p style="color:var(--ws-muted)">Provenance unavailable.</p>`;
    }
  }
}

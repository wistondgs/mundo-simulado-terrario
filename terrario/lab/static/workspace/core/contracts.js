/**
 * Shared typed contracts for the Scientific Visual Workspace.
 *
 * These JSDoc typedefs mirror the backend schemas (cross-graph, reference
 * graph, world). They are the single source of truth for frontend shapes and
 * are exercised by contract tests to detect backend/frontend drift. No `any`
 * leaks into scientific state; every field that affects identity is explicit.
 */

/**
 * @typedef {Object} CrossDomainEntityRef
 * @property {string} domain - one of the 12 registered domains
 * @property {string} entity_type
 * @property {string} entity_id
 * @property {string|null} [version_id]
 * @property {string|null} [snapshot_id]
 * @property {string|null} [content_hash]
 * @property {string|null} [schema_version]
 */

/**
 * @typedef {Object} GraphNode
 * @property {string} key - canonical DOMAIN:entity_type:entity_id
 * @property {string} domain
 * @property {string} entity_type
 * @property {string} entity_id
 * @property {string} [label]
 * @property {string} [status]
 * @property {Object} [payload]
 */

/**
 * @typedef {Object} GraphEdge
 * @property {string} link_id
 * @property {string} source - source node key
 * @property {string} target - target node key
 * @property {string} relation_type
 * @property {string} assertion_class
 * @property {string} [provenance]
 */

/**
 * @typedef {Object} Hyperedge
 * @property {string} hyperlink_id
 * @property {Array<{ref: CrossDomainEntityRef, role: string}>} members
 * @property {string} relation_type
 * @property {string} [assertion_class]
 */

/**
 * @typedef {Object} GraphSlice
 * @property {string} center
 * @property {number} depth
 * @property {string[]} nodes
 * @property {number} node_count
 * @property {GraphEdge[]} edges
 * @property {Hyperedge[]} hyperedges
 * @property {Object<string,string>} provenance_summary
 * @property {string[]} warnings
 * @property {number|null} next_cursor
 * @property {{cross_graph_snapshot: string|null, root_hash: string|null}} snapshot_manifest
 */

/**
 * @typedef {Object} PathExplanation
 * @property {string} kind - GRAPH_PATH | PROVENANCE_PATH | DEPENDENCY_PATH | SCIENTIFIC_TRACE
 * @property {string[]} node_sequence
 * @property {Array<{link_id:string, relation_type:string, relation_meaning:string, provenance:string, assertion_class:string, direction:string}>} link_sequence
 * @property {number} depth
 * @property {string[]} warnings
 * @property {boolean} is_scientific_trace
 * @property {string} note
 */

/**
 * @typedef {Object} TraceBreak
 * @property {string} trace_break_id
 * @property {string} from
 * @property {string} expected_next_domain
 * @property {string} reason
 * @property {string} [missing_identity_or_relation]
 * @property {string} [resolution_state]
 * @property {string} [discovered_at]
 */

/**
 * @typedef {Object} ResearchComposition
 * @property {string} composition_id
 * @property {string} title
 * @property {number} version
 * @property {CrossDomainEntityRef[]} refs
 * @property {Array<Object>} local_links
 * @property {string} notes
 * @property {number} versions
 * @property {string} created_by
 * @property {string} created_at
 */

/**
 * @typedef {Object} ReferenceRecord
 * @property {string} reference_id
 * @property {string} reference_type
 * @property {string} status
 * @property {string[]} constructs
 * @property {string[]} experimental_paradigms
 * @property {Array<Object>} d_level_tags
 * @property {string} discipline
 * @property {string} verification_status
 */

/**
 * @typedef {Object} WorldViewState
 * @property {string} origin - RECORDED | LIVE | PREVIEW
 * @property {number} [grid_width]
 * @property {number} [grid_height]
 * @property {Object} [objects]
 * @property {Object} [agents]
 * @property {Array} [channels]
 * @property {Array} [mask]
 */

/** Domain visual language: shape + color + icon, never color alone. */
export const DOMAIN_VISUAL = Object.freeze({
  REFERENCE:       { shape: "document",  color: "#3f6fb5", icon: "📄", label: "Reference" },
  DOCUMENT:        { shape: "document",  color: "#5a5f6a", icon: "▤", label: "Document" },
  CLAIM:           { shape: "note",      color: "#b76816", icon: "❝", label: "Claim" },
  ONTOLOGY:        { shape: "diamond",   color: "#176b55", icon: "◈", label: "Concept" },
  RAW_CONCEPT:     { shape: "diamond",   color: "#4d8a6f", icon: "◇", label: "Raw concept" },
  CANONICAL_CONCEPT:{ shape: "diamond",  color: "#176b55", icon: "◆", label: "Canonical concept" },
  THEORY:          { shape: "hexagon",   color: "#237a8b", icon: "⬡", label: "Theory" },
  HYPEREDGE:       { shape: "junction",  color: "#7a4d8a", icon: "⬢", label: "Hyperedge" },
  HYPERGRAPH:      { shape: "junction",  color: "#7a4d8a", icon: "⬢", label: "Hyperedge" },
  HYPOTHESIS:      { shape: "ellipse",   color: "#a6443a", icon: "?", label: "Hypothesis" },
  SCENARIO:        { shape: "square",    color: "#8a6d3b", icon: "▦", label: "Scenario" },
  WORLD:           { shape: "grid",      color: "#55b993", icon: "⊞", label: "World" },
  EXPERIMENT:      { shape: "flask",     color: "#3a7ca5", icon: "⚗", label: "Experiment" },
  PREREGISTRATION: { shape: "lock",      color: "#6a5acd", icon: "🔒", label: "Preregistration" },
  EVIDENCE:        { shape: "star",      color: "#b08d2e", icon: "★", label: "Evidence" },
});

/** Claim type classification, always visible. */
export const CLAIM_TYPE_LABEL = Object.freeze({
  SOURCE_TEXT: "Source text",
  SOURCE_REPORTED_CLAIM: "Source-reported claim",
  ANALYST_INTERPRETATION: "Analyst interpretation",
  MACHINE_EXTRACTION_UNVERIFIED: "Machine extraction (unverified)",
  USER_NOTE: "User note",
});

/** Error classification for the UI error model. */
export const ERROR_CLASS = Object.freeze({
  DOMAIN_UNAVAILABLE: "DOMAIN_UNAVAILABLE",
  STALE_REFERENCE: "STALE_REFERENCE",
  HASH_MISMATCH: "HASH_MISMATCH",
  TRACE_BREAK: "TRACE_BREAK",
  UNREVIEWED_CANDIDATE: "UNREVIEWED_CANDIDATE",
  INTEGRITY_FAILURE: "INTEGRITY_FAILURE",
  QUERY_BUDGET_EXCEEDED: "QUERY_BUDGET_EXCEEDED",
});

/** Operating modes, never conflated. */
export const OPERATING_MODE = Object.freeze({
  EXPLORATORY_LATEST: "EXPLORATORY_LATEST",
  PINNED_REPRODUCIBLE: "PINNED_REPRODUCIBLE",
});

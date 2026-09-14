/**
 * Scientific Visual Workspace — application entry point.
 *
 * Orchestrates the multipanel shell, the scientific canvas, the explorer, the
 * inspectors, the research composition working layer, D2 studio, World2D, and
 * the command palette. The user manipulates the science; the system preserves
 * structure, provenance, and integrity. No UI action decides which theory is
 * correct, merges concepts, approves a hyperedge, picks a winning reference,
 * or declares intelligence.
 */
import { ApiClient } from "./core/api.js";
import { WorkspaceShell } from "./core/shell.js";
import {
  serverState, compositionState, selectionState, viewportState, transientState, journal,
} from "./core/state.js";
import { DOMAIN_VISUAL, CLAIM_TYPE_LABEL, OPERATING_MODE, ERROR_CLASS } from "./core/contracts.js";
import { GraphRenderer } from "./render/graph-renderer.js";
import { LayoutEngine } from "./render/layout-engine.js";
import { World2DPanel } from "./views/world2d.js";
import { ScientificExecutionPanel } from "./views/scientific-execution.js";
import { ScientificWorld2DPanel } from "./views/scientific-world2d.js";
import { D2Studio } from "./views/d2studio.js";
import { CompositionPanel } from "./views/composition.js";
import { InspectorPanel } from "./views/inspector.js";
import { ExplorerPanel } from "./views/explorer.js";
import { OperationalHypergraphPanel } from "./views/operational-hypergraph.js";
import { CommandPalette } from "./views/palette.js";

const api = new ApiClient();
const layout = new LayoutEngine();

const state = {
  graph: { nodes: [], edges: [], hyperedges: [] },
  renderer: null,
  shell: null,
  world2d: null,
  execution: null,
  scientificWorld: null,
  d2: null,
  composition: null,
  inspector: null,
  explorer: null,
  operationalHypergraph: null,
  palette: null,
};

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function showError(errorClass, message, context = "") {
  transientState.set({ error: { class: errorClass, message, context } });
  const banner = document.createElement("div");
  banner.className = `ws-error-banner ${errorClass}`;
  banner.setAttribute("role", "alert");
  banner.innerHTML = `<strong>${escapeHtml(errorClass)}</strong> ${escapeHtml(message)}${
    context ? `<div style="margin-top:4px;font-size:11px">${escapeHtml(context)}</div>` : ""}`;
  document.body.append(banner);
  setTimeout(() => banner.remove(), 6000);
}

// ---------------------------------------------------------------- canvas
function buildCanvas(container) {
  const wrap = document.createElement("div");
  wrap.className = "ws-canvas-wrap";
  const toolbar = document.createElement("div");
  toolbar.className = "ws-canvas-toolbar";
  toolbar.innerHTML = `
    <button data-act="fit" title="Fit to selection">Fit</button>
    <select data-act="layout" title="Layout">
      <option value="force">Force</option>
      <option value="hierarchical">Hierarchical</option>
      <option value="radial">Radial</option>
    </select>
    <button data-act="expand" title="Expand neighborhood">Expand</button>
    <button data-act="ungroup" title="Clear selection">Clear</button>`;
  const canvas = document.createElement("canvas");
  canvas.setAttribute("aria-label", "Scientific graph canvas");
  wrap.append(toolbar, canvas);
  container.append(wrap);

  const renderer = new GraphRenderer(canvas, {
    onSelect: handleSelect,
    onExpand: handleExpand,
    onViewportChange: (viewport, extra) => {
      viewportState.set({ panX: viewport.panX, panY: viewport.panY, zoom: viewport.zoom });
      if (extra && extra.positions) persistPositions(extra.positions);
    },
  });
  state.renderer = renderer;

  toolbar.querySelector('[data-act="fit"]').onclick = () =>
    renderer.fitToNodes([...selectionState.get().selected]);
  toolbar.querySelector('[data-act="expand"]').onclick = () => {
    const key = selectionState.get().focusedKey || [...selectionState.get().selected][0];
    if (key) handleExpand(key);
  };
  toolbar.querySelector('[data-act="ungroup"]').onclick = () => handleSelect([], "box");
  toolbar.querySelector('[data-act="layout"]').onchange = async (e) => {
    viewportState.set({ layout: e.target.value });
    await relayout(e.target.value);
  };
}

async function relayout(kind = "force") {
  const { nodes, edges } = state.graph;
  let positions;
  if (kind === "hierarchical") positions = await layout.hierarchical(nodes, edges);
  else if (kind === "radial") positions = await layout.radial(nodes, edges, selectionState.get().focusedKey);
  else positions = await layout.forceDirected(nodes, edges);
  state.renderer.setPositions(positions);
  persistPositions(positions);
}

function persistPositions(positions) {
  const current = viewportState.get().nodePositions;
  viewportState.set({ nodePositions: { ...current, ...positions } });
}

// ---------------------------------------------------------------- selection
function handleSelect(keys, mode) {
  const current = new Set(selectionState.get().selected);
  let next;
  if (mode === "single") next = new Set([keys]);
  else if (mode === "toggle") {
    next = new Set(current);
    next.has(keys) ? next.delete(keys) : next.add(keys);
  } else next = new Set(keys);
  const focused = mode === "single" ? keys : (keys[0] || null);
  selectionState.set({ selected: next, focusedKey: focused, inspectedKey: focused, inspectedKind: "node" });
  state.renderer.setSelection([...next]);
  state.renderer.setFocus(focused);
  if (focused) state.inspector.inspect(focused);
}

async function handleExpand(key) {
  try {
    const ref = keyToRef(key);
    const slice = await api.graphSlice(ref, { depth: 1 });
    mergeSlice(slice);
    await relayout(viewportState.get().layout);
  } catch (error) {
    showError(error.code === "QUERY_BUDGET_EXCEEDED" ? ERROR_CLASS.QUERY_BUDGET_EXCEEDED
             : ERROR_CLASS.DOMAIN_UNAVAILABLE, error.message, key);
  }
}

function keyToRef(key) {
  const [domain, entity_type, ...rest] = key.split(":");
  return { domain, entity_type, entity_id: rest.join(":") };
}

function mergeSlice(slice) {
  const existing = new Map(state.graph.nodes.map((n) => [n.key, n]));
  for (const key of slice.nodes) {
    if (!existing.has(key)) {
      const [domain, entity_type, ...rest] = key.split(":");
      existing.set(key, { key, domain, entity_type, entity_id: rest.join(":"),
                          label: rest.join(":"), x: 0, y: 0 });
    }
  }
  const edgeKeys = new Set(state.graph.edges.map((e) => e.link_id));
  const newEdges = (slice.edges || []).filter((e) => !edgeKeys.has(e.link_id));
  const hyperKeys = new Set(state.graph.hyperedges.map((h) => h.hyperlink_id));
  const newHyper = (slice.hyperedges || []).filter((h) => !hyperKeys.has(h.hyperlink_id));
  state.graph = {
    nodes: [...existing.values()],
    edges: [...state.graph.edges, ...newEdges],
    hyperedges: [...state.graph.hyperedges, ...newHyper],
  };
  state.renderer.setGraph(state.graph);
  viewportState.set({ pinnedSnapshot: slice.snapshot_manifest });
  updateSnapshotBadge(slice.snapshot_manifest);
}

function updateSnapshotBadge(manifest) {
  const el = document.getElementById("wsSnapshot");
  if (manifest && manifest.root_hash) {
    el.textContent = `snapshot: ${String(manifest.root_hash).slice(0, 12)}…`;
  }
}

// ---------------------------------------------------------------- boot
async function boot() {
  const root = document.getElementById("wsRoot");
  const shell = new WorkspaceShell(root);
  state.shell = shell;

  state.explorer = new ExplorerPanel(api, { onOpen: handleExplorerOpen });
  state.operationalHypergraph = new OperationalHypergraphPanel(api, { onError: showError });
  state.inspector = new InspectorPanel(api, { onError: showError });
  state.composition = new CompositionPanel(api, { onError: showError });
  state.world2d = new World2DPanel(api, { onError: showError });
  state.execution = new ScientificExecutionPanel(api, { onError: showError });
  state.scientificWorld = new ScientificWorld2DPanel(api, { onError: showError });
  state.d2 = new D2Studio(api, { onError: showError, onOpenWorld: openWorld });

  shell.registerPanel("explorer", { title: "Explorer", region: "left",
    render: (el) => state.explorer.render(el) });
  shell.registerPanel("operational-hypergraph", { title: "Operational Hypergraph", region: "left",
    render: (el) => state.operationalHypergraph.render(el) });
  shell.registerPanel("canvas", { title: "Scientific Canvas", region: "center",
    render: (el) => { el.classList.add("no-pad"); buildCanvas(el); } });
  shell.registerPanel("inspector", { title: "Inspector", region: "right",
    render: (el) => state.inspector.render(el) });
  shell.registerPanel("composition", { title: "Research Composition", region: "right",
    render: (el) => state.composition.render(el) });
  shell.registerPanel("world", { title: "World2D", region: "bottom",
    render: (el) => state.world2d.render(el) });
  shell.registerPanel("execution", { title: "Scientific Execution", region: "bottom",
    render: (el) => state.execution.render(el) });
  shell.registerPanel("scientific-world", { title: "World2D Scientific", region: "bottom",
    render: (el) => state.scientificWorld.render(el) });
  shell.registerPanel("d2", { title: "D2 Scientific Studio", region: "bottom",
    render: (el) => state.d2.render(el) });
  shell.mount();

  state.palette = new CommandPalette(api, {
    onAction: handlePaletteAction,
  });
  document.getElementById("wsPaletteBtn").onclick = () => state.palette.toggle();
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      state.palette.toggle();
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z" && !e.shiftKey) {
      e.preventDefault();
      journal.undo();
    }
    if ((e.ctrlKey || e.metaKey) && (e.key.toLowerCase() === "y" ||
        (e.shiftKey && e.key.toLowerCase() === "z"))) {
      e.preventDefault();
      journal.redo();
    }
  });

  // initial data
  try {
    await api.initSession();
    const status = await api.crossGraphStatus();
    serverState.set({ status });
    document.getElementById("wsStatus").textContent =
      `links ${status.counts.links} · refs ${status.counts.references ?? "—"}`;
    const snapshots = await api.snapshots();
    serverState.set({ snapshots });
    if (snapshots.latest) updateSnapshotBadge(snapshots.latest);
    const breaks = await api.traceBreaks();
    serverState.set({ traceBreaks: breaks.items || [] });
    state.d2.setTraceBreaks(breaks.items || []);
    await seedGraph();
  } catch (error) {
    showError(ERROR_CLASS.DOMAIN_UNAVAILABLE, error.message, "initial load");
    document.getElementById("wsStatus").textContent = "degraded";
  }
}

async function seedGraph() {
  // Seed the canvas from the reference graph + cross-graph neighborhood.
  try {
    const refs = await api.references();
    serverState.set({ references: refs.items || [] });
    state.explorer.setReferences(refs.items || []);
    const first = (refs.items || [])[0];
    if (first) {
      const ref = { domain: "REFERENCE", entity_type: "ScientificReferenceRecord",
                    entity_id: first.reference_id };
      const slice = await api.graphSlice(ref, { depth: 1 });
      mergeSlice(slice);
      await relayout("force");
    }
  } catch (error) {
    // Degrade locally; the workspace still opens.
  }
}

function handleExplorerOpen(item) {
  if (item.kind === "reference") {
    openReference(item.id);
  } else if (item.kind === "world" || item.kind === "scenario") {
    openWorld(item.id);
  } else if (item.kind === "node") {
    handleSelect(item.id, "single");
  }
}

async function openReference(referenceId) {
  const ref = { domain: "REFERENCE", entity_type: "ScientificReferenceRecord", entity_id: referenceId };
  try {
    const slice = await api.graphSlice(ref, { depth: 1 });
    mergeSlice(slice);
    await relayout("force");
    state.inspector.inspect(`REFERENCE:ScientificReferenceRecord:${referenceId}`);
  } catch (error) {
    showError(ERROR_CLASS.DOMAIN_UNAVAILABLE, error.message, referenceId);
  }
}

function openWorld(worldId) {
  state.world2d.openWorld(worldId);
  state.shell.togglePanel("world");
}

function handlePaletteAction(action) {
  switch (action.kind) {
    case "open-reference": openReference(action.id); break;
    case "find-concept": findByConstruct(action.query); break;
    case "add-to-composition": addSelectionToComposition(); break;
    case "show-provenance": {
      const key = selectionState.get().focusedKey;
      if (key) state.inspector.showProvenance(key);
      break;
    }
    case "expand-neighborhood": {
      const key = selectionState.get().focusedKey;
      if (key) handleExpand(key);
      break;
    }
    case "pin-snapshot": togglePinnedMode(); break;
    case "open-world": openWorld(action.id || "D2"); break;
    default: break;
  }
}

async function findByConstruct(construct) {
  try {
    const result = await api.findByConstruct(construct);
    const items = result.items || [];
    for (const item of items.slice(0, 10)) {
      const ref = { domain: "REFERENCE", entity_type: "ScientificReferenceRecord",
                    entity_id: item.reference_id };
      const slice = await api.graphSlice(ref, { depth: 1 });
      mergeSlice(slice);
    }
    await relayout("force");
  } catch (error) {
    showError(ERROR_CLASS.DOMAIN_UNAVAILABLE, error.message, construct);
  }
}

function addSelectionToComposition() {
  const keys = [...selectionState.get().selected];
  if (keys.length) state.composition.addMembers(keys.map(keyToRef));
}

function togglePinnedMode() {
  const current = viewportState.get().mode;
  const next = current === OPERATING_MODE.EXPLORATORY_LATEST
    ? OPERATING_MODE.PINNED_REPRODUCIBLE : OPERATING_MODE.EXPLORATORY_LATEST;
  viewportState.set({ mode: next });
  const badge = document.getElementById("wsMode");
  badge.textContent = next;
  badge.className = `ws-mode-badge ${next === OPERATING_MODE.PINNED_REPRODUCIBLE ? "pinned" : "exploratory"}`;
}

boot();

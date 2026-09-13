/**
 * Frontend state model. State is separated by concern, never mixed into one
 * amorphous global store:
 *
 *   - serverScientificState: data fetched from the backend (read-only mirror)
 *   - compositionState: the active ResearchComposition working layer
 *   - selectionState: selected nodes/edges/hyperedges
 *   - viewportState: pan/zoom/layout (NOT scientific state)
 *   - transientUiState: ephemeral UI (hover, drag, palette open)
 *
 * Each store is a tiny observable. Layout/viewport changes never touch
 * scientific state, and never affect any scientific hash.
 */

export class Store {
  /**
   * @param {Object} initial
   */
  constructor(initial = {}) {
    this._state = initial;
    this._listeners = new Set();
  }

  get() { return this._state; }

  /**
   * @param {Object|function} patch
   */
  set(patch) {
    const delta = typeof patch === "function" ? patch(this._state) : patch;
    this._state = { ...this._state, ...delta };
    for (const listener of this._listeners) listener(this._state, delta);
  }

  /**
   * @param {function} listener
   * @returns {function} unsubscribe
   */
  subscribe(listener) {
    this._listeners.add(listener);
    return () => this._listeners.delete(listener);
  }
}

/** Server scientific state (read-only mirror of backend data). */
export const serverState = new Store({
  status: null,
  references: [],
  snapshots: null,
  traceBreaks: [],
  verify: null,
});

/** Composition working-layer state. */
export const compositionState = new Store({
  active: null,        // current ResearchComposition
  members: [],         // pinned refs in the composition
  localLinks: [],      // composition-local links (never canonical)
  localHyperedges: [], // composition-local hyperedges
  annotations: {},     // member key -> note
  dirty: false,
  versions: 0,
});

/** Selection state. */
export const selectionState = new Store({
  selected: new Set(), // node keys
  focusedKey: null,
  inspectedKey: null,
  inspectedKind: null, // "node" | "edge" | "hyperedge"
});

/** Viewport/layout state (never scientific). */
export const viewportState = new Store({
  panX: 0, panY: 0, zoom: 1,
  layout: "force",     // force | hierarchical | radial | manual
  nodePositions: {},   // key -> {x, y, pinned}
  panelLayout: null,   // persisted workspace layout preference
  mode: "EXPLORATORY_LATEST",
  pinnedSnapshot: null,
});

/** Transient UI state. */
export const transientState = new Store({
  paletteOpen: false,
  searchQuery: "",
  dragging: null,
  hover: null,
  busy: false,
  error: null,         // {class, message, context}
});

/** Undo/redo command journal (visual/composition ops only, never canonical). */
export class CommandJournal {
  constructor(limit = 200) {
    this._undo = [];
    this._redo = [];
    this._limit = limit;
  }

  /**
   * @param {{label:string, kind:string, undo:function, redo:function}} command
   * kind: "UI" | "COMPOSITION" | "CANONICAL" (CANONICAL is never undoable here)
   */
  push(command) {
    if (command.kind === "CANONICAL") {
      throw new Error("canonical scientific operations are append-only and not undoable");
    }
    this._undo.push(command);
    if (this._undo.length > this._limit) this._undo.shift();
    this._redo = [];
  }

  undo() {
    const command = this._undo.pop();
    if (!command) return null;
    command.undo();
    this._redo.push(command);
    return command;
  }

  redo() {
    const command = this._redo.pop();
    if (!command) return null;
    command.redo();
    this._undo.push(command);
    return command;
  }

  get canUndo() { return this._undo.length > 0; }
  get canRedo() { return this._redo.length > 0; }
}

export const journal = new CommandJournal();

/**
 * Layout engine facade. Runs expensive layouts in a Web Worker off the main
 * thread, with a synchronous fallback for small graphs or when workers are
 * unavailable (e.g. some test environments).
 */
import { transientState } from "../core/state.js";

export class LayoutEngine {
  constructor(workerUrl = new URL("../workers/layout-worker.js", import.meta.url)) {
    this.workerUrl = workerUrl;
    this.worker = null;
    this._pending = null;
  }

  _ensureWorker() {
    if (this.worker) return this.worker;
    try {
      this.worker = new Worker(this.workerUrl, { type: "module" });
    } catch {
      this.worker = null;
    }
    return this.worker;
  }

  /**
   * Compute a force-directed layout off the main thread.
   * @param {Array} nodes
   * @param {Array} edges
   * @param {Object} options
   * @returns {Promise<Object<string,{x:number,y:number}>>}
   */
  forceDirected(nodes, edges, options = {}) {
    const worker = this._ensureWorker();
    if (!worker) {
      return Promise.resolve(this._syncFallback(nodes, edges, options));
    }
    transientState.set({ busy: true });
    return new Promise((resolve) => {
      this._pending = resolve;
      worker.onmessage = (event) => {
        transientState.set({ busy: false });
        this._pending = null;
        resolve(event.data.positions);
      };
      worker.postMessage({
        nodes: nodes.map((n) => ({ key: n.key })),
        edges: edges.map((e) => ({ source: e.source, target: e.target })),
        iterations: options.iterations ?? 300,
        seed: options.seed ?? 42,
      });
    });
  }

  _syncFallback(nodes, edges, options) {
    // Cheap deterministic circular layout when a worker is unavailable.
    const out = {};
    const n = nodes.length;
    nodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / Math.max(1, n);
      const radius = 80 + Math.sqrt(n) * 18;
      out[node.key] = {
        x: Math.round(Math.cos(angle) * radius),
        y: Math.round(Math.sin(angle) * radius),
      };
    });
    return out;
  }

  /** Hierarchical layout (layered by BFS depth from roots). */
  hierarchical(nodes, edges, options = {}) {
    const out = {};
    const children = new Map();
    const indegree = new Map(nodes.map((n) => [n.key, 0]));
    for (const e of edges) {
      children.set(e.source, [...(children.get(e.source) || []), e.target]);
      indegree.set(e.target, (indegree.get(e.target) || 0) + 1);
    }
    const roots = nodes.filter((n) => (indegree.get(n.key) || 0) === 0);
    const depth = new Map();
    const queue = roots.map((r) => r.key);
    for (const r of queue) depth.set(r, 0);
    let head = 0;
    while (head < queue.length) {
      const current = queue[head++];
      for (const child of children.get(current) || []) {
        if (!depth.has(child)) {
          depth.set(child, (depth.get(current) || 0) + 1);
          queue.push(child);
        }
      }
    }
    const byDepth = new Map();
    for (const node of nodes) {
      const d = depth.get(node.key) ?? 0;
      byDepth.set(d, [...(byDepth.get(d) || []), node.key]);
    }
    for (const [d, keys] of byDepth) {
      keys.forEach((key, i) => {
        out[key] = { x: (i - (keys.length - 1) / 2) * 90, y: d * 110 };
      });
    }
    return Promise.resolve(out);
  }

  /** Radial/focus layout around a center node. */
  radial(nodes, edges, centerKey, options = {}) {
    const out = {};
    const center = centerKey || (nodes[0] && nodes[0].key);
    out[center] = { x: 0, y: 0 };
    const others = nodes.filter((n) => n.key !== center);
    others.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / Math.max(1, others.length);
      const radius = 140 + Math.floor(i / 12) * 70;
      out[node.key] = {
        x: Math.round(Math.cos(angle) * radius),
        y: Math.round(Math.sin(angle) * radius),
      };
    });
    return Promise.resolve(out);
  }
}

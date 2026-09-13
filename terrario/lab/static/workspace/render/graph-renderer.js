/**
 * Canvas graph renderer with pan/zoom, lasso/box selection, minimap, and
 * domain visual language (shape + color + icon, never color alone). Rendering
 * is decoupled from layout: positions come from the layout engine (Web Worker
 * for expensive layouts) and are stored as workspace preference.
 *
 * Visual state (pan/zoom/positions) is never scientific state.
 */
import { DOMAIN_VISUAL } from "../core/contracts.js";

const NODE_RADIUS = 7;
const HYPEREDGE_RADIUS = 11;

export class GraphRenderer {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {Object} options
   */
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.viewport = { panX: 0, panY: 0, zoom: 1 };
    this.nodes = [];   // {key, domain, entity_type, label, x, y, pinned, status}
    this.edges = [];   // {link_id, source, target, relation_type, assertion_class}
    this.hyperedges = []; // {hyperlink_id, members:[key], relation_type}
    this.nodeByKey = new Map();
    this.selected = new Set();
    this.focusedKey = null;
    this.onSelect = options.onSelect || (() => {});
    this.onExpand = options.onExpand || (() => {});
    this.onViewportChange = options.onViewportChange || (() => {});
    this._bindEvents();
    this._drag = null;
    this._marquee = null;
  }

  setGraph({ nodes, edges, hyperedges }) {
    this.nodes = nodes || [];
    this.edges = edges || [];
    this.hyperedges = hyperedges || [];
    this.nodeByKey = new Map(this.nodes.map((n) => [n.key, n]));
    this.requestRender();
  }

  setPositions(positions) {
    for (const node of this.nodes) {
      const pos = positions[node.key];
      if (pos) { node.x = pos.x; node.y = pos.y; node.pinned = !!pos.pinned; }
    }
    this.requestRender();
  }

  setSelection(keys) {
    this.selected = new Set(keys);
    this.requestRender();
  }

  setFocus(key) {
    this.focusedKey = key;
    this.requestRender();
  }

  // ---- viewport ----
  screenToWorld(sx, sy) {
    const { panX, panY, zoom } = this.viewport;
    return { x: (sx - panX) / zoom, y: (sy - panY) / zoom };
  }

  worldToScreen(wx, wy) {
    const { panX, panY, zoom } = this.viewport;
    return { x: wx * zoom + panX, y: wy * zoom + panY };
  }

  fitToNodes(keys) {
    const targets = keys && keys.length
      ? this.nodes.filter((n) => keys.includes(n.key))
      : this.nodes;
    if (!targets.length) return;
    const xs = targets.map((n) => n.x), ys = targets.map((n) => n.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const rect = this.canvas.getBoundingClientRect();
    const w = Math.max(1, maxX - minX), h = Math.max(1, maxY - minY);
    const zoom = Math.min(rect.width / (w + 120), rect.height / (h + 120), 2);
    this.viewport.zoom = zoom;
    this.viewport.panX = rect.width / 2 - (minX + w / 2) * zoom;
    this.viewport.panY = rect.height / 2 - (minY + h / 2) * zoom;
    this.onViewportChange(this.viewport);
    this.requestRender();
  }

  // ---- events ----
  _bindEvents() {
    const c = this.canvas;
    c.addEventListener("wheel", (e) => {
      e.preventDefault();
      const rect = c.getBoundingClientRect();
      const sx = e.clientX - rect.left, sy = e.clientY - rect.top;
      const before = this.screenToWorld(sx, sy);
      this.viewport.zoom = Math.min(4, Math.max(0.1, this.viewport.zoom * (e.deltaY < 0 ? 1.12 : 0.89)));
      const after = this.screenToWorld(sx, sy);
      this.viewport.panX += (after.x - before.x) * this.viewport.zoom;
      this.viewport.panY += (after.y - before.y) * this.viewport.zoom;
      this.onViewportChange(this.viewport);
      this.requestRender();
    }, { passive: false });

    c.addEventListener("pointerdown", (e) => {
      const rect = c.getBoundingClientRect();
      const sx = e.clientX - rect.left, sy = e.clientY - rect.top;
      const world = this.screenToWorld(sx, sy);
      const hit = this._hitNode(world.x, world.y);
      c.setPointerCapture(e.pointerId);
      if (hit) {
        this._drag = { kind: "node", key: hit.key, startX: world.x, startY: world.y,
                       moved: false, additive: e.shiftKey };
      } else {
        this._drag = { kind: e.shiftKey ? "marquee" : "pan", startX: sx, startY: sy,
                       panX: this.viewport.panX, panY: this.viewport.panY, moved: false };
        if (e.shiftKey) this._marquee = { x0: world.x, y0: world.y, x1: world.x, y1: world.y };
      }
    });

    c.addEventListener("pointermove", (e) => {
      if (!this._drag) return;
      const rect = c.getBoundingClientRect();
      const sx = e.clientX - rect.left, sy = e.clientY - rect.top;
      const world = this.screenToWorld(sx, sy);
      const drag = this._drag;
      if (drag.kind === "pan") {
        drag.moved = true;
        this.viewport.panX = drag.panX + (sx - drag.startX);
        this.viewport.panY = drag.panY + (sy - drag.startY);
        this.onViewportChange(this.viewport);
      } else if (drag.kind === "marquee") {
        drag.moved = true;
        this._marquee.x1 = world.x; this._marquee.y1 = world.y;
      } else if (drag.kind === "node") {
        drag.moved = true;
        const node = this.nodeByKey.get(drag.key);
        if (node) {
          node.x = world.x; node.y = world.y; node.pinned = true;
          const targets = this.selected.has(drag.key) ? [...this.selected] : [drag.key];
          for (const key of targets) {
            const n = this.nodeByKey.get(key);
            if (n && n !== node) { n.x += world.x - drag.startX; n.y += world.y - drag.startY; n.pinned = true; }
          }
          drag.startX = world.x; drag.startY = world.y;
        }
      }
      this.requestRender();
    });

    c.addEventListener("pointerup", (e) => {
      const drag = this._drag;
      this._drag = null;
      if (!drag) return;
      if (drag.kind === "node" && !drag.moved) {
        this.onSelect(drag.key, drag.additive ? "toggle" : "single");
      } else if (drag.kind === "marquee" && this._marquee) {
        const { x0, y0, x1, y1 } = this._marquee;
        const [minX, maxX] = [Math.min(x0, x1), Math.max(x0, x1)];
        const [minY, maxY] = [Math.min(y0, y1), Math.max(y0, y1)];
        const inside = this.nodes.filter((n) =>
          n.x >= minX && n.x <= maxX && n.y >= minY && n.y <= maxY).map((n) => n.key);
        this.onSelect(inside, "box");
        this._marquee = null;
      } else if (drag.kind === "node" && drag.moved) {
        this.onViewportChange(this.viewport, { positions: this._positions() });
      }
      this.requestRender();
    });

    c.addEventListener("dblclick", (e) => {
      const rect = c.getBoundingClientRect();
      const world = this.screenToWorld(e.clientX - rect.left, e.clientY - rect.top);
      const hit = this._hitNode(world.x, world.y);
      if (hit) this.onExpand(hit.key);
    });
  }

  _positions() {
    const out = {};
    for (const n of this.nodes) out[n.key] = { x: n.x, y: n.y, pinned: n.pinned };
    return out;
  }

  _hitNode(wx, wy) {
    let best = null, bestDist = Infinity;
    for (const node of this.nodes) {
      const radius = node.entity_type === "HYPEREDGE" || node.domain === "HYPERGRAPH"
        ? HYPEREDGE_RADIUS : NODE_RADIUS;
      const dist = Math.hypot(node.x - wx, node.y - wy);
      if (dist < radius + 4 && dist < bestDist) { best = node; bestDist = dist; }
    }
    return best;
  }

  // ---- rendering ----
  requestRender() {
    if (this._renderQueued) return;
    this._renderQueued = true;
    requestAnimationFrame(() => { this._renderQueued = false; this.render(); });
  }

  render() {
    const [ctx, w, h] = this._setup();
    ctx.clearRect(0, 0, w, h);
    ctx.save();
    const { panX, panY, zoom } = this.viewport;
    ctx.translate(panX, panY);
    ctx.scale(zoom, zoom);
    this._renderEdges(ctx);
    this._renderHyperedges(ctx);
    this._renderNodes(ctx);
    if (this._marquee) this._renderMarquee(ctx);
    ctx.restore();
    this._renderMinimap(ctx, w, h);
  }

  _setup() {
    const scale = devicePixelRatio || 1;
    const rect = this.canvas.getBoundingClientRect();
    if (this.canvas.width !== rect.width * scale) {
      this.canvas.width = rect.width * scale;
      this.canvas.height = rect.height * scale;
    }
    const ctx = this.ctx;
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    return [ctx, rect.width, rect.height];
  }

  _renderEdges(ctx) {
    for (const edge of this.edges) {
      const s = this.nodeByKey.get(edge.source), t = this.nodeByKey.get(edge.target);
      if (!s || !t) continue;
      const active = edge.assertion_class !== "MACHINE_CANDIDATE";
      ctx.strokeStyle = active ? "rgba(90,95,106,0.55)" : "rgba(166,68,58,0.4)";
      ctx.lineWidth = active ? 1.2 : 1;
      ctx.setLineDash(active ? [] : [4, 3]);
      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(t.x, t.y);
      ctx.stroke();
    }
    ctx.setLineDash([]);
  }

  _renderHyperedges(ctx) {
    // Junction-node representation: a hyperedge is drawn as a central junction
    // connected to every member, preserving n-ary semantics (not reduced to
    // pairwise edges).
    for (const hyperlink of this.hyperedges) {
      const members = hyperlink.members.map((k) => this.nodeByKey.get(k)).filter(Boolean);
      if (members.length < 2) continue;
      const cx = members.reduce((a, n) => a + n.x, 0) / members.length;
      const cy = members.reduce((a, n) => a + n.y, 0) / members.length;
      const visual = DOMAIN_VISUAL.HYPEREDGE;
      ctx.strokeStyle = visual.color;
      ctx.setLineDash([2, 2]);
      for (const member of members) {
        ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(member.x, member.y); ctx.stroke();
      }
      ctx.setLineDash([]);
      ctx.fillStyle = visual.color;
      this._polygon(ctx, cx, cy, HYPEREDGE_RADIUS, 6);
      ctx.fill();
      ctx.fillStyle = "#fff";
      ctx.font = "8px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(String(members.length), cx, cy + 3);
    }
  }

  _renderNodes(ctx) {
    for (const node of this.nodes) {
      const visual = DOMAIN_VISUAL[node.domain] || DOMAIN_VISUAL[node.entity_type] || DOMAIN_VISUAL.ONTOLOGY;
      const isSelected = this.selected.has(node.key);
      const isFocused = this.focusedKey === node.key;
      ctx.fillStyle = visual.color;
      const radius = node.entity_type === "HYPEREDGE" || node.domain === "HYPERGRAPH"
        ? HYPEREDGE_RADIUS : NODE_RADIUS;
      this._shape(ctx, visual.shape, node.x, node.y, radius);
      ctx.fill();
      // border semantics: selected = thick dark, focused = accent ring
      if (isSelected || isFocused) {
        ctx.strokeStyle = isFocused ? "#a6443a" : "#101714";
        ctx.lineWidth = isFocused ? 2.5 : 2;
        this._shape(ctx, visual.shape, node.x, node.y, radius + 2);
        ctx.stroke();
      } else {
        ctx.strokeStyle = "rgba(16,23,20,0.35)";
        ctx.lineWidth = 1;
        this._shape(ctx, visual.shape, node.x, node.y, radius);
        ctx.stroke();
      }
      if (this.viewport.zoom > 0.6) {
        ctx.fillStyle = "#101714";
        ctx.font = "9px sans-serif";
        ctx.textAlign = "center";
        const label = node.label || node.entity_id;
        ctx.fillText(this._truncate(label, 18), node.x, node.y + radius + 11);
      }
    }
  }

  _renderMarquee(ctx) {
    const { x0, y0, x1, y1 } = this._marquee;
    ctx.strokeStyle = "rgba(63,111,181,0.7)";
    ctx.fillStyle = "rgba(63,111,181,0.08)";
    ctx.setLineDash([4, 3]);
    ctx.beginPath();
    ctx.rect(Math.min(x0, x1), Math.min(y0, y1), Math.abs(x1 - x0), Math.abs(y1 - y0));
    ctx.fill(); ctx.stroke();
    ctx.setLineDash([]);
  }

  _renderMinimap(ctx, w, h) {
    if (!this.nodes.length) return;
    const mw = 130, mh = 90, pad = 8;
    const xs = this.nodes.map((n) => n.x), ys = this.nodes.map((n) => n.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const gw = Math.max(1, maxX - minX), gh = Math.max(1, maxY - minY);
    const sx = mw / gw, sy = mh / gh, s = Math.min(sx, sy);
    const ox = w - mw - pad, oy = h - mh - pad;
    ctx.save();
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    ctx.strokeStyle = "rgba(16,23,20,0.3)";
    ctx.fillRect(ox, oy, mw, mh);
    ctx.strokeRect(ox, oy, mw, mh);
    for (const node of this.nodes) {
      ctx.fillStyle = (DOMAIN_VISUAL[node.domain] || DOMAIN_VISUAL.ONTOLOGY).color;
      ctx.fillRect(ox + (node.x - minX) * s - 1, oy + (node.y - minY) * s - 1, 2, 2);
    }
    // viewport rectangle
    const { panX, panY, zoom } = this.viewport;
    const rect = this.canvas.getBoundingClientRect();
    const vw = rect.width / zoom, vh = rect.height / zoom;
    const vx = (-panX / zoom - minX) * s, vy = (-panY / zoom - minY) * s;
    ctx.strokeStyle = "#a6443a";
    ctx.strokeRect(ox + vx, oy + vy, vw * s, vh * s);
    ctx.restore();
  }

  _shape(ctx, shape, x, y, r) {
    ctx.beginPath();
    switch (shape) {
      case "diamond": this._polygon(ctx, x, y, r, 4); break;
      case "hexagon": this._polygon(ctx, x, y, r, 6); break;
      case "square": ctx.rect(x - r, y - r, 2 * r, 2 * r); break;
      case "document": ctx.rect(x - r * 0.8, y - r, 1.6 * r, 2 * r); break;
      case "star": this._star(ctx, x, y, r); break;
      case "junction": this._polygon(ctx, x, y, r, 6); break;
      default: ctx.arc(x, y, r, 0, Math.PI * 2);
    }
  }

  _polygon(ctx, x, y, r, sides) {
    for (let i = 0; i < sides; i++) {
      const angle = (Math.PI * 2 * i) / sides - Math.PI / 2;
      const px = x + r * Math.cos(angle), py = y + r * Math.sin(angle);
      i ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
    }
    ctx.closePath();
  }

  _star(ctx, x, y, r) {
    for (let i = 0; i < 10; i++) {
      const angle = (Math.PI * i) / 5 - Math.PI / 2;
      const radius = i % 2 === 0 ? r : r * 0.45;
      const px = x + radius * Math.cos(angle), py = y + radius * Math.sin(angle);
      i ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
    }
    ctx.closePath();
  }

  _truncate(value, max) {
    return value.length > max ? `${value.slice(0, max - 1)}…` : value;
  }
}

/**
 * Workspace shell: a multipanel scientific workstation. Panels dock, resize,
 * hide/show, and fullscreen; the layout persists as a user preference (never
 * scientific state). The shell hosts the Explorer, Scientific Canvas,
 * Inspector, Provenance, Composition, Timeline/History, and World panels.
 */
import { viewportState, transientState } from "../core/state.js";

const LAYOUT_KEY = "terrario.workspace.layout.v1";

export class WorkspaceShell {
  /**
   * @param {HTMLElement} root
   */
  constructor(root) {
    this.root = root;
    this.panels = new Map();
    this.layout = this._loadLayout();
  }

  _loadLayout() {
    try {
      return JSON.parse(localStorage.getItem(LAYOUT_KEY)) || this._defaultLayout();
    } catch {
      return this._defaultLayout();
    }
  }

  _defaultLayout() {
    return {
      left: { visible: true, size: 20 },
      right: { visible: true, size: 26 },
      bottom: { visible: true, size: 26 },
      center: { visible: true, size: 54 },
      fullscreen: null,
    };
  }

  persistLayout() {
    viewportState.set({ panelLayout: this.layout });
    try { localStorage.setItem(LAYOUT_KEY, JSON.stringify(this.layout)); } catch {}
  }

  /**
   * @param {string} id
   * @param {{title:string, region:string, render:function}} def
   */
  registerPanel(id, def) {
    const panel = document.createElement("section");
    panel.className = `ws-panel ws-${def.region}`;
    panel.dataset.panel = id;
    panel.setAttribute("aria-label", def.title);
    const header = document.createElement("header");
    header.className = "ws-panel-head";
    header.innerHTML = `
      <strong>${def.title}</strong>
      <span class="ws-panel-tools">
        <button data-action="hide" title="Hide panel" aria-label="Hide panel">–</button>
        <button data-action="fullscreen" title="Fullscreen" aria-label="Fullscreen">⛶</button>
      </span>`;
    const body = document.createElement("div");
    body.className = "ws-panel-body";
    panel.append(header, body);
    header.querySelector('[data-action="hide"]').onclick = () => this.hidePanel(id);
    header.querySelector('[data-action="fullscreen"]').onclick = () => this.toggleFullscreen(id);
    this.panels.set(id, { ...def, element: panel, body });
    def.render(body);
    return panel;
  }

  mount() {
    this.root.classList.add("workspace-shell");
    this.root.innerHTML = "";
    const grid = document.createElement("div");
    grid.className = "ws-grid";
    const regions = { left: [], center: [], right: [], bottom: [] };
    for (const [id, panel] of this.panels) {
      (regions[panel.region] || regions.center).push(panel.element);
    }
    const left = this._region("left", regions.left);
    const center = this._region("center", regions.center);
    const right = this._region("right", regions.right);
    const bottom = this._region("bottom", regions.bottom);
    const main = document.createElement("div");
    main.className = "ws-main";
    main.append(left, center, right);
    grid.append(main, bottom);
    this.root.append(grid);
    this._applyLayout();
    this._buildPanelSwitcher();
  }

  _region(name, elements) {
    const region = document.createElement("div");
    region.className = `ws-region ws-region-${name}`;
    region.dataset.region = name;
    for (const el of elements) region.append(el);
    if (!elements.length) region.append(this._emptyRegion(name));
    return region;
  }

  _emptyRegion(name) {
    const div = document.createElement("div");
    div.className = "ws-empty";
    div.textContent = "Panel hidden";
    return div;
  }

  _applyLayout() {
    for (const [name, region] of [["left", ".ws-region-left"], ["center", ".ws-region-center"],
                                   ["right", ".ws-region-right"], ["bottom", ".ws-region-bottom"]]) {
      const el = this.root.querySelector(region);
      if (!el) continue;
      const conf = this.layout[name] || {};
      el.style.display = conf.visible === false ? "none" : "";
      if (conf.size) {
        if (name === "bottom") el.style.height = `${conf.size}%`;
        else el.style.flex = `0 0 ${conf.size}%`;
      }
    }
  }

  _buildPanelSwitcher() {
    const bar = document.createElement("div");
    bar.className = "ws-switcher";
    for (const [id, panel] of this.panels) {
      const button = document.createElement("button");
      button.textContent = panel.title;
      button.className = "ws-switch";
      button.onclick = () => this.togglePanel(id);
      bar.append(button);
    }
    this.root.append(bar);
  }

  togglePanel(id) {
    const panel = this.panels.get(id);
    if (!panel) return;
    const region = panel.region;
    this.layout[region] = this.layout[region] || {};
    this.layout[region].visible = !(this.layout[region].visible !== false);
    this.persistLayout();
    this._applyLayout();
  }

  hidePanel(id) {
    const panel = this.panels.get(id);
    if (!panel) return;
    this.layout[panel.region] = this.layout[panel.region] || {};
    this.layout[panel.region].visible = false;
    this.persistLayout();
    this._applyLayout();
  }

  toggleFullscreen(id) {
    const panel = this.panels.get(id);
    if (!panel) return;
    const isFull = this.layout.fullscreen === id;
    this.layout.fullscreen = isFull ? null : id;
    for (const [pid, p] of this.panels) {
      p.element.classList.toggle("ws-fullscreen", pid === id && !isFull);
    }
    this.root.classList.toggle("ws-has-fullscreen", !isFull);
    this.persistLayout();
  }
}

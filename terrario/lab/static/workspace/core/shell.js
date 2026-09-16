/**
 * Workspace shell with context navigation. A context is a presentation boundary,
 * never a scientific state: panels keep their own contracts and identities.
 */
import { viewportState } from "../core/state.js";

const CONTEXT_KEY = "terrario.workspace.context.v1";

export class WorkspaceShell {
  constructor(root) {
    this.root = root;
    this.panels = new Map();
    this.contexts = new Map();
    this.pages = new Map();
    this.activeContext = null;
    this._onHashChange = () => {
      const context = location.hash.match(/^#context=([a-z-]+)$/)?.[1];
      if (context && this.contexts.has(context)) this.navigate(context, { persist: false });
    };
  }

  registerContext(id, definition) {
    this.contexts.set(id, { id, title: definition.title, description: definition.description || "" });
  }

  registerPanel(id, def) {
    const panel = document.createElement("section");
    panel.className = `ws-panel ws-${def.region || "center"}`;
    panel.dataset.panel = id;
    panel.dataset.context = def.context || "explore";
    panel.setAttribute("aria-label", def.title);
    const header = document.createElement("header");
    header.className = "ws-panel-head";
    header.innerHTML = `<strong>${def.title}</strong><span class="ws-panel-tools"><button data-action="fullscreen" title="Ampliar panel" aria-label="Ampliar ${def.title}">⛶</button></span>`;
    const body = document.createElement("div");
    body.className = "ws-panel-body";
    panel.append(header, body);
    header.querySelector('[data-action="fullscreen"]').onclick = () => this.toggleFullscreen(id);
    this.panels.set(id, { ...def, element: panel, body });
    def.render(body);
    return panel;
  }

  mount() {
    this.root.classList.add("workspace-shell");
    this.root.innerHTML = "";
    const navigation = document.createElement("nav");
    navigation.className = "ws-context-nav";
    navigation.setAttribute("aria-label", "Contextos de trabajo");
    const tablist = document.createElement("div");
    tablist.className = "ws-context-tabs";
    tablist.setAttribute("role", "tablist");
    tablist.addEventListener("keydown", (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const ids = [...this.contexts.keys()];
      const focused = document.activeElement?.dataset?.contextTarget;
      const current = Math.max(0, ids.indexOf(focused || this.activeContext));
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? ids.length - 1
        : (current + (event.key === 'ArrowRight' ? 1 : -1) + ids.length) % ids.length;
      this.navigate(ids[next]);
      this.root.querySelector(`[data-context-target="${ids[next]}"]`)?.focus();
    });
    const pages = document.createElement("div");
    pages.className = "ws-context-pages";

    for (const context of this.contexts.values()) {
      const button = document.createElement("button");
      button.type = "button";
      button.setAttribute("role", "tab");
      button.dataset.contextTarget = context.id;
      button.setAttribute("aria-controls", `ws-context-${context.id}`);
      button.innerHTML = `<strong>${context.title}</strong><small>${context.description}</small>`;
      button.onclick = () => this.navigate(context.id);
      tablist.append(button);

      const page = document.createElement("section");
      page.className = "ws-context-page";
      page.dataset.contextPage = context.id;
      page.id = `ws-context-${context.id}`;
      page.setAttribute("aria-label", context.title);
      page.setAttribute("role", "tabpanel");
      const grid = document.createElement("div");
      grid.className = `ws-context-grid ws-context-${context.id}`;
      for (const panel of this.panels.values()) {
        if (panel.context === context.id) grid.append(panel.element);
      }
      if (!grid.children.length) grid.innerHTML = '<p class="ws-empty">No hay instrumentos registrados en este contexto.</p>';
      page.append(grid);
      pages.append(page);
      this.pages.set(context.id, page);
    }
    navigation.append(tablist);
    this.root.append(navigation, pages);
    if (!this._listeningForHistory) {
      window.addEventListener("hashchange", this._onHashChange);
      this._listeningForHistory = true;
    }
    this.navigate(this._initialContext(), { persist: false, replace: true });
  }

  _initialContext() {
    const fromHash = location.hash.match(/^#context=([a-z-]+)$/)?.[1];
    if (fromHash && this.contexts.has(fromHash)) return fromHash;
    try {
      const saved = localStorage.getItem(CONTEXT_KEY);
      if (saved && this.contexts.has(saved)) return saved;
    } catch {}
    return this.contexts.keys().next().value;
  }

  navigate(id, { persist = true, replace = false } = {}) {
    if (!this.contexts.has(id)) return;
    this.activeContext = id;
    for (const [contextId, page] of this.pages) {
      const active = contextId === id;
      page.hidden = !active;
      page.classList.toggle("active", active);
    }
    this.root.querySelectorAll("[data-context-target]").forEach((button) => {
      const active = button.dataset.contextTarget === id;
      button.classList.toggle("active", active);
      button.setAttribute("aria-current", active ? "page" : "false");
      button.setAttribute("aria-selected", active ? "true" : "false");
      button.tabIndex = active ? 0 : -1;
    });
    viewportState.set({ activeContext: id });
    if (persist) {
      try { localStorage.setItem(CONTEXT_KEY, id); } catch {}
      const hash = `#context=${id}`;
      if (replace) history.replaceState(null, "", hash);
      else if (location.hash !== hash) history.pushState(null, "", hash);
    }
  }

  toggleFullscreen(id) {
    const panel = this.panels.get(id);
    if (!panel) return;
    const isFull = panel.element.classList.toggle("ws-fullscreen");
    this.root.classList.toggle("ws-has-fullscreen", isFull);
    const button = panel.element.querySelector('[data-action="fullscreen"]');
    button?.setAttribute("aria-pressed", isFull ? "true" : "false");
    button?.setAttribute("title", isFull ? "Restaurar panel" : "Ampliar panel");
    button?.setAttribute("aria-label", `${isFull ? "Restaurar" : "Ampliar"} ${panel.title}`);
  }
}

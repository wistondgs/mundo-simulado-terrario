/** Native renderer interface with permanent Canvas2D fallback and WebGL2 path. */
export class Camera {
  constructor() { this.x = 0; this.y = 0; this.zoom = 1; this.followId = null; }
  reset() { this.x = 0; this.y = 0; this.zoom = 1; this.followId = null; }
}

function normalized(view) {
  if (!view) return { width: 1, height: 1, objects: [], agents: [], mask: null, channels: null };
  if (view.kind === "AGENT_OBSERVATION") {
    const p = view.payload, grid = p.channels?.[0] || [[]];
    return { width: grid[0]?.length || 1, height: grid.length || 1, objects: [], agents: [], mask: p.mask, channels: p.channels };
  }
  const p = view.kind === "OBSERVER_VIEW" ? view.payload.world : view.payload;
  if (!p || p.status === "MISSING") return { width: 1, height: 1, objects: [], agents: [], missing: true };
  return { width: p.grid_width || 1, height: p.grid_height || 1, objects: Object.values(p.objects || {}), agents: Object.values(p.agents || {}) };
}

export class Canvas2DRenderer {
  initialize(canvas) { this.canvas = canvas; this.ctx = canvas.getContext("2d"); this.camera = new Camera(); this.last = null; this.times = []; this.pickIndex = new Map(); }
  resize(width, height, ratio = devicePixelRatio || 1) { this.width = width; this.height = height; this.ratio = ratio; this.canvas.width = Math.max(1, width * ratio); this.canvas.height = Math.max(1, height * ratio); }
  setCamera(camera) { this.camera = { ...this.camera, ...camera }; }
  renderFrame(view) {
    const started = performance.now(), d = normalized(view), ctx = this.ctx, cell = Math.max(1, Math.min(this.width / d.width, this.height / d.height) * this.camera.zoom);
    ctx.setTransform(this.ratio, 0, 0, this.ratio, this.camera.x, this.camera.y); ctx.fillStyle = "#101714"; ctx.fillRect(-this.camera.x, -this.camera.y, this.width, this.height);
    if (d.missing) { ctx.fillStyle = "#c98268"; ctx.font = "12px sans-serif"; ctx.fillText("MISSING", 8, 18); return; }
    if (d.channels) d.channels[0].forEach((row, r) => row.forEach((value, c) => { ctx.fillStyle = value ? "#3f91a1" : "#1c2924"; ctx.fillRect(c * cell + 1, r * cell + 1, cell - 2, cell - 2); }));
    this.pickIndex.clear(); d.objects.forEach((obj) => { const [r, c] = obj.pos; this.pickIndex.set(`${r}:${c}`, obj); ctx.fillStyle = obj.properties?.causal_class === "A" ? "#d9a441" : "#3f91a1"; ctx.fillRect(c * cell + 1, r * cell + 1, Math.max(2, cell - 2), Math.max(2, cell - 2)); });
    d.agents.forEach((agent) => { const [r, c] = agent.pos; ctx.fillStyle = "#55b993"; ctx.beginPath(); ctx.arc(c * cell + cell / 2, r * cell + cell / 2, Math.max(2, cell * .35), 0, Math.PI * 2); ctx.fill(); });
    if (d.mask) d.mask.forEach((row, r) => row.forEach((visible, c) => { if (!visible) { ctx.fillStyle = "rgba(0,0,0,.68)"; ctx.fillRect(c * cell, r * cell, cell, cell); } }));
    ctx.strokeStyle = "rgba(90,110,99,.35)"; for (let x = 0; x <= d.width; x++) { ctx.beginPath(); ctx.moveTo(x * cell, 0); ctx.lineTo(x * cell, d.height * cell); ctx.stroke(); }
    this.last = { view, data: d, cell }; this.times.push(performance.now() - started); if (this.times.length > 120) this.times.shift();
  }
  pick(x, y) { if (!this.last) return null; const r = Math.floor((y - this.camera.y) / this.last.cell), c = Math.floor((x - this.camera.x) / this.last.cell); return this.pickIndex.get(`${r}:${c}`) || null; }
  metrics() { const sorted = [...this.times].sort((a, b) => a - b); return { renderer: "Canvas2D", frames: sorted.length, p95RenderMs: sorted[Math.floor(sorted.length * .95)] || 0, lastEntityCount: (this.last?.data.objects.length || 0) + (this.last?.data.agents.length || 0) }; }
  dispose() { this.last = null; this.times = []; this.pickIndex.clear(); }
}

export class WebGL2Renderer {
  initialize(canvas) {
    this.canvas = canvas; this.gl = canvas.getContext("webgl2", { antialias: false, preserveDrawingBuffer: true });
    if (!this.gl) throw new Error("WEBGL2_UNAVAILABLE"); this.camera = new Camera(); this.times = []; this.last = null;
    const gl = this.gl, compile = (type, source) => { const shader = gl.createShader(type); gl.shaderSource(shader, source); gl.compileShader(shader); if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader)); return shader; };
    this.program = gl.createProgram(); gl.attachShader(this.program, compile(gl.VERTEX_SHADER, `#version 300 es\nin vec2 p;uniform vec2 scale;uniform float size;void main(){gl_Position=vec4(p*scale+vec2(-1.,1.),0.,1.);gl_PointSize=size;}`));
    gl.attachShader(this.program, compile(gl.FRAGMENT_SHADER, `#version 300 es\nprecision mediump float;out vec4 color;void main(){color=vec4(.25,.57,.63,1.);}`)); gl.linkProgram(this.program); this.buffer = gl.createBuffer(); this.capacity = 0; this.points = new Float32Array(0); this.pickIndex = new Map();
  }
  resize(width, height, ratio = devicePixelRatio || 1) { this.width = width; this.height = height; this.ratio = ratio; this.canvas.width = Math.max(1, width * ratio); this.canvas.height = Math.max(1, height * ratio); this.gl.viewport(0, 0, this.canvas.width, this.canvas.height); }
  setCamera(camera) { this.camera = { ...this.camera, ...camera }; }
  renderFrame(view) {
    const started = performance.now(), d = normalized(view), gl = this.gl, required = d.objects.length * 2; gl.clearColor(.06, .09, .08, 1); gl.clear(gl.COLOR_BUFFER_BIT); gl.useProgram(this.program);
    if (required > this.points.length) { this.capacity = Math.max(64, this.capacity || 64); while (this.capacity * 2 < required) this.capacity *= 2; this.points = new Float32Array(this.capacity * 2); gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer); gl.bufferData(gl.ARRAY_BUFFER, this.points.byteLength, gl.DYNAMIC_DRAW); }
    this.pickIndex.clear(); d.objects.forEach((obj, index) => { this.points[index * 2] = obj.pos[1]; this.points[index * 2 + 1] = -obj.pos[0]; this.pickIndex.set(`${obj.pos[0]}:${obj.pos[1]}`, obj); });
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer); if (required) gl.bufferSubData(gl.ARRAY_BUFFER, 0, this.points.subarray(0, required)); const loc = gl.getAttribLocation(this.program, "p"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    gl.uniform2f(gl.getUniformLocation(this.program, "scale"), 2 / Math.max(1, d.width), 2 / Math.max(1, d.height)); gl.uniform1f(gl.getUniformLocation(this.program, "size"), Math.max(2, Math.min(this.width / d.width, this.height / d.height) * this.ratio)); gl.drawArrays(gl.POINTS, 0, d.objects.length);
    this.last = { view, data: d }; this.times.push(performance.now() - started); if (this.times.length > 120) this.times.shift();
  }
  pick(x, y) { const d = this.last?.data; if (!d) return null; const c = Math.floor(x / this.width * d.width), r = Math.floor(y / this.height * d.height); return this.pickIndex.get(`${r}:${c}`) || null; }
  metrics() { const sorted = [...this.times].sort((a, b) => a - b); return { renderer: "WebGL2", frames: sorted.length, p95RenderMs: sorted[Math.floor(sorted.length * .95)] || 0, lastEntityCount: this.last?.data.objects.length || 0 }; }
  dispose() { const gl = this.gl; if (gl) { gl.deleteBuffer(this.buffer); gl.deleteProgram(this.program); } this.last = null; this.points = new Float32Array(0); this.pickIndex.clear(); }
}

export class ResilientRenderer {
  initialize(canvas, { preferWebGL = false, onFallback } = {}) {
    this.canvas = canvas; this.onFallback = onFallback || (() => {}); this.preferWebGL = preferWebGL;
    try { this.impl = preferWebGL ? new WebGL2Renderer() : new Canvas2DRenderer(); this.impl.initialize(canvas); }
    catch (error) { this.impl = new Canvas2DRenderer(); this.impl.initialize(canvas); this.onFallback(error); }
    canvas.addEventListener("webglcontextlost", (event) => { event.preventDefault(); this.fallback("WEBGL_CONTEXT_LOST"); });
  }
  fallback(reason) { this.impl?.dispose(); this.impl = new Canvas2DRenderer(); this.impl.initialize(this.canvas); this.onFallback(new Error(reason)); }
  resize(...args) { this.impl.resize(...args); } setCamera(value) { this.impl.setCamera(value); }
  renderFrame(value) { try { this.impl.renderFrame(value); } catch (error) { this.fallback(error.message); this.impl.renderFrame(value); } }
  pick(...args) { return this.impl.pick(...args); } metrics() { return this.impl.metrics(); } dispose() { this.impl.dispose(); }
}

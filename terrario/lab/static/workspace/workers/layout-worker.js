/**
 * Force-directed layout running in a Web Worker (off the main UI thread).
 * Receives nodes/edges, runs a simple force simulation, posts back positions.
 * Layout is a workspace preference and never affects any scientific hash.
 */

self.onmessage = function (event) {
  const { nodes, edges, iterations = 300, seed = 42 } = event.data;
  const positions = forceLayout(nodes, edges, iterations, seed);
  self.postMessage({ positions });
};

function forceLayout(nodes, edges, iterations, seed) {
  const rand = mulberry32(seed);
  const pos = new Map();
  const n = nodes.length;
  // deterministic initial placement on a circle
  nodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / Math.max(1, n);
    const radius = 80 + Math.sqrt(n) * 18;
    pos.set(node.key, {
      x: Math.cos(angle) * radius + (rand() - 0.5) * 20,
      y: Math.sin(angle) * radius + (rand() - 0.5) * 20,
      vx: 0, vy: 0,
    });
  });
  const index = new Map(nodes.map((node, i) => [node.key, i]));
  const area = Math.max(1, n) * 900;
  const k = Math.sqrt(area / Math.max(1, n));
  let temperature = Math.sqrt(area) / 10;

  for (let iter = 0; iter < iterations; iter++) {
    // repulsive
    for (let i = 0; i < n; i++) {
      const a = pos.get(nodes[i].key);
      for (let j = i + 1; j < n; j++) {
        const b = pos.get(nodes[j].key);
        let dx = a.x - b.x, dy = a.y - b.y;
        let dist = Math.hypot(dx, dy) || 0.01;
        const force = (k * k) / dist;
        dx /= dist; dy /= dist;
        a.vx += dx * force; a.vy += dy * force;
        b.vx -= dx * force; b.vy -= dy * force;
      }
    }
    // attractive
    for (const edge of edges) {
      const a = pos.get(edge.source), b = pos.get(edge.target);
      if (!a || !b) continue;
      let dx = a.x - b.x, dy = a.y - b.y;
      const dist = Math.hypot(dx, dy) || 0.01;
      const force = (dist * dist) / k;
      dx /= dist; dy /= dist;
      a.vx -= dx * force; a.vy -= dy * force;
      b.vx += dx * force; b.vy += dy * force;
    }
    // integrate with cooling
    for (const node of nodes) {
      const p = pos.get(node.key);
      const speed = Math.hypot(p.vx, p.vy) || 0.01;
      const limited = Math.min(speed, temperature);
      p.x += (p.vx / speed) * limited;
      p.y += (p.vy / speed) * limited;
      p.vx = 0; p.vy = 0;
    }
    temperature *= 0.95;
  }
  const out = {};
  for (const node of nodes) {
    const p = pos.get(node.key);
    out[node.key] = { x: Math.round(p.x), y: Math.round(p.y) };
  }
  return out;
}

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

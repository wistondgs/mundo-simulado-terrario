// Componer un organismo: elegir conceptos, elegir mundo, correr, comparar.
//
// Todo el texto que describe un concepto viene de /api/agent-concepts, nunca de
// esta página: una descripción que se despega del código es peor que ninguna.
"use strict";

const estado = { conceptos: [], ajustes: [], mezcla: {}, mundo: null, guardada: null, ultima: null, corridaId: null };

const $ = (id) => document.getElementById(id);
const texto = (el, valor) => { el.textContent = valor; return el; };

async function api(metodo, ruta, cuerpo) {
  const r = await fetch(ruta, {
    method: metodo,
    headers: cuerpo ? { "content-type": "application/json" } : undefined,
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  const datos = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(datos.error || `${r.status} en ${ruta}`);
  return datos;
}

// ── Paso 1 ────────────────────────────────────────────────────────────────
function pintarConceptos() {
  const caja = texto($("conceptos"), "");
  estado.conceptos.forEach((c) => {
    const encendido = estado.mezcla[c.key] !== undefined ? estado.mezcla[c.key] : c.default;
    const b = document.createElement("button");
    b.className = "tarjeta";
    b.type = "button";
    b.setAttribute("aria-pressed", String(encendido));
    b.innerHTML =
      `<span class="titulo">${c.label}<span class="marca">${encendido ? "puesto" : "quitado"}</span></span>` +
      `<p class="para">${c.purpose}</p>` +
      `<p class="sin">Sin esto: ${c.without_it}</p>`;
    b.onclick = () => { estado.mezcla[c.key] = !encendido; pintarConceptos(); pintarResumen(); };
    caja.appendChild(b);
  });
}

function pintarAjustes() {
  const caja = texto($("ajustes"), "");
  estado.ajustes.forEach((t) => {
    const l = document.createElement("label");
    l.className = "campo";
    l.innerHTML = `${t.label}<input type="number" step="0.01" min="${t.minimum}" max="${t.maximum}" ` +
      `value="${estado.mezcla[t.key] !== undefined ? estado.mezcla[t.key] : t.default}">` +
      `<small>${t.purpose}${t.warning ? " " + t.warning : ""}</small>`;
    l.querySelector("input").onchange = (e) => {
      estado.mezcla[t.key] = Number(e.target.value);
      pintarResumen();
    };
    caja.appendChild(l);
  });
}

function pintarResumen() {
  const puestos = estado.conceptos.filter((c) => (estado.mezcla[c.key] ?? c.default));
  const quitados = estado.conceptos.filter((c) => !(estado.mezcla[c.key] ?? c.default));
  const linea = [`Este organismo tiene: ${puestos.map((c) => c.label).join(", ") || "nada"}.`];
  if (quitados.length) linea.push(`Le falta: ${quitados.map((c) => c.label).join(", ")}.`);
  texto($("resumen"), linea.join("\n"));
  actualizarBotonCorrer();
}

// ── Paso 2 ────────────────────────────────────────────────────────────────
const COMO_ES = {
  D0: "Lo más simple: sólo hay diferencias que notar.",
  D1: "Aparecen objetos que siguen existiendo aunque no se vean.",
  D2: "Los objetos tienen propiedades que hay que ligar entre sí.",
  D3: "Las cosas tienen causas: actuar produce consecuencias.",
  D4: "Las reglas cambian a mitad de camino y hay que re-estabilizarse.",
  D4S: "Como D4, pero con energía en juego: la viabilidad está de verdad amenazada.",
  D4T: "Las reglas se invierten tres veces seguidas, a intervalos iguales.",
};

function pintarMundos(mundos) {
  const caja = texto($("mundos"), "");
  mundos.forEach((m) => {
    const b = document.createElement("button");
    b.className = "tarjeta";
    b.type = "button";
    b.setAttribute("aria-current", String(estado.mundo === m.world_id));
    const golpes = (m.interventions || []).length;
    b.innerHTML = `<span class="titulo">${m.world_id}<span class="marca">` +
      `${golpes === 0 ? "sin perturbaciones" : golpes === 1 ? "1 perturbación" : golpes + " perturbaciones"}` +
      `</span></span><p class="para">${COMO_ES[m.world_id] || m.description || ""}</p>`;
    b.onclick = () => { estado.mundo = m.world_id; pintarMundos(mundos); };
    caja.appendChild(b);
  });
  actualizarBotonCorrer();
}

// ── Paso 3 ────────────────────────────────────────────────────────────────
async function liberarSesiones() {
  try {
    const { active = [] } = await api("GET", "/api/sandbox");
    for (const sesion of active) {
      await api("POST", `/api/sandbox/${sesion.sandbox_run_id}/stop`).catch(() => {});
    }
  } catch (e) { /* si no se puede listar, el intento de correr dirá por qué */ }
  estado.corridaId = null;
}

// Medido en esta máquina: ~0.37 s por paso con el organismo completo y ~0.18 s
// sin planificador, que es la pieza cara. No es exacto y no hace falta que lo
// sea: existe para que nadie haga clic y crea que la página se colgó.
function segundosEstimados() {
  const conPlanificador = estado.mezcla.use_planner !== false;
  return Math.round(Number($("pasos").value) * (conPlanificador ? 0.37 : 0.18));
}

function comoTiempo(segundos) {
  if (segundos < 60) return `~${Math.max(1, segundos)} s`;
  return `~${Math.round(segundos / 60)} min`;
}

function actualizarBotonCorrer() {
  const boton = $("correr");
  boton.disabled = !estado.mundo;
  boton.textContent = estado.mundo
    ? `Correr esta mezcla en ${estado.mundo} — ${$("pasos").value} pasos, tarda ${comoTiempo(segundosEstimados())}`
    : "Correr esta mezcla — todavía no elegiste mundo";
}

async function correr() {
  const boton = $("correr");
  boton.disabled = true;
  texto($("estado"), `Corriendo… suele tardar ${comoTiempo(segundosEstimados())}. Podés esperar aquí.`).classList.remove("error");
  try {
    const pasos = Number($("pasos").value);
    // Sólo importa la corrida más reciente, y el laboratorio admite un número
    // fijo de sesiones abiertas. Se cierran TODAS las anteriores, no sólo la de
    // esta pestaña: recargar la página dejaba huérfanas que agotaban el cupo, y
    // la mezcla siguiente fallaba con un mensaje que no significa nada para
    // quien sólo quería probar otra cosa.
    await liberarSesiones();
    const run = await api("POST", "/api/sandbox", {
      world_id: estado.mundo, agent_reference: "A4", step_limit: pasos + 1,
      agent_configuration: estado.mezcla,
    });
    estado.corridaId = run.sandbox_run_id;
    await api("POST", `/api/sandbox/${run.sandbox_run_id}/run`, { steps: pasos });
    const linea = await api("GET", `/api/sandbox/${run.sandbox_run_id}/trace`);
    const medido = await api("GET", `/api/sandbox/${run.sandbox_run_id}/measures`);
    estado.ultima = resumirCorrida(run, linea, medido);
    pintarSalida();
    // Si ya hay una corrida guardada, la comparación es lo que el usuario vino
    // a ver: no debe haber que volver a pulsar nada para que aparezca.
    pintarComparacion();
    texto($("estado"), `Listo: ${linea.length} pasos vividos en ${estado.mundo}.`);
    $("guardar").disabled = false;
  } catch (e) {
    texto($("estado"), `No se pudo correr: ${e.message}`).classList.add("error");
  }
  actualizarBotonCorrer();
}

// Un experimento con una sola medida sólo puede encontrar lo que esa medida
// fue construida para ver. Así que cada corrida reporta todas las mallas.
function resumirCorrida(run, linea, medido) {
  const ultimo = linea[linea.length - 1] || {};
  const quitados = (ultimo.scientific_state || {}).active_ablations || [];
  const nombre = (k) => (estado.conceptos.find((c) => c.key === k) || {}).label || k;
  const filas = [{
    clave: "quitados", etiqueta: "Piezas quitadas",
    valor: quitados.length ? quitados.map(nombre).join(", ") : "nada — organismo completo",
    explica: "Qué conceptos estaban apagados en esta mezcla.",
  }, {
    clave: "mundo", etiqueta: "Mundo", valor: estado.mundo,
    explica: "Dónde vivió.",
  }];
  for (const m of (medido.measures || [])) {
    filas.push({
      clave: m.key, etiqueta: m.label,
      valor: m.evaluable ? String(m.value) : `no evaluable — ${m.reason}`,
      explica: m.means + (m.unit ? ` (${m.unit})` : ""),
    });
  }
  return { filas };
}

function tabla(columnas) {
  const t = document.createElement("table");
  const claves = columnas[0].datos.filas;
  t.innerHTML = `<tr><th>Medida</th>${columnas.map((c) => `<th>${c.titulo}</th>`).join("")}<th>Qué significa</th></tr>` +
    claves.map((fila, i) => {
      const valores = columnas.map((c) => (c.datos.filas[i] || {}).valor);
      const difiere = columnas.length > 1 && new Set(valores).size > 1;
      return `<tr><th>${fila.etiqueta}</th>` +
        valores.map((v) => `<td class="${difiere ? "dif" : ""}">${v}</td>`).join("") +
        `<td class="explica">${fila.explica}</td></tr>`;
    }).join("");
  return t;
}

function pintarSalida() {
  const caja = texto($("salida"), "");
  if (estado.ultima) caja.appendChild(tabla([{ titulo: "Esta corrida", datos: estado.ultima }]));
}

// ── Paso 4 ────────────────────────────────────────────────────────────────
function pintarComparacion() {
  const caja = texto($("comparacion"), "");
  if (!estado.guardada) return;
  const columnas = [{ titulo: "Guardada", datos: estado.guardada }];
  if (estado.ultima && estado.ultima !== estado.guardada) {
    columnas.push({ titulo: "Esta corrida", datos: estado.ultima });
  }
  caja.appendChild(tabla(columnas));
  if (columnas.length === 1) {
    const p = document.createElement("p");
    p.className = "ayuda";
    p.textContent = "Cambiá una sola pieza arriba y volvé a correr: lo que difiera se marca solo.";
    caja.appendChild(p);
  }
}

// ── Arranque ──────────────────────────────────────────────────────────────
async function inicio() {
  try {
    const catalogo = await api("GET", "/api/agent-concepts");
    estado.conceptos = catalogo.concepts;
    estado.ajustes = catalogo.tunings;
    pintarConceptos(); pintarAjustes(); pintarResumen();
    pintarMundos(await api("GET", "/api/worlds"));
  } catch (e) {
    texto($("estado"), `No se pudo cargar el laboratorio: ${e.message}`).classList.add("error");
  }
  $("correr").onclick = correr;
  $("pasos").oninput = actualizarBotonCorrer;
  $("guardar").onclick = () => {
    estado.guardada = estado.ultima;
    $("limpiar").disabled = false;
    pintarComparacion();
  };
  $("limpiar").onclick = () => {
    estado.guardada = null;
    $("limpiar").disabled = true;
    pintarComparacion();
  };
}

inicio();

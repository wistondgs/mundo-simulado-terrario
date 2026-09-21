"""Los trece gates de 1.7 · en el orden en que se construyen.

Trece porque hay trece afirmaciones causalmente distintas. No se baja a doce.

```
G0  estructura      L17-0 linaje · L17-1 par de mundos · L17-2 procedencia
                    L17-3 pureza de la eferencia
G1  incrementalidad L17-4 invariantes · L17-5 paridad del baseline
G2  instrumentos    L17-6 exposición
G3  falsificadores  L17-9 necesidad de la acción · L17-10 opacidad
G4  localización    L17-11 localización interna · L17-12 pasividad y replay
estadísticos        L17-7 adquisición · L17-8 nulo del aprendiz
```

El orden importa: un gate posterior no debe validar datos producidos por una
infraestructura ya inválida.

**Ningún gate escanea texto.** Se camina el árbol sintáctico, por la misma razón
que en 1.6: un comentario no es un nodo y una docstring que nombra lo prohibido es
una `Constant`.

Dos nulos de B que **no se fusionan**: `L17-1` audita el mundo que construimos
nosotros, analíticamente; `L17-8` audita lo que el aprendiz afirma haber
adquirido. Uno puede pasar y el otro fallar, y significan cosas distintas.
"""

from __future__ import annotations

import ast
import hashlib
import pathlib
from dataclasses import dataclass, field

import numpy as np

PACKAGE = pathlib.Path(__file__).parent
INHERITED = PACKAGE.parent / "level16"

#: Capacidades de decimales posteriores a 1.7. No están en el disco.
LATER_CAPABILITIES = ("level11", "level12", "level13", "level14",
                      "organism", "remembered", "level18")

#: Huella del código de 1.6 tal como quedó congelado.
INHERITED_FINGERPRINT = (
    "de4bb64f9f92514d08568a43dc3171d51ea7201b254b4f48927bbbc9089039c9")

#: Lo que el aprendiz de 1.7 no puede nombrar sin dejar de serlo.
FORBIDDEN_IN_LEARNER = frozenset({
    "moved", "movement", "succeeded", "success", "collision", "collided",
    "displacement", "direction", "directions", "position", "positions",
    "actuate", "grid", "cells", "reward", "value", "novelty", "target",
    "UP", "DOWN", "LEFT", "RIGHT",
})


@dataclass(frozen=True)
class GateResult:
    name: str
    certifies: str
    passed: bool
    evidence: str


@dataclass
class GateReport:
    results: list[GateResult] = field(default_factory=list)

    def add(self, name: str, certifies: str, passed: bool, evidence: str) -> None:
        self.results.append(GateResult(name, certifies, passed, evidence))

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failures(self) -> list[GateResult]:
        return [r for r in self.results if not r.passed]


# --- escáner sintáctico ------------------------------------------------------

def identifiers(source: str) -> set[str]:
    tree = ast.parse(source)
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id)
        elif isinstance(node, ast.arg):
            found.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found.add(node.name)
    return found


def attributes(source: str) -> set[str]:
    return {n.attr for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Attribute)}


def imported_modules(source: str) -> set[str]:
    tree = ast.parse(source)
    names = {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    names |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import)
              for a in n.names}
    return names


def inherited_fingerprint(root: pathlib.Path = INHERITED) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


# ============================================================================
# G0 · estructura
# ============================================================================

def gate_lineage(report: GateReport) -> None:
    """L17-0 · 1.6 presente y congelado, nada posterior en el disco."""
    root = PACKAGE.parent
    present = [c for c in LATER_CAPABILITIES if (root / c).exists()]
    inherited_here = (root / "level1").exists() and INHERITED.exists()
    digest = inherited_fingerprint()
    frozen = digest == INHERITED_FINGERPRINT
    report.add("L17-0", "1.6 presente y congelado · capacidades posteriores ausentes",
               inherited_here and not present and frozen,
               f"level1 y level16 presentes: {inherited_here} · posteriores "
               f"presentes: {present or 'ninguna'} · huella heredada "
               f"{'coincide' if frozen else 'CAMBIÓ: ' + digest[:16]}")


def gate_world_pair(report: GateReport, seeds, kernels_for) -> None:
    """L17-1 · el par A/B, comprobado en el **kernel físico**, no en una muestra.

    `kernels_for(seed)` devuelve `(T_A, T_B, firmas)`. El gate exige topología y
    dinámica marginal idénticas, `D_W^A > 0` y `D_W^B = 0` hasta precisión de
    construcción. Un B al que una sola acción le conserve el efecto se detecta
    aquí --`I_B` salta de 0.0000 a 0.1617-- y no más tarde por un `D_C` incómodo.
    """
    fallos = []
    peor_b = 0.0
    minimo_a = float("inf")
    for seed in seeds:
        kernel_a, kernel_b, signature = kernels_for(seed)
        marginal_igual = np.allclose(kernel_a.mean(axis=1), kernel_b.mean(axis=1))
        forma_igual = kernel_a.shape == kernel_b.shape
        ia = _action_information(kernel_a, signature)
        ib = _action_information(kernel_b, signature)
        peor_b = max(peor_b, ib)
        minimo_a = min(minimo_a, ia)
        if not (marginal_igual and forma_igual and ia > 0 and ib <= 1e-12):
            fallos.append((seed, round(ia, 4), round(ib, 4), marginal_igual))
    report.add("L17-1", "A y B comparten dinámica marginal · D_W^A > 0 · D_W^B = 0",
               not fallos,
               f"D_W^A mínimo {minimo_a:.4f} · D_W^B máximo {peor_b:.3e}"
               if not fallos else f"WORLD_PAIR_CONSTRUCTION_FAIL {fallos[:3]}")


def _action_information(kernel: np.ndarray, signature: np.ndarray) -> float:
    """`I(A;O'|O)` desde un kernel de estados, con estacionaria uniforme."""
    n = len(signature)
    stationary = np.full(n, 1.0 / n)
    numerator = np.zeros((16, 4, 16))
    denominator = np.zeros(16)
    for s in range(n):
        origen = signature[s]
        denominator[origen] += stationary[s]
        for a in range(4):
            for s2 in np.nonzero(kernel[s, a])[0]:
                numerator[origen, a, signature[s2]] += stationary[s] * kernel[s, a, s2]
    conditional = np.zeros((16, 4, 16))
    p_observation = np.zeros(16)
    for origen in range(16):
        if denominator[origen] > 0:
            conditional[origen] = numerator[origen] / denominator[origen]
            p_observation[origen] = denominator[origen]
    marginal = conditional.mean(axis=1)
    total = 0.0
    for o in range(16):
        if p_observation[o] == 0:
            continue
        for a in range(4):
            for j in range(16):
                p, q = conditional[o, a, j], marginal[o, j]
                if p > 0 and q > 0:
                    total += p_observation[o] * 0.25 * p * np.log(p / q)
    return float(total)


def gate_action_provenance(report: GateReport, life, replay_commands) -> None:
    """L17-2 · cada comando reconstruible desde S0, y el azar de B es propio.

    `replay_commands(seed, n)` rehace la secuencia desde el flujo motor. Una sola
    acción sustituida después de emitirse rompe la reconstrucción.
    """
    esperados = replay_commands(life.seed, len(life.all_commands))
    discrepancias = [t for t, (a, b) in enumerate(zip(life.all_commands, esperados))
                     if a is not b]
    fuentes = {p.name for p in PACKAGE.glob("*.py")
               if "integers" in attributes(p.read_text())}
    emisiones = life.motor_emitted == len(life.all_commands)
    ok = not discrepancias and emisiones and fuentes <= {"twin.py", "shuffled.py"}
    report.add("L17-2", "todo comando salió de S0 · el azar de B es propio", ok,
               f"discrepancias {len(discrepancias)}"
               + (f" (primera en t={discrepancias[0]})" if discrepancias else "")
               + f" · emitidos {life.motor_emitted}/{len(life.all_commands)}"
               + f" · otros consumidores de azar: {sorted(fuentes) or 'ninguno'}")


def gate_efference_purity(report: GateReport, efference_type) -> None:
    """L17-3 · el canal lleva el comando opaco y nada más."""
    import dataclasses

    from terrario.level17.efference import CommandToken

    campos = [f.name for f in dataclasses.fields(efference_type)]
    solo_comando = campos == ["command"]
    rechaza = True
    for intruso in (0, "A0", None, True):
        try:
            efference_type(intruso)
            rechaza = False
        except Exception:  # noqa: BLE001 — cualquier rechazo sirve, se afina en el test
            pass
    fuente = (PACKAGE / "contingency.py").read_text()
    golpes = sorted((identifiers(fuente) | attributes(fuente)) & FORBIDDEN_IN_LEARNER)
    opaco = not isinstance(CommandToken.A0, int)
    report.add("L17-3", "copia eferente: comando opaco previo a la consecuencia, y nada más",
               solo_comando and rechaza and not golpes and opaco,
               f"campos {campos} · rechaza intrusos {rechaza} · prohibidos en el "
               f"aprendiz {golpes or 'ninguno'} · token no entero {opaco}")


# ============================================================================
# G1 · arquitectura incremental
# ============================================================================

def gate_incremental_invariant(report: GateReport, inherited, model_factory,
                               observations, commands) -> None:
    """L17-4 · nacimiento y lesión, los dos bit a bit."""
    from terrario.level17.efference import EfferenceCopy

    recien = model_factory(inherited)
    nacimiento = all(
        np.array_equal(recien.predict(o, EfferenceCopy(c)), inherited.predict(o))
        for o in observations for c in commands)

    vivido = model_factory(inherited)
    for i, o in enumerate(observations):
        vivido.observe(o, EfferenceCopy(commands[i % len(commands)]),
                       observations[(i + 1) % len(observations)])
    movido = any(
        not np.array_equal(vivido.predict(o, EfferenceCopy(c)), inherited.predict(o))
        for o in observations for c in commands)
    vivido.lesion()
    restauracion = all(
        np.array_equal(vivido.predict(o, EfferenceCopy(c)), inherited.predict(o))
        for o in observations for c in commands)

    report.add("L17-4", "C_17 = 0 ⇒ M_1 = M_0^W · la lesión vuelve bit a bit a 1.6",
               nacimiento and movido and restauracion,
               f"nacimiento {nacimiento} · aprendió algo {movido} · "
               f"restauración exacta {restauracion}")


def gate_baseline_parity(report: GateReport, life) -> None:
    """L17-5 · el gate que protege el hallazgo que salvó el diseño.

    NO-ACTION y `M_1` arrancan del mismo `M_0^W`, ven las mismas transiciones,
    tienen el mismo número de oportunidades de actualización, y difieren **sólo**
    en que `M_1` puede condicionar por el comando. Congelar NO-ACTION al final de
    la fase P en vez de dejarlo aprender reintroduce exactamente el confundido ya
    descubierto: `D_C` pasaría a mezclar acción con datos extra.
    """
    mismo_origen = life.acquired.inherited_fingerprint == life.inherited.fingerprint()
    mismas_muestras = life.no_action.updates == life.acquired.updates
    siguio_aprendiendo = life.no_action.fingerprint() != life.inherited.fingerprint()
    congelado = life.no_action.frozen
    report.add("L17-5", "NO-ACTION y M_1: mismo origen, mismas muestras, sólo difieren en el comando",
               mismo_origen and mismas_muestras and siguio_aprendiendo and congelado,
               f"mismo M_0^W {mismo_origen} · actualizaciones "
               f"{life.no_action.updates} vs {life.acquired.updates} · "
               f"NO-ACTION siguió aprendiendo {siguio_aprendiendo}")


# ============================================================================
# G2 · instrumentos
# ============================================================================

def gate_exposure(report: GateReport, life, exposure, divergence, p_reference,
                  recompute) -> None:
    """L17-6 · los instrumentos existen y son consistentes con un recálculo.

    **Una cobertura baja NO hace fallar este gate**: eso sería un resultado
    experimental, no un defecto de instrumentación.
    """
    independiente = recompute(life)
    consistente = np.array_equal(independiente, life.visits)
    completos = all(getattr(exposure, campo, None) is not None for campo in
                    ("rate", "total", "weighted_coverage", "counts_min",
                     "counts_median", "counts_p10", "counts_p90"))
    coherente = (abs(exposure.total - float(np.sum(life.visits * divergence))) < 1e-9
                 and p_reference.shape == (16, 4))
    report.add("L17-6", "D_W, E_rate, E_total, C_OA y N(o,a) medidos y consistentes",
               consistente and completos and coherente,
               f"recuento independiente coincide {consistente} · instrumentos "
               f"completos {completos} · C_OA {exposure.weighted_coverage:.3f} "
               "(un valor bajo NO hace fallar este gate)")


# ============================================================================
# G3 · falsificadores de la adquisición
# ============================================================================

def gate_action_necessity(report: GateReport, audit, shuffled_advantage,
                          false_action_advantage) -> None:
    """L17-9 · destruir la correspondencia, o falsificar el canal, mata la ventaja."""
    ok = (audit.destructive and shuffled_advantage < 0.05
          and false_action_advantage < 0.05)
    report.add("L17-9", "SHUFFLED-ACTION y FALSE-ACTION eliminan la ventaja específica",
               ok,
               f"baraja destructiva {audit.destructive} "
               f"(observado {audit.observed:.4f} ≤ tolerancia {audit.tolerance:.4f}) · "
               f"ventaja barajada {shuffled_advantage:+.4f} · "
               f"ventaja con canal falso {false_action_advantage:+.4f}")


def gate_opaque_mapping(report: GateReport) -> None:
    """L17-10 · estructural: el contenido no vive en la semántica del token."""
    aprendiz = (PACKAGE / "contingency.py").read_text()
    canal = (PACKAGE / "efference.py").read_text()
    nombres_aprendiz = identifiers(aprendiz) | attributes(aprendiz)
    direcciones = {"UP", "DOWN", "LEFT", "RIGHT"}
    sin_semantica = not (nombres_aprendiz & direcciones)
    sin_fisica = not any("wiring" in m or "level1.world" in m
                         for m in imported_modules(aprendiz))
    canal_sin_direcciones = not (identifiers(canal) & direcciones)
    phi_separado = (PACKAGE / "wiring.py").exists()
    report.add("L17-10", "el contenido no depende de semántica física del token",
               sin_semantica and sin_fisica and canal_sin_direcciones and phi_separado,
               f"aprendiz sin direcciones {sin_semantica} · sin importar φ ni "
               f"física {sin_fisica} · canal sin direcciones {canal_sin_direcciones}")


# ============================================================================
# G4 · localización causal
# ============================================================================

def gate_internal_localization(report: GateReport, model, inherited, score) -> None:
    """L17-11 · quitar 1.7 devuelve a 1.6, no a la ignorancia.

    Que la pérdida suba no basta. Se exige además que `M_0^W` no se haya movido:
    una lesión que arrasa también lo heredado no aisló la capacidad de 1.7 aunque
    la competencia se desplome.
    """
    huella_heredada = inherited.fingerprint()
    aprendido = model.acquired_snapshot()
    con_estado = score(model)

    model.lesion()
    sin_estado = score(model)
    heredado_intacto = (model.inherited_is_intact()
                        and inherited.fingerprint() == huella_heredada)

    model.load_acquired(aprendido)
    restaurado = score(model)

    ok = (sin_estado > con_estado and restaurado == con_estado
          and heredado_intacto)
    report.add("L17-11", "lesionar C_17 elimina sólo 1.7, y restaurarlo recupera exactamente",
               ok,
               f"con estado {con_estado:.4f} → lesionado {sin_estado:.4f} → "
               f"restaurado {restaurado:.4f} · M_0^W intacto {heredado_intacto}")


def gate_passivity_replay(report: GateReport, model, score, replay) -> None:
    """L17-12 · evaluar no mueve nada, y la misma foto da el mismo futuro.

    El replay incluye el azar de B: sin él, dos vidas de B «idénticas» divergen y
    el fallo se leería como un defecto del ser. Ése es el falso negativo que
    apareció probando la serialización.
    """
    huella, actualizaciones = model.fingerprint(), model.updates
    for _ in range(3):
        score(model)
    pasivo = model.fingerprint() == huella and model.updates == actualizaciones
    uno, dos = replay(), replay()
    determinista = uno == dos
    report.add("L17-12", "la evaluación es pasiva y el replay determinista",
               pasivo and determinista,
               f"tres pasadas sin mover huella ni las {actualizaciones} "
               f"actualizaciones: {pasivo} · dos replays idénticos: {determinista}")


# ============================================================================
# estadísticos · construidos ahora, probados sólo con fixtures sintéticas
# ============================================================================

def gate_action_acquisition(report: GateReport, gammas) -> None:
    """L17-7 · el criterio primario. La unidad es el PAR de mundos, no la transición."""
    valores = np.asarray(gammas, dtype=float)
    n = len(valores)
    if n < 2:
        report.add("L17-7", "Γ cumple el criterio primario", False,
                   f"hacen falta al menos dos pares; llegaron {n}")
        return
    inferior = valores.mean() - 1.96 * valores.std(ddof=1) / np.sqrt(n)
    report.add("L17-7", "Γ cumple el criterio primario: CI95 inferior > 0",
               bool(inferior > 0),
               f"n = {n} pares A/B · media {valores.mean():+.4f} · "
               f"CI95 inferior {inferior:+.4f} · positivas "
               f"{int((valores > 0).sum())}/{n}")


def gate_null_world(report: GateReport, observed, null_samples) -> None:
    """L17-8 · ¿el aprendiz inventa ventaja en B?

    Contra la nula de permutaciones estratificadas preregistrada, **no** contra
    una tolerancia inventada. Distinto de `L17-1`: aquél audita el mundo que
    construimos, éste audita lo que el aprendiz afirma haber adquirido.
    """
    nulas = np.asarray(null_samples, dtype=float)
    tolerancia = float(nulas.mean() + 4.0 * nulas.std(ddof=1))
    report.add("L17-8", "B no inventa ventaja de acción, contra su propia nula",
               bool(observed <= tolerancia),
               f"observado {observed:+.4f} ≤ tolerancia {tolerancia:+.4f} "
               f"(nula de {len(nulas)} permutaciones estratificadas, "
               f"media {nulas.mean():+.4f})"
               if observed <= tolerancia else
               f"WORLD_B_OR_MODEL_NULL_FAIL · observado {observed:+.4f} > "
               f"tolerancia {tolerancia:+.4f}")

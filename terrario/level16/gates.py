"""Los doce gates, y por qué ninguno escanea texto.

Cuatro veces en este linaje un guardián se disparó contra su propia
documentación --un `grep level12` que encontraba la frase que decía que level12
no existe, un `"act" not in fuente` que encontraba la palabra «actúa». La forma
correcta es caminar el árbol sintáctico: un comentario no es un nodo, y una
docstring que nombra lo prohibido es una `Constant`, no un identificador.

La lista de señales prohibidas está partida en dos a propósito. Los nombres
inequívocos --`reward`, `novelty`, `target`-- se prohíben tanto como variable
como atributo. Los genéricos --`value`, `values`, `label`-- sólo como
identificador propio, porque `dict.values()` es Python y no una señal de valor.
Esa distinción es lo que separa un gate de un detector de falsos positivos.
"""

from __future__ import annotations

import ast
import pathlib
from dataclasses import dataclass, field

import numpy as np

PACKAGE = pathlib.Path(__file__).parent

#: Señales cuya presencia rompería el nivel, en cualquier posición.
UNAMBIGUOUS_SIGNALS = frozenset({
    "reward", "rewards", "reinforcement", "novelty", "curiosity", "surprise",
    "target", "targets", "advantage", "utility", "goal", "intrinsic_reward",
    "q_value", "state_value", "value_estimate", "epistemic_value",
})

#: Señales cuyo nombre es además Python corriente: sólo como identificador propio.
GENERIC_SIGNALS = frozenset({"value", "values", "label", "labels"})

#: Lo que A1 no puede nombrar sin dejar de ser A1.
FORBIDDEN_IN_LEARNER = frozenset({
    "direction", "directions", "action", "actions", "act", "efference",
    "moved", "movement", "position", "positions", "delta", "changed",
    "change_label", "motor", "grid", "cells",
})

#: Capacidades de decimales posteriores. No están en el disco; el gate lo prueba.
LATER_CAPABILITIES = ("level11", "level12", "level13", "level14",
                      "organism", "remembered")


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


# --- el escáner sintáctico ---------------------------------------------------

def identifiers(source: str) -> set[str]:
    """Nombres que el código *usa como nombre*. Ni comentarios ni cadenas."""
    arbol = ast.parse(source)
    encontrados: set[str] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Name):
            encontrados.add(nodo.id)
        elif isinstance(nodo, ast.arg):
            encontrados.add(nodo.arg)
        elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            encontrados.add(nodo.name)
        elif isinstance(nodo, ast.keyword) and nodo.arg:
            encontrados.add(nodo.arg)
    return encontrados


def attributes(source: str) -> set[str]:
    return {n.attr for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Attribute)}


def imported_modules(source: str) -> set[str]:
    arbol = ast.parse(source)
    nombres = {n.module or "" for n in ast.walk(arbol) if isinstance(n, ast.ImportFrom)}
    nombres |= {a.name for n in ast.walk(arbol) if isinstance(n, ast.Import)
                for a in n.names}
    return nombres


def signal_hits(source: str) -> set[str]:
    """Señales prohibidas en una fuente. Es la vía real que usan los gates."""
    return ((identifiers(source) & (UNAMBIGUOUS_SIGNALS | GENERIC_SIGNALS))
            | (attributes(source) & UNAMBIGUOUS_SIGNALS))


def learner_hits(source: str) -> set[str]:
    return (identifiers(source) | attributes(source)) & FORBIDDEN_IN_LEARNER


def _package_sources() -> dict[str, str]:
    return {p.name: p.read_text() for p in sorted(PACKAGE.glob("*.py"))}


# --- los gates ---------------------------------------------------------------

def gate_lineage_isolation(report: GateReport) -> None:
    raiz = PACKAGE.parent
    presentes = [c for c in LATER_CAPABILITIES if (raiz / c).exists()]
    report.add("L16-0", "linaje aislado: ninguna capacidad posterior en el árbol",
               not presentes,
               f"ausentes: {', '.join(LATER_CAPABILITIES)}" if not presentes
               else f"PRESENTES: {presentes}")


def gate_action_provenance(report: GateReport, life) -> None:
    fuentes = _package_sources()
    emisores = {n for n, s in fuentes.items() if "integers" in attributes(s)}
    esperado = len(life.previous) + len(life.post_previous)
    ok = (emisores == {"motor.py"}
          and life.instruments.motor_emitted == esperado)
    report.add("L16-1", "todo acto salió de la fuente del ser", ok,
               f"emisores de actos: {sorted(emisores)} · emitidos "
               f"{life.instruments.motor_emitted} de {esperado} pasos")


def gate_motor_serialisation(report: GateReport, seed: int) -> None:
    from terrario.level16.motor import EndogenousMotor
    from terrario.level16.world import motor_stream
    motor = EndogenousMotor(motor_stream(seed))
    [motor.next() for _ in range(23)]
    foto = motor.state()
    esperado = [motor.next() for _ in range(32)]
    gemelo = EndogenousMotor(motor_stream(seed + 1))
    gemelo.restore(foto)
    ok = [gemelo.next() for _ in range(32)] == esperado and "rng" in foto
    report.add("L16-2", "el azar motor se serializa y reproduce la vida", ok,
               f"32 actos reproducidos desde una foto de {sorted(foto)}")


def gate_no_reward_signals(report: GateReport) -> None:
    golpes = {n: sorted(signal_hits(s)) for n, s in _package_sources().items()
              if signal_hits(s)}
    report.add("L16-3", "sin target, recompensa, novedad ni valor", not golpes,
               "ninguna señal en el paquete" if not golpes else f"{golpes}")


def gate_learner_is_blind(report: GateReport) -> None:
    from terrario.level16.temporal import TemporalContractError, TemporalModel
    from terrario.level1.world import Direction
    fuente = (PACKAGE / "temporal.py").read_text()
    golpes = sorted(learner_hits(fuente))
    rechaza = True
    for intruso in (Direction.UP, 1, (3, 3)):
        try:
            TemporalModel().observe((0, 0, 0, 0), intruso)  # type: ignore[arg-type]
            rechaza = False
        except TemporalContractError:
            pass
    report.add("L16-4", "A1 no ve acto, eferencia, posición ni etiqueta de cambio",
               not golpes and rechaza,
               f"identificadores prohibidos: {golpes or 'ninguno'} · "
               f"aduana en tiempo de ejecución: {'sí' if rechaza else 'NO'}")


def gate_trajectory_parity(report: GateReport, life) -> None:
    from terrario.level16.life import live
    fuente = (PACKAGE / "life.py").read_text()
    ciego = not any("temporal" in m for m in imported_modules(fuente))
    repetida = live(life.seed, steps=len(life.previous),
                    post_steps=len(life.post_previous))
    ok = ciego and repetida.instruments.trajectory_hash == life.instruments.trajectory_hash
    report.add("L16-5", "paridad de trayectoria entre brazos, por hash", ok,
               f"el cuerpo no importa la tabla: {ciego} · hash "
               f"{life.instruments.trajectory_hash[:16]}")


def gate_experience_was_sufficient(report: GateReport, life) -> None:
    from terrario.level16.shadow import AnalyticShadow, teachability
    from terrario.level16.world import build_world
    disponibles = teachability(AnalyticShadow(build_world(life.seed)), life.post)
    report.add("L16-6", "K-SOMBRA demuestra que había algo que aprender",
               disponibles > 0.05, f"{disponibles:.4f} nats disponibles sobre el prior")


def gate_beats_its_own_past(report: GateReport, losses: dict[str, np.ndarray]) -> None:
    ganancia = losses["frozen"] - losses["full"]
    ok = bool((ganancia > 0).all())
    report.add("L16-7", "FULL mejora sobre PRE y FROZEN en el banco POST", ok,
               f"{int((ganancia > 0).sum())}/{len(ganancia)} vidas · media "
               f"{ganancia.mean():+.4f} nats")


def gate_beats_shuffled(report: GateReport, losses: dict[str, np.ndarray],
                        outcomes=()) -> None:
    """Ganar al control y que el control sea un control. Son un solo gate.

    `SHUFFLE_NOT_DESTRUCTIVE` es condición de parada declarada en el oráculo §17
    y durante la campaña se calculó por vida sin que ningún gate la leyera
    (`AN-1`). Su sitio no es un gate nuevo: es la **precondición** de éste. «FULL
    supera a TEMPORAL-SHUFFLED» no afirma nada si TEMPORAL-SHUFFLED conserva la
    temporalidad, así que la comparación y la validez del comparador se aprueban
    o caen juntas.
    """
    ganancia = losses["shuffled"] - losses["full"]
    n = len(ganancia)
    inferior = ganancia.mean() - 1.96 * ganancia.std(ddof=1) / np.sqrt(n)
    intactas = [o for o in outcomes if not o.shuffle_destructive]
    ok = bool(inferior > 0) and not intactas and len(outcomes) == n
    if intactas:
        detalle = (f"BARAJA NO DESTRUCTIVA en {len(intactas)} vidas: "
                   f"{[o.seed for o in intactas]}")
    elif len(outcomes) != n:
        detalle = f"sin auditoría de baraja para las {n} vidas"
    else:
        peor = max(o.shuffle_distance_shuffled / o.shuffle_distance_full
                   for o in outcomes)
        detalle = (f"baraja destructiva en {n}/{n} · peor razón de distancia a la "
                   f"marginal {peor:.4f}")
    report.add("L16-8", "FULL supera a un TEMPORAL-SHUFFLED que de verdad baraja", ok,
               f"IC95 inferior {inferior:+.4f} · media {ganancia.mean():+.4f} · "
               f"{int((ganancia > 0).sum())}/{n} positivas · {detalle}")


def gate_state_is_causal(report: GateReport, pruebas) -> None:
    ok = all(p.state_is_causal for p in pruebas)
    report.add("L16-9", "la competencia reside en el estado aprendido", ok,
               f"{sum(p.state_is_causal for p in pruebas)}/{len(pruebas)} vidas "
               "pierden la competencia al ablacionar y la recuperan al restaurar")


def gate_measurement_is_passive(report: GateReport, life) -> None:
    from terrario.level16.arms import full
    from terrario.level16.metrics import log_loss
    modelo = full(life)
    huella, actualizaciones = modelo.fingerprint(), modelo.updates
    for _ in range(3):
        log_loss(modelo, life.post)
    ok = modelo.fingerprint() == huella and modelo.updates == actualizaciones
    report.add("L16-10", "la evaluación es completamente pasiva", ok,
               f"tres pasadas sin mover la huella ni las {actualizaciones} actualizaciones")


def gate_bitcount_cannot_explain_primary(report: GateReport, life) -> None:
    from terrario.level16.arms import StaticBitcount
    from terrario.level16.metrics import PrimaryMetricNotApplicable, log_loss
    control = StaticBitcount.fitted(life)
    try:
        log_loss(control, life.post)
        ok = False
    except PrimaryMetricNotApplicable:
        ok = not hasattr(control, "probability")
    report.add("L16-11", "STATIC-BITCOUNT no explica el endpoint primario", ok,
               "el control no predice P(o'|o) y pedírselo levanta")

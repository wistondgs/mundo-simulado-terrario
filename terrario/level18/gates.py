"""Los dieciséis gates de 1.8 · escritos ANTES que el learner.

Ésta es la diferencia con 1.7 y con todo lo anterior: el instrumento existe antes
de que exista un resultado que queramos proteger. Los gates no conocen la
arquitectura de `C_18` — hablan con protocolos mínimos, de modo que un mecanismo
cualquiera pueda ser puesto a prueba sin que el gate tenga que cambiar.

`D-4` heredado entero: en 1.7 el runner ejecutó **cero** de sus trece y el «13/13»
se construyó en un script posterior a abrir las semillas. `verify_ledger` es
obligatorio antes de emitir veredicto y fatal ante cualquier hueco.
"""

from __future__ import annotations

import ast
import hashlib
import pathlib
from dataclasses import dataclass, field

import numpy as np

PACKAGE = pathlib.Path(__file__).parent
TERRARIO = PACKAGE.parent

#: Los dieciséis. Que el runner ejecute menos es fatal, no una nota al pie.
REQUIRED_GATES = tuple(f"L18-{i}" for i in range(16))

#: Capacidades posteriores. No están en el disco; el gate lo prueba.
LATER_CAPABILITIES = ("level11", "level12", "level13", "level14",
                      "organism", "remembered", "level19")

#: Lo que el aprendiz de 1.8 no puede nombrar sin dejar de serlo.
FORBIDDEN_IN_LEARNER = frozenset({
    "cell", "cells", "cell_id", "coordinate", "coordinates", "position",
    "positions", "grid", "row", "col", "x", "y", "oracle", "true_state",
    "latent_id", "ground_truth", "reward", "value", "novelty", "target",
})

#: Constantes que reintroducirían conocimiento humano de la solución.
FORBIDDEN_CONSTANTS = frozenset({
    "NUM_LATENT_STATES", "N_STATES", "MAX_STATES", "N_LATENT", "TRUE_STATES",
    "SPLIT_THRESHOLD", "MERGE_THRESHOLD", "N_CELLS",
})


@dataclass(frozen=True)
class GateResult:
    name: str
    certifies: str
    passed: bool
    evidence: str


@dataclass(frozen=True)
class GateEntry:
    name: str
    scope: str
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


class LedgerIncomplete(RuntimeError):
    """La defensa estructural contra otro `D-4`."""


def verify_ledger(ledger, expected_scopes=None) -> None:
    """Obligatorio antes de emitir veredicto. Fatal ante cualquier hueco."""
    executed = {e.name for e in ledger}
    missing = set(REQUIRED_GATES) - executed
    if missing:
        raise LedgerIncomplete(
            f"el runner no ejecutó {sorted(missing)}; así falló 1.7 exactamente")
    unknown = executed - set(REQUIRED_GATES)
    if unknown:
        raise LedgerIncomplete(f"gates no reconocidos: {sorted(unknown)}")
    if expected_scopes is not None:
        for name, scopes in expected_scopes.items():
            got = {e.scope for e in ledger if e.name == name}
            if got != set(scopes):
                raise LedgerIncomplete(
                    f"{name}: alcances {sorted(got)}, se esperaban {sorted(scopes)}")


# --- escáner sintáctico · nunca texto ---------------------------------------

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
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
    return found


def assigned_constants(source: str) -> set[str]:
    """Nombres en MAYÚSCULAS asignados a nivel de módulo o de clase."""
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id.isupper():
                names.add(node.target.id)
    return names


def imported_modules(source: str) -> set[str]:
    tree = ast.parse(source)
    names = {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    names |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import)
              for a in n.names}
    return names


def _sources(root: pathlib.Path) -> dict[str, str]:
    return {p.name: p.read_text() for p in sorted(root.glob("*.py"))}


def fingerprint(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


# ===========================================================================
# G0 · estructura y herencia
# ===========================================================================

def gate_lineage(report: GateReport) -> None:
    """L18-0 · el linaje en el disco: 1.6 y 1.7 presentes, nada posterior."""
    present = [c for c in LATER_CAPABILITIES if (TERRARIO / c).exists()]
    inherited = all((TERRARIO / c).exists() for c in ("level1", "level16", "level17"))
    report.add("L18-0", "level1/16/17 presentes · capacidades posteriores ausentes",
               inherited and not present,
               f"heredados presentes: {inherited} · posteriores: {present or 'ninguna'}")


def gate_inherited_frozen(report: GateReport, before, after) -> None:
    """L18-1 · `M_16^W` y `C_17^W` no se movieron durante la fase A.

    `before`/`after` son pares de huellas `(m16, c17)`.
    """
    ok = before == after
    report.add("L18-1", "las huellas de M_16 y C_17 sobreviven intactas a la fase A",
               ok, f"antes {tuple(h[:12] for h in before)} · después "
                   f"{tuple(h[:12] for h in after)}")


def gate_action_provenance(report: GateReport, emitted: int, steps: int,
                           learner_source: str) -> None:
    """L18-2 · todo acto salió de S0, y `C_18` no toca la política.

    Es más estricto que en 1.7: allí bastaba con que S0 emitiera; aquí el aprendiz
    ni siquiera puede nombrar la política, porque este nivel conserva la paridad
    de trayectoria precisamente porque no la modifica.
    """
    names = identifiers(learner_source) | imported_modules(learner_source)
    touches = {n for n in names if any(k in n for k in
                                       ("policy", "politica", "motor", "act_", "choose"))}
    ok = emitted == steps and not touches
    report.add("L18-2", "todo acto salió de S0 · C_18 no toca la política", ok,
               f"emitidos {emitted}/{steps} · el aprendiz nombra política: "
               f"{sorted(touches) or 'nada'}")


def gate_efference_purity(report: GateReport, efference_type) -> None:
    """L18-3 · el canal sigue llevando comando opaco y nada más."""
    import dataclasses
    fields = [f.name for f in dataclasses.fields(efference_type)]
    ok = fields == ["command"]
    report.add("L18-3", "copia eferente: comando opaco anterior a la consecuencia",
               ok, f"campos {fields}")


# ===========================================================================
# G1 · incrementalidad
# ===========================================================================

#: Tolerancia RELATIVA de la conservación de masa. Declarada, no heredada.
#:
#: El oráculo exige `Σ_z C_0(·|z) = C_17`, que es una afirmación sobre la
#: matemática y no sobre IEEE754. Un reparto en tercios o en 0.7/0.3 deja residuo
#: de orden 1e-13 sobre conteos de orden 1e3 --1e-16 relativo-- que es
#: representación, no evidencia fabricada. Exigir `0.0` obligaría a la
#: implementación a usar sólo fracciones exactamente representables: una
#: restricción que el oráculo NO impone y que no debe entrar por la puerta de
#: atrás de un gate.
#:
#: `1e-9` relativo son ~1e-6 conteos absolutos sobre 1e3: siete órdenes por
#: encima del ruido de coma flotante y seis por debajo de un solo conteo. No deja
#: pasar ninguna fabricación con significado.
MASS_RTOL = 1e-9


def gate_mass_conservation(report: GateReport, inherited_counts, per_state_counts,
                           rtol: float = MASS_RTOL) -> None:
    """L18-4 · `Σ_z C_0(o,a,o'|z) = C_17(o,a,o')`.

    Separar, fusionar o crear estado puede **redistribuir** evidencia heredada;
    jamás fabricarla ni destruirla. Lo que se congela es esto, no el `/k`.
    """
    inherited = np.asarray(inherited_counts, dtype=float)
    total = np.zeros_like(inherited)
    for counts in per_state_counts:
        total += np.asarray(counts, dtype=float)
    absolute = np.abs(total - inherited)
    relative = absolute / np.maximum(np.abs(inherited), 1.0)
    worst_abs, worst_rel = float(absolute.max()), float(relative.max())
    ok = worst_rel <= rtol
    report.add("L18-4", "crear, separar o fusionar estado no fabrica evidencia", ok,
               f"|Σ_z C_0 − C_17| absoluto {worst_abs:.3e} · relativo "
               f"{worst_rel:.3e} (tolerancia {rtol:.0e}) · estados "
               f"{len(list(per_state_counts))}")


def gate_incremental_invariant(report: GateReport, predict_18, predict_17,
                               observations, commands) -> None:
    """L18-5 · `C_18 = 0` ⇒ `P_18 = P_17` bit a bit, y la lesión vuelve a 1.7."""
    worst = 0.0
    for observation in observations:
        base = predict_17(observation)
        for command in commands:
            worst = max(worst, float(
                np.abs(np.asarray(predict_18(observation, command)) - base).max()))
    ok = worst == 0.0
    report.add("L18-5", "C_18 = 0 ⇒ P_18 = P_17 · la lesión devuelve a 1.7", ok,
               f"peor diferencia sobre {len(observations)}×{len(commands)} = {worst:.3e}")


# ===========================================================================
# G2 · que la partición no la hayamos puesto nosotros
# ===========================================================================

def gate_no_supplied_partition(report: GateReport, fit_on, loss_of,
                               worlds, learner_source: str,
                               margin: float = 0.0) -> None:
    """L18-6 · el gate que Wis afiló, y el que hay que escribir primero.

    La afirmación NO es «produce distinto número de estados»: eso lo satisface
    cualquier mecanismo arbitrario. Es que las organizaciones resultantes **no
    sean intercambiables** — y eso se prueba trasplantando:

        organización de W_i evaluada en W_i   debe batir a
        organización de W_j evaluada en W_i        para todo j ≠ i

    Un aprendiz con partición fijada de antemano, o cuya organización no dependa
    de la evidencia, trasplanta **sin coste** y cae aquí.
    """
    constants = assigned_constants(learner_source) & FORBIDDEN_CONSTANTS
    models = {w: fit_on(w) for w in worlds}
    penalties = []
    for home in worlds:
        own = loss_of(models[home], home)
        for other in worlds:
            if other == home:
                continue
            penalties.append(loss_of(models[other], home) - own)
    penalties = np.asarray(penalties, dtype=float)
    transplant_hurts = bool(penalties.size and penalties.mean() > margin
                            and (penalties > 0).all())
    ok = transplant_hurts and not constants
    report.add("L18-6",
               "misma arquitectura · mundos distintos ⇒ organización NO intercambiable",
               ok,
               f"penalización media del trasplante {penalties.mean():+.4f} · "
               f"positiva en {int((penalties > 0).sum())}/{penalties.size} · "
               f"constantes prohibidas: {sorted(constants) or 'ninguna'}")


def gate_no_oracle_leakage(report: GateReport, learner_source: str) -> None:
    """L18-7 · el aprendiz no nombra celda, coordenada ni oráculo."""
    hits = sorted(identifiers(learner_source) & FORBIDDEN_IN_LEARNER)
    modules = imported_modules(learner_source)
    imports = sorted(m for m in modules if "oracle" in m or "shadow" in m
                     or "structure" in m)
    ok = not hits and not imports
    report.add("L18-7", "sin fuga de oráculo: ni celda, ni coordenada, ni mapa", ok,
               f"identificadores prohibidos {hits or 'ninguno'} · "
               f"importaciones de oráculo {imports or 'ninguna'}")


# ===========================================================================
# G3 · la vida y los controles
# ===========================================================================

def gate_trajectory_parity(report: GateReport, hashes) -> None:
    """L18-8 · los seis brazos comparten la vida. Sobrevive porque S0 no cambia."""
    distinct = set(hashes)
    ok = len(distinct) == 1
    report.add("L18-8", "los brazos viven literalmente la misma vida", ok,
               f"{len(hashes)} brazos · {len(distinct)} hash distinto(s)"
               + ("" if ok else f" {sorted(h[:12] for h in distinct)}"))


def gate_exposure(report: GateReport, instruments, recomputed) -> None:
    """L18-9 · instrumentos medidos y consistentes. Cobertura baja NO falla."""
    consistent = np.array_equal(np.asarray(instruments["visits"]),
                                np.asarray(recomputed))
    complete = all(k in instruments for k in
                   ("visits", "coverage", "counts_min", "rate"))
    report.add("L18-9", "exposición medida y consistente · cobertura baja NO falla",
               consistent and complete,
               f"recuento independiente coincide {consistent} · instrumentos "
               f"completos {complete} · cobertura {instruments.get('coverage', float('nan')):.3f} "
               "(un valor bajo NO hace fallar este gate)")


def gate_predictive_disambiguation(report: GateReport, deltas) -> None:
    """L18-10 · el endpoint primario. Unidad: la vida/mundo, nunca la transición."""
    values = np.asarray(deltas, dtype=float)
    n = len(values)
    if n < 2:
        report.add("L18-10", "ΔL cumple el criterio primario", False,
                   f"hacen falta al menos dos vidas; llegaron {n}")
        return
    lower = values.mean() - 1.96 * values.std(ddof=1) / np.sqrt(n)
    report.add("L18-10", "ΔL = L(C17-ONLY) − L(FULL) · CI95 inferior > 0",
               bool(lower > 0),
               f"n = {n} vidas · media {values.mean():+.4f} · CI95 inferior "
               f"{lower:+.4f} · positivas {int((values > 0).sum())}/{n}")


def gate_not_explained_by_depth_one(report: GateReport, margins) -> None:
    """L18-11 · `FULL` supera a la retención de un tick, que es SUMINISTRADA."""
    values = np.asarray(margins, dtype=float)
    ok = bool(values.size and values.mean() > 0 and (values > 0).all())
    report.add("L18-11", "FULL supera a FIXED-DEPTH-1", ok,
               f"margen medio {values.mean():+.4f} · positivo en "
               f"{int((values > 0).sum())}/{values.size}")


def gate_not_explained_by_observations(report: GateReport, margins) -> None:
    """L18-12 · `FULL` supera al estado construido sólo de observaciones.

    Medido en la adjudicación: a L=1 la historia de observaciones sola recupera
    0.0097 nats de 0.1468. Si aquí no hubiera margen, la capacidad sería
    perceptiva y no sensoriomotora, y el claim cambiaría.
    """
    values = np.asarray(margins, dtype=float)
    ok = bool(values.size and values.mean() > 0 and (values > 0).all())
    report.add("L18-12", "FULL supera a O-HISTORY-ONLY", ok,
               f"margen medio {values.mean():+.4f} · positivo en "
               f"{int((values > 0).sum())}/{values.size}")


def gate_null_context(report: GateReport, unambiguous_gain,
                      tolerance: float = 1e-9) -> None:
    """L18-13 · donde `k_o = 1` no hay nada que desambiguar.

    El nulo vive DENTRO del mundo: no hace falta fabricar un gemelo. Si `C_18`
    «mejora» en contextos sin ambigüedad, está inventando distinciones.
    """
    values = np.asarray(unambiguous_gain, dtype=float)
    worst = float(values.max()) if values.size else 0.0
    ok = worst <= tolerance
    report.add("L18-13", "C_18 no inventa distinciones donde k_o = 1", ok,
               f"mayor 'mejora' en contextos inambiguos = {worst:+.3e} "
               f"(tolerancia {tolerance:.0e})")


# ===========================================================================
# G4 · localización y pasividad
# ===========================================================================

def gate_internal_localization(report: GateReport, with_state, lesioned,
                               restored, inherited_before,
                               inherited_after) -> None:
    """L18-14 · la lesión cuesta competencia, restaurar la recupera, y `C_17` no se movió."""
    ok = (lesioned > with_state and restored == with_state
          and inherited_before == inherited_after)
    report.add("L18-14", "lesionar C_18 aísla 1.8 y deja intacto lo heredado", ok,
               f"con estado {with_state:.4f} → lesionado {lesioned:.4f} → "
               f"restaurado {restored:.4f} · heredado intacto "
               f"{inherited_before == inherited_after}")


def gate_passivity_replay(report: GateReport, before, after, replays) -> None:
    """L18-15 · evaluar no mueve nada y el replay es determinista."""
    passive = before == after
    deterministic = len(set(replays)) == 1
    report.add("L18-15", "la evaluación es pasiva y el replay determinista",
               passive and deterministic,
               f"huella intacta tras evaluar: {passive} · "
               f"{len(replays)} replays, {len(set(replays))} hash distinto(s)")

"""N1.0 · la forma causal que U1 está obligado a implementar, sellada antes del código.

This exists because of level 1.8.  There the sealed oracle asked for
`Z_{t+1} = F(Z_t, A_t, O_{t+1})` and what ran was the degenerate
`Z_{t+1} = F(Z_t, A_t)`: the observation was in the routing key and never
discriminated, and twenty peripheral gates passed while the central equation
was violated.  The campaign did not falsify its hypothesis -- it measured a
different one.

So the family is written down first and checked by execution, and the check
is deliberately independent of performance.  «Accuracy went up» is not
evidence that history entered the decision; only an intervention on the
memory token is.

**The organism never sees the experiment's labels.**  `history_id` is
experimental truth and belongs to the trace and the evaluator.  What the
organism holds is an opaque token it derives from what it perceived, and it
does not know the experimenter calls those classes H0 and H1.  A mechanism
that reads `history_id` or `correct_action` is refused whatever it scores.

**The strongest guard here is contingency reversal.**  Grepping for
`if token == tau0: return UP` finds the clumsy version of a wired-in answer
and misses every other one.  Learning the normal mapping AND its inverse from
one identical starting state cannot be faked by any wiring: what the
mechanism ends up preferring has to follow what it experienced.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable, Mapping, Protocol, Sequence

SPEC_VERSION = "terrario.lab.n10-u1-causal-form/v1"

UP, DOWN = "up", "down"
ACTIONS = (UP, DOWN)
EMPTY: str = ""


class SpecRefused(ValueError):
    """Una forma que la especificación no admite, y por qué."""


class CFResult(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    INVALID = "INVALID"


# --- lo suministrado y lo adquirido, sellado -------------------------------

SUPPLIED = (
    "cue discriminator / opaque tokenization",
    "one persistent memory slot",
    "ability to retain the token across the delay",
    "two motor actions",
    "a generic 2x2 parameter table",
    "a generic update rule",
    "the transition.consequence.energy_delta channel",
    "a minimal exploration mechanism",
)

ACQUIRED = (
    "which action becomes preferable under the first token",
    "which action becomes preferable under the second token",
)

#: Lo que N1.0 NO afirma adquirir, por mucho que pase todo.
NOT_ACQUIRED = (
    "the memory mechanism itself",
    "representation formation",
    "object concepts",
    "causal understanding",
    "state creation, birth, death, split or merge",
)

ALLOWED_INPUTS = ("perceived cue value", "present observation",
                  "own memory token", "own parameter table",
                  "transition.consequence.energy_delta")

FORBIDDEN_INPUTS = ("history_id", "correct_action", "designated",
                    "observation.agent_energy", "agent.energy",
                    "station.cue_values", "world truth of any kind")

#: Las ecuaciones, en el orden en que tienen que ocurrir.
CAUSAL_FORM = (
    "m_{t+1} = G(m_t, o_{t+1})           cue writes the token",
    "m_{t+k} = m_{t+1}                   it survives the delay",
    "a_t ~ pi_theta(o_t, m_t)            and only it can branch the decision, "
    "because o_t is identical across histories at the evaluable point",
    "theta_{t+1} = U(theta_t, m_t, a_t, c_{t+1})   with "
    "c = transition.consequence.energy_delta",
    "theta_{t+1} = theta_t               under evaluation",
)


# --- el tokenizador suministrado -------------------------------------------

def opaque_token(cue_value: float, *, places: int = 2) -> str:
    """Un símbolo interno distinto por cue perceptualmente distinto.

    Cuantiza y digiere. No se compara por igualdad cruda de floats: el
    instrumento ya tuvo un guardián que preguntaba si `0.9` estaba en un
    tensor y nunca podía decir que sí, porque el valor había pasado por
    `float32`. Y el símbolo no lleva preferencia, signo ni respuesta: sólo
    distingue.
    """
    clave = f"{round(float(cue_value), places):.{places}f}"
    return "tau_" + hashlib.sha256(clave.encode()).hexdigest()[:8]


# --- el mecanismo candidato -------------------------------------------------

class Mechanism(Protocol):
    """Lo mínimo que los gates necesitan poder intervenir."""

    memory: str
    theta: dict
    learning: bool

    def perceive(self, cue_value: float | None) -> None: ...
    def decide(self, rng: Any) -> str: ...
    def learn(self, action: str, consequence: float) -> None: ...
    def theta_digest(self) -> str: ...


Factory = Callable[[], Mechanism]


def _digest(theta: Mapping) -> str:
    plano = ";".join(f"{k}={theta[k]:.12g}" for k in sorted(theta))
    return hashlib.sha256(plano.encode()).hexdigest()


# --- los gates de forma, cada uno una intervención --------------------------

def _rng(seed: int = 0):
    import numpy as np
    return np.random.default_rng(seed)


def cf1_cue_writes_memory(make: Factory, *, cue_a: float = 0.1,
                          cue_b: float = 0.9) -> Mapping[str, Any]:
    """Dos cues perceptualmente distintos, dos tokens distintos.

    La intervención es sobre el cue percibido. El test no puede inyectar
    `history_id`: el organismo no sabe que el experimentador llama a esas
    clases H0 y H1.
    """
    a, b = make(), make()
    a.perceive(cue_a)
    b.perceive(cue_b)
    ok = a.memory != b.memory and a.memory != EMPTY and b.memory != EMPTY
    return {"gate": "CF1", "result": (CFResult.PASS if ok else CFResult.FAIL).value,
            "memory_a": a.memory, "memory_b": b.memory}


def cf2_retention(make: Factory, *, cue: float = 0.9, delay: int = 5
                  ) -> Mapping[str, Any]:
    """El token sobrevive al tramo en que el discriminador ya no se ve."""
    m = make()
    m.perceive(cue)
    antes = m.memory
    for _ in range(delay):
        m.perceive(None)
    ok = antes == m.memory and antes != EMPTY
    return {"gate": "CF2", "result": (CFResult.PASS if ok else CFResult.FAIL).value,
            "before": antes, "after": m.memory, "delay": delay}


def cf3_memory_can_modulate_decision(make: Factory, *, cue_a: float = 0.1,
                                     cue_b: float = 0.9) -> Mapping[str, Any]:
    """Estructural, no evidencia de adquisición.

    Con una tabla sintética conocida, y con observación, parámetros y RNG
    idénticos, cambiar SÓLO el token tiene que poder cambiar la acción. Si no
    puede, el mecanismo no pertenece a la familia por mucho que acierte.
    """
    de_a, de_b = [], []
    for s in range(32):
        a, b = make(), make()
        a.perceive(cue_a)
        b.perceive(cue_b)
        tabla = {(a.memory, UP): 1.0, (a.memory, DOWN): 0.0,
                 (b.memory, UP): 0.0, (b.memory, DOWN): 1.0}
        a.theta.update(tabla)
        b.theta.update(tabla)
        de_a.append(a.decide(_rng(s)))
        de_b.append(b.decide(_rng(s)))
    # Sobre varias semillas, para no depender de si la exploración se dispara
    # en una concreta. Lo que se interviene sigue siendo sólo el token.
    arriba_a = de_a.count(UP) / len(de_a)
    arriba_b = de_b.count(UP) / len(de_b)
    ok = arriba_a > arriba_b
    return {"gate": "CF3", "result": (CFResult.PASS if ok else CFResult.FAIL).value,
            "p_up_token_a": round(arriba_a, 4), "p_up_token_b": round(arriba_b, 4),
            "n_seeds": len(de_a)}


def cf4_consequence_enters_update(make: Factory, *, delta: float = 4.0
                                  ) -> Mapping[str, Any]:
    """La defensa directa contra «la consecuencia está en la Transition y
    `learn` no la mira». Es la forma exacta del defecto de 1.8."""
    mas, menos = make(), make()
    for m in (mas, menos):
        m.perceive(0.9)
    mas.learn(UP, +delta)
    menos.learn(UP, -delta)
    ok = mas.theta_digest() != menos.theta_digest()
    return {"gate": "CF4", "result": (CFResult.PASS if ok else CFResult.FAIL).value,
            "theta_plus": mas.theta_digest()[:12],
            "theta_minus": menos.theta_digest()[:12]}


def cf5_memory_enters_update(make: Factory, *, cue_a: float = 0.1,
                             cue_b: float = 0.9) -> Mapping[str, Any]:
    """Actualizar bajo un token no puede tocar la fila del otro."""
    a, b = make(), make()
    a.perceive(cue_a)
    b.perceive(cue_b)
    token_a, token_b = a.memory, b.memory
    a.learn(UP, 4.0)
    tocadas_a = {k for k, v in a.theta.items() if v != 0.0}
    ok = (a.theta_digest() != b.theta_digest()
          and all(k[0] == token_a for k in tocadas_a)
          and not any(k[0] == token_b for k in tocadas_a))
    return {"gate": "CF5", "result": (CFResult.PASS if ok else CFResult.FAIL).value,
            "touched": sorted(str(k) for k in tocadas_a)}


def cf6_action_enters_update(make: Factory) -> Mapping[str, Any]:
    """Se actualiza la entrada de la acción realmente ejecutada."""
    arriba, abajo = make(), make()
    for m in (arriba, abajo):
        m.perceive(0.9)
    arriba.learn(UP, 4.0)
    abajo.learn(DOWN, 4.0)
    t_up = {k for k, v in arriba.theta.items() if v != 0.0}
    t_dn = {k for k, v in abajo.theta.items() if v != 0.0}
    ok = t_up and t_dn and t_up != t_dn
    return {"gate": "CF6", "result": (CFResult.PASS if ok else CFResult.FAIL).value,
            "touched_up": sorted(str(k) for k in t_up),
            "touched_down": sorted(str(k) for k in t_dn)}


def cf7_evaluation_freezes(make: Factory) -> Mapping[str, Any]:
    """Congelado significa bit a bit, y con consecuencias de los dos signos."""
    m = make()
    m.perceive(0.9)
    m.learn(UP, 4.0)
    m.learning = False
    antes = m.theta_digest()
    for consecuencia in (+4.0, -4.0, +4.0):
        m.perceive(0.1)
        m.decide(_rng(1))
        m.learn(DOWN, consecuencia)
    ok = antes == m.theta_digest()
    return {"gate": "CF7", "result": (CFResult.PASS if ok else CFResult.FAIL).value,
            "before": antes[:12], "after": m.theta_digest()[:12]}


def cf8_neutral_initialization(make: Factory, *, seeds: Sequence[int] = range(16),
                               cue_a: float = 0.1, cue_b: float = 0.9
                               ) -> Mapping[str, Any]:
    """No basta con «la tabla empieza en cero»: se ejecuta la política.

    Un desempate por orden de acciones, por id de token o por RNG podría
    producir conducta condicionada por la historia el primer día, y ninguna
    inspección de la tabla lo vería.
    """
    de_a, de_b = [], []
    for s in seeds:
        a, b = make(), make()
        a.perceive(cue_a)
        b.perceive(cue_b)
        de_a.append(a.decide(_rng(s)))
        de_b.append(b.decide(_rng(s)))
    ok = de_a == de_b
    return {"gate": "CF8", "result": (CFResult.PASS if ok else CFResult.FAIL).value,
            "n_seeds": len(list(seeds)), "identical": ok,
            "actions_a": de_a[:8], "actions_b": de_b[:8]}


# --- los dos gates que no se pueden falsear --------------------------------

def _entrenar(make: Factory, contingencia: Mapping[float, str], *,
              cues: Sequence[float], trials: int, seed: int,
              delta: float = 4.0, delay: int = 3) -> Mechanism:
    """Un mundo lógico mínimo: el cue decide qué acción paga, y nada más.

    La contingencia vive aquí, en el mundo sintético, y NUNCA se le pasa al
    mecanismo: éste sólo recibe el cue percibido y, después de actuar, un
    número con signo.
    """
    rng = _rng(seed)
    m = make()
    for t in range(trials):
        cue = cues[int(rng.integers(len(cues)))]
        m.perceive(cue)
        for _ in range(delay):
            m.perceive(None)
        accion = m.decide(rng)
        m.learn(accion, +delta if accion == contingencia[cue] else -delta)
    return m


def _preferencia(m: Mechanism, token: str) -> str | None:
    arriba = m.theta.get((token, UP), 0.0)
    abajo = m.theta.get((token, DOWN), 0.0)
    if arriba == abajo:
        return None
    return UP if arriba > abajo else DOWN


def contingency_reversal(make: Factory, *, cue_a: float = 0.1, cue_b: float = 0.9,
                         trials: int = 400, seed: int = 0) -> Mapping[str, Any]:
    """El gate que ningún precableado sobrevive.

    Buscar por texto un `if token == tau0: return UP` encuentra la versión
    torpe de una respuesta cableada y se le escapan todas las demás. Aprender
    la correspondencia normal Y su inversa desde un mismo estado inicial no
    se puede fingir: lo que el mecanismo acaba prefiriendo tiene que seguir a
    lo que vivió.
    """
    tok_a, tok_b = opaque_token(cue_a), opaque_token(cue_b)
    mundo_a = {cue_a: UP, cue_b: DOWN}
    mundo_b = {cue_a: DOWN, cue_b: UP}
    ma = _entrenar(make, mundo_a, cues=(cue_a, cue_b), trials=trials, seed=seed)
    mb = _entrenar(make, mundo_b, cues=(cue_a, cue_b), trials=trials, seed=seed)
    aprendido_a = {tok_a: _preferencia(ma, tok_a), tok_b: _preferencia(ma, tok_b)}
    aprendido_b = {tok_a: _preferencia(mb, tok_a), tok_b: _preferencia(mb, tok_b)}
    ok = (aprendido_a == {tok_a: UP, tok_b: DOWN}
          and aprendido_b == {tok_a: DOWN, tok_b: UP})
    return {"gate": "CONTINGENCY_REVERSAL",
            "result": (CFResult.PASS if ok else CFResult.FAIL).value,
            "world_A_learned": {k[:12]: v for k, v in aprendido_a.items()},
            "world_B_learned": {k[:12]: v for k, v in aprendido_b.items()},
            "trials": trials}


def token_permutation(make: Factory, *, cue_a: float = 0.1, cue_b: float = 0.9,
                      trials: int = 400, seed: int = 0) -> Mapping[str, Any]:
    """Renombrar los cues, y con ellos sus experiencias, no puede cambiar nada.

    Los identificadores internos no llevan semántica; si la llevaran, el
    mecanismo aprendería mejor bajo un nombre que bajo otro.
    """
    directo = contingency_reversal(make, cue_a=cue_a, cue_b=cue_b,
                                   trials=trials, seed=seed)
    permutado = contingency_reversal(make, cue_a=cue_b, cue_b=cue_a,
                                     trials=trials, seed=seed)
    ok = (directo["result"] == CFResult.PASS.value
          and permutado["result"] == CFResult.PASS.value)
    return {"gate": "TOKEN_PERMUTATION",
            "result": (CFResult.PASS if ok else CFResult.FAIL).value,
            "direct": directo["result"], "swapped": permutado["result"]}


def world_truth_nonleakage(module_or_class: Any) -> Mapping[str, Any]:
    """El mecanismo no puede nombrar la verdad del experimento.

    Se lee el cuerpo ejecutable con docstrings quitados por AST: la prosa que
    explica qué está prohibido tiene que nombrarlo, y una guarda que cazara su
    propia explicación es un modo de fallo que este proyecto ya catalogó dos
    veces.
    """
    import ast
    import inspect
    import textwrap

    arbol = ast.parse(textwrap.dedent(inspect.getsource(module_or_class)))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Expr) and isinstance(nodo.value, ast.Constant) \
                and isinstance(nodo.value.value, str):
            nodo.value.value = ""
    codigo = ast.unparse(arbol)
    encontrados = [p for p in ("history_id", "correct_action", "designated",
                               "agent_energy", "cue_values") if p in codigo]
    return {"gate": "WORLD_TRUTH_NONLEAKAGE",
            "result": (CFResult.FAIL if encontrados else CFResult.PASS).value,
            "forbidden_found": encontrados}


# --- el gate compuesto ------------------------------------------------------

CF_GATES: tuple[tuple[str, Callable[[Factory], Mapping[str, Any]]], ...] = (
    ("CF1", cf1_cue_writes_memory), ("CF2", cf2_retention),
    ("CF3", cf3_memory_can_modulate_decision), ("CF4", cf4_consequence_enters_update),
    ("CF5", cf5_memory_enters_update), ("CF6", cf6_action_enters_update),
    ("CF7", cf7_evaluation_freezes), ("CF8", cf8_neutral_initialization),
    ("CONTINGENCY_REVERSAL", contingency_reversal),
    ("TOKEN_PERMUTATION", token_permutation),
)


def causal_form_report(make: Factory, *, source: Any = None) -> Mapping[str, Any]:
    """Conjunción. No hay puntuación agregada ni promedio que compense a nadie."""
    filas = {}
    for nombre, gate in CF_GATES:
        try:
            filas[nombre] = gate(make)
        except Exception as exc:                               # noqa: BLE001
            filas[nombre] = {"gate": nombre, "result": CFResult.INVALID.value,
                             "detail": repr(exc)}
    if source is not None:
        filas["WORLD_TRUTH_NONLEAKAGE"] = world_truth_nonleakage(source)
    todos = all(f["result"] == CFResult.PASS.value for f in filas.values())
    return {"spec_version": SPEC_VERSION,
            "G_U1_CAUSAL_FORM": (CFResult.PASS if todos else CFResult.FAIL).value,
            "gates": filas,
            "failed": [k for k, v in filas.items()
                       if v["result"] != CFResult.PASS.value]}


#: Lo que este gate NO prueba, aunque pase entero. Escrito aquí para que no
#: haya que recordarlo: no dice que U1 aprenda en el mundo real, ni con el
#: presupuesto disponible, ni que generalice, ni que supere a una baseline.
#: Dice que la implementación pertenece estructuralmente a la familia causal
#: que N1.0 exige, que es exactamente lo que 1.8 no comprobó.
WHAT_THIS_GATE_DOES_NOT_PROVE = (
    "that U1 learns in the real world",
    "that it learns within the available budget",
    "that it generalises",
    "that it beats any baseline",
)

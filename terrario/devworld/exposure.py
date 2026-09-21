"""D4 y D6 · Medir si de verdad damos experiencia, y si la damos limpia.

    D4  ExposureMeter       densidad de eventos informativos
        SaturationVerifier  ¿sigue llegando información, o repetimos más rápido?
    D6  leak_gate           ¿alguna variable incidental predice la respuesta?

Ninguna de las tres toca el mundo. Sólo lo miran.

DENSIDAD NO ES SOPORTE, Y ÉSA ES LA LECCIÓN CARA

El mundo diagnóstico da una decisión cada 8,5 pasos frente a una cada 200 del
sandbox: entre 7,5 y 23,5 veces más denso. Y aun así se agota, porque sus
situaciones distintas son DOS. Densidad alta sobre soporte mínimo es repetir
lo mismo más deprisa.

Por eso hay dos cuentas y no una:

    V_inc(t)     configuraciones incidentales distintas. Puede crecer por
                 variedad cosmética -- cambiar el retraso o los distractores
                 aumenta esta cuenta sin aportar nada que aprender.
    V_sol(t)     situaciones distintas RELEVANTES PARA LA SOLUCIÓN. Aquí, los
                 valores de cue vistos, porque el umbral se induce de ellos.

`V_inc` sin `V_sol` es exactamente la trampa contra la que avisa la
orientación. La que decide es `V_sol`, y su pendiente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from terrario.devworld.instances import DevStation, DevWorld
from terrario.devworld.kernel import CUE_BOUNDARY, CUE_MAX, CUE_MIN


# --- D4 · ExposureMeter -----------------------------------------------------

@dataclass(frozen=True)
class Exposure:
    steps: int
    informative: int
    v_inc: int
    v_sol: int

    @property
    def density(self) -> float:
        """D(t) = eventos informativos / pasos."""
        return self.informative / self.steps if self.steps else 0.0

    @property
    def steps_per_event(self) -> float:
        return self.steps / self.informative if self.informative else float("inf")


def measure(world: DevWorld) -> Exposure:
    """Un evento informativo es una estación: una decisión con consecuencia."""
    sts = world.stations
    return Exposure(
        steps=world.duration,
        informative=len(sts),
        v_inc=len({st.incidental_signature for st in sts}),
        v_sol=len({round(st.cue_value, 4) for st in sts}))


# --- D4 · SaturationVerifier ------------------------------------------------

@dataclass(frozen=True)
class Window:
    index: int
    first: int
    last: int
    new_sol: int          # valores de cue NUNCA vistos antes de esta ventana
    new_inc: int
    cum_sol: int
    repeats: int
    entropy: float        # entropía de los cues de la ventana, en bits
    band: float           # intervalo donde todavía puede estar el umbral
    rule_bits: float      # bits FIJADOS sobre z. La métrica que decide.


def saturation(world: DevWorld, *, window: int = 64) -> tuple[Window, ...]:
    """Trocear la vida y preguntar en cada tramo si todavía llega algo nuevo.

    Sin aprendiz. Esto es una propiedad DEL MUNDO, y hay que demostrarla antes
    de meter un organismo: si el mundo no da experiencia nueva, un resultado
    negativo de aprendizaje no diría nada del organismo.
    """
    seen_sol: set[float] = set()
    seen_inc: set[tuple] = set()
    out: list[Window] = []
    sts = world.stations
    for w, start in enumerate(range(0, len(sts), window)):
        chunk = sts[start:start + window]
        if not chunk:
            break
        vals = [round(st.cue_value, 4) for st in chunk]
        new_sol = len({v for v in vals} - seen_sol)
        incs = {st.incidental_signature for st in chunk}
        new_inc = len(incs - seen_inc)
        repeats = len(vals) - len(set(vals))
        _, counts = np.unique(vals, return_counts=True)
        p = counts / counts.sum()
        entropy = float(-(p * np.log2(p)).sum())
        seen_sol |= set(vals)
        seen_inc |= incs
        ups = [v for v in seen_sol if v > CUE_BOUNDARY]
        dns = [v for v in seen_sol if v <= CUE_BOUNDARY]
        lo = max(dns) if dns else CUE_MIN
        hi = min(ups) if ups else CUE_MAX
        band = max(hi - lo, 0.0)
        rule_bits = (np.log2((CUE_MAX - CUE_MIN) / band)
                     if band > 0 else float("inf"))
        out.append(Window(w, start, start + len(chunk) - 1,
                          new_sol, new_inc, len(seen_sol), repeats, entropy,
                          band, rule_bits))
    return tuple(out)


def still_informative(windows: Sequence[Window], *, tol: float = 0.05) -> bool:
    """¿Sigue llegando información sobre la REGLA en las ventanas tardías?

    Ésta es la pregunta del verificador de saturación, y NO la responde
    `dV/dt`. Medido: con cue continuo `V` crece sin límite --2045 valores
    distintos en 2048 estaciones-- y `rule_bits` pasa de 3.09 a 3.15. Variedad
    infinita, información nula. `dV/dt > 0` es necesario y no suficiente.

    El agotamiento no vive en la variedad de `n`: vive en el tamaño de `z`.
    """
    if len(windows) < 2:
        return False
    return (windows[-1].rule_bits - windows[len(windows) // 2].rule_bits) > tol


# --- D6 · Puerta antifuga ---------------------------------------------------

@dataclass(frozen=True)
class LeakVerdict:
    variable: str
    mutual_information: float
    null_mean: float
    null_p95: float
    n: int

    @property
    def leaks(self) -> bool:
        """Fuga si la información mutua observada supera el percentil 95 del
        nulo. El nulo es la MISMA cuenta con las respuestas barajadas: así el
        umbral absorbe el sesgo del estimador con muestra finita, que nunca da
        cero exacto aunque la independencia sea perfecta."""
        return self.mutual_information > self.null_p95


def _mi(x: Sequence, y: Sequence) -> float:
    """Información mutua empírica en bits, por conteo."""
    xs, xi = np.unique(np.asarray([str(v) for v in x]), return_inverse=True)
    ys, yi = np.unique(np.asarray([str(v) for v in y]), return_inverse=True)
    joint = np.zeros((len(xs), len(ys)))
    for a, b in zip(xi, yi):
        joint[a, b] += 1
    joint /= joint.sum()
    px = joint.sum(axis=1, keepdims=True)
    py = joint.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = joint * np.log2(joint / (px @ py))
    return float(np.nansum(term))


def leak_gate(stations: Iterable[DevStation], *, seed: int = 0,
              draws: int = 400) -> tuple[LeakVerdict, ...]:
    """I(Y; N) para cada variable incidental, contra su nulo por barajado.

    El valor del cue NO se audita: es el canal legítimo por el que la
    estructura llega al organismo, y su información mutua con la respuesta
    debe ser alta. Se auditan las demás.
    """
    sts = list(stations)
    y = [st.designated for st in sts]
    candidates = {
        "delay": [st.delay for st in sts],
        "n_distractors": [len(st.distractor_columns) for st in sts],
        "door_column_parity": [st.door_column % 2 for st in sts],
        "station_index_parity": [st.index % 2 for st in sts],
        # Sin distractores no hay valor: se codifica como categoría propia
        # en vez de None, que no es ordenable junto a floats.
        "first_distractor_value": [
            round(st.distractor_values[0], 2) if st.distractor_values else "ninguno"
            for st in sts],
    }
    rng = np.random.default_rng(seed)
    out: list[LeakVerdict] = []
    for name, n in candidates.items():
        obs = _mi(n, y)
        null = np.array([_mi(n, list(rng.permutation(y))) for _ in range(draws)])
        out.append(LeakVerdict(name, obs, float(null.mean()),
                               float(np.percentile(null, 95)), len(sts)))
    return tuple(out)

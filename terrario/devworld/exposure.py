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


def rule_still_informative(windows: Sequence[Window], *, tol: float = 0.05) -> bool:
    """¿Queda algo por aprender de una regla ESTABLE?

    Sirve para kernels de inducción de reglas y NO como criterio universal.
    `dV/dt` tampoco sirve, y por peor motivo: medido, con cue continuo `V`
    crece sin límite --2045 valores distintos en 2048 estaciones-- y los bits
    sobre la regla pasan de 3.09 a 3.15. Variedad infinita, información nula.
    """
    if len(windows) < 2:
        return False
    return (windows[-1].rule_bits - windows[len(windows) // 2].rule_bits) > tol


# --- D4.1 · Información EPISÓDICA -------------------------------------------

@dataclass(frozen=True)
class EpisodicInformation:
    """Lo que un mundo de MEMORIA tiene que seguir dando.

    Que la regla ya esté aprendida no es agotamiento aquí. Hace falta que cada
    instancia traiga contenido que (a) no esté disponible al actuar y (b) siga
    siendo causalmente necesario.

    SE CALCULA SOBRE LA OBSERVACIÓN COMPLETA, Y LA PRIMERA VERSIÓN NO.

    La versión anterior miraba sólo los canales de las dos puertas y declaraba
    `fuga = 0.0000` con una única configuración visible. Para el mundo
    exigente era cierto; para el gemelo de control era FALSO y aun así daba lo
    mismo, porque en el control lo que se mueve es el cue y las puertas siguen
    idénticas. Medido con el contrato 6 de D5: el control daba `renueva=True`
    cuando tiene que dar False por construcción, mientras un decodificador
    sobre la observación entera acertaba 1.0000 en el control y 0.5476 en el
    exigente sobre una tasa base de 0.5541.

    Declarar `I = 0` sobre una proyección es la fuga que este mismo módulo
    audita en D6. Aquí la medida usa el tensor entero que el motor entrega.
    """
    decoder_heldout: float       # acierto del decodificador sobre reservado
    base_rate: float             # tasa base de la clase mayoritaria
    bits_per_window: tuple[float, ...]

    @property
    def leak_at_decision(self) -> float:
        """Cuánto de la respuesta está disponible al elegir, por encima del azar."""
        return max(self.decoder_heldout - self.base_rate, 0.0)

    @property
    def renews(self) -> bool:
        if self.leak_at_decision > 0.05 or not self.bits_per_window:
            return False
        b = self.bits_per_window
        return min(b) > 0.8 and abs(b[-1] - b[0]) < 0.1


def _entropy(labels: Sequence) -> float:
    if not len(labels):
        return 0.0
    _, c = np.unique(np.asarray([str(v) for v in labels]), return_counts=True)
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def _decode(records, *, seed: int = 0) -> tuple[float, float]:
    """Vecino más próximo con reserva, sobre la observación COMPLETA.

    Más fuerte que la información mutua a 100 canales: ahí cada observación es
    única y condicionar da entropía cero por memorización, no por fuga. Un
    decodificador con partición reservada sólo acierta si la fuga generaliza.
    """
    X = np.array([r.observation for r in records], dtype=float)
    y = np.array([r.correct for r in records])
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(y))
    cut = int(0.7 * len(y))
    tr, te = idx[:cut], idx[cut:]
    if len(te) == 0 or len(np.unique(y[tr])) < 2:
        return float("nan"), float("nan")
    d = ((X[te][:, None, :] - X[tr][None, :, :]) ** 2).sum(-1)
    pred = y[tr][d.argmin(1)]
    base = max(float((y[te] == c).mean()) for c in np.unique(y))
    return float((pred == y[te]).mean()), base


def episodic_information(records, *, window: int = 128,
                         seed: int = 0) -> EpisodicInformation:
    """D4.1 sobre las decisiones REALES de un oráculo, no sobre el mundo estático.

    `records` son `oracles.DecisionRecord`: cada uno lleva el tensor completo
    que el organismo tenía delante en el instante de elegir.
    """
    y = [r.correct for r in records]
    dec, base = _decode(records, seed=seed)
    per_window = tuple(_entropy(y[s:s + window]) for s in range(0, len(y), window))
    return EpisodicInformation(dec, base, per_window)


# --- D4.3 · La reparación no puede añadir facultades ------------------------

@dataclass(frozen=True)
class FacultyGate:
    """`C(W_renovable) = C(W_base)`. Si la reparación exige una facultad más,
    falla aunque produzca más bits: ya no es el mismo problema."""
    base_with_target: float
    renewable_with_target: float
    renewable_with_extra: float
    extra_faculty: str

    @property
    def adds_faculty(self) -> bool:
        """Añade facultad si el objetivo solo deja de bastar en el renovable, y
        la facultad extra recupera lo perdido."""
        return (self.base_with_target >= 0.95
                and self.renewable_with_target < 0.95
                and self.renewable_with_extra > self.renewable_with_target)


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


def _solve(world: DevWorld, *, track_regime: bool, memory_span: int = 24) -> float:
    """Un resolutor guionizado. Los dos TIENEN memoria: retienen el cue.

    La diferencia es si además rastrean el régimen, es decir si infieren la
    frontera vigente de la experiencia reciente en vez de darla por conocida.

    SIMPLIFICACIÓN DECLARADA: se evalúa sobre la clave del mundo y no
    recorriendo el pasillo con el motor. La navegación es idéntica en los dos
    mundos que se comparan, así que no puede ser lo que los distinga; y la
    disociación completa contra el motor es D5, que sigue pendiente.
    """
    ok = 0
    hist: list[tuple[float, str]] = []
    for st in world.stations:
        if not track_regime:
            thr = 0.5
        else:
            recent = hist[-memory_span:]
            up = [v for v, s in recent if s == "up"]
            dn = [v for v, s in recent if s == "down"]
            thr = (min(up) + max(dn)) / 2 if up and dn else 0.5
        ok += ("up" if st.cue_value > thr else "down") == st.designated
        hist.append((st.cue_value, st.designated))
    return ok / len(world.stations)


def faculty_gate(base: DevWorld, renewable: DevWorld, *,
                 extra_faculty: str = "deteccion_de_regimen") -> FacultyGate:
    """D4.3 · ¿la reparación antiagotamiento cambió el problema?"""
    return FacultyGate(
        base_with_target=_solve(base, track_regime=False),
        renewable_with_target=_solve(renewable, track_regime=False),
        renewable_with_extra=_solve(renewable, track_regime=True),
        extra_faculty=extra_faculty)

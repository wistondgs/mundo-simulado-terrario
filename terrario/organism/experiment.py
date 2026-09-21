"""`ORGANISM-FUSION-HM-01` · una realización.

No es un decimal y no adquiere nada: reúne capacidades ya verificadas para
comprobar que existe **un solo organismo** que las contiene y las usa juntas.

La pregunta útil no es si las piezas caben en el mismo árbol --eso lo contestaría
una suite conjunta-- sino si ambas participan en el mismo cálculo. Eso lo
contesta el factorial, y su contenido es la **interacción**: una cantidad que
ninguna rama por sí sola podía escribir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from terrario.level11.cue import CueSemantics
from terrario.level11.metrics import alignment_rate_expected
from terrario.level12.metrics import ORACLE
from terrario.organism.agent import FusedAgent, NoMemory
from terrario.organism.core import reconstruct
from terrario.organism.memory import MemoryPhase, OneStepCueMemory
from terrario.organism.metrics import (
    ORDEN, SEALED, SEALED_INTERACTION, cue_observation_information,
    ideal_reference, interaction, joint_population_brier,
)

#: Fijo, independiente del cue e idéntico para las cuatro historias.
O_PRESENT = (1, 0, 0, 0)


@dataclass
class SeedReport:
    seed: int
    fingerprints_before: dict[str, str]
    fingerprints_after: dict[str, str]
    single_core: bool
    align_before: float
    align_after: float
    leakage: float
    memory_semantics: bool
    joint: dict[tuple[str, str], float] = field(default_factory=dict)
    reference: dict[tuple[str, str], float] = field(default_factory=dict)
    skip_tick: float = 0.0
    memory_frozen: bool = False
    passive: bool = False

    @property
    def lineage_intact(self) -> bool:
        return self.fingerprints_before == self.fingerprints_after

    @property
    def measured_interaction(self) -> float:
        return interaction(self.joint)

    @property
    def reference_interaction(self) -> float:
        return interaction(self.reference)

    def gates(self) -> dict[str, bool]:
        """Las diez del preregistro sellado, con sus nombres y sus números.

        La primera versión evaluaba nueve, y tenía además un defecto peor que
        una ausencia: usaba `F-9` para «el tick hace falta», cuando el sello le
        asigna ese número a la **pasividad**. Omitir el tick es una de las seis
        fixtures negativas obligatorias, no un gate numerado; ascenderla le
        quitaba el sitio a otra cosa y dejaba la pasividad fuera del inventario
        con su número aparentemente cubierto.

        `F-2` sí estaba verificado --en `tests/test_organism_fusion.py`-- y
        `F-9` también, sin número, bajo el epígrafe de congelación. Ningún
        número medido cambia por esto.
        """
        ordenados = [self.joint[k] for k in ORDEN]
        return {
            "F-0 un solo núcleo": self.single_core,
            "F-1 linaje intacto": self.lineage_intact,
            "F-2 M sin deriva": self.memory_frozen,
            "F-3 semántica de M": self.memory_semantics,
            "F-4 coexistencia": len(self.joint) == 4,
            "F-5 uso conjunto": (ordenados == sorted(ordenados)
                                 and len(set(ordenados)) == 4),
            "F-6 interacción superaditiva": self.measured_interaction > 0,
            "F-7 sin fuga": self.leakage == 0.0,
            "F-8 política intacta": self.align_before == self.align_after,
            "F-9 pasividad": self.passive,
        }

    def negative_fixtures(self) -> dict[str, bool]:
        """Las fixtures negativas selladas que el guion puede correr en vivo.

        Omitir el tick vive aquí, que es donde el preregistro la puso. Sigue
        evaluándose en las ocho semillas; lo que deja de hacer es ocupar el
        número de la pasividad.
        """
        return {
            "omitir el tick hunde el brazo completo":
                self.skip_tick > self.joint[("ON", "ON")],
        }

    @property
    def passes(self) -> bool:
        return all(self.gates().values())


def run_seed(seed: int, *, semantics: CueSemantics | None = None) -> SeedReport:
    semantics = semantics or CueSemantics.identity()
    organismo = reconstruct(seed, semantics=semantics)
    antes = organismo.fingerprints()
    align_antes = alignment_rate_expected(organismo, semantics)

    brazos = {
        ("ON", "ON"): FusedAgent(organismo, OneStepCueMemory(), use_h=True, use_m=True),
        ("ON", "OFF"): FusedAgent(organismo, NoMemory(), use_h=True, use_m=False),
        ("OFF", "ON"): FusedAgent(organismo, OneStepCueMemory(), use_h=False, use_m=True),
        ("OFF", "OFF"): FusedAgent(organismo, NoMemory(), use_h=False, use_m=False),
    }

    # F-0 · todos los caminos referencian el MISMO núcleo, comprobado por identidad
    unico = all(a.organism is organismo for a in brazos.values())

    joint = {k: joint_population_brier(a, semantics, O_PRESENT)
             for k, a in brazos.items()}
    referencia = {k: ideal_reference(organismo.predict_near, semantics,
                                     use_h=(k[0] == "ON"), use_m=(k[1] == "ON"))
                  for k in brazos}

    completo = brazos[("ON", "ON")]
    sin_tick = joint_population_brier(completo, semantics, O_PRESENT, skip_tick=True)

    # F-3 · la semántica sellada de M, comprobada aquí y no supuesta
    m = OneStepCueMemory()
    from terrario.level11.cue import CueToken
    m.write(CueToken.C1)
    semantica = m.peek() is None                      # leer antes del tick: nada
    m.tick()
    semantica = semantica and m.peek() is CueToken.C1  # un tick: conserva
    huella = m.fingerprint()
    m.peek()
    semantica = semantica and m.fingerprint() == huella   # leer no consume
    m.tick()
    semantica = semantica and m.phase is MemoryPhase.EMPTY  # dos ticks: expira

    return SeedReport(
        seed, antes, organismo.fingerprints(), unico, align_antes,
        alignment_rate_expected(organismo, semantics),
        cue_observation_information(semantics), semantica,
        joint, referencia, sin_tick,
        _memory_frozen(), _passive(organismo, semantics))


# ── F-2 y F-9 ────────────────────────────────────────────────────────────────

#: El blob de `705239c` del que `organism/memory.py` es copia literal.
BLOB_M = "705239c:terrario/level13/memory.py"


def _memory_frozen() -> bool:
    """`F-2` · `organism/memory.py` byte-idéntico al original congelado.

    Es el idioma del repositorio --`level11/world.py` también es copia literal
    de `level1/world.py`--, y lo que el gate impide es que la copia derive en
    silencio mientras el informe sigue diciendo que es la misma memoria.
    """
    import subprocess
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[2]
    try:
        congelado = subprocess.run(["git", "show", BLOB_M], cwd=raiz,
                                   capture_output=True, text=True,
                                   check=True).stdout
    except (subprocess.CalledProcessError, OSError):
        return False
    aqui = (raiz / "terrario" / "organism" / "memory.py").read_text(
        encoding="utf-8")
    return aqui == congelado


def _passive(organismo, semantics: CueSemantics) -> bool:
    """`F-9` · medir no mueve huellas, y las métricas no sortean nada.

    Las dos mitades son del sello. La segunda es la que nada comprobaba: el
    factorial y el Brier son cerrados por diseño, así que una llamada a un
    generador dentro de `organism/metrics.py` convertiría la medición en una
    realización más --y el informe seguiría llamándola exacta--.
    """
    antes = organismo.fingerprints()
    agente = FusedAgent(organismo, OneStepCueMemory(), use_h=True, use_m=True)
    joint_population_brier(agente, semantics, O_PRESENT)
    if organismo.fingerprints() != antes or not organismo.intact:
        return False
    return _metrics_are_closed()


def _metrics_are_closed() -> bool:
    """Cero RNG nuevo en `organism/metrics.py`, comprobado por AST."""
    import ast
    from pathlib import Path

    fuente = (Path(__file__).resolve().parent / "metrics.py").read_text(
        encoding="utf-8")
    arbol = ast.parse(fuente)
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.Import, ast.ImportFrom)):
            nombres = {a.name for a in nodo.names}
            if isinstance(nodo, ast.ImportFrom):
                nombres.add(nodo.module or "")
            if any(n.split(".")[0] == "random" or "random" in n
                   for n in nombres):
                return False
        if isinstance(nodo, ast.Attribute) and nodo.attr in {
                "default_rng", "random", "choice", "permutation", "shuffle"}:
            return False
    return True

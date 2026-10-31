#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SER-INTEGRADO-01 · composición ejecutable de órganos ya medidos.

No introduce una regla cognitiva nueva. ``SerIntegrado`` ES una ``UnidadC5``:
su hipótesis, traza, estado ``q``, pila de decisiones y contadores son el único
núcleo que leen o modifican adquisición, exploración, herencia y reparación.

Adaptaciones de ingeniería tomadas de Genesis (sin importar su runtime):
una identidad estable, instantáneas serializables y una cadena hash de
transiciones. Son trazabilidad, no evidencia de una capacidad cognitiva nueva.
La política de acciones conserva tres autoridades explícitamente distintas:

* enseñanza: una palabra del ``Maestro`` de Unidad Mínima que se vive;
* exploración 08: una transición no vista de la hipótesis compartida;
* meta 04: consulta instrumental externa; no se activa sin una meta externa.

El módulo es una prueba de integración determinista. No es la campaña factorial
ni certifica que las capacidades aisladas se transfieran conjuntamente.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from unidad_minima_01 import predict, run_world, shortlex
from unidad_minima_03_regeneracion import UnidadQueSeRelee
from unidad_minima_04_eleccion import elegir_maquina
from unidad_minima_05_banco import L_de, alcanzables, paso_de, sistema_por_indice
from unidad_minima_08_fase2 import instruibilidad, mundo_2, repertorio
from unidad_minima_09_fase2 import UnidadC5
from unidad_minima_10_maestro import MaestroMundo


SCHEMA = "ser-integrado-01/v1"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


class SerIntegrado(UnidadC5):
    """Una UnidadC5 con una identidad y traza vital, no un segundo agente.

    ``organos`` es deliberadamente un mapa de referencias al mismo objeto. Es la
    guarda de integración: la composición falla si alguno deja de compartir este
    núcleo cognitivo.
    """

    def __init__(self, *, organism_id: str, lineage_id: str, n_max: int = 8):
        super().__init__(n_max=n_max)
        # ``UnidadC5`` crea este conjunto en ``heredar``. La primera vida no
        # hereda todavía, pero su método de reparación lo consulta igualmente.
        self.heredadas: set[tuple[int, str]] = set()
        self.organism_id = organism_id
        self.lineage_id = lineage_id
        self.constitution_hash = _hash({
            "schema": SCHEMA,
            "base": "UnidadC5",
            "action_authority": ["teacher", "exploration_08", "itinerary"],
            "external_goal": "unidad_minima_04",
        })
        self.world_id = "unassigned"
        self.transition_index = 0
        self.head_hash = _hash({"genesis": True, "organism_id": organism_id, "lineage_id": lineage_id})
        self.life_trace: list[dict[str, Any]] = []
        self.organos = {
            "adquisicion_02": self,
            "regeneracion_03": self,
            "exploracion_08": self,
            "herencia_reparacion_09": self,
            "meta_externa_04": self,
            "ensenanza_10": self,
        }

    def _model_payload(self) -> dict[str, Any]:
        return {
            "q": self.q,
            "n": self.n,
            "used": self.used,
            "trace_len": len(self.trace),
            "trans": [[q, a, q2, o] for (q, a), (q2, o) in sorted(self.trans.items())],
            "heredadas": sorted([list(k) for k in getattr(self, "heredadas", set())]),
            "counters": dict(sorted(self.c.items())),
        }

    def cognitive_state(self) -> dict[str, Any]:
        """Estado adquirido; no incluye estado verdadero del mundo."""
        return {
            "schema": SCHEMA,
            "organism_id": self.organism_id,
            "lineage_id": self.lineage_id,
            "constitution_hash": self.constitution_hash,
            "world_id": self.world_id,
            "model": self._model_payload(),
        }

    def _record(self, *, kind: str, before: Mapping[str, Any], action: str | None,
                observation: int | None, source: str, consequence: Mapping[str, Any]) -> dict[str, Any]:
        after = self.cognitive_state()
        payload = {
            "schema": SCHEMA,
            "index": self.transition_index + 1,
            "previous_hash": self.head_hash,
            "kind": kind,
            "organism_id": self.organism_id,
            "lineage_id": self.lineage_id,
            "world_id": self.world_id,
            "state_before_hash": _hash(before),
            "action": action,
            "action_source": source,
            "observation": observation,
            "consequence": dict(consequence),
            "state_after_hash": _hash(after),
        }
        entry = {**payload, "transition_hash": _hash(payload)}
        self.transition_index += 1
        self.head_hash = entry["transition_hash"]
        self.life_trace.append(entry)
        return entry

    def verify_trace(self) -> bool:
        previous = _hash({"genesis": True, "organism_id": self.organism_id, "lineage_id": self.lineage_id})
        for index, entry in enumerate(self.life_trace, start=1):
            payload = {k: v for k, v in entry.items() if k != "transition_hash"}
            if entry["index"] != index or entry["previous_hash"] != previous or _hash(payload) != entry["transition_hash"]:
                return False
            previous = entry["transition_hash"]
        return previous == self.head_hash

    def laboratory_trace_contract(self) -> dict[str, Any]:
        """Proyección explícita para Terrario, sin fingir que ya es un AgentInterface.

        Los símbolos A/B y la observación binaria no son compatibles de forma
        automática con acciones enteras/canales vectoriales de Terrario. Este
        contrato conserva la procedencia necesaria para escribir un adaptador
        posterior sin mezclar la adaptación de interfaz con una afirmación de
        capacidad.
        """
        return {
            "schema": "ser-integrado-terrario-adapter/v1",
            "status": "adapter_required",
            "action_space": {"source_symbols": ["A", "B"], "target": "Terrario Action.to_int"},
            "observation_space": {"source": "binary Mealy output", "target": "Observation channels+mask"},
            "state": {"source": "trans/q/trace", "target": "agent.get_internal_state"},
            "trace_mapping": {
                "step": "index", "action": "action", "observation": "observation",
                "state_hash": "state_after_hash", "decision_source": "action_source",
            },
            "trace": list(self.life_trace),
        }

    def assert_shared_core(self) -> None:
        if any(owner is not self for owner in self.organos.values()):
            raise AssertionError("integrated_organs_do_not_share_object_identity")

    def predecir(self, a: str):
        """Reutiliza literalmente el disparador interno de regeneración de 03."""
        return UnidadQueSeRelee.predecir(self, a)

    _releerse = UnidadQueSeRelee._releerse

    def elegir_meta_externa(self, letra: str, valor: int, *, robusto: bool = True) -> dict[str, Any]:
        """04 sigue siendo instrumental: sin meta no participa en ``vivir``."""
        word, evaluated = elegir_maquina(self.trans, self.q, letra, valor, robusto)
        return {"goal": {"letter": letra, "value": valor}, "word": word, "evaluated": evaluated,
                "authority": "external_goal_04"}

    def _next_action(self, itinerary_action: str, *, explore: bool, teacher: Any,
                     taught: list[str]) -> tuple[str, str]:
        if taught:
            return taught.pop(0), "teacher_10"
        if teacher is not None and teacher.interviene(self, itinerary_action):
            word = teacher.palabra(self)
            if word:
                taught.extend(word)
                self.c["intervenciones_maestro"] += 1
                return taught.pop(0), "teacher_10"
        if explore:
            action = self.letra_elegida()
            if action is not None:
                self.c["pasos_elegidos"] += 1
                return action, "exploration_08"
        return itinerary_action, "itinerary"

    def vivir_integrado(self, step: Callable[[int, str], tuple[int, int]], x: int,
                         itinerary: Iterable[str], *, world_id: str, explore: bool = False,
                         teacher: Any = None) -> dict[str, Any]:
        """Observación → acción → consecuencia → actualización sobre el mismo núcleo."""
        self.world_id = world_id
        taught: list[str] = []
        counts: Counter[str] = Counter()
        errors = 0
        for planned in itinerary:
            before = self.cognitive_state()
            action, source = self._next_action(planned, explore=explore, teacher=teacher, taught=taught)
            prediction = self.predecir(action)
            x, observation = step(x, action)
            errors += int(prediction is None or prediction != observation)
            model_hash_before = _hash(before["model"])
            self.leer(action, observation)
            if teacher is not None:
                teacher.avanzar(action, observation)
            counts[source] += 1
            self._record(kind="step", before=before, action=action, observation=observation, source=source,
                         consequence={"prediction": prediction, "world_state_after": x,
                                      "model_changed": model_hash_before != _hash(self._model_payload())})
        return {"world_state": x, "errors": errors, "action_sources": dict(counts),
                "transitions": self.transition_index, "counters": dict(self.c)}

    def ejecutar_meta_externa(self, step: Callable[[int, str], tuple[int, int]], x: int, *,
                              letra: str, valor: int, world_id: str) -> dict[str, Any]:
        """04 ejecutado como intervención externa, no como exploración encubierta."""
        decision = self.elegir_meta_externa(letra, valor)
        word = decision["word"]
        if word is None:
            return {**decision, "executed": False, "world_state": x, "outcome": None}
        before = self.cognitive_state()
        self.world_id = world_id
        actions = tuple(word) + (letra,)
        observations = []
        for action in actions:
            prediction = self.predecir(action)
            x, observation = step(x, action)
            self.leer(action, observation)
            observations.append(observation)
            self._record(kind="external_goal_step", before=before, action=action, observation=observation,
                         source="external_goal_04",
                         consequence={"prediction": prediction, "world_state_after": x})
            before = self.cognitive_state()
        return {**decision, "executed": True, "world_state": x, "actions": actions,
                "outcome": observations[-1], "goal_met": observations[-1] == valor}

    def lesionar_y_regenerar(self, probe_action: str) -> None:
        """Lesión explícita; la recuperación la hace exactamente el disparador de 03."""
        before = self.cognitive_state()
        self.trans, self.choices, self.q, self.n, self.used = {}, [], 0, 1, 1
        self._record(kind="lesion", before=before, action=None, observation=None, source="lesion_03",
                     consequence={"model_erased": True, "trace_retained": bool(self.trace)})
        before = self.cognitive_state()
        self.predecir(probe_action)
        self._record(kind="regeneration", before=before, action=probe_action, observation=None,
                     source="regeneration_03",
                     consequence={"autorelecturas": self.c["autorelecturas"],
                                  "model_restored": bool(self.trans)})

    def medir_capacidades(self, step: Callable[[int, str], tuple[int, int]], x: int,
                           future: Iterable[str], real_states: Iterable[int]) -> dict[str, Any]:
        """Lecturas existentes: predicción, repertorio de palabras e instruibilidad."""
        future = tuple(future)
        truth, _ = run_world(step, x, future)
        hits, missing, _ = predict(self.trans, self.q, future, truth)
        words = repertorio(self.trans)
        result = {"prediction_accuracy": hits / len(future), "future_missing_routes": missing,
                  "identifies": hits == len(future) and missing == 0,
                  "word_repertoire": words,
                  "external_instructionability": instruibilidad(self.trans, step, list(real_states))}
        self.c["retencion"] += 1
        return result

    def transicionar_mundo(self, *, world_id: str) -> None:
        """C5 aplicado al mismo objeto: conserva máquina, descarta sólo traza cognitiva."""
        before = self.cognitive_state()
        self.heredar(self)
        self.world_id = world_id
        self._record(kind="world_transition", before=before, action=None, observation=None,
                     source="inheritance_repair_09",
                     consequence={"trace_discarded": True, "inherited_transitions": len(self.trans)})


def _demo() -> tuple[SerIntegrado, dict[str, Any]]:
    """Una vida única que atraviesa los órganos, sin abrir la campaña factorial."""
    organism = SerIntegrado(organism_id="ser-integrado-smoke-01", lineage_id="lineage-smoke-01", n_max=8)
    organism.assert_shared_core()
    A, B = sistema_por_indice(3, 17)
    step1 = paso_de(A, B)
    life1 = shortlex(range(1, L_de(3) + 1))
    first = organism.vivir_integrado(step1, 0, life1, world_id="W1", explore=False)
    if not organism.trans:
        raise AssertionError("acquisition_did_not_update_shared_model")
    w1_metrics = organism.medir_capacidades(step1, first["world_state"],
                                             shortlex((L_de(3) + 1, L_de(3) + 2)), alcanzables(A, B))
    goal = organism.ejecutar_meta_externa(step1, first["world_state"], letra="B", valor=1, world_id="W1")
    if not goal["executed"] or not goal["goal_met"]:
        raise AssertionError("external_goal_04_did_not_act_and_observe_in_the_shared_life")
    # Regeneración 03: la experiencia permanece y dispara su relectura interna.
    organism.lesionar_y_regenerar("A")
    if organism.c["autorelecturas"] < 1:
        raise AssertionError("regeneration_03_not_connected_to_shared_trace")
    # C5 conserva la máquina regenerada y vacía la traza sin reemplazar el organismo.
    core_id = id(organism)
    organism.transicionar_mundo(world_id="W2")
    if id(organism) != core_id or organism.trace:
        raise AssertionError("continuity_or_trace_boundary_failed")
    A2, B2 = mundo_2(A, B, 3, (0, 1), True)
    step2 = paso_de(A2, B2)
    second = organism.vivir_integrado(step2, goal["world_state"], shortlex(range(1, 5)),
                                      world_id="W2", explore=True)
    # Enseñanza 10: el maestro existente entrega una palabra que la misma unidad vive.
    # ``un_bit`` fuerza el canal mínimo existente; su limitación científica está
    # documentada en 10 y aquí sólo verifica que el órgano participa en la vida.
    teacher = MaestroMundo(step2, second["world_state"], 6, canal="un_bit", disparo="siempre")
    taught = organism.vivir_integrado(step2, second["world_state"], ("A", "B", "A", "B"),
                                      world_id="W2", teacher=teacher)
    if taught["action_sources"].get("teacher_10", 0) < 1:
        raise AssertionError("teacher_10_not_connected_to_shared_action_authority")
    retention = organism.medir_capacidades(step2, taught["world_state"], shortlex((6, 7)),
                                            range(6))
    # La exploración está conectada a C5: fuerza una hipótesis con agujero verificable.
    probe = SerIntegrado(organism_id="probe", lineage_id="probe", n_max=2)
    probe.trans, probe.q = {(0, "A"): (0, 0)}, 0
    action, source = probe._next_action("A", explore=True, teacher=None, taught=[])
    if (action, source) != ("B", "exploration_08"):
        raise AssertionError("c5_exploration_action_contract_not_connected")
    organism.assert_shared_core()
    if not organism.verify_trace():
        raise AssertionError("life_trace_hash_chain_invalid")
    return organism, {"w1": first, "w1_metrics": w1_metrics, "goal": goal, "w2": second,
                      "teacher": taught, "retention": retention,
                      "probe": {"action": action, "source": source}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prueba determinista de integración del Ser Integrado")
    parser.add_argument("--self-test", action="store_true", help="ejecuta sólo la prueba técnica corta")
    parser.add_argument("--out", help="ruta explícita para publicar la traza JSON; no pisa artefactos históricos")
    args = parser.parse_args(argv)
    if not args.self_test:
        parser.error("sólo existe --self-test; las campañas factoriales no se abren desde este módulo")
    organism, results = _demo()
    report = {"schema": SCHEMA, "integration_test": "PASS", "scientific_status": "engineering_integration_only",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "results": results, "final_cognitive_state": organism.cognitive_state(),
              "life_trace": organism.life_trace, "laboratory_contract": organism.laboratory_trace_contract(),
              "trace_valid": organism.verify_trace()}
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"integration_test": report["integration_test"], "trace_valid": report["trace_valid"],
                      "transitions": len(organism.life_trace), "out": args.out}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

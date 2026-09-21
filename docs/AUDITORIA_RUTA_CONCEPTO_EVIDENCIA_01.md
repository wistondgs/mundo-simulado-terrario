# Auditoría · de concepto a evidencia, lo que el árbol puede hacer hoy

**2026-09-21** · `712a2f7` · sin modificar código.
Cada conclusión va marcada `VERIFICADO`, `NO ENCONTRADO` o `INFERENCIA`.

---

## Lo que más importa, primero

**`VERIFICADO` · El sistema dice de sí mismo que está listo, y nombra cero
bloqueos.** Ejecutado hoy contra la base viva:

```
$ python scripts/demonstrate_cl7_runtime_readiness.py --data-root .terrario

EXECUTION_STATES:              {'COMPLETED': 1, 'READY': 137, 'RUNNING': 3}
VERIFIED_TERMINAL_EXECUTIONS:  1
SCIENTIFIC_RESULTS:            0
EMPIRICAL_EVIDENCE:            0
CONSTRUCT_VALIDATED_METRICS:   ('planned-action-evaluation-pathway',)
CL7_RUNTIME_DEMO:              READY_FOR_AUTHORIZED_INGESTION
BLOCKERS:                      NONE
```

Esa única ejecución terminal —`execution-841bf1707c9c4b9ebd87221e2947a10c`,
preregistro `PR-LIVE-ead629e4464e`— tiene **sus dos artefactos sellados en CAS**:

```
SCIENTIFIC_TRACE   491.390 bytes   fd729b3d…
TRIAL_RESULT        82.498 bytes   4426ffe3…
```

Son exactamente las entradas que `seal_metric_result` consume. **La ruta mínima
end-to-end no es hipotética: está a un paso, y el paso nunca se dio.**

---

## 1 · ¿Ruta real de concepto a ejecutable por un agente?

**`VERIFICADO` · Existe, y es corta.**

```
Concept(key="use_planner", …)        agent_composition.py:74      el catálogo
        ↓
AGENT_CONFIGS[<agente>]              agent_composition.py:40      qué ofrece cada uno
        ↓
validate_selection(sel, agente)      agent_composition.py:199     contrato, no diccionario
        ↓
create_agent(spec, config, …)        agent/agents/__init__.py:48  materialización
        ↓
self._use_planner = config[...]      agent/agents/a4_advanced.py:199   el concepto ya es conducta
```

`create_agent` **no tiene arquitectura de reserva**: un agente desconocido
levanta `AgentFactoryError` ([:61](terrario/agent/agents/__init__.py:61)).

**`VERIFICADO` · Seis consumidores reales de `validate_selection`**, no cuatro
como dice §38.8 del mapa —lo corrijo aquí—:
`sandbox_runtime.py:52`, `api.py:428`, `screen_concepts.py:234`,
`experiment_capability_acquisition.py:155`, `experiment_t0_vs_t1.py:125`,
`experiment_closed_loop_t.py:127`.

---

## 2 · ¿Dónde se define qué conceptos posee cada agente?

**`VERIFICADO` · En un solo sitio, y es por organismo desde el 2026-09-21.**

`AGENT_CONFIGS` ([agent_composition.py:40](terrario/lab/agent_composition.py:40))
mapea cada agente canónico a su configuración; `concepts_for`
([:163](terrario/lab/agent_composition.py:163)) devuelve sólo los conceptos que
ese organismo **lee de verdad**, y `config_for`
([:149](terrario/lab/agent_composition.py:149)) cierra en falso ante un agente
desconocido.

A4 ofrece diez conceptos, A5 once —`use_curiosity` es suya—.

**`VERIFICADO` · El enlace concepto→corpus sigue roto.** `corpus_block` es un
`int` ([agent_composition.py:60](terrario/lab/agent_composition.py:60)) y las
otras dos apariciones en el árbol son prosa diciendo que nadie lo lee. Al lado
existe `CorpusConceptReference`, que es la cadena verificable que le falta.

---

## 3 · ¿Existe la ruta completa concepto → … → resultado?

**`VERIFICADO` · No. Hay dos rutas y ninguna llega sola.**

**Ruta A · el banco de pruebas.** Completa hasta métrica, y **estructuralmente
incapaz** de producir evidencia:

```
validate_selection → make_spec(…, ENGINEERING_SANDBOX) → SandboxService → JSONL
```

`EvidenceFirewall.register`
([sandbox_runtime.py:73](terrario/lab/sandbox_runtime.py:73)) **levanta en sus
dos ramas**: si la clasificación no es `SCIENTIFIC` dice
«non-scientific artifacts cannot enter EvidenceGraph», y si lo es dice
«sandbox process has no scientific evidence writer». No hay paso. Y
`make_spec` con `SCIENTIFIC` también se niega, fijado en
[test_sandbox_runtime.py:16](tests/test_sandbox_runtime.py:16).

**Ruta B · el carril científico.** Llega a artefactos sellados y **se detiene
antes del resultado**: 141 preregistros, 141 ejecuciones, 476 artefactos,
`scientific_results = 0`.

**`VERIFICADO` · Las dos rutas comparten vocabulario y nadie las cruza.**
`ScientificTrialIdentity` exige claves `use_*` booleanas
([execution/runtime.py:34](terrario/lab/execution/runtime.py:34)) —el mismo
vocabulario del catálogo— pero **ningún módulo de `execution/` importa
`agent_composition`**. Un concepto ajeno o mal escrito entra al carril
científico en silencio; el catálogo, que sabría rechazarlo, no se consulta.

---

## 4 · Los hipergrafos · quién escribe, quién lee, qué decide

**`VERIFICADO` · Son tres, y sólo uno decide algo.**

| | escribe | lee | decide |
|---|---|---|---|
| **teórico** `theory_operational.py` | `theory/compiler.py`, `demonstrate_cl2/3/4` | `api.py` | **sí** · 37 `raise`; `materialize` sólo admite `APPROVED_CANDIDATES = {HYPERCAND-02, HYPERCAND-08}` ([:22](terrario/lab/hypergraph/theory_operational.py:22), [:218](terrario/lab/hypergraph/theory_operational.py:218)) |
| **operacional** `operational.py` | — | sólo `adapter.py` y su test | **no** · sin consumidor de producción |
| **intercambio** `models.py`+`adapter.py` | ingesta JSON/YAML | `api.py` | **no** |

El endpoint llamado `hypergraph` a secas sirve el **binario**; el de
hiperaristas reales se llama de otra manera.

**`VERIFICADO` · La decisión más fuerte del árbol vive aquí.**
`validate_bindings` ([:185](terrario/lab/hypergraph/theory_operational.py:185))
rechaza una ligadura en siete ejes y, si la versión empieza por `sha256:`, abre
el PDF y compara el hash. Apunta al **corpus**, nunca a la evidencia.

---

## 5 · Adquisición de habilidades · implementado vs. declarado

**`VERIFICADO` · Calculado, no declarado, y hoy da 1 de 10.** Re-ejecutado:

```
$ python scripts/passport_check.py
  procedencia   falla en 5 de 10      pureza   falla en 3 de 10
  mundo         falla en 3 de 10      instrumento  falla en 8 de 10
  listas para certificar: 1 de 10 — LEARN-A1
```

`status_of` ([capability_passport.py](terrario/lab/capability_passport.py)) no
lee un campo `status`: lo deriva en orden de precondición.

**`VERIFICADO` · La restricción que manda es el instrumento, y no por falta de
instrumentos.** Ocho de diez capacidades declaran un endpoint `PENDIENTE-*` que
el registro no puede resolver. **Eso no es un placeholder disfrazado: es un
hueco declarado que la máquina puede ver**, y es lo contrario del modo de fallo
«sustituir el endpoint que falta por una métrica parecida».

**`VERIFICADO` · El flujo de adquisición existe como guion**:
`experiment_capability_acquisition.py` implementa
`experiencia → cambio interno → capacidad nueva` con los tres enlaces rompibles
a propósito. Es sandbox; no produce evidencia.

---

## 6 · Combinar habilidades y ver si aparece algo nuevo

**`VERIFICADO` · Hay dos mecanismos, y miden cosas distintas.**

* **Contribución por concepto** · `screen_concepts.py`: organismo completo menos
  un concepto, una condición por concepto, diferencia por malla. Su propia
  cabecera dice lo que vale: «la contribución de un concepto no es propiedad del
  concepto: depende del mundo y de qué más esté presente». **Resumible por
  diseño** —JSONL incremental— porque una campaña dura horas.
* **Interacción** · el factorial 2×2 de `organism-fusion-hm-01`, que es el único
  sitio del proyecto donde se midió **superaditividad** y no sólo coexistencia.

**`VERIFICADO` · Ninguno de los dos alimenta a un hipergrafo.**
`screen_concepts` escribe JSONL y declara `ENGINEERING_SANDBOX_NOT_EVIDENCE`
([:56](scripts/screen_concepts.py:56)).

---

## 7 · ¿Qué resultados de 1.0–1.8 están conectados a la teoría?

**`VERIFICADO` · Ninguno. Cero.**

Barrido sobre el grafo del snapshot vigente `theory-f59dbb6d6ee3850c`:
`level1`, `level12`, `level13`, `level14`, `level16`, `level17`, `level18`,
`fusion`, `causal-bench` y las semillas `8000001x` dan **cero coincidencias**.

Lo que sí contiene: 141 nodos de evidencia —45 `EvidenceRecord` y 45 `Metric` de
corridas de humo con `seed-42`, 33 del piloto `h_adapt_001`, 7 de fixturas de
test, 1 nodo escrito a mano— con **135 de 136 aristas en `UNRESOLVED`**.

**`VERIFICADO` · Las siete campañas viven fuera del carril**: ninguna importa
`ArtifactRepository`, `register_blob`, `seal_metric_result`, `admit_evidence`
ni `content_hash`. Sellan commiteando un markdown y **transcriben** los valores
sellados a constantes sin que nada compruebe la transcripción.

---

## 8 · Bloqueos reales, ordenados por dependencia

1. **Nadie ha dado el paso de artefacto sellado a resultado.** Hay una ejecución
   terminal verificada con traza y resultado en CAS, y `scientific_results = 0`.
   Todo lo demás depende de esto y **no requiere arquitectura nueva**.
2. **El carril científico no valida su `agent_config` contra el catálogo.** Los
   dos vocabularios son el mismo y nadie los cruza (§3). Sin esto, un concepto
   admitido como evidencia puede no ser el que el organismo lee.
3. **El concepto no resuelve al corpus.** `corpus_block` es un entero huérfano
   con `CorpusConceptReference` a dos ficheros de distancia (§2).
4. **`validate_bindings` mira al corpus y no a la evidencia** (§4). Es la pieza
   que ya sabe hacer lo que hace falta, apuntada al otro lado.
5. **Nada consume `reconcile`.** El manifiesto de gates de `712a2f7` congela lo
   que cada gate certifica; ninguna campaña lo confronta todavía.

El orden es de dependencia: 1 desbloquea a 4, y 2 y 3 son costuras cortas que
deciden si lo que entre por 1 significa algo.

---

## 9 · Lo que ya existe y no hay que reconstruir

**`VERIFICADO`, todo comprobado en ejecución o en código:**

```
CAS + canonicalización fail-closed       persistence/canonical.py · blobs.py
manifiesto de 10 roles + verify()        preregistration/commitments.py:126
sello de resultado con hypothesis_revision   metric_result_sealing.py:58
la puerta de admisión                    evidence_admission.py
autoridad de instrumentos, 3 códigos     instrument_registry.py
cuatro estados de lectura, sin coerción  measurement_status.py:67
cadena de verificación de 7 ejes         theory_operational.py:185
catálogo de composición por organismo    agent_composition.py:40
pasaporte de capacidad derivado          capability_passport.py
cortafuegos de evidencia                 sandbox_runtime.py:73
manifiesto de gates + reconcile          preregistration/gate_manifest.py
```

---

## 10 · La ruta mínima end-to-end ejecutable hoy

**`VERIFICADO` · Existe, sin añadir arquitectura, y el propio sistema la declara
lista.**

```
execution-841bf17…  COMPLETED, terminal verificada
  SCIENTIFIC_TRACE + TRIAL_RESULT ya sellados en CAS
        ↓  seal_metric_result(…)                    metric_result_sealing.py:58
  descriptor con hypothesis_revision y trace_blob_hash
        ↓  admit_evidence(endpoint_role=…, …)       evidence_admission.py
  AdmissionVerdict con sus bloqueadores
        ↓  publicación verificada                   evidence_publication.py
  content_hash(envelope) == result_hash  ∧  los dos blobs en CAS
```

La métrica validada para su constructo existe y es una:
`planned-action-evaluation-pathway`. Es la de CL-7, y es **la misma** que el
informe de readiness nombra.

**`INFERENCIA`** · Esta ruta demostraría la cadena hasta evidencia admitida,
pero **no** demuestra «una habilidad desde concepto hasta resultado»: esa
ejecución no nació de una selección de conceptos del catálogo. Cerrar *esa*
pregunta exige además el bloqueo 2.

---

## Lo que no se puede demostrar desde el árbol

* **`NO ENCONTRADO`** · Por qué el carril se detuvo con 476 artefactos sellados
  y cero resultados. No hay documento ni evento que lo explique.
* **`NO ENCONTRADO`** · Ningún consumidor de producción del hipergrafo
  operacional. Sólo su adaptador y su test.
* **`NO ENCONTRADO`** · Ningún cruce entre el `agent_config` científico y el
  catálogo de composición.
* **`INFERENCIA`** · Que las 137 ejecuciones en `READY` sean utilizables. Están
  en ese estado, no ejecutadas; no medí si su preregistro las admite.

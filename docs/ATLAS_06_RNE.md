# Atlas 06 · RNE / runtime

**2026-09-21** · genesis-v2 `db07fa9` · depositado en
`RNE_v16-genesis-v2/docs/CARTOGRAFIA_GENESIS_01.md` **§VIII** · 9 citas
verificadas.

**§I–§VI de esa cartografía ya cubren** el lazo de vida y la propiedad del
estado, la autoridad de parámetros y el ledger de Λ, el régimen de referencia,
lo neural y el harness de gemelos. Este volumen **no los repite**: completa lo
que falta y contesta la pregunta que dejó abierta el Atlas 05.

---

## 1 · La respuesta a la pregunta central

> ¿Qué tendría que modificar Genesis para convertir una receta `PROMOTED` en una
> capacidad del organismo?

Hay **tres superficies** que pueden cambiar en RNE, y **ninguna acepta un
programa**:

| Superficie | Qué acepta | Estado |
|---|---|---|
| **mandos adaptativos** · `apply_parameter_intent` | **dos escalares**: límite de recuperación de memoria, modo de filtrado | **funciona**, con ledger y procedencia |
| **`MODEL_PARAMETER`** | pesos y arquitectura de un órgano | **declarada y vacía a propósito** |
| **componentes mutables** · `SelfModificationPipeline` | seis políticas y parámetros | **cableada** desde R1 |

Genesis promueve un artefacto de programa `int → int` de siete operadores.

**No es que falte cablear: el destinatario no existe como tipo.** La ranura más
cercana, `MODEL_PARAMETER`, está declarada para pesos y arquitectura —no para
una función— y está vacía.

## 2 · Lo que sí funciona, y lo que mueve

`autoevolution.py` cuenta su propia historia: «Hasta R1, `SelfModificationPipeline`
existía pero **nada lo invocaba**». R1 lo cableó:

```
degradación sostenida → diagnóstico → propuesta ρₜ → precheck constitucional
→ sandbox → gate de seguridad → aplicar sobre mandos REALES
→ ventana vigilando ΔIoC → commit o ROLLBACK ejecutable
```

Tres propiedades que conviene separar de la promesa:

* **el rollback es ejecutable**, no declarativo: revierte mandos **y** estado del
  organismo al checkpoint pre-modificación, y lo registra en el linaje;
* **el linaje deja de ser pasivo**: génesis, aceptaciones y rollbacks quedan en
  `LineageState` y como eventos en storage;
* **los mandos se alcanzan por closures**, para no acoplar `organism → world`.

Y lo que todo ese aparato —constitución, sandbox, posterior, gate, ventana,
rollback, linaje— puede mover son **dos parámetros de comportamiento del
runner**. No es crítica: es la medida exacta de la distancia entre el mecanismo
y su carga útil actual.

## 3 · La partición que un integrador necesitaría ya existe

```
MUTABLES (primera fase)            INMUTABLES (aprobación superior)
  transport_parameters               baseline_semantics
  selection_policy                   constitutional_invariants
  benchmark_policy_experimental      baseline_fixed
  reasoning_activation_policy        constitutional_purity_minimum
  memory_scoring_secondary_weights   lineage_identity_anchor
  analogical_lab_parameters
```

Ocho etapas de `proposal_generation` a `lineage_update`. La partición dice qué
clase de cosa puede cambiar sin aprobación superior — y ninguna de las seis es
un programa.

## 4 · Qué persiste, y en qué unidad

`OrganAdaptiveState`, por `(organism_id, lineage_id, regime_id, organ_id,
backend_id)`: participación, abstención, aceptación, rechazo, residuo de
calibración, desacuerdo causal, latencias, coste, fallbacks, permanencia en
régimen.

Es **contabilidad de comportamiento del órgano, no contenido aprendido** — y
encaja con §V: los pesos no se mueven, el estado recurrente persiste, nadie le
da error a la red. Las acciones de adaptación admisibles son cuatro y ninguna
instala nada: `collect_more_evidence · replay_candidate · hold ·
quarantine_candidate`.

## 5 · El «sin regresión» existe, y está del lado aislado

**No hay ninguna clase `RetentionLedger` en el árbol.** Lo que hay es
`lab/genesis/retention/`: paquete de auditoría, recibos de línea base y de
decisión, petición de re-verificación (recertificación), medición observada con
payload externo, vista epistémica, regla A*, replay, y una política de familia
cuyo `epsilon_family_total` es el presupuesto global de degradación — **política
conservadora: los miembros no concluyentes nunca se omiten**.

La unidad es `capability_id`. Y **`runtime/` no consume nada de eso: cero
ficheros.** Sus consumidores son sus seis módulos hermanos y ocho tests.

> Es la misma frontera del Atlas 05: el mecanismo que decidiría si una capacidad
> puede integrarse sin regresión está construido, y está del lado que no toca al
> organismo.

## 6 · En una frase

```
1. un TIPO de destino que acepte un programa     NO EXISTE
2. un canal de escritura con procedencia          EXISTE · apply_parameter_intent
3. un juicio de no-regresión                      EXISTE · lab/genesis/retention,
                                                  sin consumidor en runtime
```

El lazo ρₜ ya demuestra que 2 y 3 **pueden** funcionar juntos: aplica sobre
mandos reales, vigila ΔIoC y revierte. Lo hace con escalares porque es lo único
que hay del otro lado.

## 7 · Lo que no se sabe

1. **K2** · Si `MODEL_PARAMETER` se dejó vacía esperando los seis coeficientes
   de N4 o cualquier artefacto promovible. El código declara la clase y no dice
   para qué.
2. **K1** · El contrato nombra reparaciones abiertas que **no aparecen en ningún
   árbol**: `CI-VERDAD` da **0 coincidencias en genesis-v2 y en v16**.
   `CADENA-CAUSAL` sí existe, pero en `canon/provisional/` — provisional, no
   normativo. O viven sólo en la conversación, o tienen otro nombre en código.
3. **K2** · Si la partición mutable/inmutable está alineada con las nueve clases
   de `parameters.py`. Son dos taxonomías de lo que puede cambiar, en sitios
   distintos, sin cruzar.
4. **K3** · Qué significaría «sin regresión» para una capacidad que el organismo
   no tenía. La retención mide degradación contra una línea base; una capacidad
   nueva no tiene línea base que degradar.

# Frontera del estado aprendido en A4

**LEARNED-STATE-BOUNDARY-01 · 2026-09-18**

Este documento contesta por escrito una pregunta que estaba abierta y de la que depende el diseño
del primer piloto científico:

> ¿Qué estado de A4 es conocimiento adquirido por experiencia, qué es transitorio, y cuál de los
> dos controla `learning_commit_enabled`?

No decide nada. Mide, clasifica, y nombra las opciones. La elección es humana.

## Veredicto

```
LEARNING_COMMIT_IS_COMPLETE_FREEZE = NO
```

La intervención certificada en G4 congela **perfectamente** lo que gobierna el optimizador — cero,
exacto, en tres semillas — y **no toca** cinco piezas de estado que también dependen de la
experiencia. Una de ellas se mueve muchísimo.

## La medición

`scripts/learned_state_audit.py`, mundo generado que exige LEARN-A1, física canónica
(`build_episode_components` → `run_step`), observaciones reales. 68 pasos, 68 aprendizajes.

| | FULL | ABL |
|---|---|---|
| ‖Δ parámetros‖ (bajo optimizador) | 1.714 | **0** |
| ‖Δ M‖ (fuera del optimizador) | 41.09 | **25.02** |
| ‖Δ M‖ / ‖M inicial‖ | 76.9× | **46.8×** |
| elementos de M en el tope ±10 | 9–25 % | **9–25 %** |
| slots de M movidos | 4/4 | **4/4** |
| baseline de energía | 0.000 → −0.032 | 0.000 → −0.032 |
| buffer episódico | 16/16, 4 rotaciones | 16/16, 4 rotaciones |

Tres semillas (7, 11, 23). `‖Δ parámetros‖` bajo ABL es **exactamente 0** en las tres. `‖Δ M‖` bajo
ABL va de 46.8× a 60.1× su norma inicial, y en la semilla 11 es **mayor** que bajo FULL — la
diferencia entre brazos ni siquiera tiene signo estable. Dos corridas con la misma semilla dan
resultados idénticos.

> **Corrección a la primera versión de este documento.** Decía «saturación de M = 100 %». Esa cifra
> era `|M|max / 10`, es decir *si algún* elemento tocaba el recorte — no qué fracción lo hacía. La
> fracción real es **9–25 %**. La afirmación era una mala estadística presentada como un hecho, y
> la conclusión que colgaba de ella («una constante con forma de matriz») no se sostenía.

## Clasificación

`LEARNED` = depende de la experiencia y debe viajar a un clon de evaluación.
`TRANSIENT` = se reconstruye en cada paso.
`BOOKKEEPING` = ni una cosa ni la otra.

| Estado | Escritor | Clase | ¿Bajo la intervención? |
|---|---|---|---|
| `nn.Parameter` de los módulos registrados | `learner.py:159` | LEARNED | **sí** |
| momentos de Adam | `learner.py:159` | LEARNED | **sí** |
| `longterm_memory.M` | `memory.py:239` | LEARNED | no |
| `episodic_memory._buffer` / `_write_idx` | `memory.py:51-54` | LEARNED | no |
| `_energy_baseline` / `_baseline_count` | `a4_advanced.py:648-651` | LEARNED | no |
| `last_prediction_error` / `_last_prediction` | `a4_advanced.py:597-605` | TRANSIENT | no |
| `homeostasis._energy` | `a4_advanced.py:352` | TRANSIENT | no |
| `_hidden` (recurrente, detached) | `a4_advanced.py:403` | TRANSIENT | no |
| `_last_state` / `_last_latent` / `_last_action` | `a4_advanced.py:349,409-412` | TRANSIENT | no |
| `parameter.grad` | `learner.py:117` | TRANSIENT | no |
| `_step` / `learner._step_count` | `a4_advanced.py:747`, `learner.py:91` | BOOKKEEPING | no |
| `_trace` (agente y submódulos) | varios | BOOKKEEPING | no |

**Se adopta** la línea que `_adaptive_state_hash` ([adaptation.py:198-212](terrario/experiment/adaptation.py:198))
ya trazaba —parámetros + buffer episódico + `longterm_memory.M`, excluyendo el estado recurrente—
y se le añade `_energy_baseline`, que aquella no contemplaba y que también acumula historia.

## Lo que esto significa para el contraste FULL − ABL

El brazo suprimido **no es un control de cero aprendizaje**. Conserva tres piezas de conocimiento
adquirido, y una de ellas recorre decenas de veces su magnitud inicial. Por tanto:

- Si el piloto saliera **nulo**, no se podría distinguir «LEARN-A1 no produce efecto» de «el efecto
  ya estaba capturado por M en los dos brazos».
- Si saliera **positivo**, el contraste mediría el commit del optimizador **sobre un sustrato que se
  movió en ambos**, no aprendizaje frente a su ausencia.

Ninguna de las dos lecturas es la que el piloto pretendía obtener.

## Segunda medición: ¿M transporta información, o sólo magnitud?

`scripts/m_information_audit.py`. Que M se mueva mucho no demuestra que lleve información. Se midió
con el pipeline real y con la función de lectura del propio agente.

**El camino de lectura existe y es doble.** `hidden → longterm_memory.read(hidden) → lt_context`
([a4_advanced.py:333](terrario/agent/agents/a4_advanced.py:333)), y `lt_context` entra en el estado
que ve la política ([:337](terrario/agent/agents/a4_advanced.py:337)). M aparece **dos veces** en la
lectura: `key_proj(M)` fija la atención y `attn @ M` es el valor devuelto
([memory.py:181-186](terrario/agent/memory.py:181)).

**La dinámica real de la escritura.** `g` medido: mínimo 0.43, medio 0.71–0.86, máximo ~1.0. Es
decir, `M·(1−g)` retiene entre el 0 % y el 57 % de M por escritura.

> **Segunda corrección.** La primera versión decía que la regla «no tiene término de decaimiento».
> Es falso: `M·(1−g)` **es** el término de retención, y con `g` medio ~0.79 el olvido es fuerte, no
> ausente. Escribí una propiedad formal sin medir el rango de `g`.

Estructura de M tras la historia: entropía de signo **1.0** (signos perfectamente balanceados) y
**rango efectivo 1.0–1.3 sobre 4**. M no está vacía, pero colapsa a esencialmente una dirección.

**Contrafáctico.** Dos historias con la **misma geometría, mismos cues, misma semilla** y la
contingencia invertida (mismo mundo, reglas del canal oculto dadas vuelta), ambas bajo
SUPPRESS_COMMIT:

| | semilla 7 | semilla 11 | semilla 23 |
|---|---|---|---|
| signos distintos entre M_A y M_B | 0 / 32 | 0 / 32 | 0 / 32 |
| coseno(M_A, M_B) | 0.802 | **1.000** | **1.000** |
| diferencia relativa de recuperación | 0.635 | **0** | **0** |

En dos de las tres semillas **M acaba siendo idéntica** bajo contingencias opuestas. M se escribe
desde `hidden`, que viene de la observación; si el organismo no llega a consumir nada distinto, la
inversión de las reglas no le llega.

**Prueba causal.** Mismo estado en todo salvo M, comparando logits antes del muestreo:

| | ABL | FULL |
|---|---|---|
| observaciones donde los logits cambiaron | 24 / 24 | 24 / 24 |
| ‖Δ logits‖ relativo a ‖logits‖ | 1.2e-06 … 0 | 2.5e-07 … 0.043 |
| **acciones que cambiaron** | **0** | **0** |
| **veces que se invirtió la preferencia entre puertas** | **0** | **0** |

La ruta causal existe y es real, pero su efecto va de exactamente 0 a 4.3 % de la norma de los
logits, y **en ninguna semilla, en ninguno de los dos brazos, intercambiar toda la memoria por la de
una historia con la contingencia opuesta cambió una sola decisión.**

## Desactivar la memoria a largo plazo es local

`use_longterm_memory=False`: la escritura está gateada
([a4_advanced.py:587](terrario/agent/agents/a4_advanced.py:587)) y la lectura se sustituye por ceros
**conservando la dimensión** ([:335](terrario/agent/agents/a4_advanced.py:335)).

| | ON | OFF |
|---|---|---|
| `_state_dim` | 64 | 64 |
| encoder / policy_head / temporal_core / world_model / uncertainty | idénticos | idénticos |
| módulos en el learner | 6 | 5 (sale `longterm_memory`) |

No apaga ninguna otra capacidad ni cambia ninguna dimensión.

```
LTM_DISABLE_IS_COMPOSITION_LOCAL = YES
```

## Gates

```
LSB.1  ABL_PARAMETER_DELTA_ZERO_RECONFIRMED   PASS    exactamente 0, tres semillas
LSB.2  M_MUTATION_REPRODUCIBLE                PASS    dos corridas idénticas
LSB.3  M_SATURATION_CHARACTERIZED             PASS    9–25 % en tope, entropía de signo 1.0,
                                                      rango efectivo 1.0–1.3 / 4
LSB.4  M_HISTORY_DISCRIMINATION               PARCIAL 1 de 3 semillas; en 2 M es idéntica
LSB.5  M_RETRIEVAL_DIFFERENTIATES             PARCIAL misma proporción
LSB.6  M_CAUSALLY_AFFECTS_POLICY              PASS    ruta real, efecto 0 … 4.3 % relativo
LSB.7  M_MAPPING_CARRIER                      NO      cero decisiones cambiadas, cero
                                                      inversiones de preferencia
LSB.13 LTM_DISABLE_IS_COMPOSITION_LOCAL       PASS
LSB.15 NO_PRODUCTION_CODE_CHANGED             PASS
LSB.8  EPISODIC_STATE_CLASSIFIED              UNKNOWN clasificado por lectura, sin prueba causal
LSB.9  RECURRENT_STATE_CLASSIFIED             UNKNOWN idem
LSB.10 HOMEOSTASIS_CLASSIFIED                 UNKNOWN idem
LSB.11 LEARNER_BASELINE_CLASSIFIED            UNKNOWN idem
```

Los cuatro `UNKNOWN` no se convierten en `PASS`: están clasificados leyendo el código, no probados
con el mismo contrafáctico que se aplicó a M.

## Opciones, sin elegir ninguna

1. **Declararlo como confusor conocido.** El preregistro declara que M, el buffer y el baseline se
   mueven en los dos brazos, con la medición adjunta: M no cambió ninguna decisión en ninguna
   semilla. Es la opción que la evidencia sostiene hoy para M — pero no dice nada de los otros
   tres estados, que siguen sin prueba causal.
2. **Componer el piloto sin memoria a largo plazo** (`use_longterm_memory=False`). No toca código de
   A4, sólo la configuración de la composición. Elimina el confusor mayor de raíz, a cambio de medir
   LEARN-A1 en un organismo que no es el de la campaña — y de que la composición pase a ser parte
   del claim.
3. **Extender la intervención para congelar M bajo ABL.** Haría de ABL un control limpio, pero
   **cambia la frontera causal certificada en G4** y el manifiesto de intervención aprobado. Reabre
   G4.
4. **Auditar los otros tres estados adaptativos** con el mismo contrafáctico aplicado a M: buffer
   episódico, estado recurrente y baseline del learner. Es lo único que falta para poder afirmar
   que la frontera está caracterizada y no sólo inventariada.

## Lo que queda comprobado y no hay que rehacer

- La intervención de G4 **sí** es un congelamiento perfecto de los parámetros del optimizador:
  `‖Δ‖ = 0` exacto. G4 no está en cuestión; lo que está en cuestión es si el optimizador es toda la
  frontera del aprendizaje en A4, y no lo es.
- La sonda es determinista y de sólo lectura: dos corridas con la misma semilla dan lo mismo, y
  `git status` queda limpio tras ejecutarla.

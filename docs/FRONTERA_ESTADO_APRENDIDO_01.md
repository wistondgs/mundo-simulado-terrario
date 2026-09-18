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
| saturación de M | 100 % | **100 %** |
| slots de M movidos | 4/4 | **4/4** |
| baseline de energía | 0.000 → −0.032 | 0.000 → −0.032 |
| buffer episódico | 16/16, 4 rotaciones | 16/16, 4 rotaciones |

Tres semillas (7, 11, 23). `‖Δ parámetros‖` bajo ABL es **exactamente 0** en las tres. `‖Δ M‖` bajo
ABL va de 46.8× a 60.1× su norma inicial, y en la semilla 11 es **mayor** que bajo FULL — la
diferencia entre brazos ni siquiera tiene signo estable. Dos corridas con la misma semilla dan
resultados idénticos.

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

## Hallazgo secundario, independiente del piloto

**`M` satura.** Alcanza el recorte de ±10 de `memory.py:239` al 100 % en los dos brazos, en 68
pasos, en las tres semillas. Una memoria saturada no almacena nada discriminativo: es una
constante con forma de matriz. La regla de escritura

```
M ← M·(1−g) + outer(w, v)·g
```

no tiene término de decaimiento hacia cero ni normalización, así que con `g` apreciable y escrituras
repetidas el punto fijo está en el clamp.

Esto no es asunto de LEARN-A1 y **no se toca aquí**, pero afecta a lo que LTMEM-A1 pueda afirmar
alguna vez, y conviene que quede registrado antes de que alguien construya un mundo que exija
memoria persistente. Sigue a `docs/MUNDOS_DIAGNOSTICOS_01.md`, nivel 3.

## Opciones, sin elegir ninguna

1. **Declararlo como confusor conocido.** No tocar nada; el preregistro declara que M, el buffer y
   el baseline se mueven en los dos brazos, y el claim se acota a «el commit del optimizador sobre
   este sustrato». Honesto, barato, y deja el resultado nulo sin interpretación.
2. **Componer el piloto sin memoria a largo plazo** (`use_longterm_memory=False`). No toca código de
   A4, sólo la configuración de la composición. Elimina el confusor mayor de raíz, a cambio de medir
   LEARN-A1 en un organismo que no es el de la campaña — y de que la composición pase a ser parte
   del claim.
3. **Extender la intervención para congelar M bajo ABL.** Haría de ABL un control limpio, pero
   **cambia la frontera causal certificada en G4** y el manifiesto de intervención aprobado. Reabre
   G4.
4. **Reparar la saturación primero.** Si M satura, quizá no hay nada que congelar: el confusor
   podría ser grande en norma y nulo en información. Requiere su propia auditoría, y es la única
   opción que responde *qué* está guardando M además de *cuánto* se mueve.

## Lo que queda comprobado y no hay que rehacer

- La intervención de G4 **sí** es un congelamiento perfecto de los parámetros del optimizador:
  `‖Δ‖ = 0` exacto. G4 no está en cuestión; lo que está en cuestión es si el optimizador es toda la
  frontera del aprendizaje en A4, y no lo es.
- La sonda es determinista y de sólo lectura: dos corridas con la misma semilla dan lo mismo, y
  `git status` queda limpio tras ejecutarla.

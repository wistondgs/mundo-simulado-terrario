# Revisión del generador de mundos

**2026-09-18 · `terrario/lab/world_generator.py`, `world_oracles.py` y `docs/MUNDOS_DIAGNOSTICOS_01.md`**

Escrita a petición explícita: *«yo no creé ningún mundo, creé un generador de mundos, porque cada
concepto —o par, o terna, según el pasaporte— se iba a crear cada mundo según sus necesidades».*

La premisa es correcta y el generador la cumple. Esta revisión pasó por una ronda adversarial de
quince agentes contra los PDF del corpus y contra el código; **corrigió dos afirmaciones mías** y
encontró dos defectos críticos en la parte que yo había declarado sana. Lo que sigue es la versión
posterior a esa corrección, y a las reparaciones que la siguieron.

---

## 1 · Lo que la ronda adversarial me corrigió

**(a) Sobrepasé a Ashby.** Escribí que S.5/2 «rechaza exactamente» la tarea cue→puerta correcta.
No es así. S.5/2 rechaza una **definición candidata** de «adaptativo», dentro de una sección
(S.5/1) cuyo propósito declarado es fijar una definición, y S.5/3 entrega de inmediato el
reemplazo. No rechaza el paradigma experimental: la propia derivación del segundo lazo de
retroalimentación de Ashby corre sobre una tarea cue→respuesta correcta (el gato de Thorndike,
S.7/4), y S.8/16 gradúa entornos por dificultad explícitamente. **Seis de los siete ejes son
propiedades de entorno que Ashby nombra y analiza él mismo** — `delay` en S.8/15, `hidden` en
S.7/4, `sequence` en S.5/12, `risk` en S.8/14, `novelty` en S.8/10, `inversion` en S.8/10, donde
Ashby produce su segundo entorno invirtiendo la polaridad de un conmutador del Homeostato. Sólo
`distractors` queda flojo. (La alineación es retroactiva: los ejes se derivaron de los pasaportes
y nunca citaron a Ashby. Pero existe.)

Lo que sí sobrevive, y es más estrecho y más accionable: **la clave del experimentador sobrevive en
la instrumentación, no en la física**. `correct_side` → `Score.correct` → `accuracy` es lo que
S.5/2 prohíbe. La física ya cobra en energía contra un umbral. Es un arreglo de métrica, no un
reemplazo de contenido.

Verbatim, del corpus v2 (`extracted_text/HEA-014.txt:5608-5662`, indexado como `R-HEA-014-001`):

> responds correctly to a stimulus … may be rejected … it presupposes an action by an experimenter
> … no meaning for correctly unless it means conforming to what the experimenter thinks the animal
> ought to do. Such a definition is useless.

Y el reemplazo, S.5/3: *a form of behaviour is adaptive if it maintains the essential variables
within physiological limits*.

**(b) Mi división «arquitectura sana / contenido malo» estaba al revés en lo peor.** Los dos
defectos más graves estaban en la maquinaria que yo defendí, y uno de ellos en la pieza que cité
como virtud.

**(c) Un dato mío estaba mal.** Dije que el organismo llega a 2 columnas de 34 y se muere a los 133
pasos. Medido: **0 columnas, 0 decisiones, `accuracy=None` en los siete mundos**. Los 133 pasos son
la vida de no hacer nada (20.0/0.15), no lo que pasa: el episodio se trunca vivo a los 68 pasos con
9.80 de energía en cuatro mundos, a los 132 con 0.20 en dos, y sólo TEMP-A1 muere de verdad.

---

## 2 · Los cuatro defectos medidos, y su reparación

### D1 · El control no era un control, en 4 de 7 ejes · REPARADO

`generate()` abría **un solo flujo de azar** y sorteaba un número variable de valores por estación
según la exigencia. Encender `distractors`, `sequence`, `risk` o `novelty` consumía de más, corría
el flujo, y **regeneraba todo lo sorteado después — incluido `designated`, que ningún eje debe
tocar**. Medido sobre 8 estaciones: 40 sorteos frente a 16 (distractors), 24/16 (sequence), 24/16
(risk), 20/16 (novelty). A semilla 9, LTMEM exigente daba
`['down','down','down','up','down','up','down','down']` y su control
`['down','down','down','down','up','up','up','down']`.

Lo peor: **yo cité `axis_difference` como la garantía de que el control es un control**. Compara el
`Demand` —la especificación— y nunca el mundo realizado. Devolvía `('distractors',)` para el par
contaminado. Y el único test de la propiedad, `tests/test_world_generator.py:51`, fijaba EPMEM-A1,
uno de los tres ejes limpios.

**Reparación:** `_stream(seed, station, purpose)` — un flujo por estación y propósito, de modo que
el contenido es función de `(semilla, estación, propósito)` y de nada más. Medido después:
**0 de 42 pares (capacidad × semilla) con `designated` divergente**, antes 24 de 42. Test
generalizado a las siete capacidades y tres semillas.

### D2 · El contraste de memoria era también un contraste de viabilidad · REPARADO

`duration = 2 × ancho`, y el ancho es función de `delay` y `sequence`. Apagar el eje acortaba el
pasillo y con él la vida y el gasto metabólico:

```
                 antes                        después
EPMEM-A1   19.80 / 10.20  (inicial 20.00)   19.80 / 19.80
TEMP-A1    31.80 / 19.80                    31.80 / 31.80
```

El sesgo era **de un solo lado**: el control nunca moría. Medido por la ronda adversarial, 0.175
del déficit de memoria de EPMEM-A1 era truncamiento metabólico, no falta de memoria.

**Reparación:** `generate(..., duration=...)` y `control_for` fija la duración del control a la del
mundo exigente. Los siete pares quedan con presupuesto idéntico, con test por capacidad.

**Efecto sobre el resultado científico — mejora, no lo rompe.** El brazo amputado de memoria pasa
de 0.345 a **0.521 ≈ azar**, que es el número correcto: un oráculo sin memoria debe puntuar azar,
no menos. Lo que faltaba para llegar a azar era comida, no memoria.

### D3 · Un cadáver puntuaba mejor que un superviviente · REPARADO

`Score` no tenía canal de viabilidad: sus siete campos contaban decisiones. Los datos existían y se
tiraban — `run_life` devuelve `StepOutcome` con `terminated` y energía por paso, y `life_score` los
descartaba en una línea. Medido sobre 420 vidas de oráculo: **7 vidas MUERTAS puntuaban accuracy
1.0**, y en el mismo mundo la semilla 2 moría en el paso 61 con accuracy 1.0 mientras la 1
sobrevivía los 212 pasos con 0.6.

Eso es precisamente lo que S.3/15 define como lo contrario de sobrevivir: *a line of behaviour that
takes no essential variable outside given limits*.

**Reparación:** `Viability(steps_lived, survived, final_energy, min_energy,
steps_below_threshold)`, `viability_from(world, outcomes)`, y `Score.viability` / `Score.died`
—`None` cuando nadie midió, en vez de suponer. `life_score` la rellena.

Medido después: **0 vidas muertas con accuracy 1.0**. Y las 11 muertes que quedan están **todas en
brazos amputados, ninguna en brazos completos** — la muerte pasó a ser consecuencia de la
amputación, que es el criterio de Ashby, en vez de un artefacto de la geometría.

### D4 · HOMEO-A1 perdía su mundo al componerse · REPARADO

`merge` funde `hidden` con `any()`. HOMEO-A1 es la única capacidad que declara `hidden=False`, y lo
declara a propósito: su endpoint es `modulation` = P(segura | energía baja) − P(segura | energía
alta), y si las dos puertas son idénticas a la vista el organismo no puede elegir la segura aunque
quiera. Medido:

```
HOMEO-A1               arriba [0.5, 0.1, 0.9]   abajo [0.5, 0.1, 0.1]   distinguibles: sí
HOMEO-A1 + EPMEM-A1    arriba [0.5, 0.1, 0.5]   abajo [0.5, 0.1, 0.5]   distinguibles: NO
```

Y había un test que lo **ratificaba**: `assert d.hidden is True   # HOMEO pide hidden=False pero
cualquiera que lo pida gana`. Escribí el comentario que explica la pérdida y la convertí en
comportamiento esperado.

**Reparación:** `PINNED` declara los ejes que una capacidad necesita clavados para que su endpoint
signifique algo, y `demand_for` **falla ruidosamente** al componer un conjunto incompatible en vez
de ceder en silencio. Componer LEARN con HOMEO exige decidir a mano qué endpoint se abandona, y esa
no es decisión del generador.

---

## 3 · Lo que sigue roto y no reparé

| Qué | Por qué no |
|---|---|
| **El motor tiene exactamente UNA variable esencial.** `AgentState` lleva sólo `energy`; `low_energy=14.0` es un cubo de puntuación, no un umbral fisiológico. | No se arregla en el generador: es un cambio de motor. Y tiene consecuencia dura — **con N=1 el experimento de Dulberg (HEA-005) no está sólo mal medido: está indefinido**, porque §3.3 fija una variable y mide «las restantes», y no hay restantes. |
| **No hay operador de perturbación.** Cero apariciones de perturbar/recuperar/viabilidad en los dos ficheros. | El protocolo de HEA-009 sigue sin ser aplicable. La única costura programable del motor es el intercambio de reglas (`scheduler.py:34`), que `inversion` ya usa: por ahí se puede construir, pero el endpoint es un tiempo-de-retorno sobre la traza de energía y `consumptions_from` descarta todo paso sin consumo. |
| **`Score.accuracy` sigue siendo la métrica primaria** de seis ejes. | Es el punto que S.5/2 sí prohíbe. Cambiarlo cambia los siete endpoints primarios PENDIENTE de los pasaportes, y eso es decisión de diseño, no reparación de defecto. |
| **TEMP-A1 cuesta 31.80 de 20.00 iniciales** en los dos brazos. | Ya no es asimétrico, que era el defecto. Que sea insuperable sin comer es el eje `viability_margin` que el corpus propone declarar, no un error. |
| **`DEMAND_OF` sigue sin una sola cita.** | Es tuyo: v2 ya trae `CLAIM_TO_CAPABILITY_TRACE_v2.csv` con la procedencia, y marca esas conexiones como `PROJECT_INFERENCE_NOT_AUTHOR_CLAIM`. Conectar las dos tablas es el trabajo siguiente. |

---

## 4 · Los ejes que el corpus sí sostiene

De la ronda adversarial, con locator. No los aplico: son sustitución de contenido científico, no
reparación de defecto.

| Eje | Exige | OFF | Fuente |
|---|---|---|---|
| `perturbation_magnitude` | detectar un desplazamiento de una variable esencial y compensarlo; el fallo es una integral de desviación, no una elección errónea | magnitud 0, misma geometría | HEA-007 §Adaptivity p.438; HEA-005 §3.3 p.3 |
| `recovery_window` | que la regulación sea **rápida**; lo medido es tiempo de adaptación | ventana = vida restante | HEA-014 S.11/2-11/4 pp.148-150 |
| `drive_count` | arbitrar entre ≥2 variables esenciales con set-points y decaimiento independientes | N=1, lo que hay hoy | HEA-005 §2.1 Tabla 1; HEA-014 S.11/2 p.148 |
| `decomposability` | si los éxitos parciales se conservan o no | iterado (se acumulan) | HEA-014 S.11/5-11/6, S.15/3 — T1 = 2^1000 s frente a T2 ≈ 8 min |
| `setpoint_drift` | revisar el objetivo **por anticipado**, sobre un cue indirecto, antes de la desviación | set-points fijos | HEA-011 §2 pp.4-5, Fig.3 |
| `problem_similarity` | que una adaptación anterior sobreviva a una posterior | problemas lejanos | HEA-014 S.16/12, S.16/14-15 pp.214-216 |
| `recurrence_dependence` | saber **cuál** repetición de una perturbación es ésta | una respuesta sirve para todas | HEA-014 S.10/4 p.139 |
| `observability` | **el único eje actual que sobrevive intacto** — es un eje de observabilidad, no de corrección | canal visible (`hidden=False`) | HEA-015 teorema del buen regulador |

**Advertencia que no me ahorro:** componer el segundo lazo por búsqueda aleatoria de Ashby con la
modularidad por gradiente de Dulberg y el modelo generativo de Friston es un **acto de diseño que
el corpus no hace por nosotros**. Y `drive_count` no se puede añadir editando el generador: exige
una segunda variable regulada en el motor. «Conservar la máquina, cambiar los ejes» no es una
reescritura del generador, es un cambio de motor, y conviene decirlo antes de empezar.

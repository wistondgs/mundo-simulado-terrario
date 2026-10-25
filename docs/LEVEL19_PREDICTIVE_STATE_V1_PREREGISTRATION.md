# L19 · estado predictivo adquirido y decisión — preregistro v1

`LEARNER-19-v1` es una línea experimental nueva. No modifica ni reabre
`LEARNER-18-v1 = INSUFICIENTE`: 1.8 queda como evidencia histórica de una
implementación que no incorporaba la observación a la transición estructural y
que no intervenía en la selección de acciones.

## Pregunta y claim diferencial

¿Un estado discreto adquirido de historias de `(observación, acción)` permite
predecir y escoger mejor bajo aliasing parcial que un predictor reactivo que ha
visto la misma experiencia?

El claim que puede resultar demostrado es estrecho: en el mundo de clave
sensoriomotora definido abajo, **el estado adquirido** media una mejora
reproducible de predicción y de decisión. No implica mapas, estados latentes
verdaderos, inteligencia general ni transferencia a otros mundos.

## Tarjeta de apertura

| Campo | Declaración |
|---|---|
| Pregunta | ¿El estado adquirido media predicción y selección bajo aliasing? |
| Trabajo previo | PSR/PSCM y estados causales ya cubren estados predictivos de historias `(O,A)` y control parcial; no se reclama novedad algorítmica. |
| Diferencia Terrario | Contrato opaco de eferencia, rutas auditables, lesión, persistencia y evaluación retenida en el runtime real del proyecto. |
| Falsificador primario | El reactivo o el control ciego a acción iguala a L19, o la lesión no reduce acierto. |
| Dependencias | Correctitud del mundo, aislamiento de semillas, serialización y ejecución en un entorno con `numpy`. |
| Resultado negativo | Diagnostica que esta diferenciación discreta no compra utilidad conductual bajo este contrato. |
| Definición de terminado | Manifiesto reproducible, campaña retenida, replay de checkpoints y uno de los tres dictámenes predefinidos. |
| Veredicto de apertura | `OPEN_AS_REPLICATION` |

## Lo suministrado y lo adquirido

Suministrado: observaciones binarias de cuatro bits, cuatro `EfferenceCopy`,
prior Dirichlet uniforme, actualización de conteos, comparación bayesiana de
evidencia marginal, tarea y función de utilidad de éxito. El mundo privado usa
una clave binaria y una señal cuyo significado depende de la acción-sonda.

Adquirido: qué firmas `(z, a, o')` ameritan una diferenciación; sus conteos
predictivos; rutas de transición; y la selección final que maximiza la
probabilidad predictiva de la observación de éxito. La clave privada, la acción
correcta y el resultado nunca se entregan al learner antes de actuar.

## Diseño

Una vida contiene episodios de tres transiciones: inicio → señal (sonda), señal
→ resultado (elección). La misma señal puede significar claves opuestas según la
acción-sonda previa; por ello ni la observación corriente ni la observación sin
copia eferente basta. El entrenamiento usa acciones uniformes y no selecciona
por retorno. La evaluación es pasiva: no actualiza conteos ni estructura.

Semillas de entrenamiento: `310001…310032`; semillas retenidas: `320001…320032`;
perturbación retenida: las mismas semillas con 10 % de ruido en la señal. Ninguna
semilla retenida puede entrar en selección estructural, ajuste o depuración.

## Métricas y aceptación

Unidad de inferencia: una semilla/vida. Por vida se registra:

1. `predictive_gain = loss_reactive - loss_full` en trayectorias aleatorias
   retenidas;
2. `decision_gain = success_full - success_lesioned` en los mismos episodios
   contrafactualmente emparejados;
3. éxito de `full`, `reactive`, `observation_only` y `lesioned`;
4. estados, splits, log-evidencia y huella del checkpoint.

El resultado sólo es **CAPACIDAD DEMOSTRADA** si, sobre las 32 vidas retenidas,
los límites inferiores normales pareados al 95 % de `predictive_gain` y de
`decision_gain` son estrictamente positivos, `full` supera individualmente a
`observation_only`, y cada checkpoint restaurado reproduce exactamente su
traza de decisión. Si no, el dictamen es `INCONCLUSO` o `MECANISMO REFUTADO`
según la dirección de los dos efectos; jamás se cambia este criterio después de
ver el resultado.

## Controles y falsificadores

* **Reactivo:** mismos datos y conteos, sin estado histórico; descarta que la
  mejora sea sólo más experiencia.
* **Ciego a acción:** idéntico mecanismo, pero las firmas sustituyen la acción
  por un símbolo constante; descarta que una señal visual por sí sola explique
  el efecto.
* **Lesión:** colapsa rutas y contenido estructural después de adquirirlos, sin
  tocar el resto de la vida; si no reduce la decisión, el estado no fue causa.
* **Ruido retenido:** cambia la fiabilidad de la señal sólo en evaluación;
  descarta que el resultado dependa de una secuencia exacta conocida.
* **Restauración:** serializar/restaurar debe conservar huella, predicciones y
  acciones; descarta que el resultado viva fuera del estado persistido.

El falsificador principal es que el control reactivo o el ciego a acción iguale
al learner completo, o que la lesión no reduzca la selección correcta. Los
estados adicionales, por sí solos, nunca cuentan como éxito.

## Dependencias y cierre

La teoría de PSR ya establece representaciones predictivas condicionadas por
acciones; el experimento es una réplica de integración en Terrario. La evidencia
necesaria es ejecución de la campaña sellada, manifiesto de procedencia,
resultados retenidos y replay. Se conserva todo resultado negativo.

# Plantilla · ficha de apertura de un experimento de la unidad mínima

Se copia a `APERTURA_<nombre_descriptivo>.md` y se rellena **antes de escribir código**. Sólo `OPEN` u `OPEN_AS_REPLICATION` autorizan código; `REVISE`, `DESCEND_OR_REFORMULATE`, `BLOCKED_PRIOR_ART_INCOMPLETE`, `BLOCKED_CIRCULAR` y `CLOSED_BY_THEORY` no.

**Orden obligatorio:** gate de antecedentes → esta ficha → **mutantes del punto 10** → enmienda prospectiva si un mutante refuta un criterio → corrida real. **La ficha no es final hasta que sus mutantes hayan corrido** (E-05). Toda enmienda se escribe debajo, con fecha, y dice si vino de un mutante o de un resultado; una enmienda nacida de un resultado observado **no** corrige la puerta: se declara FAIL y, si procede, se abre la reparación única.

---

# FICHA DE APERTURA · <nombre>

**Fecha:** · **Veredicto:** · **Gate previo:** `<veredicto>` en `PRIOR_ART_<nombre>.md`

0. **Guardas.** Entradas de `ERRORES_Y_GUARDAS.md` que aplican a este experimento y **cómo se cumple cada una** (campo del JSON, mutante, pregunta contestada). «Ninguna aplica» se justifica. Y: ¿qué sección vigente del mapa o qué experimento previo cubre ya parte de esto? (E-10)

1. **Pregunta.** Una sola, falsable. Y debajo: ¿qué estoy construyendo que la pregunta no pide? → va a «propuestas aparte», no al código (E-11).

2. **Constructo y medida.** Qué capacidad se afirma y con qué número se mide; nombre del campo del JSON para cada medida.

3. **Hipótesis.**

4. **Criterios**, declarados por separado cuando no son la misma pregunta.

5. **Predicciones escritas antes de correr**, por mundo y por brazo.

6. **Falsador.** El resultado concreto que diría que la hipótesis es falsa (no «que no pase la puerta»: un número).

7. **Banco y controles.** Población de mundos en orden canónico (nunca al azar). Por cada **control × mundo**: qué puede hacer ese control allí y **qué afirmación exacta controla ese mundo** (E-04, E-05). Debe haber un mundo donde el control acierta (prueba que el test discrimina) y uno donde la distinción no debe inventarse.

8. **Tres capas.** *Programado* · *disposición* (desempates, umbrales, políticas de lectura de la memoria) · *adquirido*. Y por cada brazo: **¿quién dispara cada paso del mecanismo y qué sabe el brazo que el organismo no sabría?** Si aparece el experimentador, el resultado se etiqueta SUMINISTRADO (E-02).

9. **Contadores de actividad** del componente distintivo de cada mecanismo; nombre del campo. Contador en 0 ⇒ NULO-POR-INACTIVIDAD (E-09).

10. **Mutantes del gate, antes de lo real.** Al menos: uno que **debe fallar** por no tener la capacidad (memorizador, ciego a la observación —E-06—, control mudo —E-04—, respaldo que restaura sin pagar), y uno que **debe pasar** (oráculo). Resultado de cada uno, escrito aquí.

11. **Puerta.** PASS / FAIL con **cada número acompañado de su unidad y del campo del JSON** con el que se compara (E-03); el veredicto lo calcula el programa. Curva, no punto; cobertura aparte de captura (E-08). Criterio de muerte como número, no como pendiente.

12. **Custodia.** Nombre del programa y del artefacto; sha256 del código; versión exacta del intérprete con el comando que la probó (E-01); sin `random`, dos corridas un hash; todo parámetro en el JSON (E-07). Reanudable si dura más de unos minutos.

---

## Enmiendas prospectivas
<fecha · origen (mutante / lectura) · qué criterio cambia y por qué · nunca tras un resultado observado>

## Resultado
<fecha · PASS/FAIL · si FAIL: la reparación única, declarada antes de correrla, con su propio falsador>

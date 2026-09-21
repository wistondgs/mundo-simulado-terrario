# Atlas 04 · Capacidades demostradas

**2026-09-21** · `b171098` · depositado en `CARTOGRAFIA_TERRARIO_01.md` **§XLIII**
· 6 citas locales verificadas; las de otros árboles van con su worktree delante.

Cada capacidad atada a código, experimento, instrumento, evidencia vigente,
lesión/control y estado epistemológico real.

---

## 1 · Hay dos contabilidades de capacidad y no se tocan

| | **Pasaportes** | **Niveles** |
|---|---|---|
| Qué describe | módulos de A4/A5 | organismos completos |
| Estado | **calculado** por `status_of` | **veredicto** de campaña sellada |
| Instrumento | registro canónico | gates propios por nivel |
| Cuántos | 10 | 8 |
| Con experimento propio | **0** | 8 |
| Certificables hoy | **1** | — |

Medido: **ningún nivel importa `capability_passport`, `instrument_registry` ni
`measurement_status`** — cero, en los ocho árboles. Y ningún pasaporte nombra un
nivel.

> Las capacidades **demostradas** viven en los niveles. Las contabilizadas para
> **certificación** viven en los pasaportes. No se encuentran en ningún punto.

## 2 · Lo que hay, capacidad por capacidad

| Capacidad | Código | Experimento | Control/lesión | Estado real |
|---|---|---|---|---|
| contingencia sensorimotora (1.0) | sí | sellado | reversión | **demostrada en su mundo** |
| orientación direccional (1.1) | sí | sellado | control negativo | **demostrada** |
| proximidad cualitativa (1.2) | sí | sellado | sí | demostrada · inventario divergente |
| memoria de un paso (1.3) | sí | sellado | tick omitido | demostrada · inventario divergente |
| ligadura conjuntiva (1.4) | sí | sellado | 12 fixtures | **demostrada y reconciliada** |
| composición B+Q+H+M | sí | sellado | factorial 2×2 | **interacción superaditiva** |
| memoria selectiva (1.5) | **no** | no | — | **CONGELADO · sólo diseño** |
| regularidad temporal (1.6) | sí | sellado | 3 brazos + K-SOMBRA | **POSITIVO** |
| contingencia de acción (1.7) | sí | sellado | 4 controles + gemelo A/B | **POSITIVO** |
| estado predictivo (1.8) | sí | abierto | escalera | **sin presupuesto seleccionable** |
| los 10 módulos de A4/A5 | sí | **ninguno** | declarada, no ejecutada | **1 certificable de 10** |

## 3 · El linaje B es un reinicio, no una continuación

`9b0d39b` lo dice en el asunto: «Seal the Level 1.6 oracle **on a tree where
nothing cognitive was inherited**». Verificado: `level16` importa de
`level1.world` sólo primitivas del **cuerpo y el mundo** —`Grid`, `Direction`,
`DELTA`, `Observation`— y **nada** de `level11`…`level14`.

Se hereda el cuerpo; no se hereda la cognición.

**1.6 · `POSITIVO`.** Adquiere `P(o_{t+1}|o_t)` y nada más: `observe` rechaza en
ejecución un acto, un bit de cambio, una copia eferente y una posición. La
frontera está en la firma, no en una promesa. El barajado se audita
distinguiendo dos contadores que es fácil confundir — 1 punto fijo de π
(esperanza 1) frente a 431 coincidencias de valor (esperanza 410, «el alfabeto
de 16, NO un defecto»).

**1.7 · `POSITIVO`**, 16/16 pares, 13/13 gates. Hereda el **mecanismo** de 1.6
instanciado y congelado, no una tabla forastera — `H(O'|O)` varía 0,5623–1,5464
entre mundos, así que una tabla de otro mundo sería un baseline sesgado. Y la
corrección que salvó el diseño: `NO-ACTION` **no es el predecesor congelado**,
porque contra un `M_0` congelado aparece una ventaja falsa que **crece con el
presupuesto**.

## 4 · 1.8 · un negativo bien llevado

`BUDGET SELECTION = NONE`. El confirmatorio sigue **cerrado e intacto** y la
cláusula de la Enmienda 04 §6 detiene la modificación de la estadística en vez
de seguir buscando un presupuesto que gane.

**La causa raíz está nombrada y la verifiqué en el fichero.** El oráculo selló
`Z_{t+1} = F(Z_t, A_t, O_{t+1})`; lo implementado es `Z_{t+1} = F(Z_t, A_t)`:

```
level18/predictive_state.py:168   self._came_from = (self._here, command)
level18/predictive_state.py:336   for following in range(16):
                                      self._routing[(sig[0], sig[1], following)] = born
```

Prueba hermética: mismas 400 acciones con tres secuencias de observación
distintas → **0/400 diferencias** en `Z`. Mismas observaciones, acciones
distintas → 297/400. Y cuánto se deja fuera, con `H(C)` = 2,98 nats: **dos pares
(obs, acción) con 258 contextos resuelven el 91 % de la situación; seis acciones
solas con 4 096 contextos resuelven el 48 %**.

Es un `FAMILY_MISMATCH`, no un `SCIENTIFIC_NEGATIVE`: el experimento no falsó la
hipótesis, midió otra cosa.

## 5 · 1.5 es la entrada más sana del inventario

```
ESTADO    CONGELADO · sólo diseño      CÓDIGO   ninguno
CAMPAÑA   no ejecutada
```

Tres supersesiones el mismo día y una condición explícita para volver:
«experiencia útil generada por el organismo > capacidad disponible para
conservarla». El motivo: a la memoria selectiva **le falta la necesidad** — hoy
la escasez la impone el experimentador, no la produce el organismo.

Una capacidad que no se descarta, no se finge, y dice qué haría falta.

## 6 · Una sección del mapa quedó contradicha por el código

§XXVII declara que `prediction_error` se escribe y **no lo lee nadie**. Es falso
desde `fd725e3`: `A5Cybernetic._policy_reward` lo lee y lo suma a la recompensa
— la superficie causal entera de CURIO-A1.

Y §XXVII **no cita ninguna ruta**, así que el gate no puede invalidarla: sigue
verde afirmando lo contrario de lo que hace el código.

Cerrando el K2 de §42.2: **12 de 44 secciones son invisibles para el gate**.
Cinco de ellas —§XVI, §XXIII, §XXVI, §XXVII, §XXVIII— afirman cosas sobre código
sin citar una línea, y cuatro son precisamente de capacidades. Al escribir este
volumen estuve a punto de crear la decimotercera: §XLIII no citaba ninguna ruta
local hasta que el gate lo dijo.

## 7 · Lo que no se sabe

1. **K1** · Si §XVI, §XXIII y §XXVI siguen siendo ciertas. Se comprueba
   leyéndolas contra el código, como se hizo con §XXVII.
2. **K2** · Qué diría un pasaporte de las capacidades del linaje B. 1.6 y 1.7
   están demostradas y **no tienen pasaporte**; los diez pasaportes describen
   módulos sin experimento. Unir las dos contabilidades es decisión de modelo.
3. **K2** · Si la ablación de cada `negative_prediction` produce lo que predice.
   Diez ablaciones declaradas y no ejecutadas.
4. **K3** · Para 1.8, qué familia de particiones sería la correcta. La evidencia
   dice cuál **no** es y cuánta información deja fuera; no dice cuál elegir.

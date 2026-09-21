# Agente Nivel 1.6 · cierre formal

**Fecha:** 2026-09-20 · **Estado:** cerrado · **Veredicto:** `POSITIVO`
**Oráculo:** `9b0d39b`, intacto · **Enmiendas:** `d0ce9f8`, `8f8c85d`, `5c54848`,
las tres anteriores a la campaña · **Auditoría:** `3bfc4cf`

---

## 1 · La pregunta

> ¿Puede el organismo adquirir, a partir de su propia vida sensorial, regularidades
> sobre cómo cambia su percepción en el tiempo?

No se preguntó qué cambio causó su acción. Eso es contingencia propia y no entra
aquí ni en una línea.

## 2 · Sustrato suministrado

```
cuerpo                  4 sensores · 4 motores · física del Nivel 1.0 sin modificar
S0                      fuente motora endógena, uniforme sobre {U,D,L,R}
                        PRNG propio del organismo, serializable con él
copia eferente          existe en el cuerpo · BLOQUEADA para el aprendiz
tabla asociativa        16 x 16, tamaño fijo, sin generalización
prior                   alpha_0 = 1.0
regla                   N(o_t, o_{t+1}) += 1
instrumentación         verdad de terreno, métricas, K-SOMBRA, los cuatro controles
```

**S0 no cuenta como inteligencia adquirida.** Es el sustrato que produce la vida.

## 3 · La adquisición

Una sola: `P(o_{t+1} | o_t)`.

Lo que el aprendiz recibe es el par `(o_t, o_{t+1})` y nada más. La frontera está
en la firma, no en una promesa: `observe` acepta dos tuplas de cuatro bits, y
rechaza en ejecución un acto, un bit de cambio, una copia eferente y una posición.

## 4 · El mundo

```
grid_size          7          heredado del 1.0 canónico (measurement.py:52)
wall_probability   0.25       heredado del 1.0 canónico (measurement.py:55)
vida               T = 4096 pasos · banco POST = 2048 transiciones nuevas
resets             ninguno dentro de una vida
flujos             mundo [s,0] · motor [s,1] · baraja [s,2]
```

El banco POST se genera **después del congelado**, en el mismo mundo, continuando
el mismo flujo motor. No se puntúa contra un banco poblacional: eso mediría
generalización entre mundos, que este nivel no declara.

## 5 · Controles

```
FROZEN             misma vida, la tabla se queda en el prior
TEMPORAL-SHUFFLED  o_t emparejado con o_{pi(t)+1} · mismos marginales, sin adyacencia
STATIC-BITCOUNT    q(o) = beta * k(o)/4 · un parámetro, sin tiempo
K-SOMBRA           instrumento, no brazo: P(o'|o) exacta desde la topología
```

Los tres brazos comparten la vida entera por construcción: el cuerpo no importa la
tabla, así que la trayectoria no puede depender de lo aprendido.

**Sobre el barajado.** Destruye por permutación de la pareja, no por igualdad de
valores. Dos contadores distintos, que confundirlos descalibra el criterio:

```
puntos fijos de pi          1     esperanza 1 · es «pares supervivientes»
coincidencias de valor    431     esperanza 410 · es el alfabeto de 16, NO un defecto
distancia a la marginal   FULL 0.557  ·  SHUFFLED 0.068
```

## 6 · Métricas

```
PRIMARIA     log-loss de la distribución completa P(o'|o), en nats
SECUNDARIA   BS_change, Brier sobre c = 1[o' != o]   ·   DIAGNÓSTICA, nunca evidencia
```

`STATIC-BITCOUNT` **no tiene** método `probability`: pedirle la métrica primaria
levanta `PrimaryMetricNotApplicable`. No se le fabrica una distribución para que
pueda competir donde no le corresponde.

## 7 · Resultados

```
16 vidas · semillas 140000011…140000026 · 0 descartes N-MUNDO · 16 sin consumir

ΔL vs FROZEN      +1.5947   sd 0.2639   mín +1.3533    16/16 positivas
ΔL vs SHUFFLED    +0.8308   sd 0.3067   mín +0.1290    16/16 positivas
IC95 inferior     +0.6805                              CRITERIO PRIMARIO CUMPLIDO

brecha con el óptimo analítico   media 0.0288 nats   máx 0.0450
fracción de lo disponible capturada   media 0.9813   mín 0.9701

gates 12/12 · contratos 84/84 verdes antes de lanzar
corrida reproducida bit a bit en la auditoría
```

**Secundaria:** `BS_change` FULL 0.2121 · BITCOUNT 0.2191 · **el control de un
parámetro gana en 3 de 16 vidas.** Si el endpoint primario fuese éste, el nivel no
habría demostrado nada temporal.

**Corroboración analítica** (no vuelve a correr al organismo): la ganancia sobre
SHUFFLED sigue la información mutua `I(o_t;o_{t+1})` del mundo con `r = 0.9935`,
sesgo −0.023 nats en la dirección esperada para un contador finito.

## 8 · Intervención causal

```
congelar → guardar M_T → sustituir por M_0 → reevaluar → restaurar M_T → reevaluar
```

Las tres evaluaciones sobre el **mismo banco POST inmutable**.

```
16/16 vidas: la pérdida sube a exactamente log 16 = 2.7726 al ablacionar
16/16 vidas: vuelve exactamente a su valor al restaurar
16/16 vidas: huella idéntica antes y después
```

La competencia **reside** en el estado aprendido; no está sólo correlacionada con él.

## 9 · Nulos y exclusiones

```
N-MUNDO              0    ninguna semilla descartada
N-EXPERIENCIA        0
N-PLASTICIDAD        0
NEGATIVO VERDADERO   0
POSITIVO            16
INVÁLIDO             no aplicable: los doce gates pasaron
```

**Que sólo se haya dado una categoría no significa que las demás no existan.** El
clasificador está probado sobre entradas sintéticas que alcanzan las seis, en el
orden escrito; las cinco restantes simplemente no ocurrieron en esta campaña.

Las 16 semillas no consumidas quedan **sin usar**. No se recurre a ellas.

## 10 · Desviaciones y enmiendas

Tres huecos del oráculo, los tres cerrados **antes** de la campaña y por enmienda
fechada y separada; el documento original no se editó:

| enmienda | hueco | qué fijó |
|---|---|---|
| `d0ce9f8` | §12/§16 invocaban una «regla preregistrada» de reemplazo que no existía | consumo ascendente, veredicto anterior a la vida, sólo `N-MUNDO` reemplaza |
| `8f8c85d` | §4 decía «paredes» sin densidad; §6 un prior sin valor | `size=7`, `wall_probability=0.25` heredados del 1.0; `α₀=1` verificable por `log 16` |
| `5c54848` | §15 nombraba seis categorías sin criterio | las tres magnitudes y el orden de las cinco reglas |

**Diez anomalías** están levantadas y **sin corregir** en `docs/LEVEL16_AUDITORIA_INTEGRIDAD.md`.
La única que exige trabajo antes de una campaña futura es `AN-1`:
`SHUFFLE_NOT_DESTRUCTIVE` se calcula y se guarda por vida, y ningún gate lo lee —
se cumple en 16/16, de modo que el resultado no está en cuestión, pero una baraja
defectuosa pasaría los doce gates.

## 11 · Qué demuestra

> El Agente Nivel 1.6 produjo endógenamente su trayectoria motora y, a partir del
> flujo de observaciones consecutivas generado durante esa vida, adquirió una
> representación predictiva de la estructura temporal de su propio flujo sensorial.
> La competencia supera controles congelados y con temporalidad destruida, se
> aproxima al óptimo disponible y depende causalmente del estado interno aprendido.

Se intentó recortarla. **Ninguna cláusula falla contra el código:**

| cláusula | evidencia |
|---|---|
| produjo endógenamente su trayectoria | único emisor `motor.py`; 6144 emitidos de 6144 pasos |
| a partir de observaciones consecutivas | `observe` sólo admite dos observaciones; aduana verificada |
| adquirió representación predictiva | ΔL vs FROZEN +1.5947 sobre transiciones no vistas |
| supera control congelado | 16/16 |
| supera temporalidad destruida | 16/16 · IC95 inferior +0.6805 |
| se aproxima al óptimo disponible | 0.0288 nats del cálculo exacto · 98.13 % capturado |
| depende causalmente del estado | 16/16 ablación y restauración |

## 12 · Qué NO demuestra

**No** se afirma, y el código no lo sostendría:

```
detección de cambio          el control de un parámetro gana en 3/16 vidas
                             y el 12 % de los movimientos no cambia la observación
contingencia acción→efecto   A1 nunca recibió identidad de acción
causalidad                   no hay intervención sobre el mundo, sólo sobre el estado
exploración inteligente      la política es uniforme y no cambió un bit
curiosidad · motivación      no hay señal que pudiera producirlas
valor · recompensa           ninguna en el paquete, verificado por AST
búsqueda · objetivo          no hay nada que buscar ni preferencia alguna
agencia fuerte               el ser no elige; produce variación y la sufre
memoria selectiva            la tabla cuenta todo por igual, no retiene ni olvida
descubrimiento autónomo      no hay criterio interno de interés
generalización entre mundos  contra banco poblacional queda en 2.7241 frente a
                             2.7726 de FROZEN: casi no sabe nada fuera de su mundo
```

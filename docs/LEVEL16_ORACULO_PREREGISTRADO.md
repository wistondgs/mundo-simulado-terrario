# `LEVEL1.6-DEVELOPMENTAL-SENSORY-CHANGE-01` · oráculo preregistrado

**Sellado antes de existir el código.** Todo valor sale de medición sobre el mundo
real o de aritmética; ninguno de una corrida del organismo.

Base `d278f59`, el cierre del Nivel 1.0. En este árbol **no existen** `level11`,
`level12`, `level13`, `level14` ni los paquetes de fusión: la ausencia de
capacidad cognitiva heredada es **estructural**, no una declaración.

---

## 0 · Genealogía y alcance

```
S0 variación motora endógena  ──►  1.6/A1 estructura temporal sensorial adquirida
```

`S0` es **sustrato suministrado**, no adquisición. La única adquisición de 1.6 es
`A1`. No hereda `B`, `Q`, `H`, `M`, `ψ`. No depende del 1.5, que queda congelado.

## 1 · La pregunta

> ¿Puede adquirir, a partir de su propia vida sensorial, regularidades sobre cómo
> cambia su percepción en el tiempo?

**No se pregunta** qué cambio causó su acción. Eso es contingencia propia y
pertenece al peldaño siguiente; **ni una línea de ella entra aquí**.

## 2 · Por qué no se llama «detección de cambio»

Entregar `Δ_t = o_{t+1} − o_t` o `c_t = 1[o_{t+1} ≠ o_t]` como entrada sería
programar la mitad de `A1`. El organismo recibe **sólo observaciones
consecutivas**; el evaluador sí conoce `c_t` como verdad de terreno.

```
o_t, o_{t+1}, o_{t+2}, …   ──►   modelo interno de transiciones sensoriales
```

Y hay una razón medida para no llamarlo detector de cambio: `q̂(o)` correlaciona
`r = 0.9748` con el número de direcciones libres de `o`. Ver §7.

## 3 · S0 · sustrato

```
π_S0(a) = 1/4  uniforme sobre {U,D,L,R}
llamada:  agent.motor_source.next()
NUNCA:    experiment.next_action() · teacher.choose_action() · curriculum.action()
```

El RNG **pertenece al organismo** y su estado forma parte de su serialización:
misma serialización ⇒ misma vida futura, incluidas las acciones estocásticas.

**Copia eferente** `e_t = a_t` se mantiene en el cuerpo pero **`A1` no puede
leerla**. Sin esa frontera, `A1` derivaría hacia `P(o_{t+1} | o_t, a_t)`, que ya
es contingencia propia. En 1.6 sólo se permite `P(o_{t+1} | o_t)`.

## 4 · Mundo · una vida, un mundo, sin resets pedagógicos

Física sensorimotora elemental del Nivel 1.0: rejilla de 7, cuatro movimientos,
paredes, cuatro bits, determinista. Sin reward, comida, energía ni objetivo.

**Una vida ocurre dentro de un mundo persistente.** Los resets existen sólo entre
vidas independientes, jamás para facilitar experiencia dentro de una.

**Medido sobre 1 638 400 pasos con política uniforme:**

```
tasa de movimiento                     0.5818
tasa de CAMBIO sensorial  o' ≠ o       0.5129     el mundo NO es estático
se movió sin que cambiara la obs.      0.1184 de los movimientos
observaciones distintas alcanzadas     16 de 16
transiciones distintas alcanzadas      182 de 256
I(o ; o')                              0.8957 nats = 1.2922 bits
P(cambio | o) recorre                  0.000 … 0.743
```

El `11.8 %` importa para la redacción: **`c = 1[o'≠o]` no es «se movió»** — dos
celdas contiguas pueden compartir firma de cuatro bits. El claim dice *flujo
sensorial*, nunca *movimiento*.

## 5 · Qué recibe `A1`, y qué no

```
RECIBE      el par temporal (o_t, o_{t+1})
NO RECIBE   a_t · copia eferente · posición p_t · c_t · Δ
            reward · novelty · progreso · valor · target · labels
```

## 6 · Mecanismo suministrado

```
N(o, o')   tabla asociativa temporal, 16 × 16 = 256 celdas
prior      N₀(o,o') = α₀ simétrico
regla      N(o_t, o_{t+1}) ← N(o_t, o_{t+1}) + 1
lectura    P̂(o'|o) = N(o,o') / Σ_v N(o,v)
```

Suministramos **capacidad de asociación temporal**. El contenido concreto aparece
por experiencia. **No hay generalización en 1.6**: eso es deliberado.

## 7 · El control que la auditoría hizo obligatorio

`q̂(o) = 1 − P̂(o|o)` correlaciona `r = 0.9748` con el número de direcciones
libres, y una regla estática de **un solo parámetro** que lee la observación
actual queda a `0.0039` de la tabla aprendida:

```
tabla aprendida de 16 celdas        BS_change = 0.222368
regla estática  q = 0.8363 · k/4    BS_change = 0.226245
constante global                    BS_change = 0.249899
```

Por tanto:

```
STATIC-BITCOUNT entra como cuarto brazo
BS_change queda SECUNDARIO / diagnóstico, nunca evidencia fuerte
el endpoint primario es el log-loss de P(o'|o) completa
```

`STATIC-BITCOUNT` **no puede explicar el primario**: no modela las 16
observaciones siguientes, sólo cambio/no-cambio.

## 8 · Banco POST · congelar, continuar, evaluar

No se evalúa sobre transiciones que el modelo ya usó para actualizarse, **ni**
sobre un banco poblacional — eso mediría generalización entre mundos, que §6
declara fuera de alcance.

```
vida de adquisición (T pasos)
        │
        ▼  FREEZE · se fotografía mundo + posición + estado del RNG de S0
        │
        ▼  continuación única en el MISMO mundo · N_POST pasos
        │
        ▼  banco POST no visto, IDÉNTICO para FULL, FROZEN, SHUFFLED y BITCOUNT
```

**Por qué no el banco poblacional, medido:** con él, `ΔL` va en el sentido
contrario y a `T = 16 384` el organismo queda **peor que FROZEN**.

```
T           banco de su mundo     banco poblacional
   256           1.7269               2.4628
 1 024           1.3830               2.5082
 4 096           1.2654               2.7556
16 384           1.2379               3.0815      ← peor que FROZEN (2.7726)
```

Se conserva como diagnóstico exploratorio; **nunca como gate**.

## 9 · Presupuesto y vidas

```
T        = 4 096 pasos     primer presupuesto con la curva ya saturada
                           (de 4k a 16k sólo gana 0.027 nats)
N_POST   = 2 048 transiciones
VIDAS    = 16 válidas
```

`T = 4 096` es **el presupuesto más bajo ya saturado**, no un mínimo demostrado.

## 10 · Brazos

```
FULL-1.6          S0 produce la vida · A1 actualiza N
FROZEN            misma trayectoria · N = N₀ toda la vida
TEMPORAL-SHUFFLED mismos marginales · adyacencia destruida
STATIC-BITCOUNT   q(o) = β·k/4 · sólo compite en la métrica secundaria
K-SOMBRA          aprendiz científico separado · nunca realimenta al agente
```

**Paridad de experiencia:** mismo mundo, mismo estado inicial, mismo estado
inicial del RNG motor ⇒ `a_{0:T}` y `o_{0:T}` idénticos entre brazos, verificado
por hash de trayectoria. Cualquier diferencia procede del aprendizaje.

## 11 · Valores sellados

```
ΔL  FULL vs FROZEN        media +1.5082   sd 0.1451   mín +1.2787
ΔL  FULL vs SHUFFLED      media +0.9889   sd 0.2103   mín +0.1204
                          60 de 60 vidas positivas

con 16 vidas · IC95 inferior de ΔL vs SHUFFLED ≈ +0.8858
```

**Criterio primario:** `IC95_inferior(ΔL vs SHUFFLED) > 0`.

**El barajado es destructivo, medido:**

```
distancia de P̂(·|o) a la marginal    FULL 0.5653  ·  SHUFFLED 0.0282
pares supervivientes por azar        0 de 16 384
```

## 12 · N-MUNDO · criterio estructural, antes del nacimiento

No se excluyen componentes pequeños: eso sería **selección de mundos favorables**.
Se excluye sólo lo estructuralmente degenerado.

```
N-MUNDO  ⟺  |O_alcanzables| < 2   ó   no existe transición alcanzable con o' ≠ o
```

**Medido sobre 5 000 mundos: `1.92 %`.** Estratos de las válidas:

```
≤3 celdas  2.3 %   ·   4–6 celdas  2.8 %   ·   >6 celdas  94.9 %
```

Se reporta siempre: tamaño del componente natal, observaciones alcanzables,
transiciones posibles y estrato. Las semillas `N-MUNDO` se reemplazan por regla
preregistrada **y se contabilizan y publican igualmente**. Un componente pequeño
no degenerado que produzca poca experiencia será `N-EXPERIENCIA`, no se borra.

## 13 · Gates

| gate | certifica |
|---|---|
| **L16-0** | linaje aislado · `level11…14` no existen en este árbol |
| **L16-1** | procedencia interna de todas las acciones |
| **L16-2** | RNG motor serializable y reproducible |
| **L16-3** | ausencia de target / reward / novelty / value |
| **L16-4** | `A1` no recibe acción, copia eferente, posición ni `Δ` |
| **L16-5** | paridad exacta de trayectoria entre brazos, por hash |
| **L16-6** | `K-SOMBRA` demuestra suficiencia de experiencia |
| **L16-7** | `FULL` mejora sobre `PRE` y `FROZEN` en el banco POST |
| **L16-8** | `FULL` supera a `TEMPORAL-SHUFFLED` |
| **L16-9** | el estado aprendido **causa** la competencia |
| **L16-10** | evaluación completamente pasiva |
| **L16-11** | `STATIC-BITCOUNT` no explica el endpoint primario |

**Fixtures negativas, una por gate:** importar una capacidad de 1.4 · cinta
externa de acciones · omitir el RNG al serializar · campo reward ficticio ·
entregar `a_t` o `changed` al modelo · cambiar una acción de un brazo · mundo
estático · congelar `FULL` · conservar parejas reales en el barajado · borrar
`M_T` sin caída de competencia · contador incrementado por el evaluador.

## 14 · Prueba causal del estado aprendido

```
1. congelar · 2. guardar M_T · 3. sustituir por M₀ · 4. reevaluar
5. restaurar M_T · 6. reevaluar
```

`competencia(M_T) > competencia(M₀)`, y la restauración debe recuperarla.

## 15 · Taxonomía del resultado · no PASS/FAIL

```
INVÁLIDO            cableado, fugas, pasividad o provenance rotos
N-MUNDO             no había estructura suficiente que aprender
N-EXPERIENCIA       el mundo podía enseñar, la trayectoria S0 no bastó
                    ← un nulo en A1 puede ser evidencia negativa sobre S0
N-PLASTICIDAD       experiencia suficiente, mecanismo sin cambio
NEGATIVO VERDADERO  K-SOMBRA aprende, A1 se activa y actualiza, y aun así no adquiere
POSITIVO            adquiere estructura temporal y pasa las intervenciones causales
```

## 16 · Semillas

```
140000011 … 140000042     32 reservadas · 16 vidas válidas + margen de N-MUNDO
```

Verificado disjunto de todo lo consumido y reservado en el linaje.

## 17 · Condiciones de parada

```
ADVANCED_CAPABILITY_DEPENDENCY   EXTERNAL_ACTION_LEAK
MOTOR_RNG_NOT_SERIALIZED         TRAJECTORY_NOT_REPRODUCIBLE
TARGET_SIGNAL_PRESENT            REWARD_SIGNAL_PRESENT
NOVELTY_SIGNAL_PRESENT           VALUE_SIGNAL_PRESENT
ACTION_VISIBLE_TO_A1             EFFERENCE_VISIBLE_TO_A1
CHANGE_LABEL_VISIBLE_TO_A1       HIDDEN_WORLD_STATE_VISIBLE
TRACE_PARITY_FAILED              WORLD_TOO_STATIC
EXPERIENCE_INSUFFICIENT          SHUFFLE_NOT_DESTRUCTIVE
FROZEN_MODEL_CHANGED             LEARNED_STATE_NOT_CAUSAL
MEASUREMENT_NOT_PASSIVE          BITCOUNT_EXPLAINS_PRIMARY
```

## 18 · Afirmación máxima autorizada

> El Agente Nivel 1.6 produjo endógenamente su propia trayectoria motora y, a
> partir de las observaciones consecutivas generadas durante esa vida, adquirió un
> modelo temporal de su flujo sensorial que predice mejor sus transformaciones
> futuras, dentro de su propio mundo, que su estado inicial, que un organismo
> congelado y que un control con la temporalidad destruida. El aprendizaje reside
> causalmente en su estado interno y no recibió identidad de acción, recompensa,
> valor, novedad ni etiqueta de cambio.

Y nada más. **No** se afirma detección de cambio, contingencia propia,
causalidad, exploración, curiosidad, motivación, valor, búsqueda, objetivo ni
agencia fuerte.

## 19 · El libro de suministro

```
SUMINISTRADO   cuerpo (4 sensores, 4 motores) · S0 con su PRNG · copia eferente
               bloqueada · tabla asociativa temporal · prior · regla de
               actualización · física local · continuidad temporal ·
               instrumentación, verdad de terreno, métricas, K-SOMBRA, controles

ADQUIRIDO      P(o_{t+1} | o_t)
```

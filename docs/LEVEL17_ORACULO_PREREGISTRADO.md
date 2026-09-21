# `LEVEL1.7-ACTION-CONTINGENCY-01` · oráculo preregistrado

```
┌───────────────────────────────────────────────────────────┐
│  PREDECESOR = SATURADO        ADQUISICIÓN 1.7 = PENDIENTE │
└───────────────────────────────────────────────────────────┘
```

**Fecha de sellado:** 2026-09-20 · **Campaña confirmatoria: NO CORRIDA**
Ventana ciega `160000011…160000074` **sin mirar**.

---

## 0 · Una honestidad sobre el estado de este sello

**Este oráculo no cumple el estándar de 1.6, y decirlo importa.** Allí el
documento precedió a la primera línea de código. Aquí la fase de diseño
cuantitativo —autorizada y ejecutada sobre semillas de calibración— ya produjo
código que funciona:

```
YA EXISTE, y queda congelado por este sello
   contingency.py  efference.py  wiring.py  life.py
   shadow.py  exposure.py  shuffled.py  twin.py
   23 contratos de arquitectura

NO EXISTE todavía
   los 13 gates · sus fixtures negativas · el runner de campaña
   nada que haya tocado 160000011
```

Lo que este documento sella antes de existir es: **los gates, las fixtures, el
endpoint, los presupuestos, la regla de semillas y el criterio de decisión.**
Los valores de calibración que aparecen abajo son **expectativas medidas, no
umbrales**, y ninguno entra en un criterio.

## 1 · La pregunta

> ¿Aporta el comando propio conocimiento adicional sobre lo que ocurrirá, por
> encima de todo lo que el ser ya sabía por temporalidad sola?

Y esta vez el comparador no puede contestar «sí» sólo porque recibió más
experiencia.

## 2 · Genealogía

```
1.6/A1  estructura temporal sensorial   →   1.7/C_17  desviaciones por acción
        DEMOSTRADA · exposición saturada        ÚNICA adquisición de este decimal
```

Se hereda **el mecanismo**, no una tabla de otro mundo: `H(O'|O)` varía entre
0.5623 y 1.5464 según el mundo, luego una tabla forastera no es un baseline
neutro sino uno arbitrariamente sesgado.

## 3 · Las dos fases de una vida

```
mundo W
   │
   ├── fase P · T_P = 4096 · el mecanismo de 1.6 adquiere M_0^W · FREEZE
   │
   ├── fase A · T_17 = 1024 · se abre E_t = A_t^command · adquiere C_17
   │            NO-ACTION ve las MISMAS transiciones sin el comando
   │
   └── banco POST · 2048 transiciones nuevas · el mismo para todos los brazos
```

```
T_P  = 4096    RÉGIMEN PREDECESOR = SATURADO
               L(M_0^W) = 1.2694 en calibración. Aquí la saturación es deseable:
               no volvemos a estudiar A1, queremos que esté sólidamente presente.
               NO se interpreta como mérito de 1.7.

T_17 = 1024    RÉGIMEN 1.7 = PENDIENTE
               D_K^action/D_W ≈ 0.617 · lejos de converger
               C_OA ≈ 0.999 · N mín ≈ 7.6 · la exposición ya no es el límite
               4096 todavía mejora sustancialmente
```

Regla developmental: **saturación para el predecesor, pendiente para la
adquisición nueva.** La campaña observa adquisición *mientras ocurre*, que es lo
que 1.6 no tuvo.

## 4 · Los invariantes de incrementalidad

```
C_0(o,a,o') = N_16(o,o') / 4                    prior simétrico entre comandos

nacimiento   C_17 = 0      ⇒  M_1(o,a) = M_0^W(o)  para toda a
lesión       C_17 → 0      ⇒  vuelve EXACTAMENTE a M_0^W, no a uniforme
```

Ambos verificados **bit a bit** en calibración, diferencia `0.000e+00`. Lesionar
1.7 no destruye al ser: lo devuelve al nivel anterior.

**Definición exacta de la lesión:** poner `C_17 ← 0` **sin tocar** `_inherited`.
Una lesión que también altere `M_0^W` es un defecto y `L17-11` debe rechazarla.

## 5 · `NO-ACTION` · definición exacta

```
parte de     M_0^W  (carga sus conteos, no un prior nuevo)
recibe       TODAS las transiciones de la fase A, las mismas que M_1
no recibe    el comando
se congela   al terminar la fase A
```

**No es `M_0^W` y no es un brazo duplicado.** Contra `M_0^W` congelado, el mundo
gemelo revela una ventaja falsa que crece con el presupuesto —`+0.105` a
`T_17 = 4096`— porque `M_1` recibe datos que `M_0^W` no vio. Contra `NO-ACTION`
esa ventaja desaparece (`−0.007`). El hallazgo está en
`docs/LEVEL17_HALLAZGO_01_BASELINE.md`.

## 6 · El par de mundos

```
A     física del Nivel 1.0 · contrato:  D_W^A > 0
B     T_B(s'|s,a) = ¼ Σ_b T_A(s'|s,b)  · contrato:  D_W^B = 0 EXACTAMENTE
```

Verificado al nivel del kernel de **estados**: A y B comparten topología,
dinámica marginal, estacionaria e `I(O;O')` **exacta** (diferencia `0.00e+00`), y
difieren sólo en `I(A;O'|O)`.

**El azar de B es propio y serializable.** Nunca se comparte con S0: si el efecto
del mundo saliera del mismo azar que el comando, podría aparecer dependencia
comando–efecto justo en el mundo cuyo contrato es `D_W = 0`.

```
mundo/topología        [s, 0]
S0 (motor)             [s, 1]
baraja de 1.6          [s, 2]
nulas de 1.6           [s, 3+k]
cableado φ             [s, 64]
efecto de B            [s, 65]        propio · serializable · jamás compartido
SHUFFLED-ACTION        [s, 128+k]
```

## 7 · Endpoint primario

```
D_C   =  L_POST(NO-ACTION)  −  L_POST(M_1)

Γ_i   =  D_C^A_i  −  D_C^B_i
```

**La unidad estadística es el par de mundos A/B de una misma semilla y topología**,
nunca la transición.

- `A` mide cuánto compra conocer el comando cuando de verdad importa.
- `B` mide la ventaja o coste que aparece sólo por tener un modelo condicionado
  con cuatro veces más parámetros.
- `Γ` resta ese coste. Asintóticamente `Γ → I(A;O'|O)` de A.

### Criterio confirmatorio

```
GATE PRIMARIO      CI95_inferior( media de Γ sobre 16 pares )  >  0
                   intervalo pareado por mundo
```

Condiciones necesarias, no sustitutas:

```
D_C^A > 0 en agregado
Mundo B sin ventaja positiva específica de acción
```

### El nulo de B, sin tolerancia inventada

**No** se impone un margen del tipo `|D_C^B| < 0.02`. Bajo el nulo las etiquetas
de acción son intercambiables condicionadas a `O`, así que `D_C^B` se compara
contra **su propia distribución de permutaciones estratificadas por `O_t`**:

```
32 permutaciones estratificadas de la vida de B  →  distribución nula de D_C^B
observado por encima de esa nula                 →  WORLD_B_OR_MODEL_NULL_FAIL
```

## 8 · `D_K^action` · corroboración interna, no segundo endpoint

```
ε_NA = E_p_ref KL[ P_W(·|o,a) ‖ M_NA(·|o) ]
ε_A  = E_p_ref KL[ P_W(·|o,a) ‖ M_1(·|o,a) ]

D_K^action = ε_NA − ε_A
```

Contraparte interna exacta de `D_C`. En A debe ser positivo en agregado; en B
debe comportarse como nulo. **Su función es demostrar que la ventaja externa tiene
correspondencia con conocimiento localizado dentro del estado aprendido** — no
contar la misma evidencia dos veces.

## 9 · Exposición · cuatro instrumentos, medidos antes de interpretar un fracaso

```
D_W        I(A;O'|O) del mundo · propiedad de la topología, no de la vida
E_rate     nats estructurales por transición vivida
E_total    Σ_t d(O_t, A_t)
C_OA       Σ p_ref(o,a) · 1[N_L(o,a) > 0]   sobre contextos informativos
N(o,a)     recuentos por contexto · mínimo, p10, mediana, p90
```

`E_rate ≈ D_W` **no** significa que la exposición esté resuelta: es una tasa, y se
mantiene plana mientras `C_OA` vale 0.638 y el contexto informativo mínimo tiene
cero visitas. *Encuentra información* ≠ *ha acumulado muestras suficientes*.

## 10 · `SHUFFLED-ACTION`

```
(O_t, A_t, O_{t+1})  →  (O_t, A_{π_o(t)}, O_{t+1})     π dentro de cada estrato de O_t
```

Conserva exactamente la secuencia de `O_t`, la de `O_{t+1}`, el número de acciones
por observación y el tamaño de muestra. Destruye **sólo** `A ↔ O' | O`.

```
nula        32 permutaciones estratificadas independientes
tolerancia  null_mean + 4·sd          derivada, nunca un umbral fijo
```

`32` está medido, no elegido: con 8 réplicas la `sd` carga 26.7 % de error
relativo y una vida de dieciséis falla por 0.0002; con 16, 32 y 64 la tolerancia
converge a ~0.0400 y pasan 16/16.

## 11 · Los trece gates

Trece, porque hay trece afirmaciones causalmente distintas. **No se baja a doce
artificialmente.**

| gate | certifica |
|---|---|
| **L17-0** `LINEAGE` | 1.6 presente y congelado; capacidades posteriores ausentes del disco |
| **L17-1** `WORLD-PAIR` | A y B comparten topología y dinámica marginal · `D_W^A > 0` · `D_W^B = 0` |
| **L17-2** `ACTION-PROVENANCE` | el comando lo genera exclusivamente S0 y es auditable; el azar de B es propio y serializable |
| **L17-3** `EFFERENCE-PURITY` | la copia lleva un comando opaco anterior a la consecuencia, y nada más |
| **L17-4** `INCREMENTAL-INVARIANT` | `C_17 = 0 ⇒ M_1 = M_0^W`; la lesión vuelve bit a bit a 1.6 |
| **L17-5** `BASELINE-PARITY` | NO-ACTION y `M_1` parten del mismo `M_0^W`, ven las mismas muestras, y difieren sólo en el acceso al comando |
| **L17-6** `EXPOSURE` | `D_W`, `E_rate`, `E_total`, `C_OA`, `N(o,a)` están medidos antes de interpretar cualquier fracaso |
| **L17-7** `ACTION-ACQUISITION` | `Γ` cumple el criterio primario |
| **L17-8** `NULL-WORLD` | B no inventa ventaja de acción, contra su propia nula de permutaciones |
| **L17-9** `ACTION-NECESSITY` | SHUFFLED-ACTION y FALSE-ACTION eliminan la ventaja específica |
| **L17-10** `OPAQUE-MAPPING` | el contenido no depende de semántica codificada de UP/DOWN/LEFT/RIGHT |
| **L17-11** `INTERNAL-LOCALIZATION` | lesionar `C_17` elimina sólo 1.7, y restaurarlo recupera exactamente |
| **L17-12** `PASSIVITY-REPLAY` | evaluar no modifica al ser; la vida y su replay son deterministas |

### Las cinco fixtures que deciden si los gates existen

```
L17-1    un B DEFECTUOSO donde una sola acción conserva su efecto.
         Realizable y detectable, verificado: I_B = 0.0000 (correcto) ·
         0.1617 (A0 intacta) · 0.3707 (A0+A2) · 0.8724 (A completo)

L17-3    contaminar la eferencia con `moved` o con la acción físicamente
         realizada. Debe rechazarse AUNQUE mejore espectacularmente.

L17-5    congelar NO-ACTION en M_0^W en vez de dejarlo seguir aprendiendo.
         Debe fallar paridad — esta fixture preserva el hallazgo más
         importante de la calibración.

L17-9    baraja identidad. Con la nula de 32 réplicas debe fallar
         específicamente SHUFFLE_NOT_DESTRUCTIVE.

L17-11   lesionar C_17 tocando además M_0^W. Debe fallar: la lesión correcta
         devuelve a 1.6, no a la ignorancia.
```

Una fixture que sólo falle por un `AttributeError`, por una aserción tautológica,
o por un mock que rompe también el control, **no cuenta**.

## 12 · Consumo de semillas

```
ventana ciega       160000011 … 160000074      64 reservadas
necesarias          16 pares A/B válidos
recorrido           ascendente, sin saltos, parar en el decimosexto
```

**Sólo una condición física anterior a la vida provoca reemplazo.** Jamás se
reemplaza una vida porque `Γ` sea bajo, porque B salga incómodo, porque SHUFFLED
falle, porque `D_K` sea bajo, porque la exposición sea mala o porque el resultado
sea negativo. **Esas vidas pertenecen al denominador.**

Si un mundo físicamente válido viola el contrato matemático `D_W^A > 0` o
`D_W^B = 0`, **eso no provoca reemplazo**: anula la campaña como
`WORLD_PAIR_CONSTRUCTION_FAIL`, porque sería un defecto nuestro y no del mundo.

## 13 · Condiciones de parada

```
ADVANCED_CAPABILITY_DEPENDENCY     PREDECESSOR_NOT_FROZEN
EXTERNAL_ACTION_LEAK               MOTOR_RNG_NOT_SERIALIZED
WORLD_B_RNG_SHARED_WITH_S0         WORLD_B_RNG_NOT_SERIALIZED
EFFERENCE_CARRIES_CONSEQUENCE      EFFERENCE_NOT_OPAQUE
INCREMENTAL_INVARIANT_BROKEN       LESION_TOUCHES_INHERITED
BASELINE_PARITY_FAILED             EXPOSURE_NOT_MEASURED
SHUFFLE_NOT_DESTRUCTIVE            WORLD_PAIR_CONSTRUCTION_FAIL
WORLD_B_OR_MODEL_NULL_FAIL         TOKEN_SEMANTICS_LEAK
MEASUREMENT_NOT_PASSIVE            TRAJECTORY_NOT_REPRODUCIBLE
```

## 14 · Expectativas de calibración · NO son umbrales

Medidas sobre `150000011…150000026`, `T_P = 1024`. Aparecen para que una
desviación grande se note, **no** para decidir nada.

```
D_W                 0.8817        propiedad del mundo
D_K^action a 1024   +0.5441       ratio 0.617
D_C^A a 1024        +0.5436
D_C^B a 1024        −0.0109
Γ a 1024            +0.5545  sd 0.0697  ·  16/16 positivas
24 permutaciones    sd entre cableados 0.0134 nats · 24/24 positivas
```

## 15 · Afirmación máxima autorizada, si pasa

> El Agente Nivel 1.7 adquirió, a partir de su experiencia y mediante una copia
> eferente opaca de su comando motor, una representación de las consecuencias
> sensoriales condicionadas por su propia acción que aporta información predictiva
> adicional sobre la estructura temporal ya adquirida en Nivel 1.6. La ventaja
> desaparece cuando la correspondencia acción–consecuencia se destruye o el canal
> de acción se falsifica. La asignación aleatoria de las acciones permite
> establecer experimentalmente que la dependencia aprendida corresponde a un
> efecto instrumental del mundo, **sin atribuir al organismo razonamiento causal**.

Acompañada **siempre** de las dos etiquetas de régimen.

**No se afirma:** que el organismo descubriera que la acción importa —la
factorización `(O,A) → O'` es **suministrada**—, ni razonamiento causal, ni
distinción de correlación espuria, ni exploración, curiosidad, valor, objetivo o
agencia fuerte.

## 16 · El libro de suministro

```
SUMINISTRADO   cuerpo · S0 con su PRNG · el cableado φ · la copia eferente opaca
               la factorización (O,A) → O' como hipótesis estructural
               el prior C_0 = N_16/4 · la regla de actualización
               el par de mundos A/B · toda la instrumentación

HEREDADO       el MECANISMO de 1.6, instanciado en W como M_0^W y congelado

ADQUIRIDO      C_17(O, A, O')
               las desviaciones específicas por acción respecto de la
               expectativa temporal previa

NO ADQUIRIDO   la relevancia causal o general del concepto «acción»
```

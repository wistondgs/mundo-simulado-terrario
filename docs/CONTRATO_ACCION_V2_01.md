# Contrato de Acción v2 y la validez de los instrumentos

`ENGINEERING_SANDBOX_NOT_EVIDENCE` · ningún preregistro firmado · ningún hash regenerado

## 0. Lo que cambió de fondo

Terrario ya tenía una teoría de **validez experimental**: preregistro, evidencia sellada,
cortafuegos entre banco de ingeniería y evidencia científica. No tenía una teoría de **validez
de instrumento**. Cuatro instrumentos midieron mal antes de que nadie lo notara, y tres de los
cuatro se descubrieron por choque con algo ya sabido — es decir, por suerte. Un instrumento
equivocado por un factor de dos no produce ningún choque: simplemente se cree.

Esta noche se añadieron las dos piezas que faltaban. Una registra qué mide cada métrica y no
deja que entre en un informe sin controles que pasen. La otra factoriza la acción para que el
organismo pueda decir **a qué** se refiere, que es lo que no podía decir.

## 1. La acción como estructura, no como entero

Bajo v1 una acción era un entero en `[0, 25)`: `action_type * 5 + direction`. `Action` llevaba
un campo `target_id`, pero `to_int` y `from_int` lo descartaban, así que **nada de lo que un
agente pudiera emitir llegaba nunca a ese campo**. El organismo podía decir «comer hacia
arriba»; no podía decir «comer *eso*». La tasa de direccionamiento medida era 2–4 % para todos
los agentes, incluido el aleatorio, cuyo valor analítico de azar es 1/25 = 0.04.

v2 factoriza:

```
a_t = (o_t, s_t, v_t)      operación · tipo de selector · valor
```

`o_t` conserva su significado: CONSUME sigue siendo consumir. Lo que varía es **cómo** la
operación encuentra su objeto, y ése es el eje experimental T:

| Nivel | Selector | Estado |
|---|---|---|
| T0 | DIRECTION | comportamiento v1, exactamente |
| T1 | TARGET_ID | ranura de percepción |
| T2 | RELATION | **reservado, sin implementar** |

T2 no se construyó. Se declara para que el contrato no lo impida más tarde: «el objeto que
bloquea la ruta», «el más incierto», «el miembro más nuevo de una clase» no son ni dirección ni
identidad fija, y Genesis los necesitará.

### Los seis invariantes

| | Invariante | Cómo se hace cumplir |
|---|---|---|
| AC2‑1 | **Opacidad** | El organismo emite un índice de ranura, nunca un identificador. No existe campo por el que colar uno. Los handles se salan por episodio. |
| AC2‑2 | **Observabilidad** | Las ranuras se construyen sólo con entidades dentro de la ventana de visión y no ocluidas por la máscara. Sustituye la búsqueda omnisciente de v1 en `world.objects`. |
| AC2‑3 | **Resolución determinista** | Orden por distancia y luego fila‑columna: pura geometría, que el agente ya percibe. |
| AC2‑4 | **Temporalidad** | `VALID / STALE / OUT_OF_RANGE / OCCLUDED / NONEXISTENT`. Un mundo que se movió no es un error cognitivo. |
| AC2‑5 | **Sin recaída silenciosa** | Un objetivo irresoluble falla como `FAILED_TARGET_RESOLUTION`; no se convierte en una dirección ni en «lo más cercano». |
| AC2‑6 | **Procedencia completa** | Percibido, pretendido, resuelto y ejecutado se registran por separado. |

`tests/test_action_contract_v2.py` los prueba como puertas, más los cuatro controles de
direccionamiento: objetivo perfecto, handle inexistente, handle caduco (que **no** debe
resolver a lo que ocupó la celda) y entidad no observable — ésta demostrada por **inexpresable
desde la interfaz**, no por rechazo del resolutor.

### El handle no es el identificador del mundo

```
WorldEntityID  ->  ObservationHandle_t
```

Por defecto `EPHEMERAL`: el handle se re‑acuña cada fotograma. Un handle estable a través del
tiempo regalaría **permanencia del objeto**, y reconocer que lo que se ve ahora es lo que se vio
antes es una capacidad que queremos medir, no conceder. `TRACKED_IDENTITY` existe y hay que
pedirla.

## 2. Cuatro estados que no pueden confluir

```
0.0            hubo soporte, la cantidad se calculó, salió cero
NOT_EVALUABLE  no existe soporte — el denominador está vacío
MISSING        falta un campo que el cálculo necesita
INVALID        los datos están y violan el contrato que dicen cumplir
```

`conversion_aprendizaje = 0` afirma que el organismo tuvo exposiciones informativas y no
convirtió ninguna. Con `N_informative = 0` el mismo 0 no afirma nada, y son hallazgos opuestos
con el mismo dígito. La defensa es estructural: `float(reading)` levanta excepción salvo que la
lectura sea OK, y `ratio()` devuelve `NOT_EVALUABLE` con denominador vacío en vez de dividir.

## 3. La máquina de estados del instrumento

```
UNREGISTERED -> DEFINED -> CONTROLLED -> CALIBRATED -> REPORTABLE
```

con estados de bloqueo `FAILED_CONTROL`, `UNIDENTIFIABLE`, `INSUFFICIENT_SUPPORT`,
`CONTRACT_MISMATCH`, y `EXPLORATORY_UNCALIBRATED` para lo que puede guiar el trabajo y no puede
ser un hallazgo. Sólo `REPORTABLE` entra en evidencia.

Seis métricas registradas, todas `REPORTABLE`, cada una con su condicionamiento escrito:

| Métrica | Forma condicional |
|---|---|
| `tasa_oportunidad` | `P(O_t)` |
| `tasa_interaccion` | `P(C_t)` |
| `tasa_direccionamiento` | `P(T_t \| C_t, O_t)` |
| `conversion_aprendizaje` | `P(B_t \| T_t, C_t, O_t)` |
| `tasa_realizacion` | `P(ejecutado == pretendido \| intención válida)` |
| `contabilidad_energetica` | `P(ΔV_obs == ΔV_declarado \| sin interacción)` |

Dieciséis controles de falsación, todos verdes. El que más vale: un agente uniforme debe leer
**0.0400** analítico y lee **0.0404**. Ése es el control que habría cazado el fallo de
direccionamiento en el acto, porque 0.000 no es 0.04.

## 4. Lo que los controles encontraron

**Cuarto instrumento defectuoso, hallado por control y no por suerte.** `_eating` leía su línea
base como la mediana de los pasos ociosos y caía a 0.0 cuando no había ninguno — que es
exactamente el organismo cuya política colapsó sobre CONSUME. Todo su desgaste metabólico se
contaba entonces como centenares de consumos fallidos: una tasa de acierto de 0.000 fabricada a
partir del coste por paso. Ahora manda el coste declarado, la mediana es el respaldo, y sin
ninguno de los dos la lectura se rechaza en vez de coaccionarse a cero.

**Quinto, atrapado antes de correr nada.** La tasa de direccionamiento decidía geométricamente,
leyendo `direction` — que bajo T1 está fijada a NONE por el propio contrato. Habría puntuado
**todas** las corridas T1 en 0.000 exactos: un instrumento informando de la ausencia de
precisamente la capacidad que el experimento añade, y el resultado se habría leído como
refutación decisiva. Ahora defiere al resolutor y tiene controles en ambos extremos del camino
T1.

## 5. La pureza de la intervención

T debe variar el direccionamiento y **nada aguas arriba**. Dos versiones del contrato fallaron
esto en silencio, y ninguna produjo un error:

1. La primera fijaba a NONE la dirección de *toda* operación bajo T1, incluido MOVE. El
   organismo quedó paralizado: **1 oportunidad en 300 pasos** frente a decenas bajo T0, y una
   política aleatoria puntuando **1.0** de direccionamiento sobre un denominador de 1.
2. La segunda dejaba PUSH direccionando entidades. PUSH es como este organismo se desplaza —
   empuja y sigue al objeto. Sus empujes dejaron de resolver y visitó **2 celdas** con algo
   adyacente en cada paso.

Además, la propia rama factorizada retornaba antes del planificador, de modo que un brazo
factorizado no era «el mismo organismo direccionando distinto» sino **un organismo sin
planificador** — y el tamizado había mostrado que el planificador es uno de los dos únicos
módulos que mueven la conducta (+6.67 comidas).

Y una corrección de método: la tasa de oportunidad **no sirve** como prueba de pureza, porque
comer elimina el objeto comido. Un brazo que direcciona bien despeja su entorno y reporta menos
oportunidades; uno que nunca resuelve permanece rodeado y reporta 1.0 exacto — que es lo que
hizo todo brazo T1 a toda longitud. La pureza se juzga ahora en la ventana de los primeros 100
pasos y se reporta junto a una tasa de locomoción, que ningún consumo puede influir.

## 6. Reclasificación del tamizado anterior

Las 39 corridas no se descartan ni se marcan falsas. El experimento se hizo bien con el
instrumento entonces disponible; lo que cambió después es la capacidad del laboratorio de decir
qué lecturas estaban identificadas.

| | Efectos | Interacciones |
|---|---|---|
| `CONFIRMED_UNDER_CALIBRATED_INSTRUMENT` | 108 | — |
| `IDENTIFIABLE` | — | 31 |
| `SUPERSEDED_BY_INSTRUMENT_CALIBRATION` | 18 | 2 |
| `NON_IDENTIFIABLE_BY_SATURATION` | — | 2 |

Las 18 superadas son `aciertos_al_comer` y `mejor_tramo_al_comer`, ambas hijas de la línea base
rota. Entre ellas, el 0.486 → 0.000 del modelo del mundo: descriptivamente correcto, y **no**
interpretable como «el modelo del mundo explica 48.6 puntos de discriminación», porque sin
consumos casi no hay ensayos donde medirla.

Y un hallazgo que estuvo tapado: `memoria_completa` (memoria episódica + persistente,
CON‑0014/CON‑0029, James y Darwin) es `IDENTIFIABLE` con residuo **−3.0**. Quitar las dos
memorias juntas cuesta 0 comidas; quitarlas por separado cuesta 2.67 y 0.33. Son **sustitutas,
no complementarias**. Lo tapaba un fallo propio: la puerta de suelo miraba toda la malla en vez
de los componentes de cada conjunción, y disparaba en las tres.

## 7. Esquema tipado: el selector no es global

PUSH demostró que `(operación, tipo_selector, valor)` sigue siendo demasiado genérico si el
selector se aplica globalmente. El dominio válido depende de la **semántica de cada operación**,
leída de la física y no de la intuición:

```
MOVE     → {SPATIAL_DIRECTION}      _handle_move usa DIRECTION_DELTA y nada más
PUSH     → {SPATIAL_DIRECTION}      empuja hacia una dirección y sigue al objeto
CONSUME  → {SPATIAL_DIRECTION, OBSERVED_ENTITY}
INSPECT  → {}                       _handle_inspect NO lee dirección ni target_id
NOOP     → {}
```

T deja entonces de ser «todo el agente direcciona direcciones» frente a «todo el agente
direcciona entidades» y pasa a ser la pregunta estrecha que siempre debió ser: **para la
operación semánticamente dirigida a entidad, ¿qué representación realiza el objetivo?** MOVE y
PUSH quedan idénticas entre condiciones.

## 8. La prueba que faltaba: ¿v1 podía expresar la intención?

Que el direccionamiento medido esté en azar demuestra que el agente **no aprendió** a usar el
canal. No demuestra que el canal **no pudiera** expresar el objetivo. Si hay exactamente un
objeto arriba, `CONSUME(UP)` ya dice «consume ese objeto».

```
R_T(I, s) = 1  ⟺  ∃ a ∈ A_T : Execute(s, a) realiza I
```

Medido sobre un banco de **3000 estados exógenos** — posiciones muestreadas sobre mundos recién
instanciados, ninguna trayectoria involucrada, affordance exógena 0.481:

| Contrato | Intenciones realizables | R |
|---|---|---|
| T0 direccional | 1894 | **1.0** |
| T1 entidad | 1894 | **1.0** |

Control: con la ventana perceptiva reducida a 1, T1 cae a **0.0** y T0 se mantiene en 1.0. El
instrumento sí ve una intención inexpresable; no encuentra ninguna porque no la hay.

**Action Contract v1 era expresivamente suficiente.** El defecto no es expresividad. Vive en
aprendizaje, asignación de crédito o estabilidad de política.

## 9. Paridad conductual e aislamiento de un paso

Una cabeza de entidad inicializada de forma independiente hacía que T1 significara cuatro cosas
a la vez: selector nuevo, parámetros nuevos, distribución inicial nueva y dinámica de colapso
nueva. Ahora:

```
logit_T1(e) = logit_T0(d(e)) + r(e),     r(e) = 0 en t=0
```

La paridad se afirma sobre **log-odds**, no sobre probabilidades, porque los soportes difieren
de verdad: T0 reparte masa sobre cinco direcciones incluidas las que no alcanzan ninguna casilla,
T1 sobre las entidades realmente percibidas. Esa diferencia es el contenido representacional de
T1, no un confusor.

La comparación sale del bucle cerrado: **un** agente con ambas cabezas decide dos veces sobre el
**mismo** estado, ambos brazos consumen la **misma** variable uniforme, y el mundo no avanza
entre ellos. `first_divergence` recorre la cadena y falla si difieren antes de
`selector_representation`.

### Resultado

```
INTERVENTION_ISOLATION: PASS   (0 fallos de 3000 pares)

                       resolubilidad    NONEXISTENT   OUT_OF_RANGE   VALID
T0 direccional             0.272            2608            —         392
T1 entidad                 0.327             150          2378        472

discordantes: sólo T0 225 · sólo T1 305 · McNemar χ² = 11.775 · p < 0.001
```

Dos cosas distintas, y la segunda importa más que la primera.

**Primera**: con paridad exacta en el inicio, T1 resuelve más que T0 sobre estados idénticos, y
la diferencia es estadísticamente distinguible. No es un efecto de aprendizaje — es del paso
cero.

**Segunda**: los modos de fallo son cualitativamente distintos. Bajo T0 el 87 % de los consumos
apuntan a **espacio vacío**. Bajo T1 el organismo **refiere con éxito a una entidad real en el
95 % de los casos** y lo que falla es el alcance. T0 confunde «no me referí a nada» con «me
referí a algo que no alcanzo»; T1 las separa. Para una teoría de la inteligencia esa distinción
vale más que los cinco puntos de resolubilidad.

## 10. Los dos gates previos al rollout cerrado

### Gate 1 · denominador explícito

La resolubilidad no se reporta ya como una tasa cuyo conjunto de condicionamiento haya que
reconstruir dividiendo. El instrumento emite `states_total`, `consume_attempts`,
`valid_references`, `states_with_entity_in_contact` y la tasa condicionada, más la afirmación de
que ambos brazos comparten denominador. En el banco de un paso la operación está fijada en
CONSUME por construcción, así que `consume_attempts = states_total = 3000`, y el denominador de
la tasa es el subconjunto con una entidad percibida y en contacto: **1442**, propiedad del
estado e idéntica para los dos brazos.

### Gate 2 · acoplamiento del azar exógeno — **FALLABA**

`opportunities.py` sembraba el sorteo del cooldown y el de la colocación con
`len(self.events)`, el número de oportunidades consumidas hasta ese momento:

```python
event_index = len(self.events)
rng = np.random.default_rng(self._seed + 104_729 * (event_index + 1))
```

Es decir, el calendario exógeno del mundo era **función de la conducta del organismo**. Dos
corridas desde la misma semilla de mundo, distintas sólo en cuántas veces comió el agente,
sorteaban sus retardos de respawn de streams distintos. El registro de mundos declara *«world
seed materializes layout; agent seed is independently offset»*, y con una clave por orden de
llamada eso era sencillamente falso.

Para el diseño pareado es peor que una imprecisión: T alcanzaba el resultado dos veces, una como
sí misma y otra por `T → orden de RNG → W_{t+1}`, y eso no se separa después por mucho que se
siembre arriba.

**Reparado, en dos pasos.** El primer intento — clavar la clave en
`(seed, tipo, identidad_de_oportunidad)` — no bastaba, y el residuo era el mismo defecto un nivel
más abajo: el `spawn_key` era `self._next_opportunity_id`, un **contador global**, y un objeto
que reaparecía heredaba su id de ese mismo contador. Una dependencia de orden disfrazada de
identidad.

La clave definitiva tiene cuatro coordenadas:

```
U_{i,k} ~ RNG(world_seed, stream_kind, lineage_root, generation)
```

con la generación contada **dentro** del linaje, nunca globalmente. `U(7,3)` es la misma variable
tanto si antes se consumieron dos oportunidades como cuarenta, y cada reaparición de un linaje
sortea la suya — con identidad sola, toda reaparición de la oportunidad 7 habría heredado el
mismo cooldown y la misma colocación durante toda la corrida: un latido determinista disfrazado
de azar. Nueve pruebas lo fijan.

**Lo que NO se reparó, por decisión explícita.** Conviene separar tres cantidades:

```
U        ~ RNG(seed, stream, lineage_root, generation)    EXÓGENA
C_t      = f(World_t, Agent_t, recent_positions)          ENDÓGENA
Spawn_t  = g(C_t, U)
```

La **variable latente está acoplada** entre brazos. Su **realización física puede diferir**,
porque el conjunto factible es parte del estado endógeno del mundo: con el mismo `u = 0.63`,
candidatos `[A,B,C,D]` seleccionan C y candidatos `[A,D]` seleccionan D. Eso no es fuga de RNG:
es la trayectoria. Y el camino

```
T → trayectoria → C_t → posición de respawn → experiencia futura
```

**forma parte del efecto total de T**. Eliminarlo convertiría D4T en otro mundo.

## 11. La descomposición del intento

```
N_consume = N_nonexistent + N_out_of_range + N_valid + N_other
N_valid   = N_beneficial  + N_harmful      + N_neutral
```

Ambas identidades se comprueban por corrida y `N_other` sale cero. Eso separa tres preguntas que
vivían dentro de una sola tasa de fracaso, y deja una cuarta por fin formulable:

| | Pregunta |
|---|---|
| REFERENCIA | ¿señaló algo que existe? |
| AFFORDANCE | ¿podía actuar sobre ello? |
| DISCRIMINACIÓN | ¿era correcto elegirlo? |
| APRENDIZAJE | ¿mejoró esa discriminación con la experiencia? |

## 12. Estado del contrato

```
EXPRESSIVITY_T0                = SUFFICIENT
EXPRESSIVITY_HYPOTHESIS        = REFUTED

TYPED_ACTION_SCHEMA            = PASS
SELECTOR_ISOLATION             = PASS
INITIAL_BEHAVIORAL_PARITY      = PASS
FIRST_DIVERGENCE_GATE          = PASS

EXOGENOUS_RNG_COUPLING         = PASS   (lineage + generation, 9 pruebas)
RESPAWN_CANDIDATE_DEPENDENCE   = KEEP   (endogenous world dynamics, por decisión)

LOCAL_RESOLUTION_EFFECT        = DETECTED  (McNemar χ² 11.775, p<0.001,
                                            cociente discordante 305/225 ≈ 1.36)
MECHANISM                      = ACTION-SPACE FACTORIZATION /
                                 REFERENTIAL INDUCTIVE BIAS

E                              = FROZEN
COST                           = FROZEN
CLOSED_LOOP_T0_VS_T1           = ACTIVE EXPERIMENT
```

El efecto local es **reproducible y moderado, no milagroso**: p<0.001 dice que la asimetría es
difícil de atribuir al azar bajo este diseño, no que el efecto sea grande.

Lo que se ha ganado conceptualmente es mayor que el efecto medido: el error inicial no era falta
de expresividad del organismo, sino que habíamos confundido **expresividad, referencia, alcance y
discriminación dentro de una sola tasa de fracaso**. Terrario empieza a poder decir *dónde* falla
el organismo, no solamente *que* falla.

El efecto local es **reproducible y moderado, no milagroso**: p<0.001 dice que la asimetría es
difícil de atribuir al azar bajo este diseño, no que el efecto sea grande.

## 13. Registro de decisiones · 2026-09-17

### 13.1 El lote anterior queda separado, no combinado

Las corridas interrumpidas bajo el acoplamiento defectuoso sirven como **diagnóstico de ese
defecto**. No completan parejas ni alimentan intervalos del lote corregido. En la práctica no hay
riesgo de mezcla: el experimento escribe su JSON sólo al terminar, y ambos lotes abortados
murieron antes, así que `artifacts/` no contiene nada de ellos. El análisis posterior estampa
`rng_mechanism` para que la separación quede en el registro y no en la memoria de nadie.

Precisión sobre lo demostrado: el problema era **incumplimiento del acoplamiento entre brazos**,
no necesariamente falta de reproducibilidad de cada corrida por separado. Son propiedades
distintas y conviene no confundirlas al citar el hallazgo.

`selector_isolation.json` (los gemelos de un paso) **no** queda afectado: el banco de instantáneas
llama a `materialize_scenario` y `build_world_state` y nunca construye `OpportunityLifecycle`.

### 13.2 `p_beneficial_given_valid` separa resultados; no identifica discriminación aprendida

La magnitud

```
q_i(T) = N_beneficial,i(T) / N_valid,i(T)
```

describe qué proporción de las interacciones **válidas de ese brazo** resultó beneficiosa. Se
conserva, y se conserva su límite: **T también cambia qué entidades llegan a consumirse**, así
que una diferencia entre `q(T1)` y `q(T0)` puede reflejar mejor selección, distinta exposición o
ambas. Es condicionamiento sobre una variable **posterior a la intervención**, y no equivale a
comparar capacidad discriminativa sobre los mismos objetos y oportunidades.

En el ejemplo del humo, `q(T0) = 0/1 = 0` y `q(T1) = 2/4 = 0.5`: ambos cocientes están definidos,
y el cero de T0 es **legítimo** — hubo una interacción válida — no el cero artificial que se
corrigió en §4. Pero una interacción frente a cuatro no demuestra que T1 haya aprendido nada.

| Resultado observado | Afirmación que permite |
|---|---|
| Más resoluciones válidas | Mejor **ejecución realizada** bajo ese selector |
| Más consumos beneficiosos | Mejor **resultado conductual total** en esas corridas |
| Mayor proporción beneficiosa entre consumos válidos | Mejor **composición** de los consumos realizados |
| Mejora atribuible a la actualización del agente, sobre oportunidades comparables | Evidencia específica de **aprendizaje** — *no se deduce de las tres anteriores, y este lote no la mide* |

### 13.3 Sin soporte se excluye de esa métrica, no del experimento

Una semilla sin consumos válidos **sigue siendo evaluable** para número de consumos, éxitos,
supervivencia y todo resultado no condicionado. No desaparece del análisis.

Para cada cociente condicionado se declaran cuatro cubetas: parejas con soporte en **ambos**
brazos, sólo T0, sólo T1, o ninguno. La comparación entre parejas con soporte en ambos responde a
una pregunta **restringida a ese subconjunto**: el propio tratamiento puede determinar si aparece
soporte, y eso cambia la población evaluada aunque el cálculo del cociente sea correcto.

### 13.4 Verificaciones de la inferencia

Comprobadas, no supuestas:

- **`median_delta` es la mediana de las diferencias pareadas**, no la resta de las dos medianas.
  Caso construido: Δ = `[1.0, 0.5, 0.0, 5.0, −95.0]` → mediana de las Δ = **0.5**, mientras que la
  resta de medianas da **0.0**. El script reporta 0.5.
- **El bootstrap conserva la pareja completa.** `paired_test` recibe únicamente la lista de
  diferencias y nunca ve los brazos por separado, así que partir una pareja es estructuralmente
  imposible. Contraste: IC95 pareado `[1.0, 5.125]` frente al no pareado `[−1.125, 6.75]`.

## 14. Lo que sigue abierto

- T1 no es «mejor» por construcción: un agente uniforme direcciona **peor** bajo T1 (16 ranuras,
  casi todas vacías) que bajo T0 (5 direcciones). T1 compra expresividad, no puntería. Sólo un
  aprendiz puede cobrar la diferencia.
- El colapso de política es anterior a todo esto. Cada brazo cae sobre una acción distinta en
  unos cientos de pasos, y cuál sea decide cuánto se expone al mundo.
- T2 relacional sigue reservado y sin semántica operacional, a propósito.

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

## 10. Lo que sigue abierto

- T1 no es «mejor» por construcción: un agente uniforme direcciona **peor** bajo T1 (16 ranuras,
  casi todas vacías) que bajo T0 (5 direcciones). T1 compra expresividad, no puntería. Sólo un
  aprendiz puede cobrar la diferencia.
- El colapso de política es anterior a todo esto. Cada brazo cae sobre una acción distinta en
  unos cientos de pasos, y cuál sea decide cuánto se expone al mundo.
- T2 relacional sigue reservado y sin semántica operacional, a propósito.

# Mapa de composición de capacidades primitivas · v0.1

**2026-09-21** · el mapa del programa nuevo, al otro lado de la frontera de
[CONGELACION_HISTORICA_01.md](docs/CONGELACION_HISTORICA_01.md). Código en
[primitive_composition.py](terrario/lab/hypergraph/primitive_composition.py),
contratos en [test_primitive_composition.py](tests/test_primitive_composition.py).

La unidad no es el nodo. Es:

```
{P_i, P_j, ...}  →  ?
```

y el signo de interrogación aguanta peso. `A+B = C` se escribe **después** del
experimento. Hasta entonces la arista sostiene una hipótesis con una salida que
nadie ha visto.

**Sin capacidad objetivo, sin arquitectura final, sin nivel de inteligencia
esperado.** El mapa dice qué existe, qué se combinó con qué, qué ocurrió, qué no
ocurrió y qué todavía no se sabe.

---

## El hallazgo, antes de las cuatro secciones

Importado todo lo que el programa histórico midió **como composición** —seis
aristas— el resultado es éste:

```
aristas con grado de libertad registrado ......... 0 de 6
composiciones replicadas en dos mundos ........... 0
ΔDF de la escalera histórica ..................... 0 en cada peldaño
```

**Ninguna.** Y no es un fallo del importador. El programa viejo preguntaba si un
organismo concreto adquiría una capacidad concreta; **nunca preguntó qué grado
de libertad se había ensanchado**, así que nada de lo que produjo puede poblar
esa columna.

Ésa es la justificación medida de la congelación: el mapa nuevo no puede
arrancar releyendo el viejo, porque el viejo no contiene la variable que el
nuevo mide. Hay que correr experimentos propios.

---

## I · Diccionario de primitivas · P01–P20

Cada una responde seis preguntas y **ninguna más**: qué puede, qué **no** puede,
qué necesita, cuánto cuesta, cómo se detecta, de dónde sale.

El campo «no puede» no es adorno. Una primitiva que sólo dice lo que puede crece
en la cabeza del lector hasta volver a ser una facultad, y el límite es la razón
entera de llamarlas mínimas.

### Las siete semillas históricas

Sus números de nivel son **cronología, no escalera**. Aquí son siete elementos
disponibles del banco.

| ID | nombre | puede | no puede |
|---|---|---|---|
| P01 | contingencia sensorimotora | notar que su acto cambió lo que siente | decir cuál, en qué dirección ni cuánto |
| P02 | orientación direccional | usar `g_t` para distinguir una dirección | decir cuánto, ni retenerla sin la señal |
| P03 | proximidad cualitativa | distinguir cerca de lejos como cualidad | medir, ordenar tres distancias, retenerla |
| P04 | persistencia de un paso | conservar una señal un tick tras desaparecer | recuperar episodios, elegir qué guardar |
| P05 | binding conjuntivo mínimo | sostener dos referencias como **un par** | ligar tres, religar al vuelo, nombrarlo |
| P06 | regularidad temporal | llevar `P(o_{t+1} \| o_t)` | condicionar sobre su acto, un bit de cambio, copia eferente o posición |
| P07 | contingencia de acción | llevar `C_17(O, A, O')` | adquirir la relevancia causal o la generalidad de «acción» |

### Las trece descompuestas del Mapa Global

Salen de trocear `INVENTARIO_CONCEPTOS_01.md`. **El concepto fuente está citado;
el troceo lo hice yo**, y la provenance de cada una lo dice con `DECOMPOSED
from`.

| ID | nombre | de dónde sale |
|---|---|---|
| P08 | cambiar una asociación por su desenlace | `use_online_learning` / LEARN-A1 |
| P09 | detectar desviación interna respecto de una referencia | `use_homeostasis` / HOMEO-A1 |
| P10 | distinguir caso frecuente de caso raro | `use_uncertainty` / UNC-A1 |
| P11 | retener más de un paso | `use_episodic_memory` / EPMEM-A1 |
| P12 | retener a través de un corte de episodio | `use_longterm_memory` / LTMEM-A1 |
| P13 | responder distinto al mismo presente | `use_entropy_regularization` / PLAST-A1 |
| P14 | distinguir visto de no-visto | `use_curiosity` / CURIO-A1 |
| P15 | componer un acto de dos factores | `use_factored_action` |
| P16 | resortear un parámetro propio sin gradiente | B1 ultraestabilidad · HEA-014 |
| P17 | usar una magnitud interna como refuerzo | B2 recompensa interoceptiva · HEA-001 |
| P18 | mover el punto de referencia | B3 alostasis · HEA-011 §2 |
| P19 | distinguir igual media con distinta dispersión | B4 aversión al riesgo · HEA-001 |
| P20 | leer el propio error de predicción | B5 metacognición · HEA-017 |

### Lo que el criterio de exclusión dejó fuera

> Si una capacidad contiene dentro otra capacidad funcional identificable,
> todavía no es suficientemente primitiva.

Aplicado en serio, **casi ningún concepto de nivel superior del Mapa Global lo
pasa entero.** De 22 conceptos en las tres capas salieron 13 primitivas, y las
que no entraron constan con su razón:

| concepto | por qué no |
|---|---|
| `use_planner` / PLAN-A1 | contiene un modelo del mundo **y** una búsqueda sobre él |
| `use_world_model` / WM-A1 | su núcleo mínimo ya es P06 y P07; no sobra nada primitivo |
| `use_temporal` / TEMP-A1 | su núcleo mínimo ya es P06; lo que queda contiene retención |
| B6 impulsos modulares | contiene dos funciones de recompensa y un arbitraje. Y con `N=1` **su experimento no se puede correr**: HEA-005 §3.3 fija una variable y mide «las restantes», y no hay restantes |
| capa 3 entera | les falta **sustrato**, no primitividad: una segunda variable esencial, un operador de perturbación, un espacio de estados enumerado |

Un mapa que sólo lista lo que entró no deja comprobar el criterio.

---

## II · Hipótesis de composición · `{A,B,...} → ?`

**Este apartado está casi vacío a propósito.** Las combinaciones posibles sobre
veinte primitivas son:

```
pares      190
tríos    1.140
total   1.048.555 subconjuntos no vacíos de tamaño ≥ 2
```

Elegir cuáles correr **es** la pregunta de muestreo que abre el programa nuevo,
no un hueco que se rellena escribiendo pares plausibles. Rellenarlo hoy sería
volver a elegir una campaña y llamarla programa.

Lo único que sí entra son las hipótesis que el propio programa congelado deja
abiertas, y entran marcadas:

| arista | composición | estado | por qué está abierta |
|---|---|---|---|
| `H006` | `{P04, P06, P07}` → `E004` | `UNKNOWN` | la campaña que la habría resuelto es un `FAMILY_MISMATCH`: el oráculo selló `Z_{t+1} = F(Z_t, A_t, O_{t+1})` y corrió el degenerado `F(Z_t, A_t)`. No la falsó — midió otra |
| — | identidad de `PSI_UNIDENTIFIED` | `UNKNOWN` | el oráculo de 1.4 usa el símbolo para una biyección experimental **no entregada al agente**; igualarlos sería conveniencia |

Y la advertencia de §8, escrita aquí para que no se pierda: **no basta con la
cadena acumulativa.** Con A, B, C no alcanza probar `A`, `A+B`, `A+B+C`; hacen
falta también `A+C` y `B+C`, porque puede ocurrir que `A+B → ∅` y `A+C → X`. Eso
es exactamente lo que hace falta un hipergrafo y no una escalera.

---

## III · Resultados observados · `{A,B,...} → E`

Seis aristas, **todas con provenance `HISTORICAL`** y todas con su mundo.

| arista | composición | mundo | salida | estado | grados de libertad |
|---|---|---|---|---|---|
| `H001` | `{P03, P04}` | `W-level1-grid` | `E001` | OBSERVED | **UNKNOWN** |
| `H002` | `{PSI_UNIDENTIFIED}` | `W-level1-grid` | `NONE` | **NO_EFFECT** | — |
| `H003` | `{PSI_UNIDENTIFIED, P04}` | `W-level1-grid` | `E002` | OBSERVED | **UNKNOWN** |
| `H004` | `{P06, P07}` | `W-level17-twin-A` | `E003` | OBSERVED | **UNKNOWN** |
| `H005` | `{P06, P07}` | `W-level17-twin-B` | `NONE` | **NO_EFFECT** | — |
| `H006` | `{P04, P06, P07}` | `W-level18` | `E004` | UNKNOWN | — |

**`H004` y `H005` son la misma composición en dos mundos con resultados
opuestos**, y no se contradicen. En el gemelo B la acción no mueve la
transición —`T_B(s'|s,a) = ¼ Σ_b T_A(s'|s,b)`— y la información mutua es **cero
exacto**. Dos condiciones, no una contradicción. Por eso el mundo viaja con la
arista y una arista sin mundo se rechaza en el constructor.

**`H002` y `H003` son para qué sirve `NO_EFFECT`.** ψ sola aporta cero exacto;
ψ con `P04` funciona. El mapa calcula solo que **`P04` fue el elemento
desbloqueante**, y ese cálculo sólo es posible porque la fila vacía existe. Una
ausencia de emergencia que no se escribe es una fila que después no identifica
nada.

**Y la columna de grados de libertad está entera en `UNKNOWN`.** El programa
viejo midió que la composición era superaditiva; **cuál** grado de libertad se
ensanchó no era su pregunta. `UNKNOWN`, no cero.

---

## IV · Grados de libertad acumulados · `DF(S_n)`

```
ΔDF_n = DF(S_n) − DF(S_{n−1})
```

**No hay filas.** El organismo acumulativo del programa nuevo no existe: no hay
`N1.0`. Y aunque se importara la escalera histórica, cada `ΔDF` daría **0**,
porque ninguna arista importada lleva grado de libertad.

Un `ΔDF = 0` es un resultado útil y se escribe; una escalera entera de ceros por
falta de la variable medida es otra cosa, y decir «cero» ahí sería mentir con un
número. Hay un contrato que fija las dos lecturas por separado.

Las seis preguntas con las que se responderá esta sección cuando haya qué medir:

```
¿puede distinguir más estados?                    STATE_DISCRIMINATION
¿puede depender de más pasado?                    TEMPORAL_CONDITIONING
¿puede escoger entre más acciones?                ACTION_RANGE
¿puede modificar algo por experiencia?            EXPERIENCE_DEPENDENT_CHANGE
¿puede mantener más relaciones simultáneas?       SIMULTANEOUS_RELATIONS
¿puede responder distinto al mismo presente?      SAME_PRESENT_DIFFERENT_RESPONSE
```

Y la pregunta que persigue este apartado, de §13: dado `E001`, `E002` y `E003`,
¿es `E003 = E001 + E002` o `E003 > E001 + E002`? Si la composición tiene un
grado de libertad que ninguna combinación menor mostró, hay interacción genuina.
`genuine_interaction` devuelve exactamente ese exceso, y hoy devuelve vacío para
las seis.

---

## Lo que este mapa se niega a sostener

```
un emergente con nombre de facultad     E### o nada · «atención» se rechaza
una arista sin mundo                    no se puede saber de qué condición habla
NO_EFFECT con salida o con un DOF       algo pasó
observar nada sin decir NO_EFFECT       la ausencia tiene su propio estado
una arista que se declara REPLICATED    se calcula sobre varios mundos
una primitiva sin «no puede»            no es mínima, sólo corta
```

Seis estados y no veinte: `UNKNOWN` · `HYPOTHESIS` · `OBSERVED` · `REPLICATED` ·
`NO_EFFECT` · `CONTRADICTED`.

Y no se construye sobre `theory_operational`: esa ontología funciona, pero se
diseñó para una pregunta que quedó retirada.

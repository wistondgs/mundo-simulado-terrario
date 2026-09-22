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
ΔDF de la escalera histórica ..................... NOT_MEASURED · nunca 0
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

Auditadas **una por una y por separado**, cada una contra su propio árbol
congelado, con instrucción explícita de no elegir clasificación para que la
tabla saliera simétrica. Las siete dieron `HISTORICALLY_OPERATIONALIZED`, y eso
es una afirmación **más débil** de lo que parece: dice que se construyó, corrió
y cerró con gates, no que ninguna fuente lo sostenga.

**Ninguna de las veinte es `DIRECTLY_SOURCED`. Cero claims de corpus en todo el
vocabulario.** Para `P04` el propio inventario nombra ese espacio conceptual
como un hueco de corpus declarado.

**Y `P01` es el único peldaño sin oráculo sellado**: tiene siete gates sellados
y ningún documento de oráculo preregistrado, a diferencia de 1.1–1.7. Consta en
su provenance y hay un contrato que lo fija; no se suaviza para que las siete
filas se parezcan.

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
el troceo lo hizo el proyecto**, y eso ya no vive en una cadena de texto: es un
campo tipado que el constructor comprueba.

```
sourcing              DERIVED_BY_DECOMPOSITION
source_concept        obligatorio · sin él se rechaza
derivation_authority  PROJECT_ANALYSIS
boundary_status       BOUNDARY_KNOWN
minimality_status     NOT_ESTABLISHED
```

Sin `source_concept` el registro se leería como «el corpus descubrió P08»,
cuando lo cierto es «el corpus dio un concepto fuente, y el análisis lo
troceó». Sin `derivation_authority` se pierde quién hizo el corte, que es lo
que separa análisis de atestación.

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

| arista | composición | mundo | salida | estado | medición de DF |
|---|---|---|---|---|---|
| `H001` | `{P03, P04}` | `W-level1-grid` | `E001` | OBSERVED | **NOT_MEASURED** |
| `H002` | `{PSI_UNIDENTIFIED}` | `W-level1-grid` | `NONE` | **NO_EFFECT** | — |
| `H003` | `{PSI_UNIDENTIFIED, P04}` | `W-level1-grid` | `E002` | OBSERVED | **NOT_MEASURED** |
| `H004` | `{P06, P07}` | `W-level17-twin-A` | `E003` | OBSERVED | **NOT_MEASURED** |
| `H005` | `{P06, P07}` | `W-level17-twin-B` | `NONE` | **NO_EFFECT** | — |
| `H006` | `{P04, P06, P07}` | `W-level18` | `E004` | UNKNOWN | — |

**`H004` y `H005` son la misma composición en dos mundos con resultados
opuestos**, y no se contradicen. En el gemelo B la acción no mueve la
transición —`T_B(s'|s,a) = ¼ Σ_b T_A(s'|s,b)`— y la información mutua es **cero
exacto**. Dos condiciones, no una contradicción. Por eso el mundo viaja con la
arista y una arista sin mundo se rechaza en el constructor.

**`H002` y `H003` son para qué sirve `NO_EFFECT`.** ψ sola aporta cero exacto;
ψ con `P04` funciona. El mapa calcula solo que **añadir `P04` cambió el
resultado**, y ese cálculo sólo es posible porque la fila vacía existe.

**Pero la inferencia lleva su scope y no sale de él.** Vale únicamente si las
dos aristas están emparejadas en organismo, presupuesto, implementación y demás
condiciones, variando sólo la presencia de `P04`. Lo licenciado es «añadir
`P04` cambió el desenlace **bajo este scope**», nunca «`P04` desbloquea ψ». El
cálculo se niega a emparejar aristas de scope distinto y devuelve el scope junto
al hallazgo. Que las dos de aquí lo estén lo **afirma el gate RB-7 de su propia
campaña**, y no lo reverifiqué.

**Y la columna de grados de libertad está entera en `NOT_MEASURED`.** El
programa viejo midió que la composición era superaditiva; **cuál** grado de
libertad se ensanchó no era su pregunta. Ningún instrumento de DF corrió nunca,
así que no hay valor — ni cero.

---

## IV · Grados de libertad acumulados · `DF(S_n)`

```
ΔDF_n = DF(S_n) − DF(S_{n−1})
```

**No hay filas.** El organismo acumulativo del programa nuevo no existe: no hay
`N1.0`. Y la escalera histórica no da ceros — da `NOT_MEASURED` en cada peldaño,
porque ninguna arista importada lleva medición de grado de libertad.

### `MEASURED_ZERO` y `NOT_MEASURED` son estados distintos

Ésta es una corrección a la v0.1 inicial, y era un error de bulto: el documento
decía «`UNKNOWN`, no cero» y la función `delta_df` **devolvía cero** dos líneas
después. La prosa y el código se contradecían, y el código gana siempre.

```
dof_status        NOT_MEASURED  |  MEASURED
dof_measurement_ref      null   |  obligatorio
dof_before / dof_after   null   |  los dos, del instrumento
delta_dof                null   |  calculado · puede ser 0
```

Con las invariantes en el constructor: una arista `NOT_MEASURED` que lleve una
lectura se rechaza, y una que **nombre** un grado de libertad también —nombrarlo
**es** la medición—. Y al revés, una `MEASURED` sin instrumento, sin las dos
lecturas, con un aumento que no nombra qué subió, o que nombra algo habiendo
medido delta ≤ 0, se rechaza igual.

`MEASURED` con `delta_dof = 0` es **completamente legítimo** y no equivale a
`NOT_MEASURED`. Hay un mutante dedicado que construye las dos escaleras sobre los
mismos peldaños —una con instrumento que no encontró aumento, otra sin
instrumento— y exige que las filas **nunca** comparen iguales.

Lo único que vale cero hoy es:

```
#{aristas históricas con medición de DF} = 0
```

`genuine_interaction` sigue la misma regla: devuelve `None` cuando nadie midió,
no el conjunto vacío. Vacío diría «la composición es exactamente la unión de sus
partes», y nadie miró.

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
una primitiva sin «no puede»            sin frontera negativa explícita
minimalidad afirmada sin base           una frontera no es una demostración
una arista NOT_MEASURED con lectura     nadie midió; el valor sería inventado
```

**Frontera conocida no es minimalidad demostrada**, y la v0.1 inicial las
confundía. Una cosa puede decir exactamente qué no puede hacer y seguir siendo
descomponible, así que son dos afirmaciones separadas:

```
BOUNDARY_KNOWN                    su frontera negativa es explícita
MINIMAL_UNDER_CURRENT_VOCABULARY  y además no existe descomposición operacional
                                  más fina pertinente al programa actual que
                                  preserve el fenómeno que queremos manipular
```

La segunda exige base escrita y se rechaza sin ella. **Las veinte son
`BOUNDARY_KNOWN`; ninguna afirma minimalidad.** Son la v0.1 de un vocabulario
experimental, no una afirmación sobre los átomos últimos de la inteligencia.

Seis estados y no veinte: `UNKNOWN` · `HYPOTHESIS` · `OBSERVED` · `REPLICATED` ·
`NO_EFFECT` · `CONTRADICTED`.

Y no se construye sobre `theory_operational`: esa ontología funciona, pero se
diseñó para una pregunta que quedó retirada.

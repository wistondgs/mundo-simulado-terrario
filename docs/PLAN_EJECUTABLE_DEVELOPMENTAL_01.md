# Plan ejecutable · hipergrafo developmental

**2026-09-21** · derivado del plan de trabajo v1, con siete mejoras propuestas.
Baseline congelado: **`ed17291`**, 14 contratos verdes.

---

## Parte I · El plan, en unidades entregables

Cada unidad tiene criterio de cierre comprobable. Ninguna se declara hecha por
tener pruebas verdes: el criterio es que exista un mutante que la haga fallar.

### U0 · Congelar el baseline — **HECHO**

`ed17291` con las dos aceptaciones pasando. Y una corrección ya aplicada de la
nota de control del plan, que era un defecto real:

```
antes   M REQUIRES SELECTION        se lee «M requiere SELECTION»
ahora   SELECTION --REQUIRES--> M   · READ
```

Una arista cuya dirección depende de cómo la lea quien pasa es peor que no
tenerla. La dirección ahora se renderiza desde el que depende.

### U1 · `RELATION_LEDGER_V1` · las cuatro dimensiones separadas

Hoy el modelo tiene dos ejes —`DependencyKind` y `EvidenceState`—. El plan pide
cuatro y tiene razón: la **semántica**, la **forma del efecto**, la **clase de
evidencia** y el **estado epistémico** son independientes, y colapsarlos hace
imposible expresar «medido por factorial, sinérgico, soportado, en este mundo».

```
cierre    ninguna MEASURED_* sin evidence_ref  ·  ninguna causal sin scope
          dirección inequívoca  ·  inventario machine-readable
mutante   una arista MEASURED sin experimento  → ya rechaza
          una arista causal sin scope          → debe rechazar
```

### U2 · `CeilingProbe` como objeto, no como etiqueta

Un resultado científico y una señal developmental son dos cosas y una campaña
produce las dos. 1.8 es `FAMILY_MISMATCH` **y** `CEILING_PROBE`.

```
cierre    1.5 y 1.8 existen como CeilingProbe con su blocker observado
mutante   un CeilingProbe sin evidence_ref  →  rechazado
          leer un CEILING_PROBE como negativo científico  →  imposible por tipo
```

### U3 · Tipos de acción derivados

`ACQUIRE · LESION · FACTORIAL · STRUCTURAL_AUDIT · FAMILY_PROBE`. Hoy el
analizador deriva los dos primeros; los tres restantes tienen condición de
disparo distinta y ninguna está implementada.

```
cierre    1.8 deriva FAMILY_PROBE  (firma requerida ≠ firma realizada)
          1.5 deriva LESION de PSI  (ya lo hace)
          una dependencia READ deriva STRUCTURAL_AUDIT antes de causal
mutante   un target con dos capacidades presentes e interacción sin medir
          debe derivar FACTORIAL, no ACQUIRE
```

### U4 · Política de evidencia por tipo de afirmación

El §5 del plan es más fino que mi implementación y lo prefiero: `PREMATURE` no
debe ser «nada medido» sino «por debajo del nivel exigido **para esa clase de
afirmación**».

```
presencia estructural   VERIFIED_CODE basta
necesidad causal        exige lesión / intervención / factorial
suficiencia             exige condición positiva específica
invariancia formal      puede cerrarse por prueba matemática
```

```
cierre    existe un target con PREMATURE=False por prueba formal, no por medida
mutante   subir la exigencia de una clase debe volver prematuro un target
          que antes no lo era
```

### U5 · `CAMPAIGN_BUNDLE_V1` · en paralelo, y con una precedencia que el plan no fija

Ver mejora **M6**: el bundle no es paralelo del todo.

---

## Parte II · Siete mejoras al plan

### M1 · Falta el control negativo de los empates

El §10 pide un control positivo —un target con `PREMATURE=False`— y hace bien.
Pero **no pide el simétrico para los empates**, y sin él la preservación de
empates es invérificable: si cada target empata siempre, la regla no discrimina
nada y pasaría todas las pruebas.

> **Añadir:** una fixture donde la evidencia **sí** ordene los candidatos y
> `tied_candidates` tenga exactamente un elemento.

Es el mismo defecto que el proyecto ya cazó dos veces —«un criterio que sólo
falla tampoco es criterio»— aplicado a un criterio que sólo empata.

### M2 · El scope debe rechazarse en el constructor, no pedirse en la guía

El §3.5 dice «toda relación causal debe incluir scope». Hoy eso es una
instrucción, y una prohibición textual no impide nada — es literalmente la
lección que el propio plan extrae de las fugas de 1.5.

Y sé por qué importa, con un caso: mi única arista medida, `ψ ⇐ M`, es válida
**en Ω_RB** y el plan lo señala en su punto D. Sin rechazo estructural, esa
arista local se convierte en ley universal la primera vez que alguien la lea
deprisa.

> **Añadir:** `MEASURED_*` sin `scope` levanta, igual que `MEASURED` sin
> `experiment` ya levanta hoy.

### M3 · El descompositor necesita procedencia de hipótesis

El §13 prohíbe «automatizar que un LLM decida necesidades causales» y el §A3
dice que el descompositor «genera hipótesis; no adjudica». Correcto — pero
**una hipótesis generada entra al ledger como `CANDIDATE`, exactamente igual
que una que un humano extrajo del corpus**. A los dos meses son
indistinguibles.

> **Añadir** una dimensión de procedencia del candidato:
> `HUMAN_PROPOSED · CORPUS_SOURCED · GENERATED · DERIVED_FROM_NEGATIVE`

Sin ella, la prohibición del §13 no es verificable: no hay forma de auditar
cuántas hipótesis del grafo las propuso una máquina.

### M4 · `SUPERSEDED` necesita apuntar a su sucesora

El §3.4 incluye `SUPERSEDED` en el estado epistémico. Bien — pero un estado
`SUPERSEDED` sin puntero a **qué** la superó reproduce exactamente el problema
de 1.5, donde cuatro supersesiones dejaron afirmaciones retiradas y hubo que
reconstruir a mano cuál mandaba.

> **Añadir:** `superseded_by` obligatorio cuando el estado es `SUPERSEDED`, y
> que el ledger se niegue a resolver una relación cuya cadena de supersesión no
> termine.

### M5 · Falta una clase de evidencia que el proyecto ya produce

El §3.3 lista nueve clases y le falta la que más usó Terrario en su mejor
trabajo: **réplica determinista contra tabla publicada**. Es lo que hizo la
reconciliación de 1.6 —celda por celda, tolerancia `5e-5`, cero diferencias—
cuando los artefactos originales no existían.

No es `MEASURED_*` porque no hay artefacto original; no es
`DECLARED_DOCUMENT` porque hay una comprobación ejecutada. Es un tercer estado
y ya apareció en el cierre de 1.5 como una de las tres clases de provenance
histórica.

> **Añadir:** `REPLICATED_DETERMINISTIC`.

### M6 · El Campaign Bundle no es del todo paralelo

El §9 pone el bundle como Prioridad 2 «en paralelo», y el criterio de cierre de
A1 exige «ninguna `MEASURED_*` sin `evidence_ref`». Esos dos se tocan.

Para las aristas **históricas** el `evidence_ref` puede ser commit + gate, y
funciona: `ψ ⇐ M` referencia `RB-7` y es suficiente. Pero **cualquier arista
medida nueva** necesita algo que referenciar, y hoy lo único que existiría sería
un script y su stdout — que es exactamente cómo se perdió el piloto de 540.

> **Fijar la precedencia:** el ledger admite `evidence_ref` histórico por
> commit; **una medición nueva no entra al ledger sin bundle**. Así el bundle
> deja de ser paralelo y pasa a ser precondición del primer experimento
> developmental, que es justo el que viene.

### M7 · Falta el criterio de parada del propio programa

El plan dice cuándo el programa **empieza** a ser útil (§10) y no dice cuándo
una unidad está **terminada**. Con lo aprendido esta sesión, propondría el
mismo listón que ya se usa en las campañas:

> Una unidad cierra cuando existe un mutante que la hace fallar y ese mutante
> está en la suite. No cuando las pruebas están verdes.

Y una regla de honestidad que esta sesión justificó tres veces —la traza vacua,
el recuento de 22 campos, `EVSENS` por orden alfabético—:

> Antes de leer un resultado verde, comprobar que el comparador puede
> distinguir. Un hash sobre una lista de `None` iguala cualquier cosa.

---

## Parte III · Lo que NO cambia del plan

Suscribo sin matices el §11 entero, el §13 entero, y en particular tres:

* **no unificar passports y niveles** — sigo sin evidencia de que sean la misma
  clase de objeto, y forzarlos a una tabla convertiría una pregunta abierta en
  un esquema;
* **no elegir aún entre los cinco precursores de 1.5** — el grafo dice
  explícitamente que la evidencia no los ordena, y elegir sería reintroducir a
  mano justo lo que el analizador existe para evitar;
* **la lesión de ψ como primera prueba** — es la mejor idea operativa del plan,
  porque demuestra que el sistema puede derivar una pregunta que **no** es
  «adquirir otra habilidad», y porque su respuesta cierra una incógnita real.

---

## Orden que propongo

```
U0  congelar + dirección          HECHO
U1  ledger de cuatro dimensiones  con M2 (scope) y M3 (procedencia)
U2  CeilingProbe                  1.5 y 1.8
U3  tipos de acción               FAMILY_PROBE cierra el caso 1.8
U4  política de evidencia         reemplaza «nada medido» por «bajo el umbral»
M1  control negativo de empates   junto con U1, o U1 no es verificable
U5  Campaign Bundle               precondición de la primera medición nueva
```

Y el hito que declararía el programa vivo, que no es ninguno de esos: **la
primera arista que entre al ledger desde una campaña ejecutada por este ciclo**,
no importada del histórico. Hasta entonces el grafo describe lo que ya sabíamos.

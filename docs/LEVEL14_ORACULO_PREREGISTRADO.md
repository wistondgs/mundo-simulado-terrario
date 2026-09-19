# `LEVEL1.4-CONJUNCTIVE-BINDING-01` · oráculo preregistrado

**Sellado antes de existir el código.** Todo valor sale de aritmética exacta o de
enumeración; ninguno de una corrida.

Base `7ac43fb`, cierre implementado del Nivel 1.2. Rama
`experiment/level14-conjunctive-binding-01`, en árbol propio, donde
`terrario/level13/` **no existe en disco**.

Incorpora las seis correcciones de la auditoría previa
(`docs/LEVEL14_ENTREGABLE_PREVIO.md`), marcadas **C1**–**C6**.

---

## 0 · Genealogía y precondición

```
1.0 → 1.1 → 1.2 → 1.4        ·  el Nivel 1.3 queda fuera
K_1.4 = B + Q + H + ψ
```

Precondición: `LEVEL12_STATUS = VERIFIED` sobre la semilla de cada celda, antes
de congelar. Si no: `LEVEL12_PRECONDITION_NOT_VERIFIED` y la celda se excluye.

## 1 · Qué permite probar que hoy no podemos probar

La regla vigente exige justificar una integración nueva por lo que habilita, no
por su lugar en la serie. La respuesta aquí es precisa:

> **Es el primer experimento del linaje en el que los atributos presentes son
> idénticos entre condiciones y sólo cambia la relación entre ellos.**

1.0 variaba `o`, 1.1 variaba `g`, 1.2 variaba `s`, 1.3 variaba la historia. Los
cuatro miden la respuesta a un **atributo**. Aquí los conjuntos marginales
`{g₁,g₂}` y `{s₁,s₂}` son los mismos en las dos condiciones y lo único que
difiere es qué va con qué. Ningún nivel anterior podía plantear esa pregunta.

**Y no es identidad de objeto.** Lo que persiste entre ensayos es la ligadura
`x ↔ ψ(x)` --un **canal**--, no la ligadura a un referente. Analogía exacta: dos
frecuencias de radio que se sabe que llevan la misma emisión. Saber cuáles se
emparejan no dice nada de qué se emite.

## 2 · Lo que 1.2 entrega de verdad

El Nivel 1.2 **no** da `D ∈ {NEAR,FAR}`. Da `s ∈ {S₀…S₃}` y `H(s) = P(N|s)`. El
binder recibe `(g, s)` y **nunca** `D*`, que sigue existiendo sólo para el
experimentador.

## 3 · Identificabilidad · por qué una referencia no sirve

Con dos direcciones `{g₁,g₂}` y dos evidencias `{s₁,s₂}`, los mundos

```
W_A: (g₁,s₁),(g₂,s₂)        W_B: (g₁,s₂),(g₂,s₁)
```

producen **marginales idénticos**. Con prior equiprobable,
`P(W_A|O) = P(W_B|O) = ½`, luego ningún algoritmo supera `0.5` sin evidencia de
co-pertenencia. **Es una limitación informacional, no algorítmica.**

Con una sola referencia la tarea se resuelve por cardinalidad y cualquier
arquitectura que transporte las dos variables parecería competente:
`BINDING_CONSTRUCT_NOT_FALSIFIABLE`.

## 4 · Portadores

Dos alfabetos opacos y **tipos disjuntos**, `Enum` con valores string —
nunca `IntEnum`, y sin ordinal compartido:

```
X = {X0, X1, X2, X3}     canal direccional
Y = {Y0, Y1, Y2, Y3}     canal de proximidad
ψ : X → Y                biyección experimental, NO entregada al agente
```

`X0` no significa `UP`; `Y2` no significa `NEAR`. No existe `object_id`,
`entity_id`, `reference_id` ni `track_id` en ninguna interfaz del organismo.

## 5 · Banco de adquisición · 64 escenas

Para cada `x`, las 16 combinaciones `(g,s)`, siempre con `y = ψ(x)`.
`N_binding = 64`, enumerado, sin azar.

Balance **verificado en fracciones**:

```
P(G | X) = 1/4     EXACTO para los cuatro portadores
P(S | X) = 1/4     EXACTO
```

Por tanto el portador no puede cargar semántica de atributo.

## 6 · C1 · Banco de evaluación · enumerado y con balance demostrado

**Corrección.** La especificación fijaba el banco de adquisición con precisión y
dejaba el de evaluación sin definir. Ahí vivía el atajo: si el banco no enumerara
las dos asignaciones de sensores, un *index-binder* acertaría siempre y la
métrica no podría distinguirlo. Y `P(G|X) = P(G)` estaba probado sólo para la
adquisición.

```
banco = { (x₁,x₂) ordenados distintos }   ×   { (g₁,g₂) ordenados distintos }
                                          ×   { (sₐ,s_b) ordenados distintos }
      = 12 × 12 × 12 = 1728 escenas
```

con `y₁ = ψ(x₁)`, `y₂ = ψ(x₂)`, `sₐ` unida a `y₁` y `s_b` a `y₂`. Enumerar el par
de sensores **ordenado** es exactamente la paridad `A`/`B`: cada par de
portadores recibe cada orden `72` veces.

Balance verificado sobre este banco, en fracciones:

```
P(G | X) = 1/4     EXACTO para los cuatro portadores
P(S | Y) = 1/4     EXACTO
paridad de asignación de sensores por par de portadores:  exacta
```

## 7 · Mecanismo · lo único que puede cambiar

```
A_xy          matriz 4×4, prior 1 en las dieciséis celdas
C(y|x)        = A_xy / Σ_y' A_xy'
observe_single_reference(x, y)      → A_xy ← A_xy + 1
```

La firma **no acepta** cue, sensor, dirección, `NEAR/FAR` ni identificador: así no
puede reaprender niveles anteriores. Durante la adquisición de 1.4 sólo cambia
`A_xy`; `B`, `Q` y `H` quedan con huella idéntica antes y después.

Tras el banco nominal, por fila: celda correcta `1 + 16 = 17`, las otras tres `1`,
suma `20`.

```
C(ψ(x)|x)   = 17/20          C(y≠ψ(x)|x) = 1/20
```

## 8 · Inferencia de binding y valores sellados

```
L_A = C(y₁|x₁)·C(y₂|x₂)          L_B = C(y₂|x₁)·C(y₁|x₂)
P(A|O) = L_A / (L_A + L_B)
```

La inferencia **no lee `g` ni `s`**: es puramente de portadores. Con los valores
de §7, para cualquier par de portadores del banco:

```
P(binding correcto) = 289/290 = 0.996551724…        EXACTO
```

## 9 · C6 · Métrica primaria, definida sobre un banco simétrico

**Corrección.** `(P − 1)²` presupone que una de las dos asignaciones es la
verdadera. Sobre un banco con paridad `A`/`B` exacta --que §6 ahora garantiza--
coincide con el Brier; sin esa paridad sería un error cuadrático condicionado.
Se sella la simetría y se conserva el nombre.

```
BS_binding = E_banco [ (P(binding correcto) − 1)² ]

FULL_14        1/84100 = 1.1890606e-05        ORACLE            0
UNBOUND        0.25                            FROZEN_BINDER     0.25
SHUFFLED       0.25                            SINGLE_G/SINGLE_D 0.25
```

**Cuatro empates preregistrados en `0.25`.** No son hallazgos: son la misma
ausencia de canal por cuatro vías.

## 10 · Controles

```
FULL_14          A_xy adquirida sobre el banco de 64
UNBOUND          no recibe C(y|x); por simetría P(A)=P(B)=½. No inventa asociación
FROZEN_BINDER    la estructura existe, observe es no-op
SHUFFLED         cada x coocurre EXACTAMENTE 4 veces con cada y ⇒ A_xy = 5 ∀xy
                 ⇒ C(y|x) = 1/4 exacto ⇒ P = ½ ⇒ BS = 0.25, VARIANZA CERO
ORACLE           usa ψ; techo 0
```

**`SHUFFLED` no baraja registros completos.** Mover junto `(x,y)` conserva la
relación y el control empataría con el brazo que controla — fue el defecto del
Nivel 1.1. Aquí el balance exacto hace la independencia una identidad, no una
muestra.

## 11 · Readout conjuntivo · el discriminador funcional

```
ĥ_i  = Σ_b P(b|O)·H(s_{b(i)})
V(a) = Σ_i Q(g_i,a)·ĥ_i
```

`V` es diagnóstico: **no es recompensa y no es política motora nueva.** La
política sigue siendo la del Nivel 1.1 y la distancia sigue sin modificar la
acción, como 1.2 dejó cerrado.

Referencias analíticas con el oráculo sellado de 1.2
`H* = (1/11, 1/3, 2/3, 10/11)`, sobre el banco de §6:

```
MSE UNBOUND  = 0.06504438      promedia ambas proximidades
MSE FULL     = 3.0936686e-06   con P(correcto) = 289/290
```

**En ejecución real el readout se compara contra un `ORACLE-BINDER` que usa el
mismo `H` congelado de esa celda**, para no confundir calidad de 1.2 con calidad
de 1.4.

## 12 · C2 · Congelación del linaje · tres envoltorios, no dos

**Corrección.** `QualitativeDistanceModel.observe` existe
(`terrario/level12/proximity.py:45`) y `Level12Agent` publica `self.proximity`
(`terrario/level12/agent.py:32`). Envolver el agente dejaría
`core.proximity.observe(...)` al alcance de un descuido.

```
FrozenLevel12Core
  ├── FrozenFactoredBody        B   (existe en level11)
  ├── FrozenDirectional         Q   (se reescribe aquí)
  └── FrozenProximity           H   (NUEVO — nadie lo había construido)
```

Expone `predict_body`, `predict_orientation`, `predict_near`, `fingerprint`.
**Ninguna pieza expone `observe`**, y el contrato lo recorre por AST.

*Nota de proceso:* cada nivel ha congelado lo que heredó y dejado mutable lo que
añadía. De aquí en adelante, el nivel que **añade** un modelo entrega también su
envoltorio congelado.

## 13 · C3 · Las 24 permutaciones son contrato, no campaña

**Corrección medida:** las `24` permutaciones de `ψ` producen **un** valor
distinto de `C`, `P(binding)` y `BS_binding`. El binder tampoco lee `B`, `Q` ni
`H` durante la adquisición, así que `A_xy` es idéntica en todas las líneas base, y
el readout no depende del etiquetado de `ψ`.

Presentar `8 × 24 = 192` celdas como 192 comprobaciones sobreestimaría por un
factor de 24.

```
las 24 permutaciones  →  contrato parametrizado: «ψ no puede estar cableada»
la campaña            →  8 celdas, una por línea base 1.2
```

## 14 · C4 y C5 · La escena, y dónde puede esconderse el atajo

**C5 · cardinalidad.** `frozenset` colapsa duplicados: si los dos elementos
direccionales compartieran `(portador, cue)`, la escena tendría **una** referencia
en silencio — justo lo que §3 manda rechazar. Contrato en la construcción:
exactamente dos de cada, comprobado.

**C4 · el gate de orden es invacuable con `frozenset`.** Dos conjuntos con los
mismos elementos son el mismo objeto, se construyan como se construyan: el test
de invariancia al orden **no puede fallar**. Lo que sí tiene contenido es el
negativo, y para que exista hace falta un tipo de escena **ordenado** propio.

Medido sobre esa variante ordenada --`1728 × 2 × 2 = 6912` escenas, enumerando
ambos órdenes de listado de cada modalidad--:

```
acierto del index-binder = 1/2      EXACTO
```

El atajo de índice pasa de «imposible de expresar» a «medible y rechazable».

## 15 · Gates

| gate | criterio |
|---|---|
| **L14-0** linaje | huellas `B`, `Q`, `H` idénticas pre/post; 1.2 verificado antes de congelar |
| **L14-1** atributos | `Q` y `H` siguen dando sus capacidades heredadas |
| **L14-2** ambigüedad | `UNBOUND = 0.5`; la fixture de una referencia es rechazada |
| **L14-3** adquisición | `FULL = 1/84100`; `FROZEN`/`UNBOUND`/`SHUFFLED` `= 0.25` |
| **L14-4** marginales | `A`/`B` conservan los mismos conjuntos; paridad exacta (**C1**) |
| **L14-5** sensibilidad conjunta | cambiar sólo el binding mueve el readout `FULL` y no el `UNBOUND` |
| **L14-6/7** preservación | `Q` y `H` intactas |
| **L14-8** atajos | orden, índice, ordinal y portador correlacionado no resuelven (**C4**) |
| **L14-9** necesidad | la fixture *binding-irrelevant* es rechazada |
| **L14-10** sin identidad | `P(G\|X) = P(G)` y `P(S\|Y) = P(S)` en **los dos** bancos (**C1**) |
| **L14-11** pasividad | métricas read-only, enumeración, **cero RNG nuevo** |

**Ningún gate sin fixture negativa:** mutar el core heredado · quitar una
modalidad · una sola referencia · binder sin entrenar · shuffled exacto ·
marginales alterados · swap ignorado · index-binder sobre escena ordenada ·
portador correlacionado con dirección · binding-irrelevant · portador persistente
como `object_id` · métrica que escribe.

## 16 · Condiciones de parada

```
LEVEL12_PRECONDITION_NOT_VERIFIED   BINDING_CONSTRUCT_NOT_FALSIFIABLE
BINDING_NOT_NECESSARY               ATTRIBUTE_IDENTITY_LEAK
OBJECT_IDENTITY_INTRODUCED          BINDING_SHORTCUT_DETECTED
MARGINAL_CONTROL_FAILED             SHUFFLE_CONTROL_FAILED
BINDING_ACQUISITION_FAILED          PRIOR_LEVEL_MUTATED
MEASUREMENT_NOT_PASSIVE             BINDING_GATE_NOT_FALSIFIABLE
LEVEL13_DEPENDENCY_DETECTED
```

## 17 · Semillas y azar

```
100000011 … 100000018     reconstrucción 1.2 · disjuntas (verificado, con los +7)
```

**Cero RNG nuevo.** Adquisición enumerada (64), evaluación enumerada (1728),
permutaciones enumeradas (24), métricas cerradas. Se hereda sólo el azar que
reconstruye 1.2.

## 18 · Sin holdout de generalización

El binder aprende `X ↔ Y` y **no indexa `(g,s)`**: retirar conjunciones y
acertarlas después estaría garantizado por la arquitectura, y sería otra vez un
gate cuya respuesta conocemos. El contrafactual `A`/`B` es el discriminador
correcto.

## 19 · Afirmación máxima autorizada

> El Agente Nivel 1.4 adquirió una correspondencia conjuntiva que le permitió
> vincular una señal direccional y una evidencia de proximidad cualitativa como
> pertenecientes a la misma referencia momentánea, distinguiendo configuraciones
> con atributos marginales idénticos pero asociaciones diferentes, sin modificar
> sus adquisiciones sensorimotoras, direccionales ni de proximidad anteriores.

**Obligatorio junto a ella:**

> El mecanismo de binding y los portadores transitorios fueron suministrados por
> diseño. El experimento no demuestra identidad persistente de objetos ni que el
> agente inventara autónomamente un mecanismo general de binding.

**No autorizado:** objeto, identidad de objeto, entidad persistente, permanencia
del objeto, representación de escena general, atención, memoria relacional,
razonamiento relacional, navegación, selección de objetivos, concepto general de
«la misma cosa». Lo certificado es estrictamente **co-pertenencia conjuntiva
momentánea**.

## 20 · Qué clase de resultado sería

Los positivos son calculables antes de correr, y eso **no los vacía**: los
convierte en verificación de que la implementación realiza el algoritmo
especificado. La adquisición son `log₂(4!) = 4.585` bits — el contenido de `ψ`,
no el concepto de binding.

Y hay un límite que conviene escribir ahora: **una vez conocida `ψ`, el binding
es consulta de tabla, no inferencia.** Dos elementos, dos asignaciones, un argmax
sobre dos productos. Es binding en su tamaño mínimo no degenerado.

Lo genuinamente nuevo sigue siendo lo de §1: por primera vez podemos tener
exactamente los mismos atributos presentes y cambiar sólo la relación entre ellos.

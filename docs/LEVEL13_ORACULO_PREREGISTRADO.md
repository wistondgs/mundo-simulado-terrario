# `LEVEL1.3-ONE-STEP-REFERENCE-PERSISTENCE-01` · oráculo preregistrado

**Sellado antes de existir el código.** Todo valor de este documento se calcula en
cerrado; ninguno proviene de una corrida.

Base: `ef67ee5`, el cierre exacto del Nivel 1.1. Rama
`experiment/level13-one-step-reference-persistence-01`.

---

## 0 · Genealogía · 1.3 es hermano de 1.2, no su hijo

```
1.0 → 1.1 → 1.2      proximidad cualitativa
1.0 → 1.1 → 1.3      persistencia de un paso
```

`K_1.3 = K_1.0 + K_1.1 + K_mem`. **El Nivel 1.2 no participa.**

La base se eligió `ef67ee5` y no `3697c5f` aunque su árbol de código sea
idéntico: `3697c5f` pertenece documentalmente a la campaña 1.2, y aquí se
preserva también la genealogía experimental. En el worktree de 1.3
`terrario/level12/` **no existe en disco**, así que «1.3 no depende de 1.2» es
propiedad estructural y no aserción.

## 1 · Qué se adquiere, y qué no · dicho antes de medir

**El mecanismo de memoria lo suministra la arquitectura.** El organismo no
descubre que necesita memoria, ni cuándo escribir, ni qué guardar, ni cuánto
tiempo, ni cuándo olvidar. Todo eso son capacidades distintas.

Lo que 1.3 demuestra es más estrecho:

> Un estado persistente mínimo suministrado al organismo puede conservar durante
> un tick el contenido de una referencia direccional previamente percibida y
> permitir reutilizar después la semántica direccional ya adquirida en 1.1.

Es un **hito de capacidad temporal e integración**, no un experimento de
aprendizaje estadístico. **No hay `N_TRAIN`**: no existe adquisición paramétrica
nueva, ni dosis, ni cobertura, ni tolerancia que derivar. El nivel no tiene un
solo número estimado.

## 2 · Qué queda congelado

```
B(o,a) = P(movimiento realizable | o, a)                  Nivel 1.0
Q(g,a) = P(acción compatible con cue | g, a)              Nivel 1.1
J_1.1(o,g,a) = B(o,a)·Q(g,a)
```

Dos envoltorios **sin `observe`**, igual que en 1.1 y 1.2: el método que no
existe no se puede llamar por descuido.

## 3 · La estructura nueva

```
M_t ∈ { ∅, C0, C1, C2, C3 }
```

**La memoria guarda el token, no la dirección.** Está prohibido escribir `UP`,
`DOWN`, `LEFT`, `RIGHT`. La cadena causal correcta es

```
g_t → M_{t+1} → Q(M_{t+1}, a) → a_{t+1}
```

y **no** `g_t → Direction → M → a`. Si 1.3 guardara la dirección, estaría
suplantando la semántica que es el mecanismo del 1.1, y el nivel dejaría de
medir persistencia para medir otra cosa.

Capacidad informacional: cuatro cues equiprobables, `H(G) = log₂4 = 2 bits`, más
el estado de control. **Ésa es la escala exacta de la adquisición.**

## 4 · Máquina de estados · con las tres correcciones adjudicadas

```
EMPTY  ──write(c)──▶  HELD_0  ──tick──▶  HELD_1  ──tick──▶  EMPTY
   ▲                     │                  │
   └──────reset──────────┴──────────────────┘
```

```
W(∅, c)          = (c, 0)
W((c_i,k), c_j)  = (c_j, 0)          sobrescritura: gana el último cue válido
T(c, 0)          = (c, 1)
T(c, 1)          = ∅
R(c, 0)          = NONE              ← C2 ADJUDICADO
R(c, 1)          = c
R(∅)             = NONE
```

**`R(c,0) = NONE` es la corrección que hace falsable al nivel.** Si leer a edad
cero devolviera el cue, un arnés que **se saltara el `tick()`** pasaría L13-4 y
L13-5 igual de verde, y «persistencia a través de un paso» no quedaría probada en
ninguna parte. Con `NONE`, el tick omitido es detectable y tiene contrato propio
(§11, L13-13).

**`query` es pura.** Leer no borra ni modifica. Tras la consulta el slot sigue en
`HELD_1` hasta que el arnés llama a `reset()`. Sin esto, `F_M`, `R_history` y los
256 puntos de `D_π` no podrían leer el mismo estado: la segunda métrica
encontraría un slot vacío y **L13-11 caería contra L13-5 en la misma corrida**.

**`write` sólo acepta `CueToken`.** Cualquier otra cosa —`Direction`, `None`,
`NO_CUE`, un entero— es error de contrato. «No hay cue» se expresa **no llamando
a `write`**, nunca llamándolo con nada. Así `MEMORY_EARLY_ERASURE` deja de ser
expresable.

**Horizonte contenido:** `Δt_max = 1`. Una implementación que conservara el cue
tras dos ticks no es «mejor»: es `LEVEL13_SCOPE_EXPANSION`.

## 5 · Estructura del ensayo

```
PRESENT   t      recibe (o_present, g_t)   ·  write(g_t)   ·  devuelve None
DELAY            tick()                     ·  sin cue, sin acción, sin mundo
QUERY     t+1    recibe (o_query)           ·  peek() → ĝ  ·  NO recibe cue externo
RESET            reset()                    ·  única operación que borra
```

**En PRESENT no hay acción motora y no hay transición física.** Si el agente
actuara, el pasado quedaría escrito en el mundo —acción previa, desplazamiento,
bits de pared alterados— y 1.3 podría resolver la consulta leyendo el presente en
vez de recordando. No se añade una quinta acción `WAIT`/`NOOP`: eso alteraría el
cuerpo del Nivel 1.0.

## 6 · Banco crítico

```
o_present = (1, 0, 0, 0)        UP bloqueado · fijo · idéntico para las cuatro historias
o_query   = (0, 0, 0, 0)        las cuatro direcciones libres · fijo · idéntico
historias:  C0 · C1 · C2 · C3
```

Ambas observaciones están **verificadas alcanzables** en el mundo heredado, son
**independientes del cue** e **idénticas para las cuatro historias**. Por tanto,
exactamente y sin estimador:

```
I(G ; o_query)   = 0
I(G ; o_present) = 0
```

No «aproximadamente»: es una identidad del banco, porque las observaciones son
constantes.

**`o_present ≠ o_query` por adjudicación.** El cue debe sobrevivir no sólo al
tiempo lógico sino a un **cambio real de la entrada sensorial**. Un registro
indebidamente indexado por la observación fallaría aquí y pasaría si ambas
fueran iguales. No hay transición física entre ellas: son dos contextos
sensoriales del banco.

**Consecuencia para el claim:** «un tick temporal con cambio de entrada
sensorial», nunca «un paso motor del mundo».

## 7 · Resultados sellados · contratos de implementación, no descubrimientos

```
R_NO-MEMORY        = 1/4     EXACTO
R_SHUFFLED         = 1/4     EXACTO
R_FROZEN           = 1/4     EXACTO   (write es no-op ⇒ idéntico a NO-MEMORY)
R_TICK-OMITIDO     = 1/4     EXACTO   (R(c,0)=NONE ⇒ cae a body-only)
R_FULL             = R_PRESENT-CUE    identidad, no tolerancia
D_π                = 0                bit a bit sobre 16×4×4 = 256 puntos
I(G ; o_query)     = 0                identidad del banco
I(G ; M)           = 2 bits           si la fidelidad es 1
M tras dos ticks   = ∅
```

**El suelo `1/4` es inmune al umbral de detección de empates.** Para cualquier
política que ignore la historia,

```
R = Σ_g P(g)·P(a=f(g) | o_query) = ¼ Σ_a P(a | o_query) = ¼
```

porque `f` es biyectiva sobre las cuatro direcciones. Da igual que
`np.isclose` agrupe los cuatro scores como empate —`P = ¼` cada uno, `R = ¼`— o
que no agrupe ninguno —`P` masa puntual, `R = ¼`—. En el Nivel 1.1 hizo falta
`alignment_rate_expected` precisamente porque allí los empates sí movían el
número; **aquí no pueden**.

**`D_π = 0` es exacto por composición, no por tolerancia:** si `peek` devuelve
exactamente `g`, entonces `J_memory(o,g,a)` y `J_present(o,g,a)` son la misma
llamada con los mismos argumentos.

**Cuatro empates preregistrados.** `NO-MEMORY`, `FROZEN`, `SHUFFLED` y
`TICK-OMITIDO` valen `0.25` los cuatro. No son hallazgos y no se reportan como
contraste independiente: son la misma ausencia de canal por cuatro vías
distintas.

## 8 · Controles

```
FULL-1.3         registro de un paso activo
NO-MEMORY        sin persistencia; en QUERY sólo dispone de B(o,a)
PRESENT-CUE      el cue verdadero vuelve a estar presente en QUERY · CONTROL POSITIVO y techo
SHUFFLED-HISTORY tabla 4×4 exactamente balanceada: P(M=c_j | G=c_i) = ¼ ∀i,j
FROZEN-1.3       la arquitectura existe, write() es no-op
```

**`NO-MEMORY` no inventa un cue.** No usa token neutral ni orientación media: su
score es `B(o,a)` y nada más.

**`SHUFFLED` no baraja ensayos enteros.** Mover junto `(g, o, objetivo)` no
destruye ninguna relación —fue el defecto exacto del control del Nivel 1.1, que
acabó empatando con el brazo que controlaba—. Aquí se desacopla **sólo** la
historia almacenada del cue verdadero, y con la tabla `4×4` balanceada
`M ⊥ G` es **exacto**: `R = ¼` con **varianza cero**. Es estrictamente mejor que
el barajado de 1.1 y 1.2, que permutaban un flujo muestreado y arrastraban ruido.

**No hay brazo oráculo adicional.** El techo es `PRESENT-CUE`.

## 9 · Métricas

```
F_M        = P(M_{t+1} = G_t)                      fidelidad del contenido
R_history  = Σ_g ¼ · |{a ∈ argmax s(a)} ∩ {f(g)}| / |argmax s(a)|
D_π        = max_{o,g,a} |J_memory − J_present|
I(G;o_q)   = 0                                     identidad del banco
reset      = proporción de ensayos que empiezan EMPTY
fingerprint cuerpo/orientación antes y después
```

`R_history` promedia el desempate **en cerrado**. No se muestrea.

## 10 · Cero azar nuevo

```
1.3 no añade RNG
ninguna métrica consume RNG heredado
ninguna sonda usa act() con desempate aleatorio
la paridad se calcula sobre scores, no sobre una acción muestreada
el estado del RNG heredado, si el arnés lo tiene, es idéntico pre/post evaluación
```

Cierra el canal lateral que ya dio problemas en 1.1, donde muestrear el desempate
produjo `0.5000` frente a una esperanza de `0.4688` y habría levantado una
discrepancia falsa contra el propio oráculo.

El banco se **enumera**: 4 historias en el banco crítico, 16×4 = 64 combinaciones
en el banco de paridad, 16 pares en la tabla barajada. No hace falta azar para
ninguno.

## 11 · Gates

| gate | criterio |
|---|---|
| **L13-0** integridad de linaje | fingerprints cuerpo y orientación, `pre = post`, identidad exacta |
| **L13-1** observabilidad temporal | cue en PRESENT, ausente en QUERY; `query` no acepta `CueToken` |
| **L13-2** aislamiento de la presentación | `present` devuelve `None`; ningún camino de `present` a `act` |
| **L13-3** sin fuga del presente | `I(G ; o_query) = 0` en el banco crítico |
| **L13-4** retención de un paso | `write(g) → tick → peek = g`, exacto, para los cuatro cues |
| **L13-5** uso de la historia | `FULL = PRESENT-CUE`; `NO-MEMORY = 0.25` |
| **L13-6** uso del presente | con cue fijo, variar `o` mueve `B` y el score; `Q` idéntico |
| **L13-7** historia barajada | `M ⊥ G` ⇒ `0.25` exacto |
| **L13-8** preservación del 1.1 | `D_π = 0` y fingerprints intactos |
| **L13-9** reset y sobrescritura | ensayo nuevo empieza EMPTY; `A→B→tick→query = B`, sin mezcla |
| **L13-10** falsabilidad de atajos | las fixtures de fuga hacen caer sus gates |
| **L13-11** pasividad | medir no modifica memoria, core ni mundo; sin RNG nuevo |
| **L13-12** contención del horizonte | tras dos ticks, `M = ∅` |
| **L13-13** el tick es necesario | **omitir `tick()` ⇒ FULL no recupera el cue y cae a `0.25`** |

**L13-13 es el gate que certifica el constructo.** Sin él, lo demostrado sería
«hay un registro consultable», no «hay persistencia a través de un intervalo».

**Ningún gate se acepta si su único comportamiento posible es `PASS`.** Fixtures
negativas obligatorias:

```
banco con o_query codificando el cue uno a uno   → I = 2 bits  → HISTORY_LEAKAGE
arnés que permite acción en PRESENT              → PRESENTATION_MOTOR_LEAKAGE
memoria que guarda Direction en vez de CueToken  → SEMANTIC_MEMORY_LEAKAGE
memoria que nunca expira hasta reset             → MEMORY_HORIZON_EXCEEDED
arnés que no resetea entre ensayos               → MEMORY_RESET_VIOLATION
write(None) que vacía el slot                    → MEMORY_EARLY_ERASURE
tabla barajada mal construida                    → SHUFFLED_HISTORY_INVALID
métrica que consume la memoria                   → MEASUREMENT_NOT_PASSIVE
```

**L13-2 es auditoría de la superficie de API, no del mundo.** El banco se
enumera, así que en el camino nominal no hay `Grid`, ni `step`, ni posición que
mutar: su contenido real es la fixture negativa. Queda declarado aquí para que
nadie lo lea como prueba de que el mundo no se movió.

## 12 · Semillas

```
90000011 … 90000018        ocho reconstrucciones del baseline 1.1
```

Verificado disjunto de todo lo consumido o reservado, incluidos los
desplazamientos `+7` que usa la reconstrucción (`… 90000025`): `20260919…` (1.0),
`31415926` (quemada), `31415927…31415958` (**reservadas** para la reversión, no
ejecutadas), `70000019…70000033` (1.1), `80000011…80000018` (1.2).

Las ocho semillas **no son una muestra poblacional**. Verifican que el mecanismo
se reproduce sobre ocho cuerpos y orientaciones heredados distintos. Sin
bootstrap, sin intervalos, sin `p`-valores. Si una reconstrucción no supera el
contrato del Nivel 1.1, se excluye **antes** de ejecutar 1.3:
`LEVEL11_BASELINE_REGRESSION`.

## 13 · Condiciones de parada

```
LEVEL11_BASELINE_REGRESSION     LEVEL12_DEPENDENCY_DETECTED
EXTERNAL_CUE_PRESENT_AT_QUERY   PRESENTATION_MOTOR_LEAKAGE
HISTORY_LEAKAGE                 MEMORY_WRITE_FAILED
MEMORY_EARLY_ERASURE            MEMORY_RESET_VIOLATION
MEMORY_OVERWRITE_VIOLATION      MEMORY_HORIZON_EXCEEDED
SEMANTIC_MEMORY_LEAKAGE         SHUFFLED_HISTORY_INVALID
PREVIOUS_KNOWLEDGE_MUTATED      MEASUREMENT_NOT_PASSIVE
QUERY_INTERFACE_LEAKAGE         POLICY_PARITY_FAILED
LEVEL13_SCOPE_EXPANSION         RNG_COUPLING_DETECTED
```

## 14 · Afirmación máxima autorizada

> El Agente Nivel 1.3 conservó durante exactamente un tick información sobre una
> referencia direccional previamente percibida y utilizó esa información durante
> una consulta en la que la referencia ya no estaba disponible externamente y la
> entrada sensorial había cambiado, manteniendo intactas sus adquisiciones
> sensorimotoras y direccionales anteriores.

**Obligatorio junto a ella:**

> El mecanismo de persistencia fue suministrado por diseño. El experimento no
> demuestra que el agente inventara autónomamente memoria.

**Y la precisión temporal:** «un paso» significa **un tick del registro con
cambio de la entrada sensorial**, no un paso motor del mundo. El banco no
instancia mundo, no hay dinámica intermedia y no hay interferencia.

**No autorizado:** memoria de trabajo general, memoria episódica, memoria
espacial, representación del tiempo, conciencia temporal, continuidad de
objetivos, planificación, navegación, selección de recuerdos, almacenamiento
aprendido, olvido aprendido, consolidación, memoria multietapa.

## 15 · Qué puede fallar de verdad

Los valores positivos están determinados por la arquitectura. El contenido real
de la verificación es esta lista:

```
cue borrado antes de leer            NO_CUE tratado como escritura
cue transformado a Direction         mundo mutado en PRESENT
falta de reset entre ensayos         memoria persistiendo más de un paso
índice de ensayo filtrando           query usando el registro experimental
barajado mal construido              métrica consumiendo la memoria
orientación heredada mutada          acción previa filtrando historia
tick omitido y no detectado          RNG acoplado entre brazos
```

# El contrato de admisión contra cuatro casos reales

**2026-09-21** · prueba del criterio `ADMIT(E) ⟺ I_C ∧ I_G ∧ I_M ∧ C ∧ P ∧ A ∧ R`
antes de tocar schema.

---

## Veredicto

**El contrato representa los cuatro sin excepciones ad hoc, y clasifica los dos
casos obligatorios exactamente como se pidió.** Pero los cuatro juntos fuerzan
**una corrección de forma** —no una excepción— y dejan ver que **hoy ninguna
campaña de Terrario sería admisible**, por una razón que no es científica.

| caso | veredicto del contrato | qué lo decide |
|---|---|---|
| **1.6** positivo bien cerrado | **RECHAZO** | `A` · no existe archivo de artefactos. **Su ciencia está bien; su archivo no existe.** |
| **1.8** familia equivocada | **RECHAZO** contra el claim sellado · **ADMISIÓN** contra lo que sí midió | `I_M` · el instrumento implementa la familia degenerada |
| **fusión `F-9`** identidad equivocada | **RECHAZO** | `I_G` · `dict[str, bool]` no puede contradecir su propio nombre |
| **`no_interference`** declarado, no computado | **ADMISIÓN como `NOT_COMPUTED`** | `R` · el flag ya existe en código |

---

## La matriz

Medido sobre los artefactos, no sobre la documentación.

| | 1.6 | 1.8 | fusión `F-9` | `no_interference` |
|---|---|---|---|---|
| **I_C** claim resoluble | parcial · sellado y con commit (`0503874`), pero **3 enmiendas** y la evidencia no dice a cuál responde | parcial · **7 enmiendas propias** | **sí** · sellado, sin enmiendas | **NO** · el canon no define el criterio |
| **I_G** gate semántico | **sí** · `GateResult(name, certifies, passed, evidence)` | **sí** | **NO** · `dict[str, bool]` | no hay gate |
| **I_M** instrumento válido *para esa propiedad* | sí · y su reconciliación corrigió un umbral escrito a mano | **NO para el claim sellado** | sí | **NO** · no hay instrumento |
| **C** contexto | parcial · semillas y mundos son constantes de código, no registro | parcial | parcial | n/a |
| **P** provenance por contenido | **NO** · sólo commits | **NO** | **NO** | **sí** · CAS en Genesis |
| **A** artefactos verificables | **NO** | **NO** | **NO** | **sí** |
| **R** resultado clasificable | sí · `POSITIVO` con IC95 | **taxonomía sellada de seis valores — y el resultado real cayó fuera** | sí · binario | sí · `no_interference_computed: False` |

---

## 1 · El caso que más enseña es el que parecía fácil

1.6 es el positivo mejor cerrado del proyecto: 12/12 gates, 16/16 vidas,
`IC95 inferior +0,6805`, y **ya hizo su propia reconciliación de gates**
—`LEVEL16_RECONCILIACION_GATES.md`, con réplica celda por celda contra la tabla
committeada, tolerancia `5e-5`, cero diferencias—.

Y aun así el contrato lo rechaza, por una frase que escribieron sus propios
autores:

> **No existía archivo de artefactos.** La campaña era reproducible por
> determinismo, no por archivo, y las 16 huellas de trayectoria nunca se
> commitearon —el informe sólo guarda una—.

Verificado en las tres campañas: **ninguna commiteó datos crudos.** La
reproducibilidad es por re-ejecución determinista, no por lectura de lo
congelado.

Eso no es un defecto científico. Es exactamente la diferencia entre `A`
—artefactos verificables— y «se puede volver a correr». Un validador
independiente que re-ejecuta no está verificando la evidencia: está produciendo
otra, y confiando en que el mundo no cambió debajo.

**Ellos ya lo habían registrado como deuda de backlog.** El contrato no descubre
esto; lo convierte en bloqueante.

---

## 2 · `I_G` discrimina exactamente el linaje donde ocurrió el fallo

No es una coincidencia que valga la pena dejar escrita:

```
linaje A   1.2 · 1.3 · 1.4 · fusión      def gates(self) -> dict[str, bool]
linaje B   1.6 · 1.7 · 1.8               GateResult(name, certifies, passed, evidence)
```

La condición que habría hecho detectable la usurpación de `F-9` **ya está
implementada, en el linaje donde `F-9` no ocurrió.**

`certifies` es prosa, no un identificador versionado de propiedad — así que
satisface `I_G` a medias. Pero es prosa **por gate y en máquina**, y eso basta
para que «`F-9` pasividad» y «`F-9` el tick» no puedan ocupar la misma fila sin
contradecirse a la vista.

En el linaje A un gate es un par `nombre → bool`. Un par no puede desmentirse.

---

## 3 · 1.8 fuerza la única corrección de forma

El oráculo de 1.8 selló `Z_{t+1} = F(Z_t, A_t, O_{t+1})`. Lo implementado es
`Z_{t+1} = F(Z_t, A_t)` —verificado en código y con prueba hermética: mismas 400
acciones con tres secuencias de observación distintas dan **0/400 diferencias**;
mismas observaciones con acciones distintas, 297/400—.

Bajo el contrato tal como está escrito, `ADMIT(E)` es un veredicto **sobre la
ejecución**. Y entonces 1.8 se rechaza entero — porque su instrumento no mide la
propiedad que su claim nombra.

**Pero 1.8 produjo evidencia real y valiosa**: la tabla de `H(C | k)` que muestra
que dos pares (obs, acción) con 258 contextos resuelven el 91 % de la situación
mientras seis acciones solas con 4.096 resuelven el 48 %; el techo del 16 % de la
ganancia disponible; el lavado de `ΔL` de +0,107 a +0,058. Nada de eso es falso.
Lo que pasa es que **liga a otro claim**.

Rechazarlo entero perdería esa evidencia, y conservarla requeriría una excepción
ad hoc. La forma que lo evita no es una excepción, es una corrección:

> **La admisión es un veredicto sobre un par `(evidencia, claim)`, no sobre una
> ejecución.**
>
> `ADMIT(E, C) ⟺ I_C(C) ∧ I_G ∧ I_M(E, C) ∧ C ∧ P ∧ A ∧ R`

La misma ejecución queda **RECHAZADA** contra `C_sellado` y **ADMITIDA** contra
`C_real`. Y el rechazo es en sí un hecho que conviene guardar: es la única forma
de volver a detectar una familia equivocada sin releer el código.

Esto no añade concepto nuevo — es lo que `validate_bindings` ya hace para el
corpus, donde la unidad admitida es la **ligadura**, no el documento.

---

## 4 · Tres piezas que el contrato no tiene que inventar

**La revisión del claim ya se sabe comprobar.** `validate_bindings` rechaza con
`"binding claim revision mismatch"` cuando el claim citado no está en la revisión
declarada. `I_C` no necesita mecanismo nuevo: necesita apuntar a oráculos en vez
de a papers. Y hace falta: 1.6 recibió **3** enmiendas tras sellar y 1.8 **7**,
así que «el claim» sin revisión no identifica nada.

**La taxonomía del resultado ya existe, y es más rica que `R`.** 1.8 selló seis
valores —`INVÁLIDO`, `N-MUNDO`, `N-EXPERIENCIA`, `N-PLASTICIDAD`,
`NEGATIVO VERDADERO`, `POSITIVO`— y uno de ellos lleva anotado *«← evidencia
sobre S0, NO sobre C_18»*: la propia taxonomía ya contempla evidencia real que
liga a otra cosa.

El contrato **no debería inventar una taxonomía**: debería exigir que haya una
sellada y que el resultado caiga dentro. Y eso es un gate con dientes, porque el
resultado real de 1.8 —`BUDGET SELECTION = NONE`— **cayó fuera de las seis**. Se
detuvo antes de clasificar, correctamente, por la cláusula de su Enmienda 04 §6.

**`NOT_COMPUTED` ya está implementado, una vez.** En Genesis, junto al campo que
afirma lo contrario: `metadata={..., "no_interference_computed": False}`, con el
comentario *«El día que alguien compute de verdad la no-interferencia, esto pasa
a True»*. Tu condición 6 no pide una idea nueva; pide generalizar la que ese
fichero ya tuvo la honestidad de escribir.

---

## 5 · Lo que el propio 1.8 pidió

El cierre de su Ronda C termina así, y conviene leerlo como requisito y no como
comentario:

> «Se vuelve al **mecanismo** \[…] a preguntar qué subcapacidad falta:
> estabilidad de hipótesis, discriminación, control de complejidad, persistencia,
> o generación selectiva de experiencia. **Esa pregunta es exactamente la que el
> hipergrafo tiene que contestar**, y ahora llega con números en vez de con
> intuición.»

Y su `HYPERGRAPH_C18_PREREQUISITES.md` **ya es el payload del EvidenceGraph,
escrito a mano en prosa**: capacidad, requisitos observados con su evidencia
numérica, lo no requerido *medido y no asumido*, dependencias aún hipotéticas, y
lo que podría habilitar con su reserva explícita.

Le falta exactamente lo que el contrato pide: identidad versionada del claim,
identificadores de gate, versión de instrumento, hashes de contenido. El proyecto
**ya escribe el contenido**; lo escribe sin identidad verificable.

---

## 6 · Consecuencia operativa

Si el contrato entrara en vigor hoy, el EvidenceGraph seguiría vacío de campañas
—no por `I_G` ni por `I_M`, que dos linajes ya casi satisfacen, sino por `A` y
`P`: **nadie congela artefactos y nadie direcciona por contenido**.

Ése es el orden barato:

1. **`A` y `P`** son mecánicos y desbloquean las diez campañas a la vez. Genesis
   ya tiene CAS y cadena de hashes; no hay que diseñarlo, hay que usarlo.
2. **`I_G`** es portar `GateResult` del linaje B al A, más elevar `certifies` de
   prosa a identificador versionado.
3. **`I_C`** es apuntar `validate_bindings` a los oráculos.
4. **`R`** es exigir taxonomía sellada, que tres campañas ya traen.

---

## 7 · Lo que queda abierto

1. **¿Qué hace la puerta con `BUDGET SELECTION = NONE`?** Es un resultado real
   que cayó fuera de su propia taxonomía sellada. Rechazarlo castiga una regla de
   parada bien aplicada; admitirlo exige una casilla que la taxonomía no tiene.
   Es el único caso donde el contrato todavía no tiene respuesta limpia.
2. **¿Los 141 nodos actuales del grafo migran o se barren?** Son corridas de humo
   con `seed-42`; ninguno pasaría la puerta.
3. **¿Qué pasa con los cinco tests que hoy prohíben `add_evidence(`?** Una puerta
   legítima los rompe. La regla que los sustituye no es «nadie escribe» sino
   «ningún productor promociona lo suyo», y eso hay que escribirlo como contrato
   antes de que exista el primer escritor.

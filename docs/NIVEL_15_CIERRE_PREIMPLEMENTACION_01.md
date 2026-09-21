# Nivel 1.5 · recuperación forense y cierre preimplementación

**2026-09-21** · nada implementado · semillas confirmatorias intactas.

Autoridad documental respetada: **07 > 06 > 01–05**. No se resucita ninguna
afirmación supersedida.

---

## `READY_TO_PREREGISTER = NO`

Cinco condiciones de parada disparadas. Ninguna es un fracaso; todas son
información sobre qué falta cerrar.

```
PILOT_IMPLEMENTATION_NOT_RECOVERABLE
PILOT_CLASSIFIER_NOT_RECOVERABLE
CONSTANT_STEP_ALPHA_UNKNOWN
MULTIPLE_VARIABLES_CHANGED_UNDER_CAUSAL_CLAIM
EXPLORATION_SCHEDULE_UNKNOWN
```

No disparadas, y conviene decirlo: **no** se tocó ninguna semilla confirmatoria,
**no** se mutó ningún nivel previo, y la precondición genealógica **no** quedó
ambigua — quedó resuelta.

---

## La tabla

| ITEM | STATUS | EVIDENCIA | DÓNDE | CONSECUENCIA |
|---|---|---|---|---|
| organismo `B+Q+H+M+ψ` | **VERIFIED_CODE** | campaña corrida hoy, 10 gates | `organism-remembered-binding-01`, paquete `remembered`, `core.py` | precondición cerrada |
| un solo núcleo | **VERIFIED_CODE** | identidad de objeto, `RB-0` | misma campaña | no son dos suites compatibles |
| ψ sin M no aporta | **VERIFIED_CODE** | `mejora sólo ψ = 0.000000`, `RB-7` | misma campaña | dependencia medida |
| código del piloto de 540 | **UNKNOWN** | 0 commits en 28 ramas, 0 stashes, 0 tags, 0 colgantes | `git log --all -S` | irreproducible |
| el paquete `.zip` | **UNKNOWN** | no está en disco | `find /` | sólo queda su descomprimido |
| α del paso constante | **UNKNOWN** | el documento lo declara ausente | `LEVEL15_06:206` | hay que **elegirlo**, no recuperarlo |
| regla vieja (media corrida) | **REPORTED_ONLY** | nombrada, no especificada | `LEVEL15_06:204` | sin ecuación |
| regla nueva (paso constante) | **REPORTED_ONLY** | nombrada, no especificada | `LEVEL15_06:36` | sin ecuación ni α |
| schedule de exploración | **UNKNOWN** | `ε:0.30→0.02` es **propuesta**, y v3 sigue pidiendo fijarlo | `03:63` · `07:230` | no es registro del piloto |
| clasificador H1/H2/H3 | **UNKNOWN** | «congelar el clasificador posterior» sigue pendiente | `07:231` | **bloqueante**: es el endpoint primario |
| RNG del piloto | **VERIFIED_DOCUMENT** | `random.Random` de Python para estados/exploración | `07:136` | parcialmente recuperado |
| semillas del piloto | **VERIFIED_DOCUMENT** | `20260920`, `777`, `31337`, BURNED | `MANIFEST_V3:41` | usables para diseño |
| semillas confirmatorias | **VERIFIED_DOCUMENT** | `130000011…130000026`, 16, intactas | `MANIFEST_V3:39` | no tocadas |
| constructo `X=(G,P)`, `\|X\|=16`, `\|Z\|=4` | **VERIFIED_MATH** | tabla de pérdidas, ninguna estrategia domina | `01:30-65` | adjudicado, no rediseñar |
| regímenes y óptimos | **VERIFIED_MATH** | `R_G/R_P/R_J` con 4/5 y 1/10 | `01:68-71` | adjudicado |
| resultados del piloto | **REPORTED_ONLY** | `529/540 = 97,96 %` | `MANIFEST_V3:27` | ciertos, no verificables |

---

## A · Estado real de `B+Q+H+M+ψ`

```
PRECONDITION_BQHMΨ = MATERIALIZED
```

Y no por lectura. La campaña corre hoy:

```
REMEMBERED_BINDING_STATUS = VERIFIED

  un solo núcleo, por identidad de objeto   True      RB-0
  cinco huellas idénticas pre/post          True      RB-1
  memory.py byte-idéntico al blob           True      RB-2
  ψ intacta                                 True      RB-4
  C(ψ(x)|x) = 17/20 tras la fusión          True
  invariancia a los 12 pares de portadores  0.0e+00

  diez gates, todos PASA
```

`rama` `experiment/organism-fusion-remembered-binding-01` · `worktree`
`/home/wis/organism-remembered-binding-01` · `HEAD 02d5c43`.

`B`, `Q` y `H` del núcleo congelado de 1.4; **ψ se readquiere** con su banco
determinista de 64 escenas y se congela allí —«nadie había construido un
envoltorio para el binder, porque el nivel que lo creó no lo necesitaba»—; `M`
no tiene parámetros. Se reúnen procedimientos, no artefactos.

**Tu sospecha era correcta en su premisa y falsa en su conclusión.** Es cierto
que 1.4 vive en una rama sin 1.3; lo que ese árbol hizo fue **readquirir ψ**
sobre el núcleo que sí tiene M, en vez de importar el binder entrenado. Por eso
existe un solo organismo y no dos suites.

**Requisito genealógico vs funcional**, separados como pediste:

* **genealógico**: satisfecho. El linaje llega íntegro y verificado.
* **funcional para 1.5**: `M` es **necesaria** —el canal temporal ES una
  retención—; `ψ` es **dudosa**. El constructo de 1.5 es `X=(G,P)` con
  `|X|=16`, que es exactamente el espacio del binding, así que ψ podría ser
  constitutiva o podría ser sólo el generador del espacio.

**No lo adjudico yo.** Es una pregunta para vos, y está abajo.

---

## B · El piloto de 540 · dónde está

```
PILOT_IMPLEMENTATION_NOT_RECOVERABLE
```

Barrido completo: `git log --all -S` sobre 28 ramas, 0 stashes, 0 tags, 0
commits colgantes, reflog de 719 entradas, y búsqueda de `.ipynb` y de cualquier
fichero `level15` en el disco.

**Los únicos dos commits que mencionan `20260920` son mi auditoría de hoy y el
congelado.** Y el asunto de ese congelado lo dice todo:

> `02d5c43` — **«Freeze Level 1.5 with the decisions that only lived in the
> conversation»**

El piloto corrió donde nunca entró al repositorio. El `.zip` tampoco está en
disco; sólo queda su contenido descomprimido en `docs/level15_congelado/`.

---

## C·D·J · Las dos dinámicas, y por qué no se puede atribuir causa

Ninguna de las dos está especificada: la vieja se nombra «regla de media
corrida» y la nueva «paso constante», sin ecuación en ningún documento.

Y **no cambió una sola variable**:

| | piloto antiguo | piloto de paso constante |
|---|---|---|
| regla de actualización | media corrida | paso constante |
| presupuestos | 20k · 100k · **400k** | **10k** · 20k · 100k |
| repeticiones | 40 por régimen | 20 por celda × 3 semillas |
| semillas | **no registradas** | `20260920` · `777` · `31337` |
| α | no registrado | no registrado |

```
MULTIPLE_VARIABLES_CHANGED_UNDER_CAUSAL_CLAIM
```

**Corrijo aquí mi propia auditoría de esta mañana**, que repitió la afirmación
del documento —«cambiando sólo la regla»— sin comprobarla.

Lo que el contraste **sí** permite escribir: a presupuesto **compartido de
100k**, las tasas pasan de `78 % · 70 % · 78 %` a `60/60 · 59/60 · 60/60`. El
salto es grande y va en una dirección. Lo que **no** permite: llamarlo efecto
del paso constante, porque el piloto viejo no tiene semillas registradas y su
estructura de repetición era otra.

**Consecuencia para el hallazgo central de 1.5** —que los 21 fallos atribuidos a
barreras de coordinación eran del optimizador—: sigue siendo la lectura más
razonable y **deja de ser una conclusión sostenida**. La retirada de esos 21
fallos como propiedad del problema es correcta y suficiente por sí sola; la
atribución positiva al paso constante, no.

---

## E·F·G · α, exploración y clasificador

```
CONSTANT_STEP_ALPHA = UNKNOWN
EXPLORATION_SCHEDULE = UNKNOWN
PILOT_CLASSIFIER_NOT_RECOVERABLE
```

**α** · agotadas las tres prioridades: no está en código (no hay), no está en
logs (no hay), y el propio documento que superó al piloto declara que no consta.
No elijo `0.1` ni nada «razonable».

**Exploración** · `ε:0.30→0.02` aparece como **«programa principal propuesto»** y
el propio documento aclara que **«es una elección de diseño, no una derivación
matemática»**. El v3 sigue listando «fijar el programa exacto de exploración»
como pendiente. Convertir esa propuesta en hecho del piloto sería exactamente lo
que prohibiste.

**Clasificador** · el más grave, porque **es el endpoint primario**. Está
descrito por lo que debe ser —«invariante a relabeling de mensajes», y «el
learner nunca ve el clasificador»— y nunca especificado. V3 lo mantiene en la
lista de congelados pendientes.

**Consecuencia directa: `529/540` no es una tasa reproducible.** Es un resultado
reportado del piloto. Sin el clasificador no se sabe siquiera si ese número
depende de su definición.

---

## H·I · Variantes de `J` y RNG

**Variantes** · aquí hay una confusión de nomenclatura que conviene deshacer.
`R_J` **no es una variante de un objetivo `J`**: es el tercer régimen
estacionario, aquel donde `Q_J` tiene probabilidad 4/5. Las **nueve variantes**
son las de `H3 = (γ(G), π(P))`, biparticiones balanceadas.

Qué hizo el piloto con las nueve: **UNKNOWN**. Ningún documento lo dice.

Y la lección de 1.4 aplica literalmente: si se usan las nueve para verificar
invariancia, son **nueve contratos parametrizados, no nueve réplicas
científicas** —igual que las 24 permutaciones de ψ—.

**RNG** · parcialmente recuperado: `random.Random` de Python alimentado por el
entero de semilla, para estados y exploración (`07:136`). No consta el orden de
consumo, ni si sondas y adquisición comparten flujo.

---

## K · Fugas y atajos · estado hoy

Los tres contratos anti-fuga están **especificados** en los documentos y
**ninguno está implementado**, porque no hay código. Clasificación honesta:

| atajo | estado |
|---|---|
| decoder recibe sólo `(z,q)` | `NOT_YET_GUARDED` · especificado, sin código |
| un update por tabla y ensayo | `NOT_YET_GUARDED` · especificado |
| tablas READ ONLY entre emisión y respuesta | `NOT_YET_GUARDED` · especificado |
| consulta visible antes de la retención | `NOT_YET_GUARDED` |
| más de cuatro mensajes efectivos | `NOT_YET_GUARDED` |
| régimen como entrada del encoder/decoder | `NOT_YET_GUARDED` |
| memoria adicional aparte de `Z` | `NOT_YET_GUARDED` |
| replay del mismo ensayo | `NOT_YET_GUARDED` |
| clasificación disponible durante el aprendizaje | `NOT_YET_GUARDED` · declarado prohibido en `03:114` |

**Ninguno es `IMPOSSIBLE_BY_TYPE` todavía**, y ése es el listón que 1.3 y 1.4
alcanzaron: allí la fuga dejó de ser disciplina y pasó a ser un
`AttributeError`. 1.5 debería nacer igual.

---

## M·N · Qué es reproducible y qué es histórico

```
REPRODUCIBLE HOY
  la precondición B+Q+H+M+ψ y sus diez gates
  los óptimos analíticos  L*(R_G)=1/8, L*(R_P)=1/8, L*(R_J)=1/10
  el suelo de representación fija  L ≥ 1/3
  el selector ideal  7/60
  la tabla de pérdidas y que ninguna estrategia domina

SÓLO HISTÓRICO / REPORTADO
  529/540 y todas sus tasas por celda
  las tasas del piloto viejo  31/40 · 28/40 · 31/40
  la descomposición  9 óptimos locales + 21 barreras
  la banda 15–21 %  (ya retirada por sus propios autores)
  la selección del presupuesto de 100.000
```

---

## O · Bloqueantes, en orden de dependencia

1. **El clasificador.** Es el endpoint primario y no existe. Todo lo demás
   depende de él, porque sin clasificador «llegada a clase» no está definida.
2. **α y la ecuación de actualización.** Hay que **decidirlos**, y el preregistro
   debe decir que son decisión nueva y no continuidad del piloto.
3. **El schedule de exploración**, con su sensibilidad preregistrada antes de
   correr.
4. **Las nueve variantes de `H3`**: una fija o las nueve como contratos.
5. **Los tres contratos anti-fuga**, elevados de prosa a imposibilidad por tipo.

---

## Preguntas que no puedo resolver con código, artefactos ni matemática

Son tres, y son tuyas.

**1 · ¿Es ψ funcionalmente necesaria para 1.5, o sólo genealógicamente?**
El constructo es `X=(G,P)` con `|X|=16`, que es el espacio del binding. Si ψ es
constitutiva, 1.5 hereda cinco capacidades. Si sólo genera el espacio, 1.5
podría correr sobre `B+Q+H+M` y ψ sería andamiaje. La medida de hoy —**ψ sola
aporta cero y depende de M**— es compatible con ambas lecturas.

**2 · α: ¿se elige por campaña de diseño o se declara por fiat?**
Puedo diseñar una campaña sobre las tres semillas quemadas que seleccione α
respondiendo **una** pregunta y congelando las alternativas antes de correr. Eso
cuesta tiempo. La alternativa es fijarlo por decisión declarada. Las dos son
defendibles; la que no lo es, es presentarlo como recuperado.

**3 · ¿Se rehace el piloto o se preregistra sobre lo que hay?**
Con clasificador y α nuevos, el piloto viejo no es línea base. Rehacerlo sobre
semillas quemadas daría una base verificable; no rehacerlo significa preregistrar
sin expectativa cuantitativa, lo cual es legítimo y más honesto que heredar una
banda que no se puede reproducir.

---

## Lo que no hice

No creé `terrario/level15/`, ni scripts, ni tests. No toqué ningún nivel previo.
No ejecuté ninguna semilla confirmatoria. No elegí α. No investigué literatura
externa —ése es el paso siguiente y sólo sobre los huecos que quedan arriba—. Y
1.5 sigue congelado: su condición de descongelación, escrita por sus autores,
no se ha cumplido.

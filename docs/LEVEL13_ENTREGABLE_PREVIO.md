# Nivel 1.3 · entregable previo a implementar

Auditoría de la especificación `LEVEL1.3-ONE-STEP-REFERENCE-PERSISTENCE-01`
contra el repositorio. Estado inspeccionado: `experiment/level1-reversal-plasticity-01`,
HEAD `7ac43fb`, árbol limpio.

> **VEREDICTO: NO IMPLEMENTAR TODAVÍA.**
> Cinco hallazgos. Dos son contradicciones internas del texto y bloquean; uno es
> una definición ausente que decide si el nivel es falsable; dos son decisiones
> tuyas. Ninguno obliga a cambiar la capacidad.
>
> Acertaste en tus tres predicciones. Las dos que faltaban son C2 y C4.

---

# A · Hallazgos

## C1 · §7 y §10 contradicen a §30 y §31 · BLOQUEANTE

La especificación dice las dos cosas sobre si consultar borra:

| dice | dónde |
|---|---|
| «Después de: **consulta**; reset explícito; segundo tick… la memoria vuelve a EMPTY» | §7 |
| «Después de la consulta: `M ← ∅`» | §10, QUERY |
| «`query()`: sólo lee; **no resetea**; no escribe» · «`reset()`: **única** operación que borra» | §30 |
| «`query()` debe ser read-only… permite medirla **sin consumirla**… la evaluación puede ser pasiva» | §31 |

**No es estilo: revienta en ejecución.** §44 pide seis métricas y al menos dos
leen la memoria — `F_M` (fidelidad del contenido) y `R_history`. Si la consulta
borra, la segunda métrica lee un slot vacío y **L13-11 (pasividad) cae contra
L13-5 en la misma corrida**. Y `D_π` sobre 64 casos necesita leer 64 veces.

**Resolución propuesta: sobrevive §30/§31**, que además traen la razón escrita.
La cláusula «consulta» de §7 y el `M ← ∅` de §10 pasan a ser *«el arnés llama a
`reset()` después de la consulta»*, que es exactamente lo que §26 ya exige con su
`assert M = EMPTY` antes de cada PRESENT.

Elijo la mitad que tú escribiste con justificación, no una tercera opción. Pero
es tu texto el que se corrige, así que lo adjudicas tú.

## C2 · `R(c,0)` no está definida, y decide si el nivel es falsable · BLOQUEANTE

§8 define `W`, `T`, `R(c,1)` y `R(∅)`. **No define qué devuelve leer a edad 0**,
es decir antes del tick. §7 lo insinúa —«HELD_1: ha transcurrido exactamente un
tick **y el contenido puede consultarse**»— pero no lo dice.

**Por qué importa más de lo que parece.** Si `peek` a edad 0 devuelve el cue,
entonces un arnés que **se salte el `tick()`** pasa L13-4 y pasa L13-5 igual de
verde. Y entonces «persistencia a través de un paso» no queda probada en ninguna
parte: el nivel entero se sostiene sobre que el paso haya transcurrido.

```
R(c, 0) = NONE          ← hace detectable un tick omitido
R(c, 0) = c             ← el gate de retención no puede distinguir
```

**Propongo `R(c,0) = NONE`.** Verificado compatible con todas tus secuencias:
§27 (`A → B → tick → query = B`: edades 0,0,1 ✓) y §28 (`A → tick → tick → query
= NONE`: 0,1,expirado ✓).

## C3 · §29 no dice qué hace `write` con una no-entrada · tu predicción nº 1

§29 establece que `NO_CUE` es ausencia y no un token. Pero nada dice qué ocurre
si alguien llama `write(None)`. Tres comportamientos posibles, y uno de ellos es
el defecto que tú mismo anticipaste:

```
write(None) → lanza            el slot no se puede vaciar por accidente
write(None) → no-op            silencioso; un fallo del arnés queda invisible
write(None) → borra            MEMORY_EARLY_ERASURE, que está en tu §54
```

**Propongo que `write` lance ante cualquier cosa que no sea `CueToken`.** «No hay
cue» se expresa **no llamando a `write`**, nunca llamándolo con nada. Así el
borrado temprano deja de ser expresable, igual que `FrozenFactoredBody` no puede
mutar porque el método no existe.

## C4 · L13-2 es vacío en el camino nominal

§39 y §40 deciden que el banco crítico se **enumera** y que 1.3 **no añade RNG**.
Consecuencia: en el experimento nominal **no se instancia ningún mundo**, no hay
`Grid`, no hay `step`, no hay posición.

Entonces L13-2 (PRESENTATION ISOLATION: «no acción, no movimiento, no world
mutation») vigila un arnés que el experimento nominal nunca usa. Su enunciado
—§46: «world digest cambiado; posición cambiada»— se refiere a objetos que no
existen.

No está mal, pero hay que declarar qué es: **auditoría de la superficie de API**,
no del mundo. Y entonces su único contenido real es la fixture negativa. Es la
misma forma que L12-5 y L12-6 en el nivel anterior, donde ya acordamos que un
gate que sólo puede aprobar no es un gate.

Concreto: `Level13Agent.present()` devuelve `None` y **no existe ningún camino
desde `present` a `act`**, comprobado por firma; más la fixture del arnés
defectuoso.

## C5 · §13 fija `o_query` pero no dice nada de `o_present` · decisión tuya

El banco crítico fija `o_{t+1} = o°` en los cuatro casos. **No dice qué
observación se presenta en `t`.** Si `o_present = o_query = o°`, entonces entre
PRESENT y QUERY no cambia absolutamente nada salvo el tick, y un registro
indebidamente indexado por la observación pasaría el banco sin que nadie lo
notara.

Hacerlos distintos **no añade ninguna capacidad** —la memoria sigue guardando un
token y nada más— y cierra ese agujero. Lo dejo como decisión porque toca el
banco, que es parte del diseño.

---

# B · Verificaciones contra el repositorio

## Tu predicción nº 3 · el branching, con un matiz a tu favor

```
3697c5f  = SÓLO documentos (handoff + entregable + oráculo 1.2), 1442 líneas, cero código
git diff --stat ef67ee5 3697c5f -- terrario tests scripts   →   VACÍO
7ac43fb  = sólo ficheros NUEVOS: terrario/level12/, scripts/level12_*, tests/test_level12_*
```

Tienes razón en el fondo: partir de `7ac43fb` metería `terrario/level12/` en el
disco del worktree de 1.3, y entonces «no depende de 1.2» sería una aserción en
vez de una propiedad estructural.

El matiz: **el árbol de código en `ef67ee5` y en `3697c5f` es idéntico**, así que
`3697c5f` conserva el handoff y el oráculo 1.2 en disco sin un solo byte de
código de 1.2. Si prefieres tener el handoff a mano en el worktree nuevo, sale
gratis. Si prefieres la procedencia más limpia, `ef67ee5` es literalmente el
commit que el handoff nombra como cierre de 1.1. **Me inclino por `ef67ee5`,
como especificaste.**

Worktrees existentes, ninguno colisiona:

```
/home/wis/mundo simulado terrario          experiment/cognitive-live-observatory-01
/home/wis/causal-bench-01                  experiment/level1-reversal-plasticity-01
/home/wis/exp-foraging-01                  exp/adaptive-foraging-01
/home/wis/ocf-g3-close                     ocf/g3-close
…/.claude/worktrees/sweet-dirac-968e1e     experiment/agent-level1-copy-experienced-01   ← WIP ajeno, no se toca
```

## Tu predicción nº 2 · fuga indirecta de historia · enumerada y cerrada

Barrido de todos los canales por los que `g_t` podría alcanzar la consulta:

| canal | estado |
|---|---|
| `o_query` | neutralizado: constante `o°`. **Identidad del banco**, no estimación |
| acción en PRESENT | no existe: `present` devuelve `None` y no hay mundo que pisar |
| estado del mundo | no existe: el banco se enumera |
| índice de ensayo | `query(observation)` no lo recibe |
| **estado del RNG** | **no estaba en tu lista**: §40 lo cierra al no añadir RNG y exigir métricas cerradas |
| core heredado | sin vía de mutación, dos envoltorios sin `observe` |
| la memoria | el canal previsto |

El canal del RNG merece contrato propio: **ninguna métrica de 1.3 puede consumir
azar**. En 1.1 muestrear el desempate produjo `0.5000` frente a una esperanza de
`0.4688` y habría levantado una discrepancia falsa contra su propio oráculo.

## Constantes selladas · verificadas en cerrado

```
R_NO-MEMORY   = 1/4   EXACTO
R_SHUFFLED    = 1/4   EXACTO
o° = (0,0,0,0) alcanzable en el mundo heredado          True
las 16 observaciones alcanzables                        16/16
semillas 90000011…90000018 (+7 → …90000025)   colisión con lo usado: NINGUNA
```

Tu derivación de §16 es correcta **y más fuerte de lo que dice**. Como
`R = ¼ Σ_a P(a\|o°) = ¼` sea cual sea la forma de `P(·\|o°)`, el suelo no se mueve
ni con empate perfecto ni con máximo único:

```
si np.isclose agrupa las cuatro   →  P = ¼ cada una  →  R = Σ_g ¼·¼ = ¼
si no agrupa ninguna              →  P = masa en d*  →  R = ¼·1      = ¼
```

**Es un suelo inmune al umbral de detección de empates.** En 1.1 hizo falta
`alignment_rate_expected` precisamente porque ahí sí importaba. Aquí no. Conviene
que eso quede escrito en el preregistro: ahorra una discusión futura.

---

# C · Lo que está bien y conviene no perder

**§24 · tu control barajado es mejor que los dos anteriores.** En 1.1 y en 1.2 el
barajado permutaba un flujo muestreado y arrastraba ruido de muestreo — en 1.2
tuve que corregir el informe porque preregistré `0.2504` sin su `sd = 0.0071`.
Aquí la tabla `4×4` exactamente balanceada da `M ⊥ G` **exacto**, y por tanto
`R = ¼` con varianza cero. Es una mejora metodológica real.

**§43 · rechazar el holdout de generalización es correcto**, y es la lección de
1.2 aplicada antes de tropezar: `J(o,g,a) = B(o,a)Q(g,a)` ya factoriza esas
entradas, retirar combinaciones no le quita nada a ningún factor y el gate
aprobaría por construcción.

**§42 · no hay `N_TRAIN`.** Esto elimina de golpe toda la clase de errores que
dominó 1.2: no hay dosis, no hay cobertura, no hay tolerancia que derivar, no hay
umbral que heredar mal. El nivel no tiene un solo número estimado.

**§25 · no barajar ensayos enteros** está bien visto y es exactamente el defecto
que delató el control de 1.1.

---

# D · El límite que conviene escribir antes, no después

El banco crítico no instancia mundo. No hay dinámica intermedia, no hay
interferencia, no transcurre tiempo del mundo. **«Un paso» significa, con
precisión, «una llamada a `tick()`».**

Eso no invalida nada y es coherente con tu §59. Pero tu §57 dice «durante
exactamente un paso», y conviene que el preregistro defina *paso* como **un tick
del registro**, no como un paso del mundo — o que alguien lo lea como algo que el
experimento no midió.

Si quisieras que significara lo segundo sin añadir capacidad, la vía barata es la
de C5: que `o_present ≠ o_query`. Entonces entre presentación y consulta la
entrada sensorial **sí** cambia, y la retención tiene que sobrevivir a ese cambio.
Sigue sin haber acción, sin mundo mutado y sin memoria multi-paso.

---

# E · Lo que necesito de ti para implementar

1. **C1** — ¿`query` es pura y sólo `reset()` borra? (recomiendo sí: es tu §30/§31)
2. **C2** — ¿`R(c,0) = NONE`? (recomiendo sí: sin ello un tick omitido es invisible)
3. **C3** — ¿`write` lanza ante todo lo que no sea `CueToken`? (recomiendo sí)
4. **C5** — ¿`o_present ≠ o_query` en el banco crítico? (recomiendo sí, coste cero)
5. **Base** — ¿`ef67ee5`, como especificaste? (recomiendo sí)

Con esas cinco, el orden de tu §60 es ejecutable tal cual, y el preregistro sale
en commit separado antes de una sola línea de código.

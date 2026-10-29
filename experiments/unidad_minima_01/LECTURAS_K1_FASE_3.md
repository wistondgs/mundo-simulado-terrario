# Lecturas K1 de la Fase 3 · cerradas · 28-oct-2026

**De:** Opus · **Pedidas por:** `CARTOGRAFIA_PREVIA_FASE_3.md` §4 (Fable), que las marcó K1 y pidió leerlas **antes** de la ficha. **Sólo lectura:** no se tocó ni una línea de Terrario, Genesis o RNE.

**Resultado en una línea:** de las tres, **la primera cambia una premisa de la Fase 3**: la línea base de recuperación de D4 que §5 de la orientación pensaba heredar **no existe como número**, y no por falta de corridas sino porque el experimento **falló su propia puerta** por el mismo defecto que a nosotros nos mordió dos veces hoy.

---

## K1-1 · La línea base de recuperación de D4 · **NO EXISTE COMO DATO**

**Qué se leyó.** `runs/screening/D4T-1200steps-2seeds-3concepts.report.json`, `runs/noche/tamizado/D4T-1200steps-3seeds.report.json`, y las seis corridas `runs/h_adapt_001*` (1 GB en total), incluido `runs/h_adapt_001_pilot_clean/h_adapt_001_pilot_results.json`.

**Los dos tamizados de D4T no son evidencia, y lo dicen ellos mismos.** `classification: ENGINEERING_SANDBOX_NOT_EVIDENCE`, y su propia regla de lectura es buena: «un efecto menor que la dispersión entre semillas de un mismo brazo no es un hallazgo: es la semilla; mirá `larger_than_seed_spread` antes que `effect`». Son cribas de conceptos sobre catorce mallas, no curvas de recuperación.

**El experimento de adaptación sí existe, corrió entero, y su piloto FALLA su propia puerta.** `runs/h_adapt_001_pilot_clean`, hipótesis `H-ADAPT-001`, ocho variantes (A0_RANDOM, A1_REACTIVE, A2_GRU, A3_WORLD_MODEL, A4_ADVANCED y las tres ablaciones de A4) × cuatro semillas = **32 corridas, las 32 completadas y técnicamente válidas**:

| | |
|---|---|
| `pilot_diagnostic.status` | **FAIL** |
| puerta que falla | **`P3_sufficient_signal: false`** (las otras seis pasan) |
| corridas experimentalmente válidas | **13 de 32** |
| **`NOT_LEARNED_PRE_CHANGE`** | **19 de 32** |
| `FAILED_TO_RECOVER` | 11 |
| `RECOVERED` | **2** |
| variantes con alguna corrida válida | **1 de 8** (A3_WORLD_MODEL, 2 de 4) |
| `pre_change_competence` | **NaN**, `pre_change_status: INSUFFICIENT_EVIDENCE` |
| `pre_change_opportunities` | **1** |
| `recovery_latency` | `INSUFFICIENT_EVIDENCE` |

**El diagnóstico, y es el nuestro.** `pre_change_opportunities = 1`: **una sola oportunidad** de mostrar competencia antes de que el mundo cambie. Con una oportunidad no se puede establecer que el agente supiera la tarea, así que «recuperarse» no está definido y 19 de 32 corridas salen `NOT_LEARNED_PRE_CHANGE`. No es un fallo de los agentes: es que **la medida no podía ver lo que decía medir**, porque el control no llegó a despegar del suelo antes del tratamiento.

Eso es exactamente la familia de defectos que registré hoy —**E-50** y su ampliación: un nulo que no se interpreta, se descompone; y hay que **demostrar antes de correr que la celda puede producir el efecto que busca**—, en su forma de **suelo**. Terrario lo encontró antes que nosotros, lo clasificó bien (`NOT_LEARNED_PRE_CHANGE` es un nombre honesto) y dejó la puerta en FAIL en vez de publicar la media. Está bien hecho; lo que no hay es el número.

**Qué cambia en la Fase 3, concretamente:**
1. **§1 no puede «tomar la línea base de recuperación de D4′»**: no hay ninguna. La frase se sustituye por la condición que falta: para que exista, el protocolo necesita **muchas más oportunidades de competencia antes del cambio** (una no alcanza), y eso es un cambio de protocolo de Terrario, no de la Fase 3.
2. **Deja de ser cierto que nuestro ahogo y nuestro olvido por fracaso «probablemente tengan su medida en Terrario»** (§2.2 de la cartografía). No la tienen. M-c de la Fase 2 —curva plana 0,022 contra 1,000 de la fresca, 302 y 620 topes— es, por ahora, **la única medida de ese fenómeno en todo el programa**.
3. **Y hay una guarda que la Fase 3 hereda de este fallo, no de la nuestra:** el banco de la Fase 3 tiene que garantizar **competencia establecida antes del cambio**, con su número de oportunidades declarado. Nuestra puerta del mundo caro mide justo eso por el otro lado (cuánto tarda la fresca en identificar), así que las dos condiciones se comprueban con la misma medida: **el mundo tiene que ser caro, y la competencia tiene que estar establecida antes de tocarlo.**

## K1-2 · Los informes de fusión · **NO ESTÁN EN ESTE ÁRBOL**

`docs/ORGANISM_FUSION_HM_01_INFORME.md` y `_PREREGISTRADO.md` **no se han encontrado** en el checkout principal: lo único que hay de esa rama es `.git/worktrees/organism-fusion-hm-01`, el worktree registrado pero no presente aquí. Lo que la cartografía cita de ellos viene de los **mensajes de commit** y de la cabecera, que es lo que Fable declaró. Queda **abierto**, y para cerrarlo hace falta el worktree de esa rama o el fichero; **no es bloqueante** para la ficha, porque lo que la Fase 3 toma de ahí (la distinción regla / episodio / régimen y la interacción superaditiva sellada) ya está citado por commit con su hash.

## K1-3 · El MAPA de 1 240 líneas · **PENDIENTE DE WIS**

Sigue en la caché de claude.ai. Si Wis lo baja a `literatura/`, se lee entero. **No bloqueante.**

---

## Lecturas añadidas que sí cerré, y lo que confirman

**`docs/INVENTARIO_MUNDOS_01.md` §5 y §6, completos.** Confirman la cartografía y añaden dos cosas que le dan la razón a la Fase 3:

- **§6 confirma que la ultraestabilidad no está:** «**Reorganización de parámetros** · bloquea E9 · `viability_recovery_metric` **declara explícitamente que no lo mide**» → es «el segundo lazo», y es primitiva **faltante**, no capacidad existente. El salto de disposición de la Fase 3 es nuevo de verdad.
- **§6 confirma que la variable esencial de la Fase 3 es nueva también:** falta un «**operador de perturbación** · perturbación **de la variable esencial, no de la regla**», porque `ChangeScheduler` sólo intercambia reglas. O sea: el δ⁻ que baja V no existe en Terrario y está declarado como hueco. Nuestra V no reinventa nada.
- **§5 confirma lo que sí reinventaríamos:** `ChangeScheduler` con `changes: [{at_step, rules}]` ya es el cambio de mundo por fases, y `force_action` + `replay` ya da «la misma corriente grabada para varios gemelos» —que es justo lo que la pareja de la Fase 2 necesitaba y yo implementé a mano—. Si la Fase 3 corre en Terrario y no en el árbol de la unidad, esas dos se usan y no se escriben.

**Lo que queda por leer y no bloquea:** `_reflect_one` entero y `experience_lesson.schema.json` del `Teacher` de Genesis (la clase y su `reflect` ya están verificadas en la cartografía), los dos informes de fusión, y el MAPA.

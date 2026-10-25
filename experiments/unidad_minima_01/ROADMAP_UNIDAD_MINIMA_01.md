# Programa UNIDAD MÍNIMA · plano de trabajo para las siguientes iteraciones

**Fecha:** 2026-10-25 · **Redacta:** Claude (Fable 5.1), con el contexto de las sesiones del 24 y 25 de octubre · **Ejecuta:** Opus 5.5 · **Adjudica:** Wis.

**Norma cero, antes que todo lo demás:** *aquí no se inventa nada que ya esté inventado.* Ningún ítem de este plan se construye sin haber buscado antes en la literatura si existe, y lo que existe se integra como herramienta con su nivel de evidencia declarado. Rehacer lo hecho es absurdo; reinventarlo mal es peor. Cada ítem lleva por eso su **PRIOR-ART GATE** como primer paso obligatorio, con las búsquedas mínimas escritas y con lo que ya se verificó en estas sesiones para no repetirlo.

---

## 0 · Qué es esto y cómo leerlo

Estamos criando una **unidad computacional elemental**, determinista, que adquiere sus primeras distinciones por interacción bajo orientación externa, las retiene como palabras, las compone y, más adelante, se copia. El objetivo lejano (un ser que crece solo) **no es requisito del nacimiento**; se mide fase a fase y cada fase tiene un interruptor que puede cerrar el programa.

- **Lo que ya está hecho no se rehace**: §1 lo lista con su evidencia.
- **Cada fase pasa por el mismo ciclo** (§3): antecedentes → ficha de apertura → construir → medir con controles → veredicto → custodia.
- **Las fases 0 a 2 viven en Terrario.** Genesis y RNE no se tocan hasta que un disparador medido lo pida (§5).
- **Regla de cierre del programa:** una fase que falla su puerta se repara **una** vez y se vuelve a medir; si falla dos veces, se cierra el programa y se informa. Sin excepciones por entusiasmo.

---

## 1 · Estado de partida (hechos, con su evidencia)

| Hecho | Evidencia | Dónde |
|---|---|---|
| La unidad de dos letras construye una distinción que no está en su observación, predice lo nunca vivido, pierde la capacidad al lesionar la distinción y **no** inventa distinciones en un mundo con bit inerte. Determinista (hash idéntico en dos corridas, sin `random`). | COMPUTATIONALLY-REPRODUCED, 24-oct | `experiments/unidad_minima_01/unidad_minima_01.py` (este árbol, rama `experiment/unidad-minima-01`, base `master`=`bc05def`) |
| La misma unidad **vive paso a paso**: una hipótesis, predicción antes de actuar, refutación por lo leído, retroceso a la última decisión, estado nuevo sólo si no queda alternativa. Mundo aliasado: 4 errores en 1538 pasos, último en t=21; reactivo 272, último en t=1533; máquina final igual a la mínima calculada de cero. | COMPUTATIONALLY-REPRODUCED, 24-oct | `unidad_minima_02_incremental.py` · `artifacts/*.json` |
| El tercer elemento: sobre dos letras A (conmuta) y B (escribe 0), la palabra **BA** es un mapa constante (escribe 1) que ninguna letra sola realiza; relaciones AB=B, BB=B, AA=ε; el monoide aprendido (4 elementos) coincide con el del mundo. | COMPUTATIONALLY-REPRODUCED | tabla de palabras de 01 |
| `LEARNER-19-v1`: estado discreto adquirido de historias (obs, acción) bajo aliasing, con conteos Dirichlet; `CAPACIDAD_DEMOSTRADA`, 32 semillas, pares disjuntos; LI 95 % +0,51 predicción, +0,49 decisión tras lesión. | EMPIRICALLY-REPRODUCED (otra implementación) | `/home/wis/Aplicaciones/level18-predictive-state-01` · **sin commit** · preregistro `OPEN_AS_REPLICATION` |
| 1.8 falló por `Z_{t+1}=F(Z_t,A_t)` sin observación (`FAMILY_MISMATCH`); semillas `130000011–130000026` **reservadas, prohibido correrlas**; `level18/` no se toca. | PROJECT-VERIFIED | `docs/CONGELACION_HISTORICA_01.md`, cartografía §43.6 |
| Sistema cerrado (S,F): no hay selectividad no trivial; la causalidad exige entradas. | THEOREM-CHECKED (revisión ciega) | `~/Aplicaciones/primitivo_mapa_basal/DEFINICIONES_PRE_P4.md` §4.6 |
| E1: q depende de su complemento ⟺ θ_q no es congruencia (separable y mutuamente dependiente no caben en el mismo cociente). | THEOREM-CHECKED | `PRIOR_ART_INDIVIDUALIDAD_CAUSAL.md` §5.1 |
| Restauración de PRIMITIVO = decodificación por síndrome de {0000,1111}; mayoría de tres decide; 320/320 intervenciones, 84/84 shams. | PROJECT-VERIFIED (`CAUSAL_MECHANISM_IDENTIFIED`) | `~/Documentos/codex seccion terrario-primitivo/aomalia resueelta/` |
| Genesis/RNE: no existe tipo de destino que acepte un programa; `apply_parameter_intent` escribe dos escalares con ledger; `lab/genesis/retention` existe sin consumidor; los pesos neurales no se mueven. | K0 en cartografía vigente (gate «al día», 56 ficheros) | `RNE_v16-genesis-v2/docs/CARTOGRAFIA_GENESIS_01.md` §I–§IX; Atlas 05/06 |
| Sin GPU en la máquina. Nada de las fases 0–3 la necesita. | hecho | — |

**Entorno** · *corregido el 2026-10-25 contra el estado medido de la máquina; lo que decía antes era falso en los dos sentidos.* El intérprete es `/usr/bin/python3` = **3.14.4**, y los scripts de la unidad corren ahí sin nada más (sólo biblioteca estándar). El `.venv` del checkout principal se creó el 8-sep para **3.12.3** con `/usr/bin/python3.12`, intérprete que **ya no existe** en la máquina; su `python` es un enlace a `python3`, resuelve al 3.14 y deja invisibles sus paquetes cp312, así que **no tiene numpy ni torch**. Consecuencia medida: `scripts/cartografia_check.py` muere con `ModuleNotFoundError: numpy`; el gate de cartografía está caído. Para numpy, la receta viva es `PYTHONPATH=.deps-level19 python3` (numpy 2.5.4), que ya estaba en el árbol de L19 sin declarar. Reproducir hoy en 3.14 lo grabado ayer en 3.12 dio artefactos idénticos: es evidencia más fuerte del determinismo, no más débil.

---

## 2 · Normas de la casa (todas vigentes, todas con motivo medido)

1. **No inventar lo inventado.** PRIOR-ART GATE antes de construir, con veredicto (`SOLVED · PARTIALLY_SOLVED · MULTIPLE_NEAR_SOLUTIONS · OPEN_UNDER_CURRENT_SEARCH · INCOMPLETE_GATE`) y dos columnas: *qué dice la literatura* ≠ *qué tenemos comprobado*. Fuentes bloqueadas desde aquí: ScienceDirect, ACM, AMS, OUP, Springer, DBLP (anti-bot). Funcionan: arXiv (API, abs, pdf), Crossref API, GitHub API, bioRxiv/PLOS XML. Para un PDF bloqueado, pedir a Wis que lo baje.
2. **Nivel de evidencia en cada afirmación**: LITERATURE-CLAIM → SOURCE-VERIFIED → THEOREM-CHECKED → APPLICABILITY-CHECKED → COMPUTATIONALLY-REPRODUCED → EMPIRICALLY-REPRODUCED → INDEPENDENTLY-REPLICATED → PROJECT-VERIFIED. Leer un resumen no da SOURCE-VERIFIED para el contenido de un teorema.
3. **Ficha de apertura antes de escribir código** (12 puntos; veredictos `OPEN · OPEN_AS_REPLICATION · REVISE · DESCEND_OR_REFORMULATE · BLOCKED_* · CLOSED_BY_THEORY`). Sólo `OPEN`/`OPEN_AS_REPLICATION` autorizan código.
4. **Determinismo.** Prohibido `random` y cualquier semilla; dos corridas, un hash. Si se integra una biblioteca con aleatoriedad interna (p. ej. un solucionador SAT), se fija su semilla y versión y se **declara** como disposición suministrada.
5. **Tres capas declaradas** en cada experimento: *programado* (lo que escribimos), *disposición* (desempates, umbrales, políticas), *adquirido* (lo que la unidad construyó). Chollet cobra lo que no se declara.
6. **Contador de actividad por mecanismo.** Todo mecanismo trae el conteo de cuántas veces su componente distintivo se ejecutó. Contador en 0 ⇒ el experimento no probó lo que dice probar (resultado nulo por inactividad, no negativo).
7. **Curvas, no puntos.** El endpoint es la curva de adquisición (errores frente a experiencia) y el paso del último error; nunca un presupuesto elegido donde ya saturó. Medir **cobertura** (lo que el mundo expuso) aparte de **captura** (lo que la unidad tomó).
8. **El banco decide el signo.** Antes de fijar umbral, fijar la población de mundos: enumeración canónica, no una instancia a mano ni un muestreo aleatorio.
9. **Controles obligatorios**: fresco (mismo código, sin historia), lesionado (quitar sólo la distinción), reactivo (última observación + letra), y un mundo donde el control **debe** acertar (para que el test discrimine) y otro donde la distinción **no** debe inventarse.
10. **Un criterio que sólo falla tampoco es criterio**: todo gate se prueba con mutantes antes de correr lo real.
11. **Nombres descriptivos** para humanos; clave técnica en el código. Nada de A4/E2-A en informes.
12. **Custodia**: cada proyecto en su propio worktree desde el commit base; resultados a JSON con hashes de código; corridas largas escriben incrementalmente y **se reanudan** tras un corte (es requisito, no mejora). **No se commitea sin que Wis lo diga.** Entregable (.md) sólo al cerrar la fase, no por hallazgo. No usar *workflows* multiagente: gastan el límite de Wis.
13. **No tocar**: `level18/`, las semillas reservadas, RNE y Genesis (hasta §5), el checkout principal de Terrario (está en la rama de la ETP con ficheros sueltos; hay un `docs/LEVEL18_ANALISIS_CAUSA_RAIZ.md` **vacío** sin trackear que Wis debe decidir si borrar).

---

## 3 · El ciclo de cada ítem

```
PRIOR-ART GATE  →  ficha de apertura  →  construir (sólo el residuo)  →  medir con controles y banco
     ↓                                                                          ↓
  integrar lo que existe                                       veredicto PASS / FAIL / NULO-POR-INACTIVIDAD
                                                                                ↓
                                                  custodia (JSON + hash) · informe sólo al cerrar la fase
```

Entregable por ítem: `PRIOR_ART_<ítem>.md`, `APERTURA_<ítem>.md`, código, `artifacts/<ítem>.json`, y al cierre de fase un `CIERRE_FASE_<n>.md` con los números y las predicciones escritas antes de correr.

---

## 4 · Fases

### Fase 0 · Fijar y completar lo que ya corre · 1 sesión

**0.1 · Custodia.** Pedir a Wis autorización para commitear (a) este árbol con 01, 02 y este plano; (b) `LEARNER-19-v1` en su worktree (está untracked desde el 23-oct y el worktree figura como *prunable*). Sin eso, nada de lo que sigue tiene base.

**0.2 · Regeneración tras lesión** (completa el test de ayer). Sobre 02, añadir `lesionar(conservar_traza)`: borrar hipótesis y pila de decisiones, (a) conservando la vida retenida, (b) borrando también la vida. Seguir viviendo y contar pasos hasta volver a predecir sin error.
- Antecedente ya identificado: tres modos de reparación. (1) redundancia de estructura (síndrome, PRIMITIVO); (2) reconstrucción desde la experiencia retenida; (3) regeneración viviendo. El modo (1) va a la Fase 3.
- Búsqueda obligatoria, corta: *relearning after model damage*, *adaptive model learning evolving systems* (Damasceno, Mousavi, Simão 2019 — **de memoria, verificar**), para citar y no para construir.
- Predicciones escritas antes de correr: con traza → 0 pasos nuevos (se reconstruye en el repaso); sin traza → del orden de los 21 pasos originales. Falsador: con traza tarda tanto como sin traza.
- **Desenlace, 2026-10-25** (la predicción de arriba se deja como se escribió). Medido en t ∈ {64,128,256,512,1024}: **FAIL del enunciado** — el falsador se cumplió, con traza y sin traza gastaron exactamente los mismos pasos de vida nueva en 3 de los 5 momentos (7-7, 8-8, 14-14). La traza no evita los errores anteriores a la primera refutación: el valor de lo retenido depende de que algo **dispare** la relectura, y el brazo «con traza → 0 pasos» lo conseguía con un aviso de lesión suministrado desde fuera, que un organismo no recibe. **PASS de la reparación única**: un disparador interno (al ir a predecir, si la hipótesis está vacía y la memoria no, releerse) da 0 pasos de vida nueva en los cinco momentos, máquina idéntica y coste pagado entero en relectura. Detalle y números en `CIERRE_FASE_0.md`.

**0.3 · Elección por conveniencia bajo orientación externa.** Se le da a la unidad una meta desde fuera («que la próxima reacción a B sea 1»). La unidad recorre sus palabras (BFS en orden shortlex, determinista), predice con su máquina y ejecuta la más corta que cumple. Controles: unidad lesionada y reactivo (no pueden encontrar BA). Declarar: meta = programado; elección = adquirido; desempate = disposición.
- **No inventar**: la palabra que lleva la máquina a un estado fijo desde cualquier estado es una **palabra sincronizante / de reset** (Černý 1964; survey de Volkov 2008 — **de memoria, verificar**). BA es exactamente eso para la máquina aprendida. Planificar sobre un autómata aprendido es estándar; citar, no redescubrir.
- Puerta: la unidad con máquina cumple la meta en el mínimo de pasos en el mundo aliasado; los controles no; en el mundo visible el reactivo también cumple (discrimina).

**0.4 · Determinismo y entorno**: dejar escrito el comando exacto de cada corrida y su hash.

---

### Fase 1 · Escalar sin azar: sin maestro, sin reset, hasta 8 estados · 2–3 sesiones

**Pregunta.** ¿La unidad identifica la máquina mínima de mundos ocultos de 3 a 8 estados, viviendo una sola vida, de forma incremental y determinista, con coste que crece polinomialmente y no exponencialmente?

**1.1 · PRIOR-ART GATE (obligatorio; entregable `PRIOR_ART_ESCALADO_SIN_AZAR.md`).**
Ya verificado en estas sesiones (SOURCE-VERIFIED a nivel de resumen y metadatos de repo):
- **AALpy** (Python, push 2026-10-08, PyPI 1.6.2 ago-2026): L# por *apartness* (Vaandrager et al., arXiv 2107.05419); desde CAV 2025 *state-merging* pasivo rojo-azul generalizado (arXiv 2506.06333). → candidato principal a **integrar**.
- Λ*_M, Mealy simbólico (Irie–Waga–Suenaga, TCS 2026, DOI 10.1016/j.tcs.2026.116174; repo Java `SoftwareFoundationGroupAtKyotoU/learningsma`, sin movimiento desde 2025-09). → idea de «caracteres esenciales»; no integrar código.
- L# para autómatas separadores mínimos (CAV 2026, arXiv 2605.15294). → referencia.
- Active automata learning with advice (ECAI 2025, arXiv 2508.10535). → referencia.
- CSSR / estados causales (Shalizi–Klinkner, arXiv 1408.2025): escisión por fallo de predicción sobre un solo flujo. → la variante determinista es cercana a 02.
- Rivest–Schapire 1993 (homing sequences): aprender sin reset, con maestro y garantías probabilísticas. → antecedente, no solución.
- **No encontrado** en 2025–2026: aprendizaje activo de Mealy **sin reset**. Decir «no hemos encontrado», nunca «no existe».

Búsquedas obligatorias antes de construir (y qué cambiaría el plan):
- `exact DFA identification SAT` (Heule & Verwer 2010, **verificar**): si existe implementación Python viva (p. ej. sobre `python-sat`), **sustituye** al retroceso exhaustivo de 02 como referencia exacta; declarar semilla y versión fijas.
- `incremental regular inference` / `incremental RPNI` (Dupont 1996, **verificar**): si existe versión Mealy incremental, se integra como aprendiz vivo en vez de escribir el nuestro.
- `passive Mealy learning single trace state merging` y `AALpy RPNI Mealy`: si AALpy aprende Mealy de una traza única sin reset, la unidad **envuelve** AALpy y sólo añade lo que falta (vida continua, predicción antes de actuar, contadores).
- `learning Mealy machines without reset 2025 2026` (repetir; hoy vacío).
- `minimal consistent Mealy machine from a single word identifiability`: para la columna «máquina única».
Veredicto esperado: `MULTIPLE_NEAR_SOLUTIONS`. Residuo propio probable: la **vida continua con predicción previa, sin oráculo**, y la **medida de identificabilidad** paso a paso. Sólo eso se construye.

**1.2 · Banco poblacional (antes que el umbral).** Todas las dinámicas de dos letras sobre |S| = 3 (3⁶ = 729) y |S| = 4 (4⁸ = 65 536), en orden canónico; para |S| = 6 y 8, submuestra **determinista** (uno de cada k en orden canónico, k declarado). Salida observable **declarada**: el bit de cambio `o = [x' ≠ x]`, como en 01 (es disposición suministrada; registrar una segunda salida como variante sólo si el gate lo pide). Para cada sistema, calcular la máquina mínima verdadera por minimización estándar (Moore/Hopcroft; **no reinventar**) restringida a lo alcanzable, y marcar si es identificable desde la vida. La enumeración de BASELINE-01 (`~/Aplicaciones/primitivo_mapa_basal/baseline_01/`) ya recorrió estos sistemas; no copiar código de PRIMITIVO, re-enumerar (es `itertools.product`).

**1.3 · Mecanismo.** Según 1.1: (a) referencia exacta (SAT o retroceso) para saber qué es lo mínimo; (b) aprendiz vivo incremental (AALpy envuelto, o el nuestro si no hay nada incremental sin reset). Medidas por sistema: paso del último error, pasos repasados, estados finales frente a mínimos, identificabilidad (única / ≥2), predicciones sin ruta, veces que la distinción decidió.

**1.4 · Puerta.** Escribir antes de correr: (i) todo sistema cuya máquina mínima sea identificable desde la vida termina con la máquina mínima (salvo isomorfismo); (ii) la mediana del paso del último error frente a |S| ∈ {3,4,6,8} crece **subexponencialmente** (ajuste declarado antes: log-log, pendiente; el criterio numérico lo fija la ficha de apertura, no se hereda de 01); (iii) coste por paso acotado (repaso total ≤ múltiplo declarado de la vida). FAIL si crecimiento exponencial o no-convergencias sin explicación por no-identificabilidad. **Mutantes del gate**: un aprendiz que memoriza la traza (nunca falla, nunca generaliza) debe FALLAR en (i); un aprendiz sin observación (1.8) debe FALLAR.
- Corridas reanudables: resultados por sistema a JSONL; al reiniciar, saltar los hechos.

**Cierre.** `CIERRE_FASE_1.md` con curvas, tabla por |S|, y qué se integró de la literatura frente a qué se escribió.

---

### Fase 2 · Composición: que una distinción abarate la siguiente · 2–3 sesiones

**Pregunta.** En mundos donde la segunda tarea exige la distinción de la primera, ¿la unidad que conserva su máquina y sus palabras adquiere la segunda con menos experiencia que una fresca, y la lesionada vuelve a la fresca? Y en mundos donde la segunda tarea **no** la exige, ¿no hay diferencia? (sin esto el test no discrimina).

**2.1 · PRIOR-ART GATE (`PRIOR_ART_COMPOSICION.md`).**
Verificado: **Stitch** (Rust, MIT, push 2026-09-08; arXiv 2211.16605) compresión MDL de un corpus en abstracciones reutilizables; **Twitch** (arXiv 2603.06849) lo usa sobre pruebas; **Prospective Compression in Human Abstraction Learning** (arXiv 2605.09985, may-2026): elegir abstracciones por lo que ahorran en tareas **futuras**, no pasadas — es nuestra pregunta formulada por otros; **babble** (arXiv 2212.04596).
Buscar y verificar: *adaptive model checking* (Groce, Peled, Yannakakis 2002) y *Learning to Reuse: adaptive model learning for evolving systems* (Damasceno et al. 2019): reutilizar un autómata aprendido como punto de partida cuando el sistema cambia — **es exactamente «conservar»**; si hay implementación (AALpy tiene variantes), integrar. *Options / macro-actions* (Sutton, Precup, Singh 1999) sólo como referencia conceptual (marco estocástico). *Synchronizing words as macro-actions*. *Transfer in grammatical inference / lifelong automata learning*.

**2.2 · Diseño.** Familia de pares de mundos (W1, W2), enumerada canónicamente, en dos clases: **componible** (la máquina mínima de W2 contiene la partición de W1 como congruencia, así que la distinción de W1 es reutilizable) y **control no componible** (W2 no contiene la distinción de W1). Tres brazos con el **mismo código congelado**: conserva (máquina + palabras), fresco, conserva-lesionado. Endpoints: curva de adquisición en W2 y paso del último error; contadores: predicciones que usaron estados heredados, elecciones que usaron palabras heredadas. Las palabras heredadas se usan como **acciones compuestas** en exploración y elección (0.3).

**2.3 · Palabras como biblioteca.** Calcular de la máquina aprendida las palabras de efecto constante (reset) y las permutaciones; retenerlas con nombre (clave técnica + frase legible). A esta escala no hace falta Stitch; integrarlo cuando las palabras crezcan. Registrar si se cumple la condición de descongelación de 1.5: «experiencia útil generada > capacidad de conservarla» (sólo registrar; no actuar).

**2.4 · Puerta.** Escrita antes: en la clase componible, conserva < fresco con margen preregistrado sobre la curva, y lesionado ≈ fresco; en la clase control, conserva ≈ fresco. **FAIL de programa**: conserva ≈ fresco en la clase componible (las distinciones se suman y no se componen: hay aprendizaje, no desarrollo). Mutantes: un «conserva» que ignora lo heredado debe dar ≈ fresco.

**Cierre.** `CIERRE_FASE_2.md`. Si PASS, se activa el disparador de §5.1.

---

### Fase 3 · Mitosis: copia por palabras, con fidelidad · 3+ sesiones · **construcción aún no disponible**

**Pregunta.** ¿Puede un programa de palabras (no `copy()` de Python) reproducir la máquina adquirida en una segunda unidad, de modo que la copia pase el mismo futuro que la original, y sobreviva a un bit volteado gracias a tres copias y un restaurador por síndrome?

**3.1 · PRIOR-ART GATE (`PRIOR_ART_MITOSIS.md`).**
Verificado: **Computational Life** (BFF, arXiv 2406.19108): replicadores emergen de concatenar-ejecutar-separar pares; **Coevolution of self-replication and function** (Z80, arXiv 2607.09211, jul-2026); **BFF: simple explanations** (arXiv 2607.01483, jul-2026): disputa que la interacción sea lo decisivo (paseos de mutación hallan replicadores igual). Ambos usan mutación aleatoria; **la sopa sin azar no la hemos encontrado hecha**.
Propio, PROJECT-VERIFIED: la restauración de PRIMITIVO como **órgano de fidelidad** (mayoría de tres; límites medidos: 60 % del espacio en ciclos de 12 fuera de la región autorizada).
Verificar: von Neumann 1966 (descripción + constructor + copiador + control), Langton 1984, Byl 1989, Reggia et al. 1993 (replicadores mínimos en CA), teorema de recursión de Kleene / quines, códigos de repetición y Hamming.

**3.2 · Ficha de apertura con `DESCEND_OR_REFORMULATE` como salida posible.** Lo que hay que declarar como suministrado: el sustrato (cinta de bits donde vive la máquina codificada) y las letras que actúan sobre él. Si la construcción exige más de lo que la unidad tiene, descender y decirlo.

**3.3 · Puerta.** La copia hecha por palabras pasa el futuro de 01; con un bit volteado, la versión con tres copias + síndrome lo pasa y la de una copia no. **FAIL de programa** si no hay construcción determinista tras una reformulación.

---

### Fase 4 · Meiosis · diferida

Sólo cuando 3 pase. Antecedentes a verificar llegado el momento: unicidad de factorización bajo BFC (Bigelow–Burris / Chang–Jónsson–Tarski; ya THEOREM-CHECKED en PRIMITIVO), *crossover* en programación genética, coordenadas heredadas. Idea de partida (hipótesis propia, HIPÓTESIS): capa congruente de coordenadas (lo que se recombina) sobre dinámica no congruente (lo que vive).

---

## 5 · Integración con Genesis y RNE · por disparador, no por fecha

**5.1 · Cuando la Fase 2 pase**: la máquina adquirida es un **programa**, el tipo de cosa para el que `lab/genesis` fue diseñado (síntesis → auditoría → ranura de un solo uso → `PROMOTED`), pero su DSL es `int → int` de siete operadores. Primer trabajo en Genesis: **tipo de artefacto para una máquina de Mealy adquirida**, reutilizando ledger y cadena de promoción. Cierra el K2 del Atlas 05. Prior art antes: formatos de serialización de autómatas (AALpy `.dot`, AutomataLib), no inventar uno.

**5.2 · Cuando 5.1 esté**: **tipo de destino en RNE** para lo promovido (`MODEL_PARAMETER` está declarada y vacía; o clase nueva). Cierra el K2 del Atlas 06. Primera reingeniería del cuerpo, con la necesidad de la unidad como especificación; **no antes**.

**5.3 · Siempre**: lo que la unidad necesite del cuerpo se toma de lo ya medido (checkpoint de cuatro ranuras, `apply_parameter_intent`, gemelos, rollback) — la cartografía dice dónde. Lo que ninguna necesidad tire, no se toca.

---

## 6 · Lo que no se hace

- No se construye nada sin PRIOR-ART GATE y ficha de apertura.
- No se corren las semillas reservadas de 1.8; no se toca `level18/`.
- No se reescribe ningún resultado congelado (1.5, 1.8 siguen «anomalía sin resolver» para lo que fueron).
- No se reingenieriza RNE ni Genesis antes de §5.
- No se usa azar; no se usan workflows multiagente; no se commitea sin Wis.
- No se declara «nadie lo hizo»: sólo «no hemos encontrado».

---

## 7 · Decisiones pendientes de Wis

1. Autorizar los commits de 0.1 (este árbol y L19).
2. Si un solucionador SAT con semilla y versión fijas es admisible bajo «no estocástico» (recomiendo sí, declarado como disposición).
3. La salida observable del banco de la Fase 1 (recomiendo el bit de cambio, único, declarado).
4. Borrar o no el `docs/LEVEL18_ANALISIS_CAUSA_RAIZ.md` vacío del checkout principal.

---

## 8 · Fuentes

**Verificadas en estas sesiones** (resumen y metadatos; ninguna APPLICABILITY-CHECKED todavía):
AALpy — https://pypi.org/project/aalpy/ · https://arxiv.org/pdf/2506.06333 · L# https://arxiv.org/pdf/2107.05419 · L# separadores https://arxiv.org/pdf/2605.15294 · advice https://arxiv.org/pdf/2508.10535 · Λ*_M https://arxiv.org/html/2509.14694 · https://github.com/SoftwareFoundationGroupAtKyotoU/learningsma · CSSR https://arxiv.org/pdf/1408.2025 · Stitch https://arxiv.org/abs/2211.16605 · Twitch https://arxiv.org/pdf/2603.06849 · compresión prospectiva https://arxiv.org/pdf/2605.09985 · babble https://arxiv.org/pdf/2212.04596 · Popper https://arxiv.org/pdf/2104.14426 · SgpDec https://github.com/gap-packages/sgpdec · holonomía https://arxiv.org/pdf/1508.06345 · BFF https://arxiv.org/pdf/2406.19108 · Z80 https://arxiv.org/pdf/2607.09211 · BFF explicaciones https://arxiv.org/pdf/2607.01483 · ARC-AGI-3 https://arxiv.org/abs/2603.24621 · Tycho https://arxiv.org/pdf/2607.28287 · Crespo-Fernández et al. 2026 https://arxiv.org/abs/2602.17217 (texto completo leído).

**De memoria, verificar antes de citar en un entregable:** Rivest & Schapire 1993 (homing sequences) · Heule & Verwer 2010 (exact DFA identification, SAT) · Dupont 1996 (incremental regular inference) · Groce, Peled & Yannakakis 2002 (adaptive model checking) · Damasceno, Mousavi & Simão 2019 (learning to reuse) · Černý 1964 y Volkov 2008 (palabras sincronizantes) · Shalizi & Klinkner 2004 (CSSR, UAI) · von Neumann 1966 · Langton 1984 · Byl 1989 · Reggia et al. 1993 · Sutton, Precup & Singh 1999.

**Del proyecto:** cartografías de Terrario y Genesis (gates vigentes), `CONGELACION_HISTORICA_01.md`, `BLOQUE10_*`, `DEFINICIONES_PRE_P4.md`, `PRIOR_ART_INDIVIDUALIDAD_CAUSAL.md`, informe corregido de la autopsia causal, `LEVEL19_PREDICTIVE_STATE_V1_PREREGISTRATION.md`, y la memoria de sesión (`MEMORY.md`) que resume las decisiones de Wis.

# Orientaciones para la Fase 1 · escalar sin azar

**Fecha:** 2026-10-25 · **Para:** Opus 5.5, en el árbol `experiment/unidad-minima-01` (`/home/wis/Aplicaciones/worktrees/unidad-minima-01`) · **De:** la revisión de la Fase 0 (Fable 5.1) · **Adjudica:** Wis.

**Lo primero que hay que saber:** el trabajo de esta sesión es **el experimento**, no la custodia. Commitear no es trabajo; es lo último que se hace y una sola vez. Documentos: exactamente tres (gate de antecedentes, ficha de apertura, cierre). Nada de dashboards, refactors de 01–04, gates nuevos ni infraestructura que la medición no pida. Si una tarde se va en herramientas y no en curvas, la tarde se perdió.

**Pregunta de la fase.** ¿La unidad de 02 identifica la máquina mínima de mundos ocultos de 3 a 8 estados, viviendo una sola vida, sin maestro, sin reset, de forma determinista, con un coste que crece polinomialmente y no exponencialmente?

Si la respuesta es sí con el mecanismo que ya existe, **no se escribe ningún algoritmo nuevo**. Ese es el mejor desenlace posible y hay que estar dispuesto a aceptarlo.

---

## 0 · Quince minutos antes de empezar (y no más)

1. En `ROADMAP_UNIDAD_MINIMA_01.md`, **en el sitio y con fecha**: reemplazar el párrafo «Entorno» de §1 por la receta real (`/usr/bin/python3` = 3.14.4; el `.venv` apunta a un 3.12 que ya no existe; numpy sólo con `PYTHONPATH=.deps-level19 python3`); y bajo el ítem 0.2 añadir el desenlace (FAIL del enunciado, PASS de la reparación) con puntero a `CIERRE_FASE_0.md`. No reescribir la predicción.
2. Un solo commit con la Fase 0 completa más esas correcciones **y los tres ficheros nuevos del 25-oct: `ERRORES_Y_GUARDAS.md`, `PLANTILLA_FICHA_APERTURA.md` y `.claude/skills/apertura/SKILL.md`**. Wis aceptó la revisión del 25-oct; ese commit está autorizado. Después, **ningún commit más hasta cerrar la fase**.
3. No tocar los 14 worktrees `prunable` (están movidos a `~/Aplicaciones/`, no perdidos); el `repair` lo decide Wis. No arreglar el gate de cartografía: no hace falta en esta fase.

---

## 1 · Decisiones ya adjudicadas (no se reabren)

- **Salida observable del banco:** sólo el bit de cambio, `o = [x′ ≠ x]`. Es disposición suministrada y se declara.
- **Solucionador SAT:** admisible como **referencia exacta**, no como mecanismo vivo; semilla y versión fijas registradas en el JSON; cruce obligatorio con el retroceso propio en |S| ≤ 4 (deben coincidir en todos los sistemas; si discrepan, parar e informar). Sólo se instala si el retroceso de 01 no alcanza para la comprobación de identificabilidad en |S| = 4; si se instala, va a `.deps-unidad/` con `pip install --target`, versión anotada.
- **Política de lectura de la memoria:** en esta fase la unidad relee sólo al refutar (el comportamiento de 02). El disparador de 03 no se usa: no hay lesiones aquí. Se declara como disposición.
- **L19 no se toca.** El trabajo es en este árbol.

---

## 2 · PRIOR-ART GATE · entregable `PRIOR_ART_ESCALADO_SIN_AZAR.md`

Dos columnas siempre: *qué dice la literatura* ≠ *qué tenemos comprobado*. Veredicto con el vocabulario de la casa. No decir «nadie lo hizo»; decir «no lo hemos encontrado».

**Ya verificado (no repetir la búsqueda, sí citar):** AALpy (L# por apartness, arXiv 2107.05419; merge pasivo rojo-azul, CAV 2025, arXiv 2506.06333; PyPI 1.6.2); Λ*_M (TCS 2026); L# separadores (CAV 2026, arXiv 2605.15294); CSSR (arXiv 1408.2025); Rivest–Schapire 1993; inaproximabilidad de la palabra de reset mínima (Gawrychowski–Straszak, arXiv 1408.5248); Volkov 2008; Damasceno 2019; Ferreira–van Heerdt–Silva 2022 (arXiv 2209.00122).

**Búsquedas obligatorias, y qué cambiaría el plan si aparecen:**

| búsqueda | si existe y está vivo… |
|---|---|
| `exact DFA identification SAT` (Heule & Verwer 2010) y una implementación Python viva | …sustituye al retroceso de 01 como referencia exacta para |S| ≥ 4 |
| `incremental regular inference` / `incremental RPNI Mealy` (Dupont 1996 y sucesores) | …se integra como aprendiz vivo en vez de escribir uno |
| `AALpy RPNI Mealy single trace` · `passive learning Mealy from one word` | …la unidad **envuelve** AALpy y sólo añade vida continua, predicción previa y contadores |
| `learning Mealy machines without reset 2025 2026` (repetir; ayer vacío) | …se lee antes de decidir nada |
| `characteristic sample passive automata learning single trace` | …fija cómo justificar la longitud de vida L (§3.3) en vez de elegirla a ojo |
| `Moore minimization Mealy machine` (Moore 1956, Hopcroft 1971) | …es de libro: se implementa de libro y se cita, no se redescubre |

Veredicto esperado: `MULTIPLE_NEAR_SOLUTIONS`. Residuo propio probable: la vida continua con predicción previa y sin oráculo, y la medida de identificabilidad paso a paso. **Sólo eso se construye, y sólo si 02 no alcanza.**

---

## 3 · Diseño · lo que la ficha de apertura tiene que fijar

*Añadido el 25-oct, por decisión de Wis («no repetir los mismos errores una y otra vez»):* la ficha se escribe sobre `PLANTILLA_FICHA_APERTURA.md` (13 puntos; el **punto 0** son las guardas de `ERRORES_Y_GUARDAS.md` que aplican y cómo se cumple cada una), con el skill `/apertura` si la sesión lo ve, o leyendo los dos ficheros si no. Orden: gate → ficha → mutantes → enmienda prospectiva → corrida; **la ficha no es final hasta pasar sus mutantes**. Para esta fase aplican al menos E-01, E-03, E-05, E-06, E-07, E-08, E-09, E-12.

### 3.1 El banco (antes que el umbral)

- Sistema: estados `{0..n−1}`, dos letras `A`, `B` como mapas arbitrarios `S → S`. Son `n^(2n)` sistemas: 729 con n=3, 65 536 con n=4. Orden canónico: `itertools.product` sobre las tablas, letra A primero.
- Estado inicial 0. Sólo cuenta la **parte alcanzable** desde 0: lo no alcanzable no existe para la unidad y no se le exige.
- Salida: bit de cambio. Máquina verdadera: Mealy sobre la parte alcanzable con `λ(x, a) = [F_a(x) ≠ x]`.
- **Máquina mínima verdadera:** minimización por refinamiento de particiones (Moore), de libro, polinómica. `n_min = 1` ⇒ clase «inerte bajo esta salida»: la unidad **no debe** abrir distinciones ahí. Es el control negativo gratis del banco.
- n = 3 **completo** primero. Medir tiempo por sistema. Con ese tiempo, **declarar antes de correr** la fracción 1-de-k canónica para n = 4 (o completo si cabe en el presupuesto de reloj declarado) y para n = 6 y 8. Nada de muestreo aleatorio.
- Reanudable: un JSONL con una línea por sistema; al reiniciar se saltan los hechos. Es requisito, no mejora: las corridas tienen que sobrevivir un corte.

### 3.2 La unidad

La `Unidad` de 02 tal cual, con `n_max = n + 1` como tope de seguridad (si lo toca, se registra: es hallazgo, no excepción). Por sistema se registra: paso del último error, errores, refutaciones, distinciones abiertas, pasos repasados, predicciones sin ruta, veces que la distinción decidió, estados finales, tiempo de reloj. Y el futuro: un segmento fijo declarado (por ejemplo las palabras de longitud L+1), con su acierto.

### 3.3 Vida

Shortlex de todas las palabras de longitud 1..L, concatenadas, sin reset, como en 01. **L se declara por n antes de correr** y la justificación viene del gate (§2, muestra característica); si no hay literatura que la fije, se declara a ojo **y se dice que es a ojo**. Si un sistema no se identifica y la causa es vida corta, se verá en la columna de identificabilidad, no se parchea subiendo L a mitad de corrida.

### 3.4 Identificación e identificabilidad

- **Aprendida ≡ verdadera**: isomorfismo de máquinas de Mealy alcanzables, por forma canónica (renumerar por BFS desde el inicio con orden fijo de letras y comparar diccionarios). Exacto y barato.
- **Identificable desde la vida**: la máquina mínima compatible con toda la vida es única salvo isomorfismo. Para n ≤ 4, contar con el `minimal_mealy` de 01 (`count_cap = 2`). Para n = 6 y 8, calcularlo **sólo** en los sistemas donde aprendida ≠ verdadera (son pocos o el gate ya falló).
- Los casos aprendida ≠ verdadera se clasifican, sin excepción: *no identificable desde la vida* (≥ 2 mínimas) · *presupuesto* (la vida se acabó antes del último error) · **sin explicación** (eso es un defecto del mecanismo y es FAIL).

### 3.5 Mutantes del gate, antes de la corrida real

- **Memorizador:** predice sólo historias ya vistas; nunca generaliza. Debe FALLAR en «aprendida ≡ verdadera» y en el futuro.
- **Ciego a la observación (1.8):** estado = f(estado, letra). Debe FALLAR en los sistemas con n_min ≥ 2.
- **Oráculo:** se le da la máquina verdadera. Debe PASAR. Si no pasa, el criterio está roto, no el aprendiz.
- **Vida invertida:** la misma vida leída al revés (determinista). Debe cambiar el paso del último error y **no** la máquina final en los identificables. Si cambia la máquina, el aprendiz depende del orden más de lo declarado.

### 3.6 La puerta (la ficha pone los números; esto es la forma)

- (i) Todo sistema con n_min ≥ 2 e identificable desde la vida termina con la máquina mínima verdadera (salvo isomorfismo). Los que no, clasificados por §3.4; **cero** casos «sin explicación».
- (ii) En la clase n_min = 1, cero distinciones abiertas en todo el banco.
- (iii) Escala: mediana y máximo del paso del último error, y de los pasos repasados, frente a n ∈ {3, 4, 6, 8}. Con cuatro puntos un ajuste log-log es débil: **declarar el criterio de muerte como número**, no como pendiente (por ejemplo: FAIL si en n = 8 más del X % de la muestra agota la vida sin identificar, o si los pasos repasados exceden k veces la vida; X y k los fija la ficha antes de correr y no se heredan de 01).
- Falsador escrito antes: qué resultado concreto diría «02 no escala y hace falta otro mecanismo».

### 3.7 Si 02 no escala

Entonces, y sólo entonces, el residuo del gate: o se envuelve AALpy, o se escribe el aprendiz incremental por apartness (observaciones como árbol, pares apartados por testigo, hipótesis sobre la base no apartada, sin maestro ni reset). Con su propia ficha, sus mutantes y su falsador. **No se empieza por aquí.**

---

## 4 · Lo que la Fase 0 dejó escrito y aquí se aplica

- El coste de relectura es un eje propio: vida nueva, pasos repasados y refutaciones se informan **separados**, siempre.
- La minimalidad de palabras de reset es inaproximable en general: si se mide algo de palabras en esta fase (opcional, y sólo si sobra tiempo), con longitud acotada declarada (≤ 2n) y sin reclamar mínimo.
- Identificabilidad **salvo isomorfismo**: etiquetas distintas con la misma conducta no son fallo (ya se vio en 0.2, t = 512 y 1024).
- Orden de trabajo: ficha → mutantes → enmienda prospectiva si hace falta → corrida real. Tres criterios mal escritos en la Fase 0 dicen que el paso de mutantes va **antes** de darle la ficha por terminada, no después.
- Determinismo: sin `random`, dos corridas un hash, JSON con sha256 del código y la versión exacta del intérprete (3.14.4) y de cualquier biblioteca instalada.

---

## 5 · Qué no se hace

No refactorizar 01–04. No construir infraestructura más allá del JSONL reanudable. No escribir más de tres documentos. No tocar RNE, Genesis, L19, `level18/`, las semillas reservadas, los worktrees ni el gate de cartografía. No commitear a mitad de fase. No subir L ni cambiar k después de ver resultados. No usar workflows multiagente. No declarar «no existe»; declarar «no hemos encontrado».

---

## 6 · Entregables y cierre

1. `PRIOR_ART_ESCALADO_SIN_AZAR.md` (§2).
2. `APERTURA_ESCALADO_SIN_AZAR.md` con la puerta numérica, el falsador, los mutantes y su resultado, y las enmiendas prospectivas si las hay.
3. `unidad_minima_05_banco.py` (la campaña) y, si §3.7 se activa, `unidad_minima_06_<mecanismo>.py`.
4. `artifacts/unidad_minima_05_banco.jsonl` (una línea por sistema, reanudable) y `artifacts/unidad_minima_05_banco.json` (resumen por n, curvas, clasificación de los no identificados, mutantes).
5. `CIERRE_FASE_1.md`: tabla por n, las curvas en texto, qué se integró de la literatura frente a qué se escribió, los hallazgos laterales, **qué guardas del registro saltaron y qué entradas nuevas se añaden a `ERRORES_Y_GUARDAS.md` (cada una con su guarda; sin guarda quedan ABIERTAS)**, qué parte de la sesión fue experimento y qué parte custodia, y **una sola pregunta para Wis** al final.
6. Un commit, al cerrar, con todo lo anterior, sólo cuando Wis lo autorice.

**Regla de cierre, recordada:** si la puerta da FAIL, una reparación declarada antes de correrla y una segunda medición. Dos FAIL cierran el programa y se informa sin adornos. Un FAIL bien medido vale más que un PASS con el criterio aflojado.

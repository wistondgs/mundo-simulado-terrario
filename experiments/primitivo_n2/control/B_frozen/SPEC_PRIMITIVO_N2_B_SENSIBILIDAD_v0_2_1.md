# ESPECIFICACIÓN PRIMITIVO · N=2 · VERSIÓN B — SENSIBILIDAD INSTRUMENTAL

**Versión:** v0.2.1 · **Fecha:** 2026-09-22
**Estado:** PROPUESTO — corregido tras la revisión estática; pendiente de freeze. Nadie ejecuta nada de B antes del freeze.
**Requiere:** Versión A v0.1. Todo lo que no se redefine acá queda como en A.

**Convenciones fijas:** C1, C2, C3, C6, C10.
**Convenciones abiertas:** C4, C5, C7, C8, C9, C11.

**Preguntas:**
1. ¿Sobreviven los resultados de A cuando se deja de privilegiar una única definición razonable?
2. ¿Qué resultados desaparecen o cambian cuando se modifica también el operador con el que el laboratorio perturba el sistema?

**Principio de trabajo:**

> resultado observado = f(dinámica, factorización, perturbación, scheduler, lesión, métrica)

Antes de incorporar una propiedad al mapa mínimo, se declara qué transformaciones deberían dejarla invariante.

---

## 0. Preregistro (antes de ejecutar)

1. Aceptar el conjunto mínimo de alternativas (sección 1) y la tabla de clasificación de simetría (sección 2.2).
2. Opcional: agregar como máximo una alternativa propia por convención abierta, con una justificación de una o dos líneas y su clasificación de simetría.
3. Congelar el documento de preregistro (este texto más los agregados) y registrar su SHA-256.
4. Recién entonces ejecutar.

La clasificación de simetría forma parte del preregistro. Si una salida falla su guardia, no se la puede reclasificar después para salvarla. Cualquier salida o alternativa pensada después del freeze se reporta aparte como EXPLORATORIO y no entra en las decisiones.

Nadie ejecuta B antes del paso 3, incluidas las IA que redactaron o revisaron esta especificación.

---

## 1. Alternativas mínimas

El sufijo ".a" indica la definición de la Versión A.

### C4 · Operador de perturbación

P(s) es el conjunto de estados contrafácticos contra los que se evalúa la recuperación desde s. En un corte (a, b):

- **C4.a · una coordenada (A):** P(s) = {s ⊕ m_a, s ⊕ m_b}. Una perturbación cambia a y conserva b; la otra, al revés.
- **C4.b · ambas coordenadas:** P(s) contiene un único estado s′, el que cumple a(s′) ≠ a(s) y b(s′) ≠ b(s). Se construye como s ⊕ m_a ⊕ m_b y se verifica la propiedad en los 4 estados.
- **C4.c · intrínseca:** P(s) = {s′ ∈ S : s′ ≠ s}, es decir, tres perturbaciones por estado. No depende de ningún corte.

Sin interpretación previa: que C4.c no dependa del corte no la vuelve el operador correcto. Funciona como contraste frente a perturbaciones definidas sobre variables.

**Identidad estructural (verificada con álgebra de máscaras, sin tocar dinámicas).** En cada corte, las perturbaciones de C4.a y la de C4.b son disjuntas y juntas forman exactamente las tres de C4.c. La máscara de C4.b es 3 en C12, 2 en C13 y 1 en C23. Consecuencias:

- C4.a y C4.b no son alternativas independientes: son las dos partes de C4.c, y lo que el corte decide es cuáles de las tres direcciones de perturbación cuentan como "cambiar una variable".
- Con C7.a, para cada atractor A y cada corte x: 3·r_A(C4.c) = 2·r_A(C4.a, x) + r_A(C4.b, x). La dependencia del corte de C4.a queda compensada exactamente por la de C4.b.

### C5 · Dependencia

- **C5.a (A):** la dependencia se manifiesta en al menos un estado.
- **C5.b · régimen:** sólo cuentan los estados s que pertenecen a algún atractor de F. El estado s ⊕ m_j puede estar fuera del régimen.
- **C5.c · total:** la dependencia se manifiesta en los 4 estados.

Las manifestaciones vienen de a pares (s y s ⊕ m_j). Por eso "al menos 2 de 4" equivale a C5.a y no cuenta como alternativa.

### C7 · Agregación de la recuperación

El atractor se identifica por su conjunto de estados (C6, fija). Para cada atractor A:

r_A = #{(s, s′) : s ∈ A, s′ ∈ P(s), el atractor de s′ es A} / #{(s, s′) : s ∈ A, s′ ∈ P(s)}

C4 define qué se perturba; C7 define sólo cómo se agregan los r_A.

- **C7.a (A):** promedio sobre todos los pares (s, s′); los atractores más grandes pesan más.
- **C7.b:** promedio simple de r_A sobre los atractores.
- **C7.c · peor caso:** mínimo de r_A.
- **C7.d · por cuenca:** Σ_A (|cuenca(A)| / 4) · r_A, donde cuenca(A) son los estados cuya trayectoria llega a A.

### C8 · Scheduler (en C12)

- **C8.a (A):** órdenes secuenciales determinísticos sec12 y sec21.
- **C8.b · asincronía general:**
  - Desde cada s salen dos aristas: una a (f1(s), x2) y otra a (x1, f2(s)); se admiten lazos.
  - Los atractores son las componentes fuertemente conexas terminales, es decir, sin aristas hacia otras componentes.
  - Un ciclo sincrónico sobrevive si alguna componente terminal tiene exactamente su conjunto de estados.
- **C8.c:** mismo grafo que C8.b; el ciclo sobrevive si su conjunto de estados está contenido en alguna componente terminal.

En C8.b y C8.c, `atractores_distintos` compara los atractores sincrónicos con las componentes terminales.

### C9 · Lesión (en C12)

**Semánticas primarias:**
- congelar y fijar0 (las de A);
- fijar1: la variable lesionada pasa a valer 1.

**Semánticas derivadas.** Se calculan a partir de fijar0 y fijar1; no son simulaciones nuevas:
- fijar_∃: el veredicto es verdadero si lo es con fijar0 o con fijar1;
- fijar_∀: el veredicto es verdadero si lo es con ambos.

**Veredictos:**
- V1: cambia la unión de estados de atractor (A);
- V2: cambia el conjunto de atractores;
- V3: cambia el número de atractores.

### C11 · Consecuencias y vocabularios

Vocabulario y consecuencia se calculan siempre en un mismo corte x, con el C4 y el C7 de la celda.

**Consecuencias:**
- **T1:** K = (periodos, robustez_x). Descriptiva; no decide.
- **T2:** robustez_x sola. Es la única consecuencia que decide H1.
- **T3:** periodos solos. Es una fixture negativa: debe quedar marcada por la guardia.

T4 de la v0.1 (robustez con las tres perturbaciones) queda absorbida por las celdas C4.c, que cumplen su función de fixture negativa (sección 3).

**Vocabularios:** cruzada_x, grafo_x, grafo_3_cortes (la tupla de los tres `grafo`), tipo_S4.

**Guardia de intrinsicidad.** Si H(T | tipo_S4) = 0, T está determinada por el tipo por construcción. La celda se reporta como EXCLUIDA_POR_INTRINSICIDAD y no cuenta ni como éxito ni como fallo de H1.

---

## 2. Guardia de simetría (transversal)

### 2.1 Grupos

- **G_S4:** las 24 permutaciones de los estados.
- **G_x**, para cada corte x = (a, b): las 8 permutaciones que, escritas en las coordenadas de ese corte, tienen la forma (a, b) ↦ (a ⊕ n1, b ⊕ n2) o (a, b) ↦ (b ⊕ n1, a ⊕ n2), con n1, n2 ∈ {0,1}.

Cada corte se evalúa con **su propio** grupo, no sólo con el de C12.

Una permutación p transforma la dinámica como F ↦ G con G(p(s)) = p(F(s)).

### 2.2 Tabla de clasificación (forma parte del preregistro)

| Salida | Clase | Chequeo | Regla esperada bajo el grupo |
|---|---|---|---|
| periodos, tipo_S4 | INTRINSIC_S4 | INVARIANCE | igual bajo G_S4 |
| robustez con C4.c (cualquier C7) | INTRINSIC_S4 | INVARIANCE | igual bajo G_S4 |
| robustez_x con C4.a o C4.b | CUT_RELATIVE | INVARIANCE | igual bajo G_x |
| cruzada_x | CUT_RELATIVE | INVARIANCE | igual bajo G_x |
| grafo_x | CUT_RELATIVE | EQUIVARIANCE | si p intercambia a↔b, [d(a,a), d(a,b), d(b,a), d(b,b)] pasa a [d(b,b), d(b,a), d(a,b), d(a,a)]; las negaciones no lo cambian |
| grafo_3_cortes | exento de SYM-02 | EXEMPT | lo cubre el control de consistencia 2 (sección 3) |
| atractores_distintos, ciclo_muere (C8.a–c) | CUT_RELATIVE | INVARIANCE | igual bajo G_C12 (el intercambio cambia sec12 por sec21; los booleanos usan ambos) |
| lesión con congelar, fijar_∃ o fijar_∀, por variable | CUT_RELATIVE | EQUIVARIANCE | si p lleva la coordenada x_i de F a la coordenada x_i′ de G, el veredicto sobre x_i en F es igual al veredicto sobre x_i′ en G |
| lesión con fijar0 o fijar1, por separado | LABEL_RELATIVE | LABEL_TRANSFORM | si p lleva x_i a x_i′ sin negarla, fijar_v sobre x_i en F es igual a fijar_v sobre x_i′ en G; si la niega, es igual a fijar_(1−v) sobre x_i′ en G |

El tipo de chequeo queda preregistrado con la tabla: no se elige al momento de reportar.

**Caso evaluado:** un par (F, p), con F entre las 256 dinámicas y p en el grupo de la fila. Hay violación si la salida de G = pFp⁻¹ no coincide con la regla aplicada a la salida de F.

### 2.3 Chequeos

- **SYM-01 · intrínsecas.** Una salida INTRINSIC_S4 debe tener el mismo valor en todos los miembros de cada clase tipo_S4. Si no: SYM_FAIL_INTRINSIC, y la salida queda excluida de cualquier claim intrínseco.
- **SYM-02 · relativas al corte.** Una salida CUT_RELATIVE debe comportarse como indica la tabla bajo cada elemento de G_x. Si no: SYM_FAIL_CUT.
- **SYM-03 · relativas a etiquetas.** Una salida LABEL_RELATIVE no puede usarse sola como propiedad del sistema. Sí puede usarse como intervención, para medir cuánto depende un resultado del operador experimental. No se le exige invariancia: se verifica su regla LABEL_TRANSFORM. Si esa regla falla: SYM_FAIL_LABEL, que indica un error de implementación, no una propiedad del sistema.
- **SYM-04 · fixtures.** Un caso individual sólo vale como fixture de una propiedad si la propiedad se mantiene en toda su clase de simetría. Si no, sigue siendo diagnóstico, pero se etiqueta FIXTURE_LABEL_DEPENDENT.

---

## 3. Diseño

Se calcula la grilla completa. Cada hipótesis se evalúa sólo sobre los factores de los que depende:

| Hipótesis | Factores | Consecuencia |
|---|---|---|
| H1 | C4 × C5 × C7 × retador | T2 |
| H2 | C5 × C8 | muerte o supervivencia de ciclos |
| H3 | C9 (semántica × veredicto) | desacuerdo entre semánticas |

**Controles de consistencia.** Si alguno falla, es un bug y se detiene todo antes de interpretar.

1. **Factores irrelevantes.** Las salidas de una hipótesis no cambian entre niveles de factores de los que no depende. En particular, H2 y H3 son idénticas en C4.a, C4.b y C4.c.
2. **Simetría entre cortes.** H1 se calcula en x = C12, C13 y C23 con C4.a y C4.b; los valores deben ser idénticos en los tres cortes. Vale también para grafo_3_cortes.
3. **Fixtures negativas de intrinsicidad.** Todas las celdas C4.c y la consecuencia T3 deben quedar marcadas por la guardia. Es una predicción analítica: si alguna no queda marcada, la guardia está rota y se detiene todo.
4. **Celda de referencia.** Todas las ".a", T1, y congelar vs fijar0 con V1 deben reproducir exactamente los valores de A.
5. **C4.b.** La verificación de que s′ cambia ambas etiquetas pasa en todos los estados de los tres cortes.
6. **Identidad C4.** Con C7.a, 3·r_A(C4.c) = 2·r_A(C4.a, x) + r_A(C4.b, x) se cumple exactamente para todo atractor, toda dinámica y los tres cortes. Es aritmética de fracciones exactas; cualquier diferencia es un bug.

---

## 4. Hipótesis y reglas de decisión (preregistradas)

**Métrica principal:** exceso = I(V;T) − E[I], en bits. **Secundaria:** AMI_max; se reporta, no decide.

**Empates.** Si |exceso₁ − exceso₂| ≤ 1e-9, la comparación es EMPATE y cuenta como "no se cumple".

**H1a.** En cada celda no excluida de C4 × C5 × C7: exceso(tipo_S4 ; T2) > exceso(grafo_x ; T2).

**H1b.** Lo mismo, con grafo_3_cortes como retador. Si H1a sobrevive y H1b no, la conclusión se restringe a "acoplamiento medido en un solo corte".

Las celdas C4.c quedan excluidas por construcción. Por eso H1 existe sólo para perturbaciones definidas sobre variables: la tabla final debe decirlo explícitamente.

C4.a y C4.b son complementarias dentro de C4.c (sección 1, C4), así que no cuentan como dos confirmaciones independientes. El estado de H1 se reporta global y también por separado para C4.a y para C4.b.

**H2.** Para cada categoría de `cruzada` en C12, sea p_cat = (dinámicas con ciclo que muere) / (dinámicas con ciclo sincrónico). En cada celda C5 × C8 se cumple p_mutua > p_separable y p_mutua > p_unidir. Una comparación con una categoría sin ciclos queda indefinida: se reporta y no cuenta.

**H3 (descriptiva).** El veredicto de una lesión puede depender de la semántica con la que se implementa. Para cada veredicto V1–V3 y cada par de semánticas se reporta la fracción de los 512 pares (dinámica, variable) con veredictos distintos, junto con la clase de simetría de cada semántica.

- Un desacuerdo que involucra una semántica LABEL_RELATIVE demuestra dependencia del instrumento, no una propiedad de la dinámica.
- Las comparaciones entre congelar, fijar_∃ y fijar_∀ son las únicas libres de dependencia de etiqueta.

**Estados de cada hipótesis:**
- SOBREVIVE: se cumple en todas las celdas decisivas.
- RESTRINGIDO: se cumple en al menos la mitad de las celdas decisivas; se listan las celdas y convenciones que la rompen.
- NO_SOBREVIVE: se cumple en menos de la mitad.
- NO_EVALUABLE: no hay ninguna celda decisiva, o todas las comparaciones quedaron indefinidas. Nunca se declara SOBREVIVE por vacuidad.

Una celda es decisiva si no está excluida y su comparación está definida. Correspondencia con la política de no-canon: CONSERVAR / RESTRINGIR / REFUTAR / SIN DECISIÓN, siempre en N=2 y bajo estas convenciones.

---

## 5. Salidas → `resumen_B.json`

- SHA-256 del preregistro y alternativas agregadas.
- Por celda: los valores de cada hipótesis.
- Por hipótesis: el estado y la lista de celdas que fallan.
- `celdas_excluidas_H1`: celda y razón.
- `C4`: por variante, `numero_perturbaciones_por_estado` y `depende_del_corte`.
- `simetria.por_metrica`, por cada fila de la tabla 2.2:
  - `clasificacion`;
  - `grupo_pretendido`;
  - `tipo_chequeo`: INVARIANCE, EQUIVARIANCE, LABEL_TRANSFORM o EXEMPT;
  - `casos_evaluados` y `violaciones` (sección 2.2);
  - `estado`: PASS si no hay violaciones, FAIL si las hay, NOT_APPLICABLE si el chequeo es EXEMPT (nunca PASS);
  - `clases_mixtas`: opcional, sólo para INTRINSIC_S4.
- Controles de consistencia 1–6, con PASS/FAIL.
- EXPLORATORIO, en una sección aparte.

---

## 6. Lo que B no cubre

- C6 (identidad del atractor) sigue fija.
- C3 también: qué cortes existen, y que los estados se factoricen en dos bits.
- Todo vale para N=2 y con peso uniforme sobre las 256 dinámicas.
- B no dice qué es un ser. Separa numéricamente cuatro cosas:
  - propiedades intrínsecas;
  - resultados que dependen de las coordenadas;
  - resultados que dependen de etiquetas;
  - fallos reales de invariancia.

---

## 7. Registro de cambios

### v0.1 → v0.2

**Del parche propuesto:**
- C4 pasa a estar abierta, con las variantes a, b y c.
- C7 se generaliza con P(s): C4 define qué se perturba y C7 cómo se agrega.
- Guardia de simetría con las clases INTRINSIC_S4, CUT_RELATIVE y LABEL_RELATIVE, y los chequeos SYM-01 a SYM-04.
- H1 pasa a C4 × C5 × C7, con exclusión por intrinsicidad.
- H3 se reformula.
- Se agregan salidas nuevas.

**Agregado en la revisión estática:**
- La clasificación de simetría se congela en el preregistro; no se puede reclasificar después para salvar una salida.
- Grupo propio para cada corte y regla de transformación explícita por salida. Sin esas reglas, SYM-02 no se puede ejecutar de forma determinística.
- Las celdas C4.c pasan a ser fixture negativa de la guardia; absorben a T4.
- Estado NO_EVALUABLE, para impedir un SOBREVIVE por vacuidad cuando todas las celdas quedan excluidas.
- Regla de empate con tolerancia numérica.
- Semánticas de lesión derivadas fijar_∃ y fijar_∀, invariantes bajo negación, para que H3 tenga al menos una comparación libre de dependencia de etiqueta.
- grafo_3_cortes queda exento de SYM-02 porque su invariancia relevante ya la cubre el control de consistencia 2.
- Identidad estructural de C4: en cada corte, C4.a y C4.b se reparten las tres perturbaciones de C4.c. Se agrega el control 6 y se exige reportar H1 por nivel de C4.

### v0.2 → v0.2.1 (revisión estática de la otra IA)

- **Fix 1.** Las salidas exigen los controles 1–6. El control 6 se había agregado al diseño pero no a las salidas.
- **Fix 2.** El reporte de simetría distingue INVARIANCE, EQUIVARIANCE, LABEL_TRANSFORM y EXEMPT, con `casos_evaluados`, `violaciones` y estado PASS / FAIL / NOT_APPLICABLE. Consecuencias necesarias del mismo fix:
  - columna "Chequeo" en la tabla 2.2, para que el tipo de chequeo quede preregistrado;
  - reglas de equivariancia y de transformación de etiqueta escritas con la correspondencia de coordenadas;
  - definición de caso evaluado;
  - SYM-03 ya no dice que fijar0 y fijar1 "fallan": se verifica su regla, y un fallo es SYM_FAIL_LABEL.
- Encabezado: versión y estado.

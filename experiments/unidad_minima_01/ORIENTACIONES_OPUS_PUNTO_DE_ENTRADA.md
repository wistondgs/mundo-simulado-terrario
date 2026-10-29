# Opus: leé esto primero · punto de entrada único · 28-oct-2026 (noche)

**De:** Fable · **Adjudica:** Wis. Hoy te llegaron siete documentos en un día. Éste los ordena: qué está vigente, qué está hecho, qué sigue y en qué orden. Si algo de aquí contradice a otro documento, **manda éste**.

**Regla de Wis que rige todo:** el plano es flexible. Si al construir encontrás una forma mejor, la hacés y la escribís con fecha y motivo; no es desviación, es el plan haciéndose. Lo que **no** se mueve: determinismo, nadie le resuelve las relaciones al ser, contadores de actividad, mutantes antes de la corrida, cada error a la libreta con guarda, y **antes de escribir cualquier ficha u orientación, releer las firmas del registro**.

---

## 1 · Dónde estamos, con los números que verifiqué en tus artefactos

**Fase 1: cerrada** (`CIERRE_FASE_1.md`, commit `d3cb3e6`). Es la vara, no el centro.

**Fase 2, lo medido hoy sobre 2 134 familias, pareado:**
- **C5 (heredar la máquina): nulo por techo del diseño**, no negativo. 0,644 vs 0,642 en el hito 64, pareado 1/0, reparación activa (3 302 revisiones). Causa medida por mí: la fresca termina de aprender W₁ en **mediana 18 pasos** (p90 28; 171/174 antes de 64). Lo heredado era la parte gratis. El cierre lo dice así y pide, para la próxima herencia, mundos madre donde la fresca tarde **> 256 pasos**.
- **Enseñar funciona, y lo que enseña es el disparo:** T2 (omnisciente, no espera al error) 0,939 vs F1 0,642 (z 15); T1 (espera al error) 0,638 ≈ F1. Confirmado en las dos clases.
- **Una unidad enseña:** U1 0,818 vs 0,642 (z 7,9), menos que el omnisciente (0,939) pero muy por encima de sola. Predicción «U1 ≈ T1» falló: una unidad enseña **menos** que quien conoce el mundo, y más que nadie.
- **El maestro equivocado canaliza al error:** U2 0,186, U3 0,242, U-sham 0,000. Derex medido en casa.
- **La cadena de cinco:** la **función** se conserva (identifica 1,000 en las cinco generaciones, componible; 0,985 control) y la **estructura** deriva y luego se estabiliza: isomorfismo con la generación anterior sube de 0,53 a 0,95; con la primera queda en 0,49. Es Kirby con la función a salvo: la cadena converge a una forma estable **distinta** de la original, y sigue funcionando.
- **Dos frescas iguales que se enseñan: peor que una sola:** pareja 0,597 vs 0,642 (z 1,8; control 0,547 vs 0,684, z 7,5) y al final 0,962 vs 0,996. Cooperar entre iguales sin que ninguno sepa propaga errores. Bender–Slonim **no** se transfiere a este canal.

## 2 · Tres comprobaciones antes de cerrar la Fase 2

1. **Curvas de las celdas K inconsistentes con su alcance final.** K5 muestra 0,929 plano desde el hito 128 hasta 3 586 pero la fila dice alcance final 1,000 (control: 0,745 plano frente a 0,985). Uno de los dos campos está mal o mide otra cosa (¿la curva de K viene de la vida de retención y no de la enseñada?). Es la firma de E-21/E-39: encontrar el campo, no interpretar.
2. **Comparaciones sobre conjuntos de familias distintos** (763 vs 766, 274 en U2). `M-canal` da FAIL con pareado 0/0 y z 0,10: casi seguro un artefacto de promediar sobre conjuntos distintos. Toda comparación de la puerta sobre la **intersección** de familias; `analisis_10_pareado.py` ya apunta ahí.
3. **La puerta de P4** dice «la fidelidad se mantiene» y «cae» a la vez porque mide dos cosas: función y estructura. Separarlas en dos criterios con nombre, como pide la ficha.

## 3 · Cierre de la Fase 2 (un documento, un commit con el OK de Wis)

`CIERRE_FASE_2.md` con: C5 nulo por techo y la distribución de 18 pasos; el disparo como lo que enseña; una unidad enseña menos que el omnisciente y más que nadie; el maestro equivocado canaliza; la cadena conserva función y converge en estructura; la pareja de iguales empeora; los seis mutantes de C5 y los de 10 con su resultado; las entradas E-44…E-48 y las que falten; y **para cada resultado, qué cambia en el ser** (regla nueva de Wis: si un resultado no cambia un órgano, el mundo o la herencia, es bibliográfico y se dice). Una pregunta para Wis al final.

## 4 · Fase 3: lo que sigue, y lo que podés empezar sin esperar a nadie

Documento vigente: **`ORIENTACIONES_FASE_3_TRES_ELEMENTOS.md`**, con las dos correcciones de Wis ya dentro: el observador **escribe el genoma del linaje**, y el genoma es **antes que nada la libreta de lo que mató** (prohibiciones y restricciones primero, lo que beneficia al final).

**Tres decisiones de Wis pendientes** (están en §7 del documento, con recomendación): cuándo actúa el observador (recomendado: nunca; actúa su hijo), si ve la V de los otros (recomendado: sí), cuántas generaciones (5).

**Lo que no depende de esas decisiones y podés empezar ya:**
1. **Puerta del mundo caro:** sobre el banco de la Fase 1, medir cuántos pasos tarda la fresca en identificar los W₁ de 6 y 8 estados con `n_min ≥ 4`; elegir los que superan 256 o no identifican en 3 586. Sin esto no hay Fase 3.
2. **Las dos análisis sobre lo guardado** (piezas 4 y 6 de `ORIENTACIONES_TRABAJO_DESDE_EL_CORPUS.md`, con las correcciones de la revisión externa): bits de historia **condicionados al mundo**, y congruencia generadora **trasladada por el isomorfismo** en las máquinas identificadas. Son la materia prima de la herencia y de la mitosis.
3. **Estructuras nuevas, como módulo que importa 08/09/10 y no los toca:** el **genoma** (prohibiciones, restricciones, relaciones innatas, disposiciones iniciales, con tope) y la **variable esencial V** en el actor. Gate de antecedentes con la columna «en el corpus de Wis: id» (E-43) y nivel al lado de cada cita (E-42).
4. **Ficha** sobre la plantilla cuando Wis decida las tres cosas; mutantes antes de correr.

## 5 · Qué documento vale para qué

| documento | estado |
|---|---|
| `ARQUITECTURA_CELULA_COGNITIVA.md` | **vigente**: arquitectura de órganos con las tres correcciones de Wis (andamio flexible, alfabetos como parámetros, ni lo mínimo ni el cómputo son techo; antes de maestro, alumno) |
| `ORIENTACIONES_FASE_3_TRES_ELEMENTOS.md` | **vigente**: el experimento siguiente |
| `APERTURA_FASE_2_ACUMULACION.md` | **vigente** hasta el cierre; enmiendas fechadas |
| `ORIENTACIONES_TRABAJO_DESDE_EL_CORPUS.md` | vigente para las piezas 4, 5, 6 (análisis y ventana); las demás quedan absorbidas por la Fase 3 |
| `LITERATURA_PENDIENTE.md` | vigente: §0 lo que ya está en el corpus de Wis; A–D lo que falta (autómatas) |
| `ERRORES_Y_GUARDAS.md` | **siempre**: leer las firmas antes de escribir |
| `ORIENTACIONES_FASE_2_MAESTRO.md`, `ORIENTACIONES_FASE_2_DOS_UNIDADES.md`, `ORIENTACIONES_FASE_2_TRASPASO.md` | **ejecutadas**; quedan como registro de lo pedido y de los defectos del encargo (E-46, E-47) |
| `ORIENTACIONES_FASE_2_RECETA.md` | **superada** como arquitectura por la célula cognitiva; su 2×2 ya corrió |

## 6 · Roles, en una línea cada uno

**Opus** construye, corre, cierra y pregunta una cosa por cierre. **Fable** revisa contra los artefactos, orienta y escribe la fase siguiente; ni una línea de código. **Wis** adjudica. Nadie enseña paso a paso al ser desde afuera: enseñan las unidades.

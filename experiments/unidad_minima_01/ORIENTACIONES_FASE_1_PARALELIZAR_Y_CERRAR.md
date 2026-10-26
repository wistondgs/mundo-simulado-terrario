# Orientaciones · Fase 1 · paralelizar el banco y cerrar la fase

**Fecha:** 2026-10-25 · **Para:** Opus 5.5, en `/home/wis/Aplicaciones/worktrees/unidad-minima-01` · **De:** la revisión de Fable sobre la corrida en curso · **Adjudica:** Wis.

**Regla de este paquete:** nada de lo que sigue cambia una medida. Cambia el reloj y el cierre. La ciencia de la fase es la que está corriendo; no se toca su ficha, su puerta, su L ni su k.

---

## 1 · Lo que medí sobre la corrida (para que no lo vuelvas a medir)

- Proceso `python3 unidad_minima_05_banco.py 3 4 6 8`, vivo, **99,5 % de un solo núcleo** de 12 lógicos (6 físicos, i7-10750H). La máquina está al 13 %.
- Wis puso el gobernador en `performance` (antes `powersave`): los núcleos van a **4,1 GHz**. Turbo ya estaba activo. Eso le da un 10–20 % al hilo que corre; no más.
- **Temperatura: 92 °C de paquete con un solo núcleo cargado** (límite 100 °C). Con seis trabajadores el portátil estrangula y puede ir más lento que con cuatro.
- RAM: 430 MB por proceso; 15 GB disponibles. No es límite.
- Tu propia estimación: n=6 a 44 503 de 108 840; n=8 sin empezar, 28 148 sistemas; restante ~9 h (7–14) en un hilo. Cola: mediana 3,3 ms, peor sistema 182 s (×55 000).

---

## 2 · Paralelizar sin tocar la medida

Cada sistema se calcula sólo desde `(n, idx)`, sin estado compartido y de forma determinista. Repartirlos entre procesos no cambia ninguna cifra; sólo el orden en que las filas caen al JSONL.

1. **No matar la corrida hasta tener la versión paralela probada** sobre un tramo ya hecho (por ejemplo 200 índices de n=4): las filas deben ser **idénticas** campo a campo a las que ya están en el JSONL. Ésa es la prueba de que paralelizar no cambió nada; va al cierre.
2. Después, parar la corrida (es reanudable) y relanzar saltando lo hecho.
3. `concurrent.futures.ProcessPoolExecutor` con **4 trabajadores** (no 6, por la temperatura), una tarea por sistema, `map` por trozos de tamaño fijo en orden canónico. Los trabajadores devuelven la fila; **un solo escritor** la añade al JSONL (o un shard por trabajador y fusión al final; cualquiera de las dos, declarada).
4. El resumen (`unidad_minima_05_banco.json`) y el hash de determinismo se calculan sobre las filas **ordenadas por `(n, idx)`**, nunca sobre el orden del fichero. Si el hash doble ya existía sobre el fichero crudo, se recalcula sobre las filas ordenadas y se anota el cambio.
5. Mirar `sensors` los primeros minutos: si el paquete se pega a 100 °C, bajar a 3 trabajadores. Anotar en el cierre a cuántos corrió y a qué temperatura.
6. **Prohibido** un tope de tiempo por sistema que descarte en silencio: sería seleccionar contra la cola, y la cola es parte de la respuesta de la fase. Si la logística obligara a un tope, el sistema se registra como clase `sin terminar por reloj`, declarada en la ficha **antes** de aplicarla, y cuenta en el denominador.
7. Anotar en `APERTURA_ESCALADO_SIN_AZAR.md`, con fecha, debajo de lo demás: «paralelizado por procesos el 25-oct; verificado idéntico sobre N filas de n=4; no cambia la medida». Es E-13: la corrección va en el sitio.
8. Opcional, decisión de Wis, no tuya: PyPy (no instalado) suele dar ×3–10 en retroceso puro de Python; cambiaría el intérprete registrado (E-01) y habría que repetir la prueba de identidad del punto 1 bajo PyPy.

Esperable: ×3,5–4 neto con cuatro trabajadores a ~3,5–4 GHz; las ~9 h pasan a **2–3 h**, con un piso que fija el peor sistema individual.

---

## 3 · Lo que el `CIERRE_FASE_1.md` tiene que traer (además de la puerta)

Son las cosas que vi en el artefacto en curso y que la puerta, tal como está escrita, no obliga a informar. No cambian la puerta; completan el cierre.

1. **Colas, no sólo medianas.** Por n: mediana, p90, p99 y máximo de `trabajo/vida_len`, de `retrocedidos/vida_len` y de `reloj_s`; y la suma de reloj. En n=6 ya hay p99 = 4224 veces la vida y un sistema de 182 s: si la mediana pasa (iv) y la cola explota en n=8, **no se declara PASS y se sigue**: se nombra la cola como el problema abierto de la fase.
2. **Los 24 sistemas de n=4 con futuro < 1** (mín 0,9933). Son los únicos del banco donde la máquina alternativa importa conductualmente. Qué los distingue: tamaño, clase, qué palabra del futuro falló. Un párrafo con los índices.
3. **La fracción «la vida no determina la verdad» frente a n** (n=3: 31 %; n=4: 37 % de los que tienen distinción; n=6 parcial: 24 %), separada en «dos del mismo tamaño» y «admite una menor». Es el hallazgo de **cobertura** de la fase: el límite de un ser que no elige qué vivir. Se informa como hallazgo, no como fallo, y se deja escrito que es la puerta de entrada de la elección (Fase 2), sin diseñar nada aquí.
4. **La clase inerte como control**: n_min = 1 ⇒ 0 distinciones abiertas en todo el banco (hoy 0 en 19 493). Decirlo con el número.
5. **El cruce**: todos los no coincidentes de n = 3 y 4 cruzados con el retroceso exhaustivo, 100 % coincidencia (hoy 19 344/19 344). Si en algún momento discrepa uno, parar e informar: es el falsador de la reparación.
6. **Si la cola mata la practicabilidad**, el candidato de integración ya está identificado en tu propio gate: **AALpy 2.0.0 (publicada hoy) trae `hW`**, aprendizaje sin reset en la línea Rivest–Schapire, y L# por apartness. Se propone como 1-bis **medido contra este mismo banco**, con la misma puerta, como integración y no como algoritmo nuevo. No se instala ni se escribe nada de eso en esta fase.
7. **Registro de errores.** Desde hoy existe `ERRORES_Y_GUARDAS.md` (14 entradas) y `PLANTILLA_FICHA_APERTURA.md` en este directorio; léelos. El cierre añade las entradas de la Fase 1 con su guarda, al menos: **mutantes que ejerciten el instrumento y no sólo la capacidad** (el oráculo no pasaba por el tope ni por el contador: una unidad con `n_max = 1` debe tocar el tope; un sistema cuyo coste se conozca por construcción debe dar ese coste exacto), y **calibrar el reloj sobre la cola, no sobre 24 muestras** (una calibración de coste se hace sobre los deciles del orden canónico ya recorrido, y se declara su error esperado).
8. **Tiempo de la sesión**: qué parte fue experimento, qué parte instrumento, qué parte custodia (E-14).
9. **Una sola pregunta para Wis** al final. Un commit, al cerrar, cuando Wis lo autorice.

---

## 4 · Lo que no se hace mientras corre

No cambiar L, k, la salida observable ni la puerta. No reescribir predicciones. No instalar AALpy ni `dfa-identify`. No tocar 01–04 (congelados y commiteados). No borrar el JSONL: si hay que relanzar, se reanuda. No commitear hasta el cierre.

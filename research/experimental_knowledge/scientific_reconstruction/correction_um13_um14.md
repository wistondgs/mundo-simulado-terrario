# Corrección primaria: Unidad Mínima 13, 14 y banco madre

**Procedencia:** commit
[`d643be18b2d23b86f934747ad27868770d98e94e`](https://github.com/wistondgs/mundo-simulado-terrario/tree/d643be18b2d23b86f934747ad27868770d98e94e/experiments/unidad_minima_01).
La clasificación anterior `LOCAL_ONLY` para estos tres conjuntos era errónea:
pueden existir variantes locales posteriores, pero los artefactos descritos
aquí son recuperables remotamente y no deben confundirse con ellas.

## Banco madre y Unidad 14

El banco publicado contiene 195 mundos (165 de n=8 y 30 de n=6; proyecto,
líneas 58–62). El resultado de 14 contiene 32 disposiciones × 35 mundos =
1.120 vidas para el banco madre. En
[`unidad_minima_14_disposicion.json`](https://github.com/wistondgs/mundo-simulado-terrario/blob/d643be18b2d23b86f934747ad27868770d98e94e/experiments/unidad_minima_01/artifacts/unidad_minima_14_disposicion.json),
`v512_n256_p2000000` tiene alcance final `0.885714...`, `1.342857...`
olvidos/vida y cuatro paralizadas; `v512_nmaquina+reparacion_p2000000` tiene
`0.685714...`, `2.542857...` y once paralizadas.

**Qué muestra:** bajo este banco y disposición, conservar máquina con reparación
no supera a núcleo 256. **Qué no muestra:** una regla para un organismo futuro:
la unidad no elige (`vivir_simple`) y el tope de 45 s paraliza aprendizaje
(`unidad_minima_14_disposicion_olvido.py:68-70,87-92`). Las diferencias de
paralización son un confusor explícito, no una exclusión.

## Unidad 13

Los artefactos
[`JSON`](https://github.com/wistondgs/mundo-simulado-terrario/blob/d643be18b2d23b86f934747ad27868770d98e94e/experiments/unidad_minima_01/artifacts/unidad_minima_13_tres.json)
y JSONL registran 65 filas agregadas: cinco celdas × cinco generaciones × 13
mundos. En generación 5, TRES tiene `harlow=0`, `vivas=0.5`; DOS,
`harlow=0.384615...`, `vivas=0.653846...`. TRES y `O-todo` coinciden en las
métricas agregadas publicadas para las cinco generaciones.

**Medición:** el código calcula `harlow` como proporción que identifica al final
de la vida (`unidad_minima_13_tres_elementos.py:440-467`), no tasa temprana de
aprendizaje de un mundo nuevo. `muertes_evitadas` incrementa al evitar una
palabra prohibida (`:407-411`); no establece contrafactualmente una muerte.
El control O-todo altera la composición del genoma (`:444`), pero sus métricas
agregadas no discriminan el efecto en esta ejecución.

**Conclusión:** 13 es evidencia exploratoria recuperable de ausencia de ventaja
observable con esas métricas, no evidencia de inutilidad del observador ni de
mejora de aprendizaje generacional. Falta una medida de adquisición temprana,
resultado contrafactual de la palabra evitada y control de exposición/tiempo.

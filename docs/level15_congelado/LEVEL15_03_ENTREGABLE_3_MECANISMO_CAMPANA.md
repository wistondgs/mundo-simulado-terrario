# NIVEL 1.5 — ENTREGABLE 3
## Mecanismo provisional, coaprendizaje y campaña

**Estado:** diseño; todavía NO IMPLEMENTAR.

## 1. Enmienda central

Se retira el decoder Bayes óptimo gratuito como mecanismo del experimento real.

El organismo debe aprender simultáneamente:

1. qué mensaje emitir ante cada estado;
2. cómo interpretar ese mensaje cuando llega una consulta posterior.

Formalmente:

\[
X\xrightarrow{encoder\ aprendido}Z\xrightarrow{1\ tick}(Z,Q)\xrightarrow{decoder\ aprendido}\hat y\xrightarrow{}r\in\{0,1\}.
\]

## 2. Mecanismo mínimo propuesto

Dos tablas de conteo/adaptación:

- tabla de **encoder**: evidencia local para qué mensaje Z emitir en cada X;
- tabla de **decoder**: evidencia local para qué respuesta emitir dado (Z,Q).

No existen etiquetas H1/H2/H3 dentro del learner.

El mecanismo debe poder expresar cualquier encoder determinista de las 16 entradas a los 4 mensajes. La semántica de los mensajes es opaca y co-emerge con el decoder.

## 3. Contrato de crédito

Por ensayo:

\[
1\ presentación\to1\ mensaje\to1\ tick\to1\ consulta\to1\ respuesta\to1\ bit.
\]

Se actualiza exactamente una elección del encoder y una elección del decoder por ensayo.

Nunca se prueba una alternativa sobre el mismo ensayo.

## 4. Invariante contable

Tras N ensayos válidos:

- actualizaciones del encoder = N;
- actualizaciones del decoder = N.

En el piloto de 100.000 ensayos se midió exactamente:

- encoder: 100.000 actualizaciones;
- decoder: 100.000 actualizaciones.

Tocar más de una celda de cualquiera de las tablas por ensayo viola el contrato local de crédito.

## 5. Exploración

Programa principal propuesto:

\[
\epsilon:0.30\to0.02
\]

decreciente durante la campaña.

**Este programa es una elección de diseño, no una derivación matemática.**

Debe existir un programa alternativo preregistrado como análisis de sensibilidad. Si la clase informacional cambia sistemáticamente con el programa, el resultado debe etiquetarse como dependiente de exploración.

## 6. Piloto de coaprendizaje

Resultados exploratorios:

| Presupuesto | R_G → H1 | R_P → H2 | R_J → H3 |
|---:|---:|---:|---:|
| 20.000 | 65 % | 62 % | 78 % |
| 100.000 | 78 % | 70 % | 78 % |
| 400.000 | 80 % | 65 % | 85 % |

Referencia idealizada con decoder óptimo:

| Idealizado | 79 % | 82 % | 85 % |

## 7. Presupuesto seleccionado

Se propone:

\[
\boxed{100.000\ ensayos\ por\ corrida}
\]

porque 20k→100k produce mejora material y 100k→400k muestra aplanamiento/no mejora sistemática; R_P incluso empeora en el piloto.

Esto es una **selección empírica por saturación**, no una derivación matemática.

## 8. Repeticiones

Se propone:

\[
\boxed{40\ repeticiones\ por\ régimen}
\]

idealmente organizadas como 40 tripletes emparejados R_G/R_P/R_J con la misma inicialización de partida.

Total FULL propuesto: 120 corridas.

## 9. Endpoint primario

La variable primaria es la **clase informacional** del encoder final, determinada sólo después del aprendizaje mediante un clasificador diagnóstico invariante a relabeling de mensajes.

El learner nunca ve el clasificador.

Resultados secundarios:

- pérdida poblacional exacta;
- óptimo global sí/no;
- óptimo local exacto sí/no;
- movimientos/actualizaciones;
- consumo de ensayos;
- trayectoria de coordinación encoder↔decoder.

## 10. Dificultad por régimen — estatus

El piloto de coaprendizaje muestra que R_P es el peor de los tres en 20k, 100k y 400k.

Se puede preregistrar como predicción secundaria débil:

> R_P tenderá a ser el régimen más difícil.

No se sella una explicación causal. La hipótesis anterior de “rendimientos decrecientes de proximidad / gradiente más plano” queda fuera del preregistro porque no está demostrada y el fallo dominante resultó ser de coordinación.

No se sella un orden estricto R_P > R_G > R_J porque a 100k R_G y R_J empatan aproximadamente.

## 11. Sensibilidad a exploración

Interpretación preregistrada:

- si cambia principalmente la tasa de éxito pero se conserva el enriquecimiento de clase por régimen, la adquisición sobrevive y cambia la eficiencia de optimización;
- si cambia sistemáticamente qué clase se aprende, marcar `EXPLORATION_DEPENDENT_REPRESENTATION`.

## 12. Estado

El mecanismo de dos tablas es el candidato mínimo vigente. Todavía requiere preregistro final de actualización exacta, semillas, programa alternativo de exploración, clasificador de clase y gates antes de autorizar implementación.

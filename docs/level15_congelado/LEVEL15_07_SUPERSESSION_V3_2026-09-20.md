# NIVEL 1.5 — SUPERSESIÓN v3 · RECONCILIACIÓN DE PILOTO, SEMILLAS Y PRESUPUESTO

**Fecha:** 2026-09-20  
**Estado:** diseño/piloto; Nivel 1.5 sigue sin rama, carpeta ni código de implementación.  
**Autoridad:** este documento supersede las afirmaciones incompatibles de `LEVEL15_06_SUPERSESSION_2026-09-20.md` y de los documentos 01–05. No reescribe el snapshot histórico.

## 0. Regla de archivo

La versión v2 permanece congelada y verificable.

SHA-256 del paquete v2:

`ab7785bbe76acb421fe59a7fb77574d823e5bddfafd2b7cff91b7557e03bc7ab`

SHA-256 de la supersesión v2:

`3d5632d99b659565273b7f1b844152618ecd27fb5bf4a1605e3406f3f713ede6`

Los documentos 01–06 incluidos en este paquete v3 son copias byte-idénticas de v2. La corrección se hace mediante supersesión explícita, no mediante edición retroactiva.

---

## 1. Reconciliación cerrada de las 540 corridas

La discrepancia `PENDING_RECONCILIATION` de v2 queda cerrada. El piloto usó tres semillas, tres presupuestos, tres regímenes y 20 repeticiones por celda:

`3 × 3 × 3 × 20 = 540` corridas.

Agregados por presupuesto:

| presupuesto | R_G | R_P | R_J | total |
|---:|---:|---:|---:|---:|
| 10.000 | 59/60 | 55/60 | 60/60 | 174/180 = 96,67 % |
| 20.000 | 57/60 | 60/60 | 59/60 | 176/180 = 97,78 % |
| 100.000 | 60/60 | 59/60 | 60/60 | 179/180 = 99,44 % |
| **TOTAL** | 176/180 | 174/180 | 179/180 | **529/540 = 97,96 %** |

La fila que faltaba en v2 era:

`20.000 → R_G 57/60 · R_P 60/60 · R_J 59/60 · total 176/180`.

---

## 2. Retirada definitiva de una dificultad especial de R_P

La formulación de v2 que describía una desventaja transitoria de `R_P` queda retirada.

Los tres presupuestos no muestran un orden estable de dificultad:

- a 10.000: `R_P` queda por debajo de `R_G` y `R_J`;
- a 20.000: `R_P` es el mejor de los tres;
- a 100.000: las diferencias prácticamente desaparecen.

La única celda individual por debajo de `19/20` entre las 27 celdas es:

`seed 777 · 10.000 · R_P = 17/20`.

La formulación canónica pasa a ser:

> **No se observa una dificultad estructural ni un orden estable de dificultad para `R_P`. La celda baja de `17/20` a 10.000 no autoriza una explicación causal del régimen y es compatible con variación del piloto.**

Por tanto se retiran también como preguntas abiertas vigentes:

- “¿por qué `R_P` es más difícil?”;
- la hipótesis no verificada de rendimientos decrecientes o gradiente más plano de proximidad.

No entran al preregistro confirmatorio.

---

## 3. Qué significan ahora las 540 corridas

Las 540 corridas son exclusivamente:

`PILOT / DISCOVERY`.

No forman parte del endpoint confirmatorio futuro.

Lo que apoyan es que, con la regla de paso constante probada, la misma arquitectura de dos tablas alcanza con alta frecuencia la clase informacional alineada al régimen.

No convierten el resultado en una identidad arquitectónica. El mecanismo no contiene las reglas:

- `R_G → H1`;
- `R_P → H2`;
- `R_J → H3`.

Las clases siguen siendo regiones diagnósticas del espacio completo de encoders y no acciones disponibles para el organismo.

Formulación canónica del Nivel 1.5:

> **La misma arquitectura aprende a preservar información diferente según lo que la experiencia hace útil.**

---

## 4. Presupuesto confirmatorio

La justificación anterior de `100.000` ensayos por saturación queda retirada porque dependía de una regla de actualización ya supersedida.

Con paso constante:

- 10.000 ensayos ya producen `174/180 = 96,67 %`;
- 20.000 producen `176/180 = 97,78 %`;
- 100.000 producen `179/180 = 99,44 %`.

Para no añadir una segunda pregunta científica al decimal, se adopta:

`N_train = 10.000` ensayos por corrida confirmatoria.

La interpretación autorizada es únicamente:

> **10.000 es el presupuesto piloto más bajo ya demostrado con alta tasa de alineación.**

No se afirma:

- que 10.000 sea mínimo;
- que sea óptimo;
- que presupuestos menores no funcionen.

Medir la curva de dosis por debajo de 10.000 queda como opción separada. Puede hacerse con las semillas de diseño ya quemadas y no necesita consumir semillas confirmatorias, pero no forma parte de la pregunta primaria de Nivel 1.5.

---

## 5. Colisión conocida de semilla de diseño

La semilla piloto:

`20260920`

colisiona numéricamente con la ventana registrada del Nivel 1.0:

`20260919 … 20260950`.

La colisión queda registrada como **conocida y sin efecto científico identificado**, porque los usos fueron distintos:

- en Nivel 1.0 alimentó el generador NumPy que construía mundos/cuerpos;
- en el piloto de Nivel 1.5 alimentó `random.Random` de Python para estados/exploración.

Son generadores distintos y papeles experimentales distintos. No se infiere contaminación estadística por compartir el entero.

La consecuencia es archivística: la semilla debe figurar explícitamente como reutilización histórica para que no parezca una omisión del libro de semillas.

---

## 6. Semillas de diseño quemadas

Quedan clasificadas como `PILOT / DESIGN / BURNED` y prohibidas en la campaña confirmatoria:

- `20260920`;
- `777`;
- `31337`.

No deben reutilizarse para estimar el endpoint confirmatorio de Nivel 1.5.

---

## 7. Semillas confirmatorias reservadas

Se reserva la serie:

`130000011 … 130000026`

Total:

`16` semillas confirmatorias.

El chequeo reportado incluye los desplazamientos `+7` y no encuentra colisión con las semillas registradas previamente.

Cada semilla produce un triplete emparejado:

- `R_G`;
- `R_P`;
- `R_J`.

Total previsto:

`16 × 3 = 48` corridas confirmatorias.

Con `10.000` ensayos por corrida:

`480.000` ensayos totales de adquisición confirmatoria.

Las 540 corridas piloto no se mezclan con estas 48 corridas.

---

## 8. Decisiones canónicas de Nivel 1.5 · numeración reconciliada

Esta lista reemplaza cualquier lista previa con huecos de numeración.

1. **Nivel 1.5 se mantiene**: selección de información bajo capacidad temporal limitada.
2. **Mecanismo mínimo candidato**: encoder y decoder aprendidos mediante dos tablas de conteo/valor local.
3. **Actualización**: paso constante; la variante exacta debe quedar sellada en el preregistro antes de implementar.
4. **Feedback**: `1 ensayo → 1 retención → 1 respuesta → 1 bit`, sin crédito contrafactual.
5. **Presupuesto confirmatorio operativo**: `10.000` ensayos por corrida como *lowest demonstrated pilot budget*, no como mínimo teórico.
6. **Endpoint primario**: clase informacional aprendida.
7. **Óptimo exacto**: resultado secundario.
8. **Las 540 corridas actuales son PILOT/DISCOVERY** y no participan en la estimación confirmatoria.
9. **Curva de dosis sub-10k**: opción declarada, barata y realizable con semillas quemadas; no forma parte del decimal actual.
10. **Semillas confirmatorias**: `130000011 … 130000026`, 16 tripletes emparejados.
11. **No existe dificultad especial preregistrada de `R_P`** ni orden de dificultad entre regímenes.
12. **No se preregistra una frecuencia de “barreras de coordinación”** a partir de reglas de actualización ya supersedidas.
13. **No se afirma presupuesto mínimo**; 10k es únicamente el menor presupuesto piloto ya demostrado.
14. **H1/H2/H3 siguen siendo diagnósticos externos**, nunca acciones, labels ni opciones del learner.
15. **Las tres fugas permanecen cerradas por contrato**: decoder sólo `(z,q)`, una actualización por tabla/ensayo y tablas read-only durante el intervalo.

---

## 9. Qué permanece intacto del Entregable 1

Nada de esta supersesión modifica:

- `16 estados → 4 mensajes`;
- presupuesto abstracto de 2 bits;
- clases diagnósticas H1/H2/H3;
- matriz de pérdidas;
- óptimos `1/8`, `1/8`, `1/10`;
- techo de representación fija `L ≥ 1/3`;
- selector ideal `7/60`;
- lema combinatorio;
- isomorfismo de las nueve variantes de `J`;
- cierre del encoder estocástico por convexidad.

Estas son propiedades del constructo, no del piloto de optimización.

---

## 10. Qué permanece abierto antes de preregistro final

1. fijar y documentar la magnitud exacta del paso constante;
2. fijar el programa exacto de exploración y su control de sensibilidad;
3. congelar el clasificador posterior de clases;
4. congelar gates y fixtures negativas;
5. sellar el protocolo confirmatorio sobre las 16 semillas reservadas;
6. mantener separación explícita entre validity gates y resultado científico.

Hasta entonces:

`NO IMPLEMENTAR`.

---

## 11. Claim conceptual provisional

La formulación breve de la adquisición es:

> **La misma arquitectura aprende a preservar información diferente según lo que la experiencia hace útil.**

La campaña confirmatoria deberá determinar si ese fenómeno se reproduce en semillas no utilizadas durante el diseño, con mecanismo y protocolo congelados previamente.

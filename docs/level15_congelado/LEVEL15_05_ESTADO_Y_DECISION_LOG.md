# NIVEL 1.5 — ESTADO CANÓNICO Y DECISION LOG

**Fecha:** 2026-09-20

## 1. Estado del proyecto

Nivel 1.5 está exclusivamente en fase de diseño y validación matemática.

Actualmente NO existe:

- código de Nivel 1.5;
- carpeta de Nivel 1.5;
- rama de Nivel 1.5;
- preregistro implementable definitivo;
- autorización de implementación.

## 2. Precondición acumulativa

El organismo previo disponible conceptualmente contiene:

\[
B+Q+H+M+\psi.
\]

La fusión fue verificada antes de abrir 1.5.

## 3. Capacidad adjudicada

\[
\boxed{\text{Nivel 1.5 = selección de información bajo capacidad temporal limitada}}
\]

Pregunta:

> ¿Puede aprender qué información conservar cuando no puede conservarla toda?

La candidata “detección de cambio” queda provisionalmente desplazada a Nivel 1.6.

## 4. Decisiones adjudicadas

1. **Resultado primario:** clase informacional aprendida.
2. **Óptimo exacto:** resultado secundario.
3. **Feedback:** un bit `acierto/error` por ensayo.
4. **Contrato:** un ensayo → una retención → una respuesta → un bit.
5. **Prohibición:** ninguna reevaluación contrafactual del mismo ensayo.
6. **H1/H2/H3:** regiones diagnósticas; nunca opciones/acciones del agente.
7. **Decoder gratuito:** retirado del experimento real; encoder y decoder deben co-aprender.
8. **Mecanismo candidato:** dos tablas de aprendizaje local, una de emisión y una de lectura.
9. **Presupuesto candidato:** 100.000 ensayos por corrida, seleccionado empíricamente por saturación del piloto.
10. **Repeticiones candidatas:** 40 por régimen, preferentemente tripletes emparejados.
11. **Exploración:** programa principal 0.30→0.02 declarado como elección de diseño y sometido a sensibilidad.

## 5. Decisiones retiradas/corregidas

### Retirada 1

`15–21 % de óptimos locales` NO describe el experimento real. Procedía del escenario idealizado con decoder óptimo.

### Retirada 2

La mayoría de los fallos NO son óptimos locales exactos. A 100k/40 repeticiones por régimen, de 30 fallos sólo 9 son óptimos locales; 21 son fallos de coordinación no-local-optimum.

### Retirada 3

La firma Σ=12 no basta para concluir “atrapamiento”. Debe verificarse optimalidad local caso por caso.

## 6. Evidencia piloto vigente

Tasas de llegada a la clase esperada:

| Presupuesto | R_G | R_P | R_J |
|---:|---:|---:|---:|
| 20k | 65 % | 62 % | 78 % |
| 100k | 78 % | 70 % | 78 % |
| 400k | 80 % | 65 % | 85 % |

A 100k y 40 repeticiones:

| Régimen | Llegó | Óptimo local | Coordinación/no óptimo local |
|---|---:|---:|---:|
| R_G | 31/40 | 1/40 | 8/40 |
| R_P | 28/40 | 4/40 | 8/40 |
| R_J | 31/40 | 4/40 | 5/40 |

## 7. Predicción secundaria permitida

Puede preregistrarse como expectativa de piloto:

> R_P tenderá a ser el régimen más difícil.

No se conoce la causa. No se afirma un orden estricto entre R_G y R_J.

## 8. Tres fugas críticas ya auditadas conceptualmente

1. **Decoder side information:** decoder sólo `(z,q)`.
2. **Counterfactual credit:** una actualización de encoder + una de decoder por ensayo.
3. **Temporal side channel:** tablas read-only entre retención y respuesta.

## 9. Próximo trabajo antes del código

Cerrar un preregistro final que especifique:

- regla exacta de actualización de ambas tablas;
- schedule exacta de exploración y programa alternativo;
- semillas;
- construcción exacta de los 40 tripletes;
- clasificador de clases invariante a relabeling;
- gates y fixtures negativas;
- definición operativa de fallo de coordinación;
- separación entre validity gates y resultado científico;
- fingerprints/pasividad/RNG;
- claim máximo permitido.

Hasta entonces:

\[
\boxed{\text{NO IMPLEMENTAR}}
\]

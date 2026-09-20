# NIVEL 1.5 — ENTREGABLE 2
## Aprendibilidad sin entregar H1/H2/H3

**Estado:** piloto/diseño. No existe implementación de Nivel 1.5.

## 1. Espacio de hipótesis

El organismo no elige entre tres estrategias nombradas. El espacio es el conjunto completo de funciones:

\[
f:\{16\ estados\}\to\{4\ mensajes\}
\]

con cardinalidad:

\[
4^{16}=4.294.967.296.
\]

H1, H2 y H3 son regiones diagnósticas posteriores de ese espacio.

## 2. Vecindad local

Un encoder tiene 48 vecinos elementales:

\[
16\ estados\times3\ mensajes\ alternativos.
\]

Cada movimiento cambia un único estado a un único mensaje alternativo.

## 3. Piloto idealizado con decoder óptimo gratuito

Con búsqueda local desde inicializaciones aleatorias y decoder Bayes óptimo suministrado, 2.000 reinicios exploratorios produjeron aproximadamente:

| Régimen | Tasa de alcanzar el óptimo/clase esperada |
|---|---:|
| R_G | 79.1 % |
| R_P | 82.2 % |
| R_J | 85.0 % |

Media aproximada: ~11 movimientos aceptados.

Estas cifras pertenecen a un **problema idealizado** porque el decoder ya sabía interpretar los mensajes. No deben trasladarse como tasas esperadas al experimento real con coaprendizaje encoder↔decoder.

## 4. Coste de resolver mejoras locales

Piloto de crédito:

- mejora mediana aceptada: \(\Delta\approx0.04375\) → escala ~520 ensayos;
- mejora mínima observada: \(\Delta=0.00625\) → escala ~25.600 ensayos.

La separación entre clases (~0.20) es mucho más gruesa que el último refinamiento local (~0.00625).

## 5. Decisión primaria — ADJUDICADA

\[
\boxed{\text{resultado primario = clase informacional aprendida}}
\]

El óptimo exacto queda como resultado secundario.

La motivación es científica: 1.5 pregunta qué información termina preservándose, no si el algoritmo de búsqueda exprime el último incremento numérico.

## 6. Feedback mínimo — ADJUDICADO

Contrato:

\[
\boxed{1\ ensayo\to1\ retención\to1\ respuesta\to1\ bit}
\]

El bit informa únicamente `acierto/error`.

Está prohibido:

- revelar la respuesta correcta;
- reevaluar el mismo ensayo con otra retención;
- comparar dos mensajes sobre el mismo (X,Q);
- entregar ranking contrafactual;
- entregar H1/H2/H3 como acciones.

La reevaluación contrafactual del mismo ensayo constituye fuga de crédito.

## 7. Corrección de la expectativa 15–21 %

La banda 15–21 % provino del piloto idealizado con decoder óptimo. **Queda retirada como expectativa del experimento real de coaprendizaje.**

No debe confundirse:

1. no alcanzar la clase esperada;
2. terminar en un óptimo local exacto del objetivo verdadero;
3. detenerse por una barrera de coordinación encoder↔decoder.

Estas tres categorías se separan explícitamente en los documentos posteriores.

## 8. Estatus epistemológico

La globalidad de los óptimos R_G/R_P/R_J se sostiene en el argumento analítico y el lema exhaustivo del Entregable 1. Los reinicios numéricos son corroboración de aprendibilidad/dinámica, no prueba de globalidad.

# NIVEL 1.5 — AUDITORÍA DE FUGAS Y BARRERAS DE COORDINACIÓN

**Estado:** auditoría conceptual/piloto; no existe implementación de Nivel 1.5.

## 1. Corrección material sobre los fallos

Se había sugerido interpretar los fallos de coaprendizaje como óptimos locales con firma estructural Σ=12.

Esa afirmación queda **RETIRADA**.

Verificación caso por caso sobre 40 repeticiones por régimen a 100.000 ensayos:

| Régimen | Llegó a clase esperada | Óptimo local exacto | Ni llegó ni es óptimo local |
|---|---:|---:|---:|
| R_G | 31/40 | 1/40 | 8/40 |
| R_P | 28/40 | 4/40 | 8/40 |
| R_J | 31/40 | 4/40 | 5/40 |

Totales:

- fallos de llegar: 30;
- óptimos locales exactos entre esos fallos: 9;
- fallos que NO son óptimos locales: 21.

Por tanto la mayoría de los fallos no son atrapamiento por el paisaje del encoder.

## 2. Diagnóstico actual

En esos 21 casos existe al menos un cambio elemental del encoder que mejoraría el objetivo verdadero, pero el aprendiz no lo toma.

La explicación operacional es una **barrera de coordinación encoder↔decoder**:

- mover un estado a otro mensaje puede empeorar mientras el decoder conserve la convención anterior;
- cambiar el decoder puede empeorar mientras el encoder siga usando la convención anterior;
- el bit local no revela directamente la mejora conjunta contrafactual.

Esta barrera no existía en el piloto con decoder óptimo gratuito.

## 3. Consecuencia para el preregistro

No preregistrar “15–21 % de óptimos locales” para el experimento real.

Separar siempre tres resultados:

1. tasa de clase esperada;
2. tasa de óptimo local exacto;
3. tasa de fallo de coordinación no-local-optimum.

La firma Σ=12 puede aparecer, pero no demuestra por sí sola atrapamiento.

## 4. Fuga A — decoder

El decoder debe aceptar exclusivamente:

\[
(z,q)
\]

y producir una respuesta.

No acepta x, no acepta registro de ensayo, no acepta una estructura q que contenga la respuesta.

Contrato:

- q es sólo una etiqueta de tipo de consulta;
- la firma de lectura es `(z, q)` y nada más.

Riesgos a bloquear:

- pasar x “sólo para logging”;
- empaquetar respuesta correcta dentro de q;
- dejar accesible el input original desde el decoder.

## 5. Fuga B — crédito contrafactual

Invariante conductual:

\[
\#updates_{encoder}=\#trials
\]

\[
\#updates_{decoder}=\#trials.
\]

Cada ensayo toca una sola elección/celda de cada tabla.

Medido en piloto de 100.000 ensayos:

- encoder = 100.000 actualizaciones;
- decoder = 100.000 actualizaciones.

Cualquier algoritmo que actualice mensajes alternativos, respuestas alternativas o varias celdas por ensayo rompe este contrato.

## 6. Fuga C — side channel durante el intervalo

El riesgo real no es sólo el token z. Las tablas mismas pueden actuar como memoria si se escriben entre retención y respuesta.

Contrato temporal:

1. presentación;
2. encoder produce z;
3. desde ese instante hasta emitir la respuesta, todas las estructuras aprendibles quedan read-only;
4. llega q;
5. decoder responde usando sólo (z,q);
6. se produce el bit;
7. sólo entonces pueden ocurrir las dos actualizaciones locales.

La huella de las tablas debe permanecer idéntica durante el intervalo.

## 7. Resultado de la auditoría de las tres fugas

Las tres fugas son cerrables con contratos estructurales/conductuales:

- decoder limitado a `(z,q)`;
- conteo exacto de una actualización por tabla por ensayo;
- huella inmutable de ambas tablas durante el intervalo.

No se ha identificado una contradicción conceptual que invalide 1.5.

## 8. Pregunta causal abierta

R_P aparece sistemáticamente como el régimen más difícil en los tres presupuestos piloto. La causa NO está establecida.

La explicación previa basada en rendimientos decrecientes/gradiente más plano queda como hipótesis no verificada y no entra en el preregistro.

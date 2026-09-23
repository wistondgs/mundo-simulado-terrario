# ETP-EXP-02 · External Data Restoration / Termination Release

EXP-01 closing commit: **c19a0a28415b0ffa96cb9d3247249b89ae942558**  
Estado: **EXP-02 ejecutado exhaustivamente sobre A / P-DATA autorizado**.

Pregunta: desde el punto fijo creado por ACTION_CUT, ¿restaurar sólo DATA al
blanco original libera D/E/L y permite q*=0? Es una prueba de mediación, no de
entidad.

## Diseño

Para cada una de las ocho P-DATA:

1. se reprodujo ACTION_CUT hasta z_cut_4;
2. se verificó q_cut_4 igual a q_natural_4;
3. se usaron cuatro brazos: NATURAL, ACTION_CUT_ONLY, NO_OP_WRITE y
   TARGET_RESTORATION;
4. TARGET_RESTORATION escribió sólo x=blanco en t4 y preservó q bit a bit;
5. G se reanudó sin cambio y se usó detección exacta de repetición.

Artefactos:

- [run_exp02_external_repair.py](run_exp02_external_repair.py)
- [trazas completas](artifacts/exp02_external_repair_traces.csv)
- [resumen de 32 brazos](artifacts/exp02_external_repair_summary.csv)
- [aristas efectivas](artifacts/exp02_effective_edges.csv)

## Chequeo crítico de identidad

| comprobación | 8 de 8 |
| --- | --- |
| q_cut_4 = q_natural_4 | sí |
| x_cut_4 distinto de x_natural_4 | sí |
| x_natural_4 = blanco | sí |
| P en z_cut_4 | 0000 |
| D/E/L no basal en z_cut_4 | sí |
| q se preserva durante TARGET_RESTORATION | sí |
| estado reparado en t4 = estado natural en t4, 21/21 bits | sí |

TARGET_RESTORATION se etiqueta NATURAL_STATE_REJOIN: no inyecta un patrón
arbitrario, vuelve a una observación natural ya verificada.

## Resultados de los brazos

| brazo | n | DATA recovery | full recovery | desenlace |
| --- | ---: | ---: | ---: | --- |
| NATURAL | 8 | 4 | 7 | blanco full original |
| ACTION_CUT_ONLY | 8 | no ocurre | no ocurre | punto fijo no objetivo desde t4 |
| NO_OP_WRITE | 8 | no ocurre | no ocurre | mismo punto fijo que ACTION_CUT_ONLY |
| TARGET_RESTORATION | 8 | 4 | 7 | blanco full original |

NO_OP_WRITE excluye que el mecanismo de escritura explique la relajación.

## Relajación temporal

En TARGET_RESTORATION, las coordenadas que estaban no basales en t4 siguen
exactamente la cola natural:

| familia | retorno basal de las coordenadas activas |
| --- | --- |
| D | t5 |
| E | t6 |
| L | t7 |
| P | ya 0000 en t4 y permanece 0000 |

No apareció un segundo pulso P. ACTION_CUT_ONLY y NO_OP_WRITE conservaron D/E/L
no basales en su punto fijo, mientras que TARGET_RESTORATION —con el mismo q en
t4— alcanzó q*=0 en t7.

## Comparación con la predicción

La predicción preregistrada se confirmó en los ocho casos:

x externo restaurado en t4 + q_cut_4 preservado = estado natural t4; G desde
ahí reproduce D abajo en t5, E abajo en t6, L abajo en t7 y recuperación full
en t7. No hubo timeout, attractor alternativo ni anomalía de control.

## Claims permitidos

**A_EXTERNAL_DATA_RESTORATION_SUFFICIENT_FOR_AUXILIARY_RELAXATION_FROM_ACTION_CUT_STATE**  
Estatus: INSTANCE_CAUSAL.  
Alcance: A; ocho P-DATA autorizadas; estado post-ACTION_CUT t4; escritura
externa de DATA al blanco conservando q.

**A_DATA_RESTORATION_CAUSALLY_MEDIATES_D_E_L_TERMINATION_AFTER_RAAC**  
Estatus: INSTANCE_CAUSAL.  
Alcance: A; ocho P-DATA autorizadas; D/E/L posteriores al pulso RAAC.

El segundo claim combina EXP-01 y EXP-02: retirar la única acción p→x deja
D/E/L sostenidos; reponer sólo x, con q idéntico, restablece su relajación.
No incluye P: EXP-01 mostró que P termina aunque DATA no se recupere.

## Dos clases de terminación

1. **PULSE TERMINATION**: P cesa porque L alcanza E. No requiere que x se
   recupere.
2. **SUPPORT TERMINATION**: D/E/L cesan cuando x corregida elimina el
   desacuerdo que las sostiene.

No se fusionan bajo una única explicación de terminación.

## Límites y siguiente paso

No se establece entidad, proto-orgánulo, emergencia, autonomía, intención,
sensing, conocimiento o generalización. H0–H3 siguen abiertas.

Propuesta, no ejecutada: EXP-03 ONSET BLOCK, para separar la necesidad del
onset de la necesidad de la arista de acción ya establecida.


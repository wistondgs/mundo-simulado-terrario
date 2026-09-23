# ETP-EXP-01 · Surgical RAAC Action Cut

Pre-EXP baseline commit: **68119ce68ea4ac8e0cf861b04ffd7225fff98941**  
Estado: **EXP-01 ejecutado exhaustivamente sobre A / P-DATA autorizado**.

Pregunta: ¿la arista directa observada en PRE-01, p_i(t=3) → x_i(t=4), es
necesaria para reconstrucción DATA y para el retorno full normal? Este
experimento no pregunta por entidad.

## Diseño y aislamiento

Para cada una de las ocho trayectorias P-DATA se dejó correr G sin cambio hasta
z3. La intervención de ACTION_CUT cambió sólo la salida x_i de la transición
t3→t4: x_i(t+1)=x_i(t), manteniendo p_i(t3)=1 dentro de q y dejando toda otra
coordenada igual a G(z3). Desde t4 se restauró G intacta.

Se ejecutaron cuatro brazos por trayectoria: NATURAL, TEMPORAL_SHAM (misma
arista t2 cuando p_i=0), SPATIAL_SHAM (arista p_j→x_j en t3 con p_j=0) y
ACTION_CUT. No se ejecutó ninguna otra familia de intervención.

El instrumento y artefactos son:

- [run_exp01_action_cut.py](run_exp01_action_cut.py)
- [trazas completas](artifacts/exp01_action_cut_traces.csv)
- [resumen de 32 brazos](artifacts/exp01_action_cut_summary.csv)
- [aristas efectivas por transición](artifacts/exp01_effective_edges.csv)

## Controles

| brazo | n | DATA recovery | full recovery | desenlace |
| --- | ---: | ---: | ---: | --- |
| NATURAL | 8 | 4 | 7 | blanco full original alcanzado |
| TEMPORAL_SHAM | 8 | 4 | 7 | idéntico a NATURAL |
| SPATIAL_SHAM | 8 | 4 | 7 | idéntico a NATURAL |
| ACTION_CUT | 8 | no ocurre | no ocurre | repetición exacta desde t4, ciclo de longitud 1 |

Los dos sham y el natural reproducen PRE-01 para las ocho trayectorias. Por
tanto no apareció confusión temporal, espacial ni de la maquinaria de corte.

## Integridad del corte

En los ocho ACTION_CUT:

- z3 es idéntico a la trayectoria natural;
- p_i(t3)=1, observable y sin modificación;
- la arista congelada p_i→x_i era contextualmente efectiva y RAAC bajo G;
- la transición realizada no tiene RAAC: x_i queda como x_i(t);
- se retiró una sola arista efectiva, p_i→x_i;
- todas las otras actualizaciones t3→t4 son iguales a G;
- desde t4 se usa G sin cambio.

Así, el brazo corta un efecto de arista, no el estado fuente ni la organización
auxiliar observada.

## Resultado ACTION_CUT

| clase PRE-01 | trayectorias | estado fijo desde t4: x | D | E | L | P |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | 0000:x1, 0000:x2, 1111:x1, 1111:x2 | x inicial perturbada | tres desacuerdos | evento correspondiente | carry correspondiente | 0000 |
| A2 | 0000:x3, 1111:x3 | x inicial perturbada | 01100 | 0010 | 0010 | 0000 |
| A3 | 0000:x4, 1111:x4 | x inicial perturbada | 00011 | 0001 | 0001 | 0000 |

Las clases complementarias tienen q idéntico y x complementaria. La tabla
completa conserva los valores por coordenada.

Secuencia post-corte común: t3 conserva D/E/L/P naturales, incluido p_i=1.
En t4, x queda perturbada y p_i pasa a 0 porque L_i ya es 1. D, E y L siguen
no basales. G aplicado desde t4 reproduce exactamente el mismo estado en t5:
es un punto fijo, no una clasificación por timeout. No aparece un segundo pulso
p_i tras t3.

## Comparación con predicción preregistrada

La predicción se confirmó en los ocho casos:

1. x permaneció perturbada en t4.
2. L ya había registrado E.
3. P volvió a cero.
4. D, E y L permanecieron no basales.
5. No hubo segundo pulso correctivo.
6. Se alcanzó x distinto de blanco, q distinto de q*, P=0, como punto fijo.

La descripción no implica intención, memoria, deseo, frustración ni fallo de
entidad.

## Claims permitidos

**A_DIRECT_RAAC_EDGE_NECESSARY_FOR_PDATA_RECONSTRUCTION**  
Estatus: INSTANCE_CAUSAL.  
Alcance: espécimen A; las ocho trayectorias P-DATA autorizadas; transición
p_i(t3) → x_i(t4); controles temporal y espacial definidos arriba.

**A_ACTION_EDGE_IS_CAUSALLY_UPSTREAM_OF_NORMAL_FULL_TERMINATION**  
Estatus: INSTANCE_CAUSAL.  
Alcance idéntico: sin esa arista, las ocho trayectorias no alcanzan q*=0.

No se afirma que reconstrucción DATA cause terminación: ACTION_CUT no restaura
x por separado. Esa mediación requiere el posterior EARLY EXTERNAL REPAIR.

## Límites y siguiente paso

H0, H1, H2 y H3 permanecen abiertas. EXP-01 caracteriza arquitectura causal,
no entidad. No hay anomalías ni sham divergentes.

Propuesta, no ejecutada: EXP-02 EARLY EXTERNAL REPAIR. Tras ACTION_CUT, fijar
externamente x en el blanco original y observar si la cadena D→E→L se relaja.


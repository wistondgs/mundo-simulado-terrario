# Preregistro · ETP-EXP-04A · Effector Output Remapping

Estado: **PREREGISTERED BEFORE EXECUTION**  
Commit de cierre EXP-03: **e559326fd348ddc7b9e4004e762d688cd742e4c1**.

## Pregunta y alcance

¿Cuánto de la dirección reconstructiva inmediata está suministrado por el
cableado efector final P_i→x_i? El experimento mantiene selección de fuente
D/E/P y modifica sólo el destino de la acción del único pulso activo durante
t3→t4. No adjudica dónde reside toda la dirección reconstructiva ni entityhood.

## Especimen congelado

A: x1..x4; D=d12,d13,d23,d14,d24; E=e1..e4; L=l1..l4; P=p1..p4; 21
coordenadas, q*=0^17, blancos (0000,q*) y (1111,q*). G es síncrona,
determinista, homogénea en el tiempo y conserva las ecuaciones congeladas:

- D son XOR de los pares declarados.
- E son las cuatro AND de D declaradas.
- L_i'=E_i; P_i'=E_i AND NOT L_i.
- x_i'=x_i XOR P_i.

EXP-04A no cambia G; construye una capa externa de routing para una transición.

## Casos autorizados y tabla de direcciones

| error | clase | D t1 | E t2 | P t3 | destino natural |
| --- | --- | --- | --- | --- | --- |
| x1 | A1 | 11010 | e1 | p1 | x1 |
| x2 | A1 | 10101 | e2 | p2 | x2 |
| x3 | A2 | 01100 | e3 | p3 | x3 |
| x4 | A3 | 00011 | e4 | p4 | x4 |

Cada relación se ejecuta con blancos 0000 y 1111: ocho P-DATA en total.
Prerrequisito: UNIQUE_ACTIVE_PULSE=8/8, con exactamente P_i activo en t3 para
el error x_i.

## Diseño de 48 corridas

| brazo | n | routing |
| --- | ---: | --- |
| N NATURAL | 8 | G sin intervención |
| I IDENTITY | 8 | R(i,i), routing experimental al destino natural |
| C NULL | 8 | ninguna coordenada DATA recibe el pulso |
| R WRONG | 24 | cada R(i,j), i distinto de j |

La matriz R tiene 16 celdas fuente/destino; cada una ocurre en ambos contextos
de blanco. Hay 8 diagonales y 24 off-diagonales, más 8 N y 8 C.

## Semántica de intervención

Para cada condición, correr G hasta z3 y calcular z4_nat=G(z3). Copiar q4_nat
bit a bit. Construir únicamente la porción DATA de z4:

- I: x4=x4_nat; el estado completo debe ser idéntico a natural.
- C: deshacer sólo el flip natural de x_i; debe reproducir EXP-01.
- R(i,j): deshacer el flip de x_i y aplicar ese flip a x_j.
- N: usar z4_nat.

Desde t4 en adelante se retira el routing y se usa G canónica. Ninguna AUX se
modifica directamente.

## Invariantes y etiquetas

Todos los brazos correspondientes son idénticos en sus 21 coordenadas para
t<=3. Para las 40 rutas intervenidas q4=q4_nat. I se etiqueta
NATURAL_STATE_REJOIN, no NATURAL_PDATA. R se etiqueta
INTERVENTION_REACHABLE. C mantiene su etiqueta de estado intervenido de EXP-01.
El blanco analítico de rutas R permanece el blanco original.

## Predicciones primarias t4

| routing | dH a blanco original | diferencia DATA respecto a natural |
| --- | ---: | --- |
| N | 0 | ninguna |
| I | 0 | ninguna |
| C | 1 | i |
| R(i,j), i distinto de j | 2 | i,j |

Para R, x_i queda errónea y x_j, antes correcta, se conmuta. Los 24 casos deben
satisfacer dH=2 y q4 idéntica a natural. El endpoint primario es el destino
DATA que cambia en t4, no la recuperación posterior.

## Observables y seguimiento secundario

Por timestep: identificador de corrida, blanco original, inicial, error,
clase A, brazo, fuente P, destino asignado, routing, estado de 21 bits, x,
D/E/L/P/q, distancias a blanco original/opuesto/q*, intervención, siguiente x
natural y real, DATA cambiada, paridad q4, P activos, RAAC, repetición y
alcanzabilidad. Tras t4: cada pulso P posterior, RAAC posterior, recuperación
de blanco original/opuesto, inicio y longitud de ciclo y clase final.

Taxonomía: O1 recuperación original; O2 recuperación opuesta; O3 fijo no
blanco; O4 ciclo determinista; O5 retorno a un-error; O6 multipulso; O7
reparación alternativa; O8 otro, preservando la traza sin forzar lectura.

## Claims permitidos

Si pasan los invariantes y endpoint:

- A_ACTIVE_PULSE_EFFECT_FOLLOWS_ASSIGNED_OUTPUT_DESTINATION
- A_P_TO_X_IDENTITY_MAPPING_NECESSARY_FOR_NATURAL_T4_PDATA_CORRECTION
- A_P_TO_X_WIRING_CAUSALLY_CONTRIBUTES_TO_RECONSTRUCTIVE_DIRECTION

Todos INSTANCE_CAUSAL; scope A × P-DATA autorizada × RAAC natural t3→t4.
No se permite afirmar que toda la dirección resida en P→x, necesidad
estructural/familiar, entityhood, proto-orgánulo, emergencia, intención,
detección, sensing, memoria o generalización.

## Auditoría supplied/generated

SUPPLIED: cableado P_i→x_i, regla XOR de acción, arquitectura upstream,
sincronía y blancos. DYNAMICALLY_GENERATED: patrón D/E/L/P realizado.
TRAJECTORY_CONTINGENT: P_i activado y dinámica posterior a remap. CAUSALLY
NECESSARY: sólo dependencias demostradas quirúrgicamente. OBSERVED_ONLY:
regularidades downstream sin intervención independiente.

## Acceptance criteria

1. EXP-03 tiene commit propio.
2. Este preregistro se comitea antes de resultados.
3. A y G canónicas no cambian.
4. N reproduce baseline y UNIQUE_ACTIVE_PULSE=8/8.
5. Paridad pre-t4 para las 48 corridas.
6. I=N bit a bit, 8/8.
7. C=EXP-01, 8/8.
8. q4 parity 40/40 intervenidas.
9. 24 off-diagonales ejecutadas; dH=2 y destino verificado 24/24.
10. G se reanuda tras t4; matriz 4x4 completa; blancos original/opuesto
    separados.
11. No remap E→P ni D→E; ninguna conclusión entityhood.

## Stop conditions

Detener sin claim ante drift baseline, P no único, divergencia pre-t4, I distinto
de N, C distinto de EXP-01, q4/AUX alterada, G canónica cambiada, intervención
persistente, necesidad de cambiar protocolo tras resultados o edición
retrospectiva de este preregistro.


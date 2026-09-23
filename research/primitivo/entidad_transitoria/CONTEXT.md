# Contexto heredado y límites

## Registro de apertura

| campo | valor |
| --- | --- |
| rama previa | `experiment/cognitive-live-observatory-01` |
| commit padre | `41fccbf1028a45c78a023b6f37800a1690f671eb` |
| estado al abrir | sucio: `docs/LEVEL18_ANALISIS_CAUSA_RAIZ.md` y `experiments/primitivo_n2/` sin seguimiento |
| rama creada | `research/primitivo-entidad-transitoria` |
| alcance | documentación preexperimental PRIMITIVO |

Los elementos sin seguimiento precedían esta rama y no son parte de ETP-PRE-00.
No se modifican ni se usan como evidencia sin fuente explícita.

## Fenómeno y pregunta

La pregunta es qué composición causal explica, por separado, aparición,
contribución reconstructiva y desaparición de una organización no basal. No se
presupone una entidad con frontera fija. La auditoría distingue:

1. **ONSET**: qué lleva de la perturbación a `q != q*`.
2. **ACTION / RECONSTRUCTION**: dónde reside y dónde se usa causalmente la
   dirección correctiva.
3. **TERMINATION**: qué quita el soporte del estado auxiliar no basal.

«Porque las reglas lo dicen» sólo identifica la capa de diseño y no sustituye
estas tres explicaciones causales.

## Especímenes congelados

### A — objeto primario

`C4` tiene `x=(x1,x2,x3,x4)` y
`q=(d12,d13,d23,d14,d24,e1,e2,e3,e4,l1,l2,l3,l4,p1,p2,p3,p4)`:
4 DATA + 17 AUX = **21 variables**. Blancos: `(0000,0^17)` y `(1111,0^17)`;
el mismo `q*=0^17` aplica a ambos. La sincronía es estricta y `d_max<=2`
globalmente. No hay reloj, scheduler, etiqueta de blanco ni oráculo persistente.

| regla | actualización |
| --- | --- |
| D | `d12'=x1 XOR x2`; `d13'=x1 XOR x3`; `d23'=x2 XOR x3`; `d14'=x1 XOR x4`; `d24'=x2 XOR x4` |
| E | `e1'=d12 AND d13`; `e2'=d12 AND d23`; `e3'=d13 AND d23`; `e4'=d14 AND d24` |
| L | `l_i'=e_i` |
| P | `p_i'=e_i AND NOT l_i` |
| DATA | `x_i'=x_i XOR p_i` |

Toda coordenada primada depende sólo del estado en `t`.

### B — contraste congelado

`COORDINATEWISE_HEADROOM_APD_FEASIBLE` es factibilidad proyectada, no red
auxiliar implementada. Su testigo tiene `N(Phi)=H(Phi)={3,4}` y
`H0=(x3 AND x4,x3 AND x4,x2,x1)`. No se compila ni continúa en esta rama.

## Resultados heredados cerrados

Se preservan dentro de su alcance: `DISCOVERY-00..03`, con
`DISCOVERY-03 = NO_LOCAL_SOLUTION · INDEPENDENTLY_VERIFIED`; `RAAC =
REACHABLE_AUXILIARY_CONTROL_PROVED`; `RDDA = RDDA_NOT_STRUCTURALLY_NECESSARY`;
`PROJECTED_APD = PROJECTED_APD_FEASIBLE`; `STARTUP APD =
STARTUP_COMPATIBLE_APD_FEASIBLE`; `HEADROOM =
COORDINATEWISE_HEADROOM_APD_FEASIBLE`.

Para A se heredan P-DATA 8/8, latencia full-state 7, recuperación DATA ~t4;
P-FULL 42/42, latencia máxima 9; y SELF_START/SELF_HALT verificados. D aislado
puede lavarse sin cambiar DATA; E puede pulsar, inducir error temporal y
reparar; L aislado puede lavarse; P cambia DATA directamente y el mecanismo
normal restaura. Ninguno prueba entidad.

## RAAC no equivale a entidad

RAAC establece un estado autorizado alcanzado `(x_t,q_t)` donde `q_t != q*` y
`pi_x G(x_t,q_t) != pi_x G(x_t,q*)`. Prueba que estado auxiliar activo importa
causalmente en algún lugar de su alcance; no prueba tamaño, frontera,
persistencia, modularidad, identidad, integración interna ni H3.

**RAAC != ENTITYHOOD.**

## Material ausente o no adjudicado

No se localizaron los tres MD de cierre identificados como «660 preguntas», ni
artefactos con los rótulos textuales completos de FULL_STATE_INTERNALIZATION,
RAAC, RDDA o APD. Las trazas crudas P-DATA/P-FULL, freezes E/P, `p=e`,
SELF_START/SELF_HALT y RAAC tampoco se identificaron en una fuente de resultados
cerrados. Se mantienen como contexto heredado suministrado para la apertura;
detalle no respaldado: `UNKNOWN`.


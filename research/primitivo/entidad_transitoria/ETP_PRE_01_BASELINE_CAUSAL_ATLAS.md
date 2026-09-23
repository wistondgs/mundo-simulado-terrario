# ETP-PRE-01 · Baseline Causal Atlas + Provenance Recovery

Estado: **BASELINE_TRACE_ATLAS_VERIFIED · RAAC_ATLAS_VERIFIED ·
TERMINATION_SEQUENCE_CHARACTERIZED · P_FULL_RESPONSE_CLASSES_CHARACTERIZED**.

PRE-01 observa y reconstruye solamente A congelado. No declara entidad, no
altera regla o arquitectura y no ejecuta intervención experimental.

## Método y artefactos

El verificador [build_baseline_atlas.py](build_baseline_atlas.py) implementa
literalmente las ecuaciones congeladas. Enumera los 8 P-DATA y 42 P-FULL
autorizados hasta el primer retorno al blanco completo. Sus contrafactuales
RAAC y de arista efectiva son consultas de un paso a la transición congelada:
no cambian una trayectoria, regla ni arquitectura.

- [verificación](artifacts/verification.json)
- [trazas](artifacts/p_data_traces.csv) y
  [resumen P-DATA](artifacts/p_data_summary.csv)
- [trazas P-FULL](artifacts/p_full_traces.csv) y
  [resumen P-FULL](artifacts/p_full_summary.csv)
- [atlas RAAC](artifacts/raac_atlas.csv)
- [aristas efectivas](artifacts/p_data_effective_edges.csv),
  [nodos temporales](artifacts/p_data_temporal_nodes.csv) y
  [dominadores](artifacts/p_data_dominators.csv)

## Recuperación de procedencia

Se buscó en checkout, artefactos experimentales y la historia Git alcanzable.
Los instrumentos DISCOVERY-02 y DISCOVERY-03 están presentes y se introdujeron
en el commit padre 41fccbf; ambos declaran no escribir artefactos de resultado.
No se localizó una traza cerrada de los veredictos DISCOVERY, RAAC, RDDA o APD.

Los tres MD de las 660 preguntas no están en el checkout:

CONTEXT_SOURCE = RESEARCHER_SUPPLIED / RAW FILE NOT LOCAL.

Su ausencia local no rebaja un resultado heredado. Claim status es el estatus
científico heredado; provenance status identifica cómo llegó a esta rama.

| claim | claim status | provenance status | fuente localizada / límite |
| --- | --- | --- | --- |
| DISCOVERY-00 | cerrado heredado | RESEARCHER_SUPPLIED_CONTEXT | resultado bruto no localizado. |
| DISCOVERY-01 | cerrado heredado | RESEARCHER_SUPPLIED_CONTEXT | resultado bruto no localizado. |
| DISCOVERY-02 | cerrado heredado | RESEARCHER_SUPPLIED_CONTEXT | instrumento SOURCE_LOCATED e histórico; salida cerrada no localizada. |
| DISCOVERY-03 / NO_LOCAL_SOLUTION | cerrado heredado | RESEARCHER_SUPPLIED_CONTEXT | instrumento SOURCE_LOCATED e histórico; salida cerrada no localizada. |
| FULL_STATE_INTERNALIZATION | cerrado heredado | RESEARCHER_SUPPLIED_CONTEXT | auditoría no localizada. |
| RAAC / REACHABLE_AUXILIARY_CONTROL_PROVED | cerrado heredado | RESEARCHER_SUPPLIED_CONTEXT | traza heredada no localizada; PRE-01 deriva atlas nuevo. |
| RDDA_NOT_STRUCTURALLY_NECESSARY | cerrado heredado | RESEARCHER_SUPPLIED_CONTEXT | informe no localizado. |
| PROJECTED_APD_FEASIBLE | cerrado heredado | RESEARCHER_SUPPLIED_CONTEXT | informe/testigo no localizado. |
| STARTUP_COMPATIBLE_APD_FEASIBLE | cerrado heredado | RESEARCHER_SUPPLIED_CONTEXT | informe/testigo no localizado. |
| COORDINATEWISE_HEADROOM_APD_FEASIBLE | cerrado heredado | RESEARCHER_SUPPLIED_CONTEXT | informe/testigo no localizado; B no se compiló. |
| ecuaciones, A y resultados PRE-01 | verificado PRE-01 | DERIVED_FROM_FROZEN_EQUATIONS | context card congelada + verificador. |

Ningún claim se etiqueta MISSING_SOURCE: todos fueron suministrados por el
investigador. Falta el archivo bruto local para elevar su cadena de procedencia.

## Modelo congelado verificado

| propiedad | resultado |
| --- | --- |
| variables | 21 = 4 DATA + 17 AUX |
| blancos completos | (0000,0^17) y (1111,0^17) son puntos fijos |
| auxiliar basal | q*=0^17 común |
| aridad esencial estática máxima | 2 |
| sincronía / orden | cada RHS lee sólo estado t; no existe orden de actualización |
| reloj oculto | ninguno: transición función sólo de 21 bits |
| mutaciones | ninguna |

Las dos corridas fallidas del verificador se detuvieron antes de producir
artefactos; revelaron una implementación no síncrona del lector y se corrigieron
antes de publicar el atlas. El resultado final satisface sincronía estricta.

## P-DATA: latencias exactas

| clase | trayectorias | onset | D / E / L / P | efecto DATA | DATA recovery | full recovery | cola | max dH(q,q*) |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| A1 | 0000:x1, 0000:x2, 1111:x1, 1111:x2 | 1 | 1 / 2 / 3 / 3 | 3→4 | 4 | 7 | 3 | 6 |
| A2 | 0000:x3, 1111:x3 | 1 | 1 / 2 / 3 / 3 | 3→4 | 4 | 7 | 3 | 5 |
| A3 | 0000:x4, 1111:x4 | 1 | 1 / 2 / 3 / 3 | 3→4 | 4 | 7 | 3 | 5 |

Las ocho son exitosas: T_ONSET=1, T_FIRST_DIRECT_DATA_EFFECT=3,
T_DATA_RECOVERY=4 y T_FULL_RECOVERY=7. A1 tiene tres desacuerdos D; A2/A3 dos.

## Simetrías y clases verificadas

El complemento global empareja 0000 con 1111: q es idéntico y x es complemento
global. La única permutación no identidad que preserva dependencia y funciones
es (x1 x2), con d13↔d23, d14↔d24, e1↔e2, l1↔l2 y p1↔p2. No hay S4: E
distingue x3 de x4. Estas simetrías dan A1, A2 y A3.

Las bolas Hamming-1 de 0000 y 1111 son disjuntas. Esto muestra
INFORMATION_AVAILABLE en x, no INFORMATION_USED_CAUSALLY.

## Cadena basal: onset, acción y terminación

A1: x1 perturbada produce d12,d13,d14 en t1; éstos producen e1 en t2; e1
produce l1,p1 en t3; p1 cambia x1 en t3→t4. A2 usa
d13,d23 → e3 → l3,p3; A3 usa d14,d24 → e4 → l4,p4. Las trayectorias
complementarias comparten q.

La terminación funcional exacta es:

1. P cesa en t4 porque L ya está alto en t3 y p=e AND NOT l.
2. D cesa en t5 porque x corregida es entrada de la recomputación.
3. E cesa en t6 porque D es cero en t5.
4. L cesa en t7 porque E es cero en t6.

Esto deriva reglas y contrafactuales locales, no una intervención sobre entidad.
No se denomina self-extinction.

## RAAC atlas

Cada estado P-DATA naturalmente alcanzado con q distinto de q* fue comparado
con (x_t,q*): 48 consultas, 6 por trayectoria. Sólo 8 son RAAC, una por
trayectoria, siempre en t=3.

| clase | RAAC t | q→x afectada | actual siguiente x | q* contrafactual |
| --- | ---: | --- | --- | --- |
| A1 | 3 | coordenada x1/x2 perturbada | blanco correcto | x aún perturbada |
| A2 | 3 | x3 | blanco correcto | x aún perturbada |
| A3 | 3 | x4 | blanco correcto | x aún perturbada |

Los otros 40 estados no basales no son RAAC. q distinto de q* no fue usado como
sustituto de esa prueba.

## Aristas efectivas y dominadores

Cada fila de aristas efectivas es estáticamente esencial y contextualmente
efectiva. Una arista estática ausente no fue efectiva en ese contexto. Los ocho
DAG P-DATA suman 1,584 aristas efectivas.

Desde (xi,0) hasta (xi,4) hay exactamente tres caminos efectivos por
trayectoria. Sólo los dos extremos son dominadores temporales: no hay
dominador interno común. Es descripción basal, no dictamen de entidad ni de
proceso distribuido.

## P-FULL: clases de respuesta

| perturbación inicial | n | latencia full | x cambia | RAAC | DATA recovery | cola | respuesta |
| --- | ---: | ---: | --- | --- | ---: | ---: | --- |
| DATA | 8 | 7 | sí | sí, t3 | 4 | 3 | P-DATA basal. |
| D | 10 | 1 | no | no | 0 | 1 | se lava al recomputar D. |
| E | 8 | 9 | sí | sí, t1 y t5 | 6 | 3 | pulso induce error DATA y cascada reparadora. |
| L | 8 | 1 | no | no | 0 | 1 | se lava sin tocar x. |
| P | 8 | 8 | sí | sí, t0 y t4 | 5 | 3 | cambia DATA y dispara reparación. |

Total 42/42. Distribución de latencia: 1×18, 7×8, 8×8, 9×8. Una coordenada
AUX volcada es una state perturbation, no lesión estructural.

## Veredictos PRE-01

- BASELINE_TRACE_ATLAS_VERIFIED
- RAAC_ATLAS_VERIFIED
- TERMINATION_SEQUENCE_CHARACTERIZED
- P_FULL_RESPONSE_CLASSES_CHARACTERIZED
- ENTITY_LEVEL_INTERPRETATION = OPEN

## Siguiente paso, sólo propuesto

Si el investigador autoriza ejecución posterior, candidato único:
EXP-01 ACTION CUT. Preservaría onset en una clase P-DATA y bloquearía sólo la
influencia p_i(t=3)→x_i(t=4), con sham temporal y de coordenada. No se autoriza
ni ejecuta aquí. EARLY REPAIR, ONSET BLOCK y PATTERN INJECTION quedan después;
esta última es off-manifold.


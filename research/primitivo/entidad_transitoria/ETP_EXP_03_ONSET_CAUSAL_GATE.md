# ETP-EXP-03 · Onset Causal Gate

EXP-02 closing commit: **9ba600d8e78987f250f7b22a6f0399fe6c7d1471**  
Estado: **EXP-03 ejecutado exhaustivamente sobre A / P-DATA autorizado**.

Pregunta: ¿el onset es generado continuamente por la configuración DATA
perturbada presente, o depende de un evento histórico irrepetible? No se prueba
entityhood.

## Diseño

La intervención sustituye solamente la contribución del padre DATA perturbado
en cada salida D incidente, usando el valor original de blanco de ese padre.
DATA permanece perturbada; ninguna D se sobrescribe y E/L/P no se modifican.

- x1: d12,d13,d14
- x2: d12,d23,d24
- x3: d13,d23
- x4: d14,d24

Se ejecutaron cuatro brazos para cada una de las ocho P-DATA:

1. NATURAL.
2. NO_OP_SPATIAL_SHAM: sustitución sobre un padre DATA que ya vale su blanco.
3. TRANSIENT_ONSET_BLOCK: sustitución sólo t0→t1.
4. PERSISTENT_ONSET_BLOCK: sustitución en cada transición.

Artefactos:

- [run_exp03_onset_gate.py](run_exp03_onset_gate.py)
- [trazas completas](artifacts/exp03_onset_gate_traces.csv)
- [resumen de 32 brazos](artifacts/exp03_onset_gate_summary.csv)
- [comparación exacta de fase](artifacts/exp03_phase_shift_comparison.csv)
- [aristas efectivas](artifacts/exp03_effective_edges.csv)

## Controles

| brazo | n | onset | RAAC | DATA | FULL | desenlace |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| NATURAL | 8 | 1 | 3 | 4 | 7 | blanco full original |
| NO_OP_SPATIAL_SHAM | 8 | 1 | 3 | 4 | 7 | idéntico a NATURAL |
| TRANSIENT_ONSET_BLOCK | 8 | 2 | 4 | 5 | 8 | blanco full original |
| PERSISTENT_ONSET_BLOCK | 8 | no ocurre | no ocurre | no ocurre | no ocurre | configuración fija intervenida |

El sham conserva el estado completo en t1 y la trayectoria entera, por lo que
la maquinaria de sustitución no introduce un confusor detectable.

## Bloqueo transitorio

El bloqueo de una sola transición mantiene x perturbada y q basal en t1. Al
liberar la puerta y restaurar G en t1, D aparece en t2, E en t3, L/P y RAAC en
t4, DATA se restaura en t5 y el blanco full en t8.

Las 64 comparaciones fase a fase, ocho tiempos por cada trayectoria, son
exactas: estado transitorio en t+1 = estado natural en t, sin coordenadas
divergentes. Se registra:

**ONE_STEP_ONSET_DELAY_EQUIVALENCE**

La lectura descriptiva permitida es que la perturbación DATA todavía presente
regenera la cascada tras liberarse la transmisión causal. No se llama memoria,
detección ni evento histórico almacenado.

## Bloqueo persistente

Con la sustitución sostenida, cada trayectoria repite exactamente su estado
inicial en t1:

x sigue siendo la perturbación de un bit, D=E=L=P=0 y q=q*. La repetición tiene
longitud 1 desde t0 bajo la dinámica intervenida.

Esto se clasifica como **INTERVENTION-SUSTAINED FIXED CONFIGURATION**, no como
punto fijo natural de A.

## Clases de equivalencia

A1 (x1/x2) altera tres salidas D; A2 (x3) y A3 (x4) alteran dos. Pese a esa
diferencia suministrada, las ocho trayectorias comparten los tiempos y
desenlaces de cada brazo. Las parejas de complemento permanecen equivalentes.

## Auditoría supplied / generated

| categoría | contenido |
| --- | --- |
| SUPPLIED | topología x→D, reglas XOR, blanco experimental y sincronía. |
| DYNAMICALLY_GENERATED | patrón D no basal realizado tras una perturbación. |
| TRAJECTORY_CONTINGENT | qué D concretas se vuelven no basales: tres en A1, dos en A2/A3. |
| CAUSALLY_NECESSARY | transmisión del padre DATA perturbado a las D incidentes, para onset P-DATA dentro del alcance probado. |

Por tanto, la respuesta de instancia a “quién le dijo que apareciera” es:
las relaciones XOR suministradas mapean continuamente la perturbación DATA
actual a D no basal. No existe una orden externa durante la ejecución.

## Claims permitidos

**A_X_TO_D_CAUSAL_TRANSMISSION_NECESSARY_FOR_ONSET_IN_PDATA**  
INSTANCE_CAUSAL; A × ocho P-DATA autorizadas.

**A_ONSET_IS_REGENERATED_FROM_PERSISTING_CURRENT_DATA_PERTURBATION_AFTER_TRANSIENT_INPUT_BLOCK**  
INSTANCE_CAUSAL; A × ocho P-DATA autorizadas.

**A_TRANSIENT_ONSET_BLOCK_PRODUCES_ONE_STEP_PHASE_SHIFT_WITHOUT_CHANGING_CAUSAL_SEQUENCE**  
INSTANCE_CAUSAL; A × ocho P-DATA autorizadas.

CAUSAL ONSET != ENTITYHOOD. H0, H1, H2 y H3 permanecen abiertas.

## Límites y siguiente paso

No se establece detección, memoria, decisión, intención, proto-orgánulo,
emergencia ni universalidad. El resultado aplica a las reglas suministradas de
A.

Propuesta, no ejecutada: localizar la dirección reconstructiva suministrada
mediante un experimento de output remapping E/P→x que conserve onset y acción,
pero cambie una sola asignación correctiva.


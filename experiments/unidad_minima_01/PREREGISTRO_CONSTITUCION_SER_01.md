# Prerregistro · Constitución del Ser Integrado 01

**Estado:** abierto antes de la campaña confirmatoria; las ejecuciones A6 ya
archivadas son humo de integración, no resultados de esta prueba.

## Pregunta y alcance

¿La misma instancia de `SerIntegrado` conserva el núcleo de Unidad Mínima y
mantiene activas adquisición, reparación, exploración, olvido, herencia y
enseñanza a través de una cadena de cinco mundos del banco madre, sin que un
órgano destruya la evidencia de otro? Esta es una prueba de composición y
transferencia de mecanismos ya medidos; no una afirmación de novedad cognitiva.

El antecedente operativo es
`PROYECTO_SER_INTEGRADO_01.md` §§1--6. La revisión de antecedentes (30-oct-2026)
clasifica el objeto como integración/replicación local: modelos de estado
predictivo y exploración dirigida tienen antecedentes públicos, pero no sustituyen
la evidencia de que estos contratos concretos comparten una vida. Fuentes de
contexto: [PSR](https://arxiv.org/abs/2207.05738),
[self-predictive RL](https://arxiv.org/abs/2401.08898) y
[continual learning/replay](https://arxiv.org/abs/1811.11682).

## Material congelado

* Banco madre: `artifacts/banco_madre.json`, SHA-256
  `483ce34fed5d8758cecb337d49391a3d8cb9f7230d2900fc3c793a1a85fa79ba`
  (195 mundos: 165 de n=8 y 30 de n=6).
* Base Git: `d643be18b2d23b86f934747ad27868770d98e94e`.
* Composición: `ser_integrado_01.py`, SHA-256
  `abb37011169afd2cdd3e93ad9dbfa6df4a338a35bf6467bf70aa602a0d26badf`.
* Todo archivo que cambie después de esta ficha invalida la corrida
  confirmatoria hasta actualizar esta sección antes de iniciarla.

## Diseño fijo

Hay 16 celdas pareadas por mundo, el producto de:

| Factor | Encendido | Apagado/control |
|---|---|---|
| exploración | `UnidadFase2.letra_elegida` | itinerario shortlex fijo |
| olvido | contrato 08, presupuesto 2 000 000, ventana 512, núcleo 256 | M-c: sin olvido |
| enseñanza | `MaestroMundo`; palabra recibida se vive | fresca, sin canal |
| herencia | C5: máquina sin traza y reparación local | nacimiento vacío |

La referencia adicional es una fresca pura. Cada celda vive una cadena declarada
de cinco mundos: transición componible y su control no componible, según el
generador histórico de Fase 2. No se permiten semillas, reintentos, exclusiones
ni cambios de presupuesto post hoc. Una falla de infraestructura se conserva con
su traza y se repite sólo si no produjo ni una transición; una falla semántica
termina la corrida y exige una enmienda de esta ficha.

## Resultados, guardas y falsadores

La celda completa sólo puede pasar si registra en la misma identidad de objeto:

1. identidad de todos los órganos con el núcleo; cadena hash íntegra;
2. los ocho contadores requeridos activos cuando el mundo ofrece la ocasión
   (`refutaciones`, `distinciones_abiertas`, `autorelecturas`, `olvidos`,
   `pasos_elegidos`, revisión/supervivencia heredada, maestro, retención);
3. continuidad a través de cinco cambios, y alcance final no menor que el órgano
   aislado correspondiente;
4. adquisición básica (identificar, predecir y repertorio) no inferior al mejor
   órgano aislado, pareado por mundo;
5. ausencia de interacción destructiva fuera de elegir × esqueleto falso,
   que es una excepción conocida y se informa separadamente.

Un contador en cero cuando hubo oportunidad, una sustitución de objeto, una
ruptura hash, o rendimiento inferior en adquisición falsan la constitución de
esa celda. Interacciones nulas significan coexistencia, no sinergia. Los
resultados negativos se publican con la misma matriz.

## Límites explícitos

L16, L17 y L19 se prueban primero en el adaptador A6/Terrario, con sus propios
alfabetos observables; **no entran en este factorial** hasta que un protocolo
demuestre compatibilidad con la cadena Mealy. La interfaz A6 tampoco convierte
una métrica de energía de Terrario en evidencia de la meta externa 04. El
Teacher de Génesis queda excluido: no se importa 7B, llama.cpp ni CUDA.

Antes de abrir los 3 315 recorridos (16 × 195 + fresca), el ejecutor debe pasar
las guardas de mutantes en un único mundo y escribir el manifiesto de código,
configuración, mundo y posición de cada vida. Esas prepruebas son ingeniería y
no se mezclarán con las comparaciones confirmatorias.

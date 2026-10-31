# Ser Integrado 01 · constitución ejecutable, antes del factorial

**Estado:** una vida integrada ejecutada contra constructores de mundo
existentes. No es una campaña factorial ni una certificación científica
conjunta. **Sin commits, pushes, merges ni cambios en Génesis.**

## Núcleo y contratos reutilizados

`ser_integrado_01.py` hereda de `UnidadC5`: `trans`, `trace`, `q`, `choices`,
`n`, `used` y `c` son el único estado cognitivo compartido. El mapa `organos`
contiene referencias al mismo objeto y `assert_shared_core()` lo exige.

Se adaptaron sólo tres contratos funcionalmente compatibles de Génesis, en
`050700001d2fa86e926126d471a7978ca63c6d76`, sin importar su runtime:

1. Identidad estable de organismo y linaje, compatible con
   `runtime/organism/state.py:110-151` y `:232-300`.
2. Instantánea serializable antes/después de cada transición, sin exponer estado
   verdadero del mundo como estado cognitivo.
3. Cadena verificable de transiciones con hash previo, inspirada en el contrato
   de integridad —no en sus componentes cognitivos— de
   `runtime/organism/life_transition.py:15-89` y `:110-220`.

No se reutilizó `Teacher` de Génesis, ni sus dependencias 7B, llama.cpp o CUDA.
La enseñanza proviene de `MaestroMundo` de Unidad Mínima 10. La regeneración
llama a `UnidadQueSeRelee._releerse`; C5 conserva su reparación local; y la
exploración usa `UnidadFase2.letra_elegida` sobre esa misma hipótesis. La vida
corre adquisición W1 → meta 04 vivida → lesión/regeneración → transición C5 →
exploración W2 → enseñanza 10 → lectura de retención, siempre sobre este objeto.

## Autoridad de acción

| Autoridad | Código reutilizado | Cuándo gobierna | No demuestra |
|---|---|---|---|
| Enseñanza | `unidad_minima_10_maestro.py` | Hay palabra de maestro que debe vivirse | Meta propia |
| Exploración | `unidad_minima_08_fase2.py` | Hay hueco no visto y no hay palabra enseñada | Utilidad de explorar en todo mundo |
| Itinerario | módulos 01/08 | No hay propuesta anterior | Elección adaptativa |
| Meta externa | `unidad_minima_04_eleccion.py` | Sólo ante consulta `elegir_meta_externa` | Exploración ni motivación propia |

Esto corrige la ambigüedad C5 + exploración: C5 histórico no activaba
`letra_elegida` (`unidad_minima_09_fase2.py:344-347`). Aquí la conexión es una
adaptación de interfaz explícita, no evidencia retrospectiva de que C5 aislado
ya la hubiese demostrado.

## Evidencia de la prueba técnica

Comando ejecutado desde este directorio:

```bash
python3 -m unittest -v test_ser_integrado_01.py
python3 ser_integrado_01.py --self-test --out artifacts/ser_integrado_01_smoke.json
```

Resultado: 2/2 pruebas, `PASS`; 365 transiciones; cadena válida. La traza
`artifacts/ser_integrado_01_smoke.json` contiene para cada transición: hash
previo, acción y fuente, observación, consecuencia, hash del estado antes y
después. En la ejecución quedaron fuentes `itinerary`, `lesion_03`,
`regeneration_03`, `external_goal_04`, `inheritance_repair_09`,
`exploration_08` y `teacher_10`.

El artefacto incluye `laboratory_contract` con la proyección de sus transiciones
hacia la traza de Terrario. Declara `adapter_required`: A/B y la observación
binaria de Unidad Mínima no se convierten automáticamente en `Action.to_int` ni
en canales/máscara de Terrario. Esa frontera prepara el adaptador sin convertir
compatibilidad de serialización en evidencia cognitiva.

## Adaptador Terrario A6 · ejecución separada

`terrario/agent/agents/a6_integrated.py` registra `A6_INTEGRATED` sin copiar un
segundo núcleo: cada transición de Terrario entra en el `SerIntegrado` anterior.
El codec de cuatro bits usa únicamente `Observation.channels` y `mask`; la
copia eferente se deriva de la acción A/B que A6 emitió. No entra posición,
objeto, regla, recompensa ni verdad del mundo.

La corrida local inmutable `ser_integrado_terrario_smoke_02`, semilla
`26010302`, configuración SHA-256
`5e23d226f1df033b33b9d6f7c4eaa74d1504dec6114941db6f1a23e2bbfbc1bb`, dejó
32 filas en
`artifacts/terrario_a6_smoke_02/observations/ser_integrado_terrario_smoke_02/A6_INTEGRATED/seed_26010302/episode_0000/events/transition.jsonl`.
La última transición verificable informa: cadena del núcleo válida; temporal
1.6 = 8 actualizaciones y congelado; contingencia 1.7 = 24 actualizaciones;
L19 = 32 actualizaciones y 1 estado predictivo. La ejecución declara HEAD
`d643be18…`; como los archivos de integración aún no están comprometidos, la
procedencia de código se completa con SHA-256 de `a6_integrated.py`
`cd1209a6c3a1dfbc443874128d196088ac89401fbae04d20ce743aa10209ab02` y no se
confunde el HEAD con una captura completa del árbol sucio. El contrato automático
`test_a6_integrated_01.py` reproduce esos cuatro hechos en un directorio
temporal; junto con `test_ser_integrado_01.py`, da **3/3 PASS**.

Esto demuestra actualización conjunta y trazable, no que L19 haya seleccionado
acciones (A6 aún no recibe una observación objetivo externa compatible) ni que
la energía final de Terrario sea una meta 04. La primera se mantiene como
transferencia no verificada; la segunda conserva la autoridad de meta externa
exclusivamente en Unidad Mínima.

| Órgano / lectura | Resultado de esta vida | Estado |
|---|---|---|
| adquisición 02 | W1: exactitud 1.0, sin rutas vacías, identifica | Integrado técnicamente |
| palabras | 3 `escribe`, 0 `permuta`, 5 clases | Integrado técnicamente |
| meta 04 | eligió `A`; vivió `A,B`; observó `B=1` | Integrado y separado de explorar |
| regeneración 03 | `autorelecturas=1`, 260 pasos releídos | Integrado técnicamente |
| C5 | 6 heredadas y 6 revisadas | Integrado técnicamente |
| exploración 08 | 3 pasos elegidos sobre la hipótesis C5 | Integrado; sin inferencia de beneficio |
| enseñanza 10 | 4 acciones enseñadas vividas | Sólo actividad: canal `un_bit` |
| retención | W2: exactitud 1.0, instruibilidad 2 | Lectura técnica, no controlada |

La discrepancia del banco madre queda cerrada como verificación local:
`artifacts/banco_madre.json` y el blob del commit
`d643be18b2d23b86f934747ad27868770d98e94e` tienen ambos SHA-256
`483ce34fed5d8758cecb337d49391a3d8cb9f7230d2900fc3c793a1a85fa79ba`.

## Límites que permanecen abiertos

1. Esta prueba no compara estas lecturas contra sus controles históricos en una
   misma celda. El factorial sigue siendo necesario para transferencia,
   interferencia y sinergia.
2. El contador de olvido 08 queda en cero en la vida Mealy de 365 transiciones;
   el adaptador A6 produjo un olvido bajo sus propias observaciones, pero no es
   equivalente a la condición del banco madre. Forzarlo bajando presupuesto
   cambiaría las condiciones históricas y no se presenta como demostración.
3. La traza hash prueba continuidad de registro e identidad de objeto, no
   continuidad psicológica ni validez de una teoría de identidad.
4. La prioridad enseñanza → exploración → itinerario es un contrato de
   integración. Cambiarla alteraría la interpretación científica y requiere
   decisión y preregistro antes de una campaña.
5. El prerregistro `PREREGISTRO_CONSTITUCION_SER_01.md` fija el factorial de
   16 celdas y la fresca sobre los 195 mundos. El material histórico no contiene
   una definición ejecutable de la cadena concreta de cinco transformaciones
   para ese banco ni el orden de sus controles componible/no componible. No se
   sustituirá ese dato científico por una cadena inventada; ése es el único
   bloqueo para iniciar la campaña confirmatoria completa.

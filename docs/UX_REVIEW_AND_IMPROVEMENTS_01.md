# UX_REVIEW_AND_IMPROVEMENTS_01

Fecha: 2026-09-15
Rama: `experiment/cognitive-live-observatory-01`
Alcance: diagnóstico de la experiencia de uso de las tres superficies reales, cambios aplicados y
backlog priorizado. No modifica dominio, contratos, máquinas de estado ni identidades científicas.

Documentos previos que este trabajo continúa: `UI_FORENSIC_AUDIT_01` (inventario),
`INFORMATION_ARCHITECTURE_01` (arquitectura conceptual, `NEXT_VALID_OBJECTIVE=INTERACTION-ARCHITECTURE-01`)
y `TERRARIO_USER_MANUAL` (guía de uso).

## 1. Diagnóstico

### 1.1 Tres superficies, tres lenguajes visuales, ninguna vía entre ellas

| Superficie | Ruta | Lenguaje | Papel real |
| --- | --- | --- | --- |
| Centro de revisión | `/review-center.html` | sobrio, prosa, mucho aire | punto de entrada del lanzador; la mejor diseñada |
| Lab | `/` | panel denso, barra lateral de 15 vistas | teoría, diseño, protocolo, lectura de lo registrado |
| Workspace | `/workspace/index.html` | estación de instrumentos, 9 paneles en 4 contextos | cross-graph, sandbox y ejecución/observación |

El lanzador abre la primera; la ruta canónica atraviesa las tres; y el Lab **no enlazaba al Workspace
en su navegación** (sólo dentro de un párrafo del Manual). El usuario que empezaba por `/` no tenía
forma de descubrir dónde se ejecuta un experimento.

### 1.2 El sistema tenía una ruta y no la mostraba

La cadena `ExperimentDraft → TrialMatrix → preregistro bloqueado → autorización → plan sellado →
intento → frame → traza` está implementada, probada y documentada. La pantalla de inicio mostraba
ocho contadores y ninguna acción. Ese es el hueco entre "hay una ruta canónica" y "la interfaz la
enseña".

### 1.3 Se ofrecían acciones ilegales

- World Lab: los siete botones de sandbox estaban siempre activos; `sandboxAction` hacía `return`
  silencioso sin sesión. Pulsar **Step** no hacía nada y no decía nada.
- Scientific Execution: `START`, `PAUSE`, `RESUME` y `CANCEL` se ofrecían en todos los estados,
  aunque `execution/service.py` sólo acepta cada uno en estados concretos. El error llegaba después
  del clic, como un banner de seis segundos.

Esto contradice el invariante de la IA: *exponer sólo las acciones legales del modo explícito*.

### 1.4 Procedencia (L4) ocupando el lugar de la operación (L1)

El panel de ejecución volcaba el JSON completo de la ejecución como contenido principal. El estado,
la revisión y el siguiente paso legal quedaban enterrados bajo cincuenta líneas de hashes.

### 1.5 Los estados vacíos eran rectángulos vacíos

Lienzo científico, canvas de preview, `Instance Identity`, `Reproducibility` y la columna
`TrialMatrix` no distinguían "no hay datos todavía" de "esto está roto".

### 1.6 Honestidad de la interfaz

- El hipergrafo dibujaba 240 de 1176 nodos sin decirlo.
- World Lab mostraba un rótulo de catorce pasos que parecía un asistente y no es navegación.
- La insignia `H-ADAPT · BLOCKED_CUDA` estaba escrita a mano en el HTML en vez de leerse de
  `/api/status`.
- El sandbox de la vista Configuración, que sólo mueve un contador del navegador, se anunciaba como
  `CONTROLLABLE` junto a controles de reproducción.

### 1.7 Defectos de presentación

- `.graph-tools input{min-width:150px}` también estiraba las casillas de verificación, separándolas
  de su etiqueta ~60 px.
- El Manual reutilizaba `.portfolio-card`, cuya rejilla de dos columnas comprimía los títulos a una
  columna de una palabra por línea.
- `Configuracion` sin tilde en la navegación.

### 1.8 Deuda de pruebas encontrada de paso

Cuatro specs quedaron desalineados con el shell de contextos del WIP en curso: `scientific-live`
(×2) y `d2-visual-fixture` conducían paneles montados en un contexto no activo, y
`hypergraph-design-bridge` fijaba el texto exacto de una insignia que el WIP ya había cambiado.
Fallaban antes de este trabajo.

## 2. Cambios aplicados

Todos preservan los contratos: ninguna entidad se fusionó, ninguna procedencia se eliminó, ninguna
transición cambió de autoridad. Lo que cambia es qué se ve primero y qué se ofrece cuándo.

### Lab (`/`)

| Cambio | Archivo | Efecto |
| --- | --- | --- |
| Navegación agrupada en las cinco etapas de la ruta canónica, más `Sistema` y `Otras superficies` | `static/index.html`, `styles.css` | un destino llega con su etapa; ninguna vista se eliminó |
| Enlaces a Workspace y Centro de revisión en la barra lateral | `static/index.html` | las tres superficies dejan de ser islas |
| Barra lateral fija con desplazamiento propio | `styles.css` | la navegación no se pierde en vistas largas |
| `Preregistros` se inserta en el grupo de protocolo | `preregistration.js` | el botón dinámico cae donde corresponde |
| Inicio muestra la **Ruta canónica** de siete pasos antes de los contadores | `index.html`, `app.js` | responde "qué hago ahora" |
| Los contadores son botones hacia su vista | `app.js` | un número es una entrada, no un adorno |
| Insignia H-ADAPT y franja **Salud local** leídas de `/api/status` | `app.js`, `index.html` | integridad, artefactos durables, modo, conflictos y ambigüedades visibles |
| Manual extendido a 7 pasos (ejecución, observación y lectura) y con mapa de superficies | `index.html` | la guía ya no termina en el preregistro |
| Tipografía del Manual corregida | `styles.css` | los pasos se leen como pasos |
| Sandbox de World Lab con controles según estado y mensaje de precondición | `index.html`, `app.js` | un botón gris explica el protocolo en vez de fallar en silencio |
| Estados vacíos en `Instance Identity`, `Reproducibility`, `TrialMatrix` e identidad de Compose | `index.html` | "todavía no" se distingue de "roto" |
| Franja de etapas en Compose (`Validar → Versión durable → TrialMatrix → Preregistro`) | `index.html`, `app.js` | tres acciones simultáneas se leen como un orden |
| Leyenda del hipergrafo y recuento honesto `240 NODES de 1176` | `index.html`, `app.js`, `styles.css` | el recorte deja de ser invisible |
| Casillas de verificación junto a su etiqueta; `Configuración` con tilde | `styles.css`, `index.html` | |
| El sandbox de Configuración deja de anunciarse `CONTROLLABLE` y se rotula `CONTADOR LOCAL DE UI · SIN RUNTIME`, con enlaces al sandbox real | `index.html`, `styles.css` | cierra el riesgo de control ficticio de `UI_FORENSIC_AUDIT_01` §9 sin eliminar la vista |
| `dd{word-break:break-all}` → `overflow-wrap:anywhere` | `styles.css` | los hashes siguen partiéndose; la prosa deja de partirse a mitad de palabra |

### Workspace (`/workspace/index.html`)

| Cambio | Archivo | Efecto |
| --- | --- | --- |
| Resumen L0/L1 de la ejecución: estado, `execution`, root, revisión, plan y **siguiente paso legal** | `views/scientific-execution.js` | la operación va arriba, la procedencia debajo |
| El registro completo pasa a un `<details>` | `views/scientific-execution.js` | L4 sigue a un clic, no ocupa la pantalla |
| Comandos habilitados según `COMMAND_STATES`, espejo de `execution/service.py` | `views/scientific-execution.js` | el servidor sigue siendo la autoridad; la UI no ofrece lo imposible |
| Validación en vivo del root con pista y enlace a Preregistros | `views/scientific-execution.js` | `n/64 caracteres hex` mientras se escribe |
| Barra de World2D agrupada: Fuente · Modo · Sesión sandbox · Cursor · Comparación · Cámara y diagnóstico | `views/world2d.js`, `workspace.css` | veinte controles se leen como cinco grupos; ninguno se quitó ni se deshabilitó |
| Estado vacío del lienzo científico | `main.js`, `workspace.css` | dice qué acción lo llena |
| Crear un preregistro durable aterriza en su Overview en vez de dejar el formulario abierto | `preregistration.js` | corrige una creación sin confirmación visible (ver §3) |
| `aria-label` conciso en las seis tarjetas de la ruta canónica | `index.html` | evita que un lector anuncie los cuatro fragmentos como un nombre corrido |

### Pruebas

- Realineados `scientific-live.spec.js`, `d2-visual-fixture.spec.js` y `hypergraph-design-bridge.spec.js`
  con el shell de contextos y la insignia actual.
- Regeneradas las tres líneas base visuales de `chromium-linux`. Las de `chromium-win32` no se
  pueden regenerar en este entorno y quedarán obsoletas en una corrida de Windows.

## 3. Recorrido de extremo a extremo (ejecutado en navegador)

Además de las suites, se recorrió la ruta canónica real contra un servidor local en el puerto 8899.

| Paso | Resultado |
| --- | --- |
| Inicio → tarjeta **Paso 3** | navega a Compose y marca la vista activa |
| Contador **CANONICAL CANDIDATES** | navega a Hipergrafo: los contadores son entradas reales |
| Compose · Validar | 4 hallazgos no bloqueantes; franja `validate:done / persist:current` |
| Compose · Guardar durable | `version-8e3e01176af54d5aa131fc3fec4a10b4`; franja `persist:done / matrix:current` |
| Compose · Crear TrialMatrix | `TM-16f26b13415e42cb946e`, 16 celdas, `execution_performed=false`; franja `matrix:done / prereg:current` |
| **Continuar a preregistro** | ambos `version_id` llegan al Builder sin copiar nada a mano |
| Preregistros · Crear draft durable | `prereg-ux-walkthrough-02`, `DRAFT`, root `64f49e1f…` |
| Preregistros · Readiness | **Bloqueado**, correctamente: `PR-REV-001 REFERENCE_ERROR` (falta aprobación humana del diseño) y `PR-SOFTWARE-001 INTEGRITY_ERROR` (árbol sucio frente a `allow_dirty_tree=false`) |
| Ejecución · campo root | `24/64 caracteres hex` con `aria-invalid=true` → `ROOT_SHAPE_OK` al llegar a 64 |
| Ejecución · ejecución existente `READY` | `Start` y `Cancel` habilitados; `Pause`/`Resume` deshabilitados, como manda `execution/service.py` |
| Mundo · New live sandbox | sesión `LIVE SANDBOX · CONNECTED`; tres vistas `SYNCHRONIZED` y visiblemente distintas |
| Mundo · dos STEP | `tick 0 → tick 2`, estado `READY → PAUSED` |

La cadena no se llevó hasta un lock ni hasta un `START` científico: ambas son decisiones humanas de
gobernanza con razón registrada, y el preregistro falla cerrado por diseño. Que se detenga ahí es el
comportamiento correcto, no un fallo del recorrido.

### Fallo encontrado y corregido durante el recorrido

`preregistration.js`: al enviar **Crear draft durable**, el preregistro se creaba (`201 Created`) pero
la interfaz se quedaba en el formulario con el JSON bajo el pliegue, mientras la tira de pestañas ya
marcaba `overview` como activa. El estado de la pestaña y el contenido del panel se contradecían y
una creación durable no daba ninguna confirmación visible. Ahora el envío aterriza en el Overview del
objeto creado, con su estado, versión y root.

## 4. Verificación

```text
npx playwright test                        113 passed (chromium + firefox)
.venv/bin/python -m pytest                   1 failed (preexistente)
```

El fallo de `tests/test_system_baseline_characterization.py::test_protected_source_and_historical_artifact_hashes_match_baseline`
es previo, pero **no lo causa el WIP**, como se afirmó en una versión anterior de este documento. El
fixture se baselinó en el commit `410b2693b40b1462180bff8bcbb64bb1f378688e` y HEAD es `a9bfb7a5`;
comprobado extrayendo un árbol limpio con `git archive HEAD`:

| Archivo protegido | fixture | HEAD limpio | worktree |
| --- | --- | --- | --- |
| `terrario/agent/scientific.py` | `734aa34e…` | `ea67f4c0…` ✗ | `ea67f4c0…` ✗ |
| `terrario/experiment/controller.py` | `6845940974…` | `f8080bee…` ✗ | `1707841a…` ✗ |

`scientific.py` ya diverge en HEAD limpio y el WIP no lo toca; `controller.py` también diverge en
HEAD y el WIP sólo lo lleva a un tercer valor. Limpiar o commitear el árbol no arreglaría el gate:
el fixture está desfasado respecto a HEAD y re-baselinarlo es una decisión deliberada, no una
limpieza. Ningún archivo Python fue modificado por el trabajo de UX; `terrario/lab/api.py` sí se
modificó después, para el endurecimiento del servidor, y no está entre los 70 archivos protegidos.

### Estabilidad del servidor local bajo una suite completa

Una corrida completa de la suite mostró cinco fallos en Firefox, todos
`NS_ERROR_CONNECTION_REFUSED` en `page.goto`, agrupados a mitad de la corrida y con recuperación
posterior. No eran fallos de aserción ni de interfaz: los mismos specs pasan 9/9 en Firefox
aislados, y Chromium pasó sus 58 en la misma corrida.

Causa: `terrario/lab/api.py` usaba `ThreadingHTTPServer` con los valores por defecto de
`socketserver`, entre ellos `request_queue_size = 5`. Medido con `ss -ltn`, el socket escuchaba con
un backlog de 5. Un navegador abre varias conexiones paralelas por origen y esta API además sostiene
streams SSE de larga vida; cinco conexiones pendientes se superan con facilidad en una corrida
larga, y el desbordamiento llega al navegador como conexión rechazada, no como conexión lenta.

Corrección: `LabHTTPServer` con `request_queue_size = 128`, `daemon_threads = True` y
`block_on_close = False`, de modo que un stream SSE abierto tampoco retenga el proceso al cerrar.
Verificado: el backlog pasa de 5 a 128 y la suite completa vuelve a `113 passed`.

Segundo defecto, corregido después: el registro del servidor escupía una traza de `BrokenPipeError`
cada vez que el navegador cerraba una página a mitad de respuesta. El origen es
`BaseHTTPRequestHandler.handle_one_request`, cuyo `self.wfile.flush()` final sólo protege
`TimeoutError`; cualquier desconexión se escapa hasta `handle_error` y se imprime como si fuera un
fallo del servidor. No había fuga de suscriptores —ambos handlers SSE capturan `BrokenPipeError` y
`ConnectionResetError` y liberan en un `finally`—, pero el ruido oculta trazas que sí importan.

`LabHTTPServer.handle_error` ahora suprime únicamente `BrokenPipeError`, `ConnectionResetError` y
`ConnectionAbortedError`, y delega todo lo demás en el comportamiento estándar. Verificado con 30
cortes abruptos a mitad de respuesta: cero trazas y el servidor sigue sirviendo; y con una prueba
directa de `handle_error`, donde un `ValueError` sí imprime su traza y su mensaje.

## 5. Sugerencias priorizadas

### P1 — dan el mayor retorno y no requieren decidir nada nuevo

1. **Cabecera común de las tres superficies.** Un único componente con identidad del sistema, modo,
   snapshot y los tres enlaces. Hoy cada superficie inventa la suya. Es el paso que convierte tres
   páginas en un producto.
2. **Barra de objeto activo en el Workspace.** El `execution_id`/`attempt_id` con el que se trabaja
   debería sobrevivir al cambio de contexto y mostrarse siempre. Hoy hay que volver a pegarlo a mano
   en el viewer científico.
3. **Cerrar el traspaso de la root a mano.** Un botón *copiar root* en el preregistro bloqueado y
   *pegar la última root bloqueada* en Ejecución. Hoy la interfaz pide 64 caracteres hexadecimales
   escritos por una persona, que es exactamente donde se rompe una cadena de procedencia.
4. **Aviso de par obsoleto en Compose.** Riesgo abierto en `INFORMATION_ARCHITECTURE_01` §24: el
   frontend puede conservar `draft` y `matrix` que ya no se corresponden. El preregistro falla
   cerrado, pero el aviso debería llegar antes y con cobertura E2E.

### P2 — mejoran mucho y tocan decisiones ya tomadas por el canon

5. **Controles de World2D acotados por modo.** Deshabilitar (no ocultar) los comandos de sesión en
   `PREVIEW` y `TRACE PLAYBACK`, igual que se hizo en Ejecución. Requiere ajustar
   `accessibility.spec.js`, que hoy enfoca esos botones en secuencia.
6. **Distribución legible del hipergrafo.** La rejilla actual produce una maraña. Un layout
   dirigido por fuerzas o jerárquico haría legible el corpus; antes hay que quitar de
   `hypergraph-design-bridge.spec.js` la dependencia de la coordenada fija `(34, 30)` y seleccionar
   el nodo por dato.
7. **Los errores merecen un registro, no un aviso de seis segundos.** Un panel de incidencias con
   clase de error, identidad afectada y acción de recuperación; la clase ya está modelada en
   `core/contracts.js` y se pierde al desaparecer el banner.
8. **Estados vacíos en las tres vistas de World2D.** `STALE` sobre un rectángulo blanco no dice si
   falta una sesión, una traza o una frame.

### P3 — consolidación

9. **Sistema de diseño compartido.** Tres paletas y tres escalas tipográficas conviven hoy;
   unificarlas en variables CSS comunes eliminaría la sensación de tres productos.
10. **Paleta de comandos también en el Lab.** El Workspace tiene `Ctrl+K`; el Lab tiene quince
    destinos y ninguna búsqueda.
11. **Auditoría de contraste y foco.** El ámbar sobre blanco de los avisos queda por debajo de AA en
    texto pequeño; el foco visible depende del estilo del navegador en varias superficies.
12. **Guardar el último contexto del Lab** como ya hace el Workspace con `localStorage`.

### Decisiones humanas que siguen abiertas

Estas sugerencias no las resuelven, y este trabajo no las presupone: `HD-01` contexto por defecto,
`HD-02` actividad dominante, `HD-03` centralidad de World2D, `HD-04` prominencia de la teoría,
`HD-05` comparación frecuente, `HD-06` variables cognitivas prioritarias, `HD-07` qué persiste
durante una corrida, `HD-08` consolidación de los dos D2 Studio. La ruta canónica que ahora muestra
Inicio es el orden que el dominio ya impone, no una respuesta a `HD-02`.

## 6. Lo que deliberadamente no se hizo

- No se fusionaron entidades ni se unificaron los dos hipergrafos, los tres mundos ni los dos D2
  Studio.
- No se ocultó procedencia: todo lo que se contextualizó sigue accesible desde el objeto.
- No se cambió ninguna máquina de estado, autorización, lock, seed ni plan. Los controles
  deshabilitados reflejan reglas del servidor; no las crean.
- No se tocó ningún archivo Python.

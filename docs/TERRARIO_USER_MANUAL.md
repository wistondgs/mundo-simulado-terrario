# Terrario — manual operacional del laboratorio

Este manual explica cómo operar el Terrario que existe hoy. No presupone nombres de clases ni lectura del código. Los límites científicos son parte del uso correcto: un resultado visual, un sandbox o una traza no se convierten por sí solos en evidencia científica.

## 0. Inicio rápido — los primeros 15 minutos

Si nunca abrió Terrario, haga exactamente esto y nada más.

```bash
./scripts/launch_terrario_lab.sh          # arranca el servidor y abre el Centro de revisión
```

Si el navegador no abre solo, use estas tres URL; son las tres superficies del sistema y
ninguna reemplaza a las otras:

| URL | Superficie | Para qué |
| --- | --- | --- |
| `/review-center.html` | Centro de revisión humana | decidir sobre versiones exactas; punto de entrada recomendado |
| `/` | Lab | teoría, diseño, protocolo y lectura de lo ya registrado |
| `/workspace/index.html` | Workspace científico | cross-graph, sandbox World2D y ejecución/observación científica |

Recorrido mínimo para entender el sistema sin crear nada:

1. Abra `/` → **Inicio**. La franja **Ruta canónica** son los siete pasos reales del sistema; cada
   tarjeta lleva a la vista que ejecuta ese paso. Los contadores son enlaces, no adornos.
2. Pulse **Manual** en la barra lateral. Es la misma ruta explicada paso a paso dentro de la
   aplicación.
3. Abra **Hipergrafo**. Verá `240 NODES de 1176 · OVERVIEW`: la vista general muestra sólo los
   nodos de mayor grado. Filtre o busque para pasar a `CONTEXT`. La leyenda bajo los filtros dice
   qué significa cada color.
4. Abra **World Lab** y pulse **PREVIEW ONLY**. Eso materializa un mundo determinista sin sesión ni
   agente. Los botones de sandbox siguen deshabilitados: es correcto, todavía no hay sesión.
5. Abra el **Workspace científico** (enlace al final de la barra lateral) y recorra sus cuatro
   contextos: Explorar, Diseño, Ejecución, Mundo. Sólo se monta un contexto a la vez.

Al terminar no habrá creado ningún artefacto científico. Eso es intencional: en Terrario mirar y
comprometerse son operaciones distintas.

### Qué hago ahora — tabla de decisión

| Si quiere… | Vaya a | Lo que obtiene | Lo que **no** obtiene |
| --- | --- | --- | --- |
| entender qué afirma el corpus | Lab · Hipergrafo | conceptos, relaciones y candidatos con procedencia | un mecanismo demostrado |
| convertir una relación en pregunta | Lab · Diseño experimental | rivales, predicciones, controles y bloqueos | permiso para ejecutar |
| definir qué se compara | Lab · Compose | `ExperimentDraft` durable y `TrialMatrix` | un run |
| fijar el protocolo | Lab · Preregistros | versión revisada y root bloqueada | autorización de ejecución |
| que una persona decida | Centro de revisión | decisión auditada con razón obligatoria | ejecución automática |
| probar configuración o ver el mundo | Workspace · Mundo (World2D) | sandbox de ingeniería y replay de traza | evidencia científica |
| ejecutar y observar | Workspace · Ejecución | autorización, plan sellado, frames LIVE de sólo lectura | una hipótesis confirmada |
| leer lo ya registrado | Lab · Experimentos / Run / Mundo | catálogo, métricas y replay | una reejecución |

### Cómo está organizada la barra lateral del Lab

Las quince vistas están agrupadas por etapa de la ruta canónica, no por orden histórico:

```text
1 · Orientación            Inicio · Manual
2 · Teoría y diseño        Hipergrafo · Diseño experimental · Capabilities · Metrics
3 · Protocolo y gobernanza Compose · Preregistros · Revisión científica
4 · Mundo · ingeniería     World Lab · D2 Studio
5 · Registro y análisis    Experimentos · Run · Mundo · Analizador
Sistema                    Configuración
Otras superficies          Workspace científico · Centro de revisión
```

No se eliminó ninguna vista. Un grupo es una etapa, no un permiso: estar en el grupo 3 no autoriza
nada del grupo 4.

## 1. Qué es Terrario

Terrario es un laboratorio local de experimentos con agentes en mundos deterministas. Permite definir mundos y protocolos, comparar agentes, registrar la ejecución, observar frames científicos en vivo y conservar artefactos con procedencia.

Terrario **no** es una demostración automática de inteligencia, aprendizaje, adaptación, causalidad, transferencia o ganancia cognitiva. Es la infraestructura con la que esas afirmaciones pueden ponerse a prueba bajo un protocolo adecuado.

## 2. El modelo mental correcto

```text
World       el entorno y sus reglas
Agent       el sistema que percibe, decide y aprende
Observer    registra sin dirigir al agente
Experiment  combina mundo, agentes, semillas, controles y métricas
Protocol    fija cómo se hará la comparación
Trace       registro de lo ocurrido
Recorded Playback  recorrer una traza registrada
State Restoration  recuperar un checkpoint de estado
Evidence    conclusión científica: nunca se crea automáticamente sólo por ejecutar
```

Hay tres planos que se deben distinguir siempre:

| Plano | Para qué sirve | Qué no debe concluirse |
| --- | --- | --- |
| CLI clásica | desarrollo, diagnóstico, comparaciones directas | que el resultado esté preregistrado o sea evidencia sellada |
| Engineering Sandbox / WorldStream | probar configuración y visualizar comportamiento | que sea una ejecución científica |
| Scientific Lab | diseño, preregistro, autorización, ejecución, artefactos y observación | que una ejecución ya confirme una hipótesis |

La ruta oficial recomendada es el **Scientific Lab**. La CLI no está eliminada: es una superficie avanzada.

## 3. Iniciar el laboratorio

Desde la raíz del repositorio:

```bash
./scripts/launch_terrario_lab.sh
```

También puede iniciar `./.venv/bin/python -m terrario.lab.api --root . --host 127.0.0.1 --port 8765`. El servidor local expone la UI y API en el host/puerto configurado por `terrario.lab.api` (por defecto, host local y puerto 8765). La primera vez que se use el Lab, sus artefactos locales viven bajo `.terrario/`: SQLite, CAS, backups, exports, locks y runtime. Esa carpeta es estado de laboratorio, no fuente para editar manualmente.

El acceso de Escritorio abre el **Centro de revisión humana**. Es el punto de entrada recomendado: muestra las solicitudes pendientes con su versión y hash exactos, exige una razón antes de registrar una decisión y ofrece una comprobación D2 que sólo valida/previsualiza. Desde allí, abra **Lab** para Hipergrafo, Diseño, Compose y Preregistros, o **Workspace** para el hipergrafo operacional y las visualizaciones científicas.

### Navegación por contextos

El **Workspace científico** ya no muestra todos sus instrumentos simultáneamente. Use su barra superior de contextos; el navegador conserva el último contexto y permite compartirlo como `#context=...`:

| Contexto | Úselo para | Instrumentos que aparecen |
| --- | --- | --- |
| **Explorar** | recorrer referencias, conceptos y relaciones de trabajo | Explorer, Scientific Canvas, Inspector y Research Composition |
| **Diseño** | revisar la cadena operacional y configurar D2 | Operational Hypergraph y D2 Scientific Studio |
| **Ejecución** | usar un root bloqueado, autorizar, observar y verificar | Scientific Execution y World2D Scientific, que es de sólo lectura |
| **Mundo** | previsualizar, usar sandbox de ingeniería o abrir una traza | World2D |

Los enlaces **Guía de uso**, **Diseño y protocolo** y **Preregistros** en la parte superior del Workspace abren directamente el manual, Compose o el Builder de preregistro. No cambian el experimento actual: sólo trasladan la navegación. Puede recorrer los contextos con clic o con las flechas izquierda/derecha cuando el contexto activo tiene foco. Los IDs, hashes, seed y provenance completos continúan disponibles al seleccionar el objeto correspondiente; se hicieron contextuales, no se eliminaron.

No confunda los contextos: **Mundo** controla únicamente `ENGINEERING_SANDBOX`; **Ejecución** controla el protocolo autorizado y observa Scientific LIVE; **Replay** aparece dentro del instrumento de Mundo o de World2D Scientific como lectura de una traza registrada.

Para una ejecución clásica avanzada:

```bash
./.venv/bin/python main.py run --config configs/default.yaml
./.venv/bin/python main.py verify --steps 10
./.venv/bin/python main.py ablate --config configs/default.yaml
```

`main.py run` y `scripts/run_experiment.py` son alternativas equivalentes para el runner clásico. No use ambas como si fueran dos protocolos distintos.

## 4. Mundos y dificultad

Un **World** define geometría, objetos, canales observables, reglas, cambios temporales, límites y semillas. Los escenarios versionados están en `scenarios/*.yaml`.

| Nivel | Qué intenta poner a prueba | Uso prudente |
| --- | --- | --- |
| D0 | discriminación de firmas perceptuales | baseline y único mundo hoy calificado con A0 para fork exacto |
| D1 | persistencia/movimiento de objetos | escenario histórico; confirme su protocolo antes de usarlo científicamente |
| D2 | propiedades funcionales de objetos | disponible en Studio/Lab |
| D3 | causalidad frente a correlación | mundo implementado; no prueba por sí mismo causalidad del agente |
| D4 | cambio de reglas, adaptación y variantes de transferencia | requiere protocolo y análisis específicos; no inferir adaptación/transferencia sólo por cargarlo |

### World2D y D2 Studio

En el workspace actual, use **World2D** para elegir D2, D3 o D4, cargar un preview o abrir un sandbox live. Sus controles de preview, live, trazas, cámara, comparación, marcadores y exportación sirven para inspección de ingeniería. El rótulo `ENGINEERING_SANDBOX · NOT EVIDENCE` es una frontera deliberada.

Use **D2 Studio** para inspeccionar/validar una configuración D2 y ver un diff científico de configuración. No ejecuta un experimento ni reemplaza preregistro.

Antes de pasar a un experimento, confirme:

- el scenario que se quiere comparar;
- seeds de mundo y agente;
- acciones y observaciones disponibles;
- controles y métrica;
- si la condición es un preview/sandbox o un protocolo científico.

## 5. Agentes A0–A4

| Agente | Qué tiene | Qué no debe suponerse |
| --- | --- | --- |
| A0 | acciones aleatorias | aprendizaje, memoria, modelo de mundo o competencia |
| A1 | política reactiva entrenable | estado temporal o memoria |
| A2 | estado temporal GRU | modelo de mundo o memoria persistente |
| A3 | temporalidad y modelo de mundo | memoria episódica/largo plazo |
| A4 | temporalidad, memorias, modelo de mundo, incertidumbre, planner, homeostasis y aprendizaje online configurables | prueba automática de cognición o superioridad |

En **World2D Scientific**, una traza científica identificada puede mostrar las señales cognitivas que la arquitectura declaró para ese frame. En un sandbox válido puede inspeccionar un snapshot runtime; eso no sustituye un experimento controlado.

## 6. Hipergrafos: conectar una propuesta sin falsear el resultado

En la pestaña **Hipergrafo**, los nodos `HyperedgeCandidateRecord` (naranja) representan relaciones de varios elementos hacia un resultado. Son candidatos con procedencia, no comportamientos demostrados. Seleccione uno y pulse **Abrir diseño derivado**: el Lab filtra el portfolio al diseño que conserva ese mismo identificador. Si no existe un diseño derivado, la UI lo indica; no inventa una relación experimental.

En **Diseño experimental**, revise los rivales, predicciones, intervenciones, controles, confounders y bloqueos. El botón **Usar como procedencia en Compose** sólo transfiere el ID del hipergrafo al formulario: deja explícita la procedencia sin cambiar el mundo ni crear datos.

El **hipergrafo operacional**, visible en el Workspace científico, es distinto: representa la cadena tipada diseño → preregistro → intento → frame → traza. Es una descripción del flujo del sistema, no una afirmación de que un agente mostró el comportamiento.

## 7. Preparar el diseño de un experimento

La pestaña **Compose** crea y valida un `ExperimentDraft`: seleccione escenario, agente, control, variantes, semillas, métrica y Observer. Esos componentes —no el hipergrafo por sí solo— definen qué comportamiento se compara. Pulse **Validar borrador** para revisar el contrato y **Crear TrialMatrix durable** para derivar las celdas de comparación.

Después de validar, pulse **Guardar ExperimentDraft durable**. La pantalla muestra su `version_id` y hash exactos; sólo entonces puede solicitar una revisión humana, escribiendo la razón que debe auditarse. La solicitud no se duplica por un doble clic. El Centro de revisión muestra ese objeto exacto y permite aprobarlo, pedir cambios o rechazarlo de forma explícita.

Pulse **Crear TrialMatrix durable** para materializar la matriz no ejecutora. Compose conserva localmente los IDs exactos del draft y matriz y el botón **Continuar a preregistro** los rellena en el Builder: no copie versiones de memoria ni sustituya una por otra.

Un `ExperimentDraft` y una `TrialMatrix` siguen siendo diseño: **no hay ejecución todavía**. Revise el diseño humano antes de pasar a preregistro.

### Precondiciones ocultas que ahora debes hacer explícitas

- La matriz necesita variantes, controles, seeds y métricas coherentes.
- Una ejecución científica no parte de un draft: parte de una raíz de preregistro exacta y bloqueada.
- Un lock de preregistro tampoco autoriza a ejecutar: la autorización humana es un objeto adicional.
- Los parámetros del operador, las semillas y el plan posterior quedan vinculados a identidad/hashes; no cambies valores “a mitad de camino”.

## 8. Preregistrar y bloquear

El preregistro conserva versiones, revisión, decisiones, paquetes y una cadena de auditoría. El workspace visual actual consume una root hash ya bloqueada; no expone botones para crear, derivar, revisar, someter o bloquear preregistros.

Flujo operacional:

1. Parta de un diseño ya validado.
2. Complete la revisión requerida y registre decisiones humanas donde correspondan.
3. Someta el preregistro.
4. Bloquéelo sólo cuando su protocolo esté listo para ejecutarse.
5. Verifique el resultado y copie/seleccione la **root hash exacta** de 64 caracteres hexadecimales.

No trate la hash como una contraseña arbitraria: identifica exactamente el objeto bloqueado que la ejecución va a usar. Si cambia diseño, semillas, controles o límites de forma material, cree la versión/derivación apropiada en vez de editar retrospectivamente el objeto bloqueado.

## 9. Autorizar y ejecutar científicamente

En **Scientific Execution**:

1. Introduzca la root hash de preregistro bloqueada.
2. Pulse **Request** para crear la solicitud de ejecución.
3. Cree una autorización explícita: modo, máximo de ejecuciones, razón y techo de recursos. La autorización es una política operacional y un registro de responsabilidad; no es un resultado científico.
4. Vincule la autorización y selle el plan. Revise estado, revisión y `plan_hash`.
5. Use **Start** para iniciar y despachar el plan autorizado. Use **Pause at safe boundary**, **Resume** o **Cancel** sólo si el estado lo permite; `Resume` vuelve a despachar el trabajo pendiente.
6. Al finalizar, use **Verify integrity**.

La ejecución genera intentos identificados, artefactos crudos y eventos de estado. El dispatcher usa leases e idempotencia para no convertir una pérdida de sesión en una reejecución silenciosa.

### Estados y recuperación

| Estado o señal | Significado operativo | Qué hacer |
| --- | --- | --- |
| `RUNNING` | hay un intento activo | observar LIVE; no modifique protocolo/identidad |
| `PAUSING` / `PAUSED` | pausa solicitada/alcanzada en frontera segura | revisar y reanudar o cancelar según protocolo |
| `COMPLETED` | intento y artefactos requeridos terminaron | ejecutar verificación; no equivale a hipótesis confirmada |
| `MATERIALIZATION_FAILED` | falló materialización/observación requerida; no hay traza científica completa sellable | revisar diagnóstico; no tratar el intento como evidencia |
| `RECOVERY_REQUIRED` | expiró lease o se interrumpió estado activo | usar recuperación explícita, nunca asumir continuidad |
| `ABORTED` | ejecución detenida | conservar la razón; no borrar el registro |
| `DEVIATED` | la verificación detectó desviaciones registradas | interpretar contra protocolo y no promocionar automáticamente |

## 10. Observar LIVE correctamente

La vista **World2D Scientific** es de sólo lectura. Recibe `ScientificFrame` por SSE cuando hay un intento live y puede pasar a playback después de terminal. Sus estados visibles incluyen `IDLE`, `CONNECTING`, `LIVE`, `RESYNCING`, `TERMINAL`, `PLAYBACK`, `LOST` y `ERROR`.

Un frame identifica ejecución, trial, intento y secuencia. Si un cursor no corresponde al intento, está vencido o hay un gap, el sistema exige resync en vez de inventar continuidad.

El frame reúne en un tick:

- World Truth serializada;
- observación que recibió el agente;
- vista/anotaciones del observer;
- proyección cognitiva científica;
- cursor de traza y estado runtime.

La proyección cognitiva se toma después de `learn()` y está acotada. Puede mostrar política, temporalidad, memoria, predicción/error, incertidumbre, pérdida o cambios de parámetros **sólo si esa arquitectura los declara**. `NOT_APPLICABLE`, `NON_FINITE` y `MALFORMED` son información honesta: no los conviertas en cero ni los ocultes.

### Qué puedes y no puedes inferir del observatorio

Puedes inspeccionar cómo el contrato expone señales de una arquitectura en un frame identificado y comparar cambios de frames de la misma identidad.

No puedes inferir que el agente “entendió”, que una señal interna es completa, que hubo aprendizaje útil o que existe causalidad/transferencia. El observatorio mira; el protocolo y el análisis sostienen la afirmación científica.

## 11. Resultados, traza y análisis

Los outputs de ejecución científica se guardan como artefactos crudos direccionados por contenido. La verificación revisa cadena de eventos, CAS, preregistro, plan y desviaciones. Esto protege la procedencia; no escribe automáticamente una conclusión confirmatoria.

Al inspeccionar resultados, separe cuatro niveles:

1. **Software verification:** ¿los contratos/artefactos son íntegros?
2. **Experimental validity:** ¿el protocolo, controles, exclusiones y desviaciones permiten la comparación?
3. **Scientific validation:** ¿el análisis respalda la afirmación definida?
4. **Cognitive/transfer/persistence evidence:** ¿el diseño realmente mide esos constructos y supera confusores?

Una respuesta afirmativa en 1 no implica las demás.

## 11. Recorded Playback y State Restoration

### Recorded Playback

El replay visual recorre eventos/frame ya registrados. Puede avanzar, retroceder, reiniciar y saltar a cambios, primera interacción, recuperación o ventana forense cuando esos marcadores existen. Es ideal para inspección y presentación de una trayectoria registrada.

No reejecuta el agente, no vuelve a sortear aleatoriedad y no demuestra por sí mismo reproducibilidad experimental.

### State Restoration / Experimental Reconstruction

Un checkpoint puede contener parámetros del agente, estado de optimizador, RNG Python/NumPy/Torch/generador del agente y una WorldTruth serializada. Restaurarlo recupera estado para una reconstrucción, si el checkpoint está completo y el runtime es compatible.

No confunda restaurar con abrir un playback. La primera operación altera un runtime de trabajo; la segunda sólo mueve un cursor de lectura.

## 12. Forks, controles y experimentos causales

El Fork Core no es un botón causal general. Su contrato actual sólo califica:

```text
A0_RANDOM × d0_differences.yaml
```

Fuera de ese rango el sistema debe responder `NOT_FORKABLE`. Las intervenciones registradas son control (`C00`), sham (`C01_SHAM`) y una intervención de prueba (`TEST_ENERGY_DELTA`). No presente una reejecución con la misma seed como fork causal exacto y no generalice A0×D0 a A1–A4 o D1–D4.

Cuando sea elegible, un fork crea ramas restauradas aisladamente desde el límite `POST_STATE(t*) / PRE_DECISION(t*+1)`, conserva historia compartida, aplica control/intervención y compara trazas. La identidad, hashes y aislamiento son parte del resultado; una divergencia visual sola no lo es.

## 13. Errores frecuentes

| Error de interpretación | Corrección |
| --- | --- |
| “El sandbox funcionó, por tanto el experimento es válido.” | Sandbox es ingeniería, no evidencia. Pase por diseño, preregistro, autorización y ejecución científica. |
| “El live mostró memoria, por tanto A4 aprendió.” | La señal es observabilidad; mida hipótesis, controles y resultados. |
| “Replay prueba reproducibilidad.” | Playback reproduce una visualización registrada; use seeds/checkpoints/contratos y pruebas de reproducción. |
| “Puedo modificar una configuración después del lock.” | Cree una versión o derivación; no altere retrospectivamente el objeto bloqueado. |
| “Un resultado COMPLETED confirma la teoría.” | Sólo significa que terminó la ejecución; verifique integridad, validez y análisis. |
| “Todos los forks son causales exactos.” | Sólo A0×D0 está calificado hoy. |
| “La CLI y Lab tienen las mismas garantías.” | La CLI es avanzada; Lab enlaza preregistro, autorización, plan, intentos y CAS. |

## 13 bis. Cuando la interfaz no deja avanzar

Un control deshabilitado en Terrario no es un fallo: es una precondición del protocolo dicha en voz
alta. Esta tabla traduce lo que la pantalla está diciendo.

| Lo que ve | Qué significa | Qué hacer |
| --- | --- | --- |
| World Lab: Step/Run/Pause/Resume/Stop en gris | no hay sesión `ENGINEERING_SANDBOX` | **Validate ENGINEERING_SANDBOX** y luego **Create** |
| World Lab: `Sin sandbox activo` | el estado del panel es honesto, no hay runtime detrás | cree la sesión antes de esperar frames |
| Compose: la franja de etapas se detiene en `1 · Validar` | no hay versión durable todavía | **Guardar ExperimentDraft durable**; el `version_id` aparece en el panel de identidad |
| Compose: `REVIEW_REQUIRED · NOT_PREREGISTERED` | el diseño existe y no está comprometido | es el estado normal antes del preregistro |
| Preregistros: readiness `Bloqueado` | hay hallazgos bloqueantes estructurales | resuélvalos en el diseño; no bloquee el preregistro para saltarlos |
| Ejecución: `Start` en gris con estado `REQUESTED` | falta la autorización explícita | cree la autorización; luego el plan se sella y el estado pasa a `READY` |
| Ejecución: `Pause`/`Resume` en gris | la transición no es legal en el estado actual | lea la línea de estado: dice cuál es el siguiente paso legal |
| Ejecución: el campo de root marca `n/64 caracteres hex` | la root está incompleta o mal copiada | cópiela desde el preregistro bloqueado, no la escriba |
| World2D Scientific: `No scientific attempt attached` | no hay intento vinculado al viewer | pegue execution, trial y attempt, o abra el playback CAS |
| World2D Scientific: sin controles de start/step/seed | es la frontera de sólo lectura, no un fallo | use el contexto **Mundo** si lo que quiere es un sandbox de ingeniería |
| Workspace: lienzo con `Sin porción de grafo cargada` | no hay slice abierta todavía | abra una referencia o mundo desde Explorer, o busque con `Ctrl+K` |
| Hipergrafo: `240 NODES de 1176 · OVERVIEW` | la vista general recorta por grado | filtre, busque o use el buscador de caminos para pasar a `CONTEXT` |
| Un error rojo transitorio arriba a la derecha | clase de error del transporte o del dominio | la clase importa: integridad, SSE, configuración y ejecución no son el mismo fallo |

## 14. Ruta canónica resumida

```text
Explorar referencias, mundos y configuración en el workspace
  -> preparar/validar ExperimentDraft y TrialMatrix por el flujo técnico versionado
  -> preregistrar, revisar y bloquear
  -> introducir la root hash bloqueada en Scientific Execution
  -> autorizar, sellar plan y usar Start (inicia + despacha)
  -> observar LIVE de sólo lectura
  -> completar y verificar integridad
  -> Recorded Playback / análisis derivado
  -> State Restoration o Fork sólo cuando el contrato lo permite
```

Si una pantalla no permite avanzar, no busques un atajo en el sandbox o la CLI: identifica primero qué prerequisito explícito falta.

## 15. Glosario

| Término | Qué es | Relación / no confundir con |
| --- | --- | --- |
| Agent | arquitectura A0–A4 que percibe, decide y puede aprender | no es Observer |
| Observer | componente que registra y proyecta información | no debe dirigir trayectoria del Agent |
| WorldTruth | estado autoritativo del mundo | distinto de la observación parcial del agente |
| ScientificFrame | captura atómica de un tick identificado | distinto de un estado visual libre |
| ExperimentDraft | diseño validable pero no ejecutado | distinto de preregistro bloqueado |
| TrialMatrix | expansión de condiciones y repeticiones | distinto de resultados |
| Preregistration root | hash exacta del protocolo bloqueado | necesaria, pero no suficiente, para ejecutar |
| Authorization | permiso y techo operativo explícitos | política, no prueba científica |
| CAS | almacenamiento direccionado por hash de bytes | no equivale a EvidenceGraph |
| Raw artifact | output sellado de ejecución | no equivale a evidencia confirmatoria |
| Recorded Playback | navegación de datos registrados | no reejecución |
| State Restoration | recuperación de checkpoint/rng/WorldTruth | no es un viewer |
| Fork | ramas causalmente comparables desde snapshot | actualmente sólo A0×D0 |
| WorldStream | stream de sandbox de ingeniería | no Scientific LIVE |
| Scientific World2D | viewer read-only de intento científico | no control del runtime |

## 16. Qué no tocar en operación cotidiana

No edites SQLite, CAS, hashes, checkpoints, artefactos sellados ni migraciones manualmente. No uses UI, filtros, cámara, playback o inspección como entradas del agente. No cambies una autorización/lock para “hacer que pase”. No cambies de rama, reset, clean o borres artefactos para solucionar una discrepancia: conserva la evidencia del estado y usa las rutas de recuperación/verificación.

La forma de simplificar Terrario no es quitar estos mecanismos. Es permitir que el operador siga esta ruta canónica sin tener que manipular internamente cada hash, lease, cursor, checkpoint o servicio.

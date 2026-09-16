# DOCKER_HARNESS

Fecha: 2026-09-15
Alcance: entorno contenerizado de **desarrollo y pruebas**. No es un entorno de ejecución
científica y no sustituye a `ENVIRONMENT.md`.

## 1. Qué resuelve y qué no

Resuelve la fricción operativa real de este repositorio: servidores huérfanos en 8765/8877,
colisiones de puerto, procesos de Playwright colgados y estado de ejecución mezclado entre una
corrida y la siguiente. Cada corrida obtiene su propio espacio de red y su propio estado.

**No** resuelve, y no pretende resolver:

| Bloqueo | Por qué el contenedor no lo toca |
| --- | --- |
| Árbol de trabajo sucio (`PR-SOFTWARE-001`) | es estado de git, no de entorno |
| Falta de aprobación humana del diseño (`PR-REV-001`) | es gobernanza |
| CUDA | la GPU falla a nivel de driver (Código 43, `Failed to copy vbios to system memory`); eso está por debajo del contenedor. El harness va con el wheel CPU de torch y sin librerías CUDA |

## 2. La frontera científica

Esta es la razón por la que el harness se limita a desarrollo y pruebas.

`ObservedEnvironment` captura `operating_system`, `python_version`, `torch_version`,
`cuda_compiled_version`, `cuda_available`, `device_count` y `captured_at`
(`preregistration/domain.py:373-380`, capturados en `preregistration/service.py:703-713`). Ese
registro es uno de los diez componentes sellados del bundle bajo el rol `environment_and_software`
(`preregistration/commitments.py:40,65-68`), así que **entra en la root hash**.

Dos consecuencias que hay que tener presentes:

1. Un preregistro creado dentro del contenedor produce una root hash distinta de la que produciría
   el mismo diseño en el host. No son objetos comparables en entorno.
2. **Ningún gate compara el entorno preregistrado con el de ejecución.** `grep -rn "observed"
   terrario/lab/execution/` no devuelve nada: `verify()` revisa cadena de eventos, CAS y binding de
   variantes, no el entorno. Es decir, el sistema *no* te va a detener si ejecutas en un entorno
   distinto del que preregistraste. La disciplina tiene que ser tuya.

Por eso: **la ejecución científica se queda en el host** hasta que decidas re-basear
`ENVIRONMENT.md` de forma deliberada y versionada.

## 3. Decisiones de diseño y su motivo

Cada una responde a un hallazgo verificado en el código, no a una costumbre de contenedores.

| Decisión | Motivo verificado |
| --- | --- |
| El repositorio se monta en **su ruta absoluta del host**, no en `/repo` | `config_hash` incluye la ruta absoluta del escenario (`experiment/config.py:73`) y se sella en el artefacto `TRIAL_RESULT` (`execution/dispatcher.py:78`). Montar en otra ruta cambia bytes de evidencia |
| La imagen lleva **sólo el toolchain**; el repo llega por bind mount | evita que `pyproject.toml`, `package-lock.json` o `.git` falten del contexto y produzcan hashes vacíos pero válidos |
| **git es obligatorio** en la imagen, más `safe.directory` | `_git` en `preregistration/service.py:715-720` y `execution/service.py` se tragan el fallo y devuelven `''`. Sin git, o con git rechazando el repo por propiedad, se registraría `git_commit=''` y `dirty_tree=False`: un preregistro afirmando un árbol limpio que nunca comprobó |
| `.terrario` se **oculta con un volumen** | `playwright.config.js:39` arranca el servidor con `--root .` y sin `--data-root`, así que escribiría en el data root real del host (2,5 GB, 141 preregistros bloqueados), abriéndolo y migrándolo |
| `.venv` se oculta con un volumen | el `.venv` del host pesa 7,6 GB y tiene rutas absolutas del host en `pyvenv.cfg`; no es reubicable. `playwright.config.js` invoca `.venv/bin/python` literalmente, así que el contenedor necesita su propio `.venv` en esa misma ruta |
| `node_modules` se oculta con un volumen | se instala contra el Node del contenedor |
| El contenedor corre como **uid 1000** | de lo contrario lo que escriba en el bind mount vuelve como root y el usuario del host no puede tocarlo |
| Los puntos de montaje se crean en la imagen con `chown 1000` | un volumen nombrado nuevo hereda la propiedad del directorio de la imagen; si no existe, nace `root:root` y el contenedor no puede escribir en su propio `.venv` |
| El puerto se publica en `127.0.0.1` | las rutas mutantes exigen `Host`/`Origin` de localhost. Hay que entrar por `127.0.0.1:8765`, no por nombre ni IP del contenedor |
| El corpus externo se monta en `/corpus` con `TERRARIO_PRIMARY_SOURCE_ROOT` | cuatro módulos de test importan un corpus verificado de 516 MB que vive fuera del repositorio. `tests/theory_helpers.py:14-26` lo resuelve primero por esa variable y después por `$HOME/Documentos`; como `HOME` se remapea dentro del contenedor, la variable es la única vía fiable. Sin ella los cuatro módulos fallan en la recolección |
| El wheel de torch es **CPU** por defecto | la GPU está muerta; cargar 3 GB de librerías CUDA para un dispositivo que no arranca no compra nada. El coste está medido y aislado abajo |
| `pyarrow` se instala aunque sea un extra | sin él el escritor de trazas degrada a JSONL y el fixture de comportamiento, que registra `events/consequence.parquet`, deja de coincidir |

## 4. Uso

Desde la raíz del repositorio:

```bash
docker compose -f docker/compose.yaml build
```

```bash
docker compose -f docker/compose.yaml run --rm pytest
```

```bash
docker compose -f docker/compose.yaml run --rm e2e
```

```bash
docker compose -f docker/compose.yaml up lab
```

`lab` deja la UI en `http://127.0.0.1:8765`. `shell` abre una consola interactiva dentro del
harness. Para descartar el estado acumulado del contenedor sin tocar nada del host:

```bash
docker compose -f docker/compose.yaml down -v
```

## 5. Desviaciones conocidas respecto al host

Medidas, no supuestas. Un harness que promete verde donde no lo hay es peor que ninguno.

### Verificado por medición

**El build de torch no es intercambiable.** Con `torch 2.5.1+cpu` en lugar del `2.5.1+cu121` del
host, `test_d2_d3_d4_a0_a1_a4_match_checked_in_behavior` falla. La divergencia es real y numérica,
no de identidad:

```text
cases.D2:A4_ADVANCED.metrics.prediction_errors[1]
  fixture (host, +cu121) = 0.0878492594
  contenedor  (+cpu)     = 0.0878492892
```

Los kernels CPU de las dos ruedas no son bit a bit idénticos. Un solo float a ~1e-8 cambia el
`semantic_digest` y tumba el gate.

**Cómo se trata esto.** Como la GPU está muerta a nivel de driver, el harness va con el wheel CPU y
paga ese precio de forma explícita: el servicio `pytest` **deselecciona ese test por su nombre
completo**, no por un marcador ni por un skip condicional. La exclusión es una línea visible en
`docker/compose.yaml` que cualquiera puede leer, y el gate sigue siendo **una prueba obligatoria en
el host**. Un skip silencioso habría dejado que una regresión real se escondiera detrás de una
divergencia conocida.

El servicio `pytest-all` corre la suite sin excluir nada, para confirmar que ese gate es lo único
que cuesta el wheel CPU. Si alguna vez quieres reproducir el host byte a byte dentro del
contenedor:

```bash
docker compose -f docker/compose.yaml build --build-arg TORCH_INDEX_URL=https://download.pytorch.org/whl/cu121
```

Eso añade unos 3 GB de librerías CUDA para una GPU que no puede ejecutarlas.

**`pyarrow` no es opcional pese a ser un extra.** Sin él la comparación pasa de 9 a 54 campos
distintos, porque el escritor de trazas degrada:

```text
cases.D2:A0_RANDOM.trace_file_kinds[0]
  fixture     = events/consequence.parquet
  sin pyarrow = events/consequence.jsonl
```

**La versión de numpy no fue la causa.** Fijar `numpy==2.5.2` no cambió el resultado; la diferencia
restante es íntegramente del build de torch.

**Los volúmenes anidados se inicializan desde la imagen.** Comprobado con un caso mínimo: con el
repositorio bind-montado y un volumen nombrado sobre un subdirectorio, el volumen se puebla con el
contenido de la imagen y hereda `1000:1000`. Es lo que permite que el `.venv` del contenedor exista
en la ruta que `playwright.config.js` espera sin copiar gigabytes en cada arranque.

**Arranque en frío del backend en el host:** 9,8 s hasta la primera respuesta, de los cuales 3,5 s
son `import torch`. El presupuesto de `webServer` en `playwright.config.js:42` es de 30 s. Hay
margen, pero no es holgado en un contenedor frío con límites de CPU.

### Verificado en el harness ensamblado (prueba de humo)

```text
uid=1000(ubuntu)                              nada vuelve root-owned
cwd = /home/wis/mundo simulado terrario       ruta idéntica al host
python 3.12.3 · torch 2.5.1+cpu · numpy 2.5.2
git rev-parse HEAD -> a9bfb7a5…               git honesto: safe.directory funciona
git status --porcelain -> 104 entradas        el WIP se ve tal cual
/corpus montado                               los 4 módulos que lo importan colectan
.terrario del contenedor: vacío               el data root del host es invisible
```

**Aislamiento del estado del host, medido con la suite corriendo dentro del contenedor:**

```text
                 sha256 terrario.db   mtime                 runtime/
antes            05e6cb1309f50fea     2026-09-15 21:16:02   140
durante/después  05e6cb1309f50fea     2026-09-15 21:16:02   140
```

Byte por byte idéntico. `.venv` y `node_modules` del host, intactos.

### Tamaño de la imagen: medido y corregido

La primera imagen pesaba 6,57 GB porque un `chown -R 1000:1000` posterior duplicaba la capa del
venv (1,16 GB): cambiar metadatos en una capa nueva copia los archivos. Ahora el venv se crea ya
como uid 1000 (`USER 1000` antes de `python3.12 -m venv`) y el `chown` sólo toca los puntos de
montaje vacíos. Resultado: **5,1 GB**, con la capa de 1,16 GB una sola vez (`docker history`).

### Lo que las suites del host hacían con el data root vivo — y el cierre

Al revisar el estado de CL‑7 apareció esto en `.terrario/terrario.db` del host:

| Razón de la solicitud de revisión | Nº |
| --- | ---: |
| `review exact design` | 141 |
| `review root` | 141 |
| la revisión humana real de CL‑7 (`review-82c0a332…`) | **1** |

282 de 283 solicitudes eran residuo de pruebas; había además 141 `scientific_executions` de test.
Diez de esas solicitudes cayeron en la ventana exacta de una corrida de la suite: **5 tests de
`scientific-live` × 2 solicitudes cada uno**.

**Atribución precisa** (corrige una afirmación anterior de este documento que culpaba a `pytest`):
el contaminador era la suite **e2e**. `tests_frontend/e2e/scientific-live.spec.js:10` pasaba
`".terrario"` **literalmente** al seed, y el `webServer` de `playwright.config.js:39` arrancaba con
`--root .` sin `--data-root`; el docstring del seed exige que ambos compartan root, y compartían el
vivo. `pytest` sólo lo *abría* desde tres archivos con `LabAPI(".")` — migraciones, `recover_staging`
y sidecars WAL, sin escribir revisiones.

Cierre aplicado, verificado con huella del DB vivo antes y después:

| Fuga | Corrección | Verificación |
| --- | --- | --- |
| `webServer` sobre el root vivo | `playwright.config.js` resuelve `TERRARIO_E2E_DATA_ROOT` (default `.sandbox/e2e-data-root`, absoluto, gitignored) y lo pasa como `--data-root` y como env a los workers | `human-entrypoints` corrió: DB/WAL/runtime del host idénticos; el root temporal apareció con `terrario.db`, `blobs/`, `runtime/` |
| seed con `".terrario"` literal | el spec lee la variable y **falla** si no está | — |
| seed con default al root vivo | `seed_scientific_live_e2e.py` exige root absoluto y rechaza el root vivo | las tres invocaciones inseguras rechazadas con mensaje; DB intacto |
| `LabAPI(".")` en tres tests | `data_root=tmp_path/".terrario"` | 23 tests pasan, guardián en silencio |
| nada vigilaba el root vivo | `tests/conftest.py`: huella de `terrario.db`, `terrario.db-wal` y `runtime/` al inicio y al final; cualquier deriva pone la sesión en rojo con la diferencia impresa | `tests/test_live_root_guard.py` prueba que dispara ante escritura al DB, escritura aparcada en el WAL y un intento nuevo en `runtime/` |
| el contenedor habría escrito e2e en `.sandbox/` del host | `compose.yaml` fija `TERRARIO_E2E_DATA_ROOT` dentro del volumen `.terrario` | — |

Lo que **no** se corrió: `scientific-live.spec.js` completo, porque instancia agentes y esa decisión
es humana mientras CL‑7 siga pendiente. Correrlo una vez es la prueba definitiva del cierre y no
produce evidencia científica alguna: escribe en el root temporal.

### Medido el 2026-09-16

Esta sección reemplaza a la anterior, titulada «No medido», según la instrucción que ella misma
dejó escrita: *cuando se midan, esta sección debe reemplazarse por resultados, no ampliarse con
más hipótesis*. Las corridas fueron autorizadas por el investigador como parte de la revisión
nocturna; ninguna escribió en el root científico vivo (hash `5527cf7b…` sin cambio, verificado
al principio y al final).

#### Suite Python: el coste de la rueda CPU es exactamente un test

| | tests | pasan | skip | fallan | tiempo |
|---|---:|---:|---:|---:|---:|
| Host | 562 | 560 | 1 | 1 | 10 min 09 s |
| Contenedor (1 deseleccionado) | 561 | **559** | 1 | 1 | 15 min 55 s |

560 − 559 = 1, **exactamente el gate de caracterización deseleccionado por nombre**. La hipótesis
queda confirmada: la rueda `+cpu` no cuesta nada más. El único fallo en ambos lados es el gate de
hashes protegidos, que es una decisión de línea base pendiente, no un defecto del contenedor.

Sobrecoste de tiempo: **factor 1,57×**.

El guard de `tests/conftest.py` imprimió `terrario live data root: unchanged (guard passed)`
también dentro del contenedor, lo que confirma que el volumen nombrado **sombrea de verdad** el
`.terrario` del host — la parte del diseño que no se podía comprobar sin correrla.

#### Suite e2e: 101 pasan, 12 fallan, y los 12 estaban predichos

| Hipótesis previa | Veredicto | Evidencia |
| --- | --- | --- |
| Las tres pruebas de `visual-qa` fallarán por la pila de fuentes del host | **CONFIRMADA** | exactamente 3 fallos, los tres `toHaveScreenshot`: `workspace shell`, `world2d panel`, `d2 studio` |
| Firefox sin display pierde WebGL2 | **CONFIRMADA** | 9 fallos, todos en Firefox: las 8 de `world2d-performance` (100 → 50 000 entidades) y la de `world2d-renderer-resilience` |
| `webServer` podría superar los 30 s en el primer arranque frío | **REFUTADA** | arrancó dentro del plazo; la suite corrió entera en 7 min 58 s |
| `tests/test_scientific_live_observability.py` puede colgarse | **REFUTADA** | no se colgó; la suite Python cerró en 15 min 55 s |

Total: 113 pruebas, las mismas que en host. En host pasan 113/113; en contenedor 101/113, y la
diferencia son **las 12 que dependen de fuentes del sistema y de aceleración gráfica** — ninguna
de ellas es una prueba de lógica científica.

**Conclusión operativa:** el contenedor sirve para la suite Python y para las e2e que no
dependen del renderizado. Las tres de `visual-qa` y las diez de WebGL2 siguen siendo **gates de
host**, por la misma razón que el gate de caracterización: comparan contra una línea base
grabada con la pila del host.


# TUTORIAL — la cadena científica completa, paso a paso

Fecha: 2026-09-15
Qué es: un recorrido **real** por todo el protocolo, ejecutado contra un data root de tutorial.
Qué no es: evidencia. El diseño es desechable, el root es un directorio de borrador y las tres
compuertas humanas las firmó un script. Esa sustitución es la única diferencia entre este tutorial
y ciencia — y es toda la diferencia.

## Cómo reproducirlo

```bash
./.venv/bin/python scripts/tutorial_scientific_chain.py "$PWD/.sandbox/tutorial-data-root"
```

El script exige un root **absoluto** y **se niega** a correr contra `.terrario`, el root vivo. Para ver
el resultado en la interfaz, levanta un lab sobre ese root en otro puerto:

```bash
./.venv/bin/python -m terrario.lab.api --root . --data-root "$PWD/.sandbox/tutorial-data-root" --host 127.0.0.1 --port 8899
```

y abre `http://127.0.0.1:8899/workspace/index.html#context=execute`. El lab vivo en 8765 no se entera.

## La corrida que documenta este tutorial (`TUTORIAL 5057b020`)

Cada paso produce **una identidad distinta**. Ninguno convierte al anterior en evidencia.

| # | Quién | Paso | Identidad que nace |
| --- | --- | --- | --- |
| 1 | Compose | `ExperimentDraft` durable | `version-659939cd…` · hash `532c4d5a…` · estado `REVIEW_BLOCKED` |
| 2 | Compose | `TrialMatrix` durable | `TM-6629c6eb…` · `total_trials 1` · `execution_performed False` |
| 3 | Compose | solicitud de revisión del diseño | `review-86a066a9…` vinculada a la versión exacta |
| 4 | **◆ humana** | decisión sobre el diseño | `decision-c5a2b406…` `APPROVE_FOR_EXPERIMENT_DESIGN` |
| 5 | Preregistros | crear preregistro desde las versiones exactas | `PR-TUTORIAL-5057b020` · `DRAFT` |
| 6 | Preregistros | readiness | `completo True` · bloqueantes `[]` · avisos `PR-EXPOSURE-001`, `PR-PROXY-001` |
| 7 | Preregistros | preparar revisión: sella el bundle | root `37be29b1390e3bace13151e5cbe1fd63d80ac689948889b11fc90d87f6365a34` |
| 8 | Preregistros | someter el root | `review-45c529e1…` |
| 9 | **◆ humana** | decisión sobre el preregistro, aceptando cada aviso por su hash | `decision-a9d1d1e5…` |
| 10 | **◆ humana** | ceremonia de lock — a mano se teclea `LOCK 37be29b1390e` | root bloqueada = la misma |
| 11 | Ejecución | solicitud contra la root bloqueada | `execution-b95819dd…` · `REQUESTED` · rev 0 |
| 12 | **◆ humana** | autorización explícita con techo de recursos | `authorization-93db62db…` · `ONE_EXECUTION` · máx 1 |
| 13 | Ejecución | bind + sellar plan | `READY` · rev 4 · plan `53ce286c…` |
| 14 | Ejecución | `START` consume la autorización; `dispatch` al worker | `RUNNING` → `COMPLETED` en 12,3 s |
| 15 | Ejecución | estado terminal y artefactos | 2 artefactos · 1 `SCIENTIFIC_TRACE` · `trial-intent-8dfea0e4…` / `trial-attempt-5aab48e9…` |
| 16 | Ejecución | verificación de integridad | `classification PASS` · `warnings []` |

## Lo que cada compuerta humana significa

| Compuerta | En el tutorial | En producción |
| --- | --- | --- |
| 4 · decisión sobre el diseño | el script escribe `APPROVE_FOR_EXPERIMENT_DESIGN` con actor `local-user` | una persona lee el diseño, escribe qué revisó y teclea `REVIEW <hash[:12]>`. Es la que hoy está pendiente para CL‑7 (`review-82c0a332…`) |
| 9 · decisión sobre el preregistro | el script acepta los dos avisos por su `finding_hash` | la persona decide si `PR-EXPOSURE-001` y `PR-PROXY-001` son aceptables para *este* estudio |
| 10 · lock | el script envía `LOCK 37be29b1390e` | se teclea a mano; congela el protocolo. **No autoriza nada** |
| 12 · autorización | el script firma `ONE_EXECUTION`, techo 1 CPU / 1 GiB / 3600 s | es un registro de responsabilidad: quién permite gastar qué, cuántas veces, por qué |

Nótese el paso 6: el readiness salió limpio **solo porque** el paso 4 ya estaba firmado. En el preregistro
real de CL‑7, hoy, ese mismo readiness devuelve `PR-REV-001` bloqueante — exactamente porque la
decisión humana sigue sin registrarse.

## Lo que NO produjo esta corrida

- Ninguna escritura en `.terrario` (huella del DB vivo idéntica antes y después; ver abajo).
- Ningún `EvidenceGraph`. `COMPLETED` + `PASS` significa «terminó y es íntegro», no «la hipótesis se
  sostiene». La publicación empírica es un paso posterior, con su propia elegibilidad.
- Ninguna afirmación sobre el agente: una traza de 100 pasos de A4 en D2 con una semilla es una
  traza, no un resultado.

## Un detalle de honestidad

El preregistro se creó con `allow_dirty_tree: True` porque el árbol de trabajo está sucio. En
producción, marcar esa casilla es una decisión que se toma sabiendo que el `SoftwareManifest`
registrará `dirty_tree: true` y el hash del diff — no un flag para que pase.

## Verificación medida tras la corrida

```text
root VIVO (.terrario)          antes                    después
  terrario.db sha256           05e6cb1309f50fea         05e6cb1309f50fea
  runtime/ entradas            140                      140
  review_decisions             282                      282
  CL-7 (review-82c0a332…)      sin decisión             sin decisión

root de TUTORIAL (.sandbox/tutorial-data-root)   2 decisiones · 1 ejecución · 19 MB
```

El tutorial vivió entero en su propio root. El data root científico no recibió un byte.

## Qué se ve después, en el observatorio (Workspace · Ejecución, puerto 8899)

Con la ejecución terminal, `World2D Scientific` se vincula al intento por sus tres identidades
(`execution`, `trial`, `attempt`) y pasa por dos modos, ambos de **solo lectura**:

| Acción | Modo | Qué muestra |
| --- | --- | --- |
| Attach live sobre un intento ya terminado | `SCIENTIFIC · TERMINAL` | la última frame (step 100) con su proyección cognitiva |
| Open playback | `SCIENTIFIC · PLAYBACK` | «Durable CAS playback · 101 frames · provenance identical to live», cursor 0–100 |

Lo que la proyección cognitiva de A4 dice en dos frames de la misma traza — leído del DOM, no
inventado:

| Campo | frame 0 | frame 50 |
| --- | --- | --- |
| Selected action | 0 | 1 |
| Selected action probability | `UNSUPPORTED` | 0.96967 |
| Policy entropy | `UNSUPPORTED` | 0.145732 |
| Policy logits · projection | `NULL` | array[25] · 25 finitos · 0 no finitos |
| Uncertainty | — | 0.30638 |
| Prediction error ε | — | 0.367764 |
| Current loss | — | `UNSUPPORTED` |
| Episodic memory / Long-term norm | — | `UNAVAILABLE` |

Dos lecciones están ahí mismo. En el frame 0 no hay decisión todavía, y el observatorio dice
`UNSUPPORTED` y `NULL` en vez de pintar ceros: los estados de ausencia son información, no vacío.
Y en el frame 50, `UNAVAILABLE` en memoria no significa que A4 no tenga memoria: significa que esta
arquitectura, en esta configuración, no declaró ese dominio para transporte. El observatorio
enseña lo que el contrato expone de un frame identificado; **no prueba aprendizaje, creencia ni
competencia**. Eso lo sostienen el protocolo y el análisis, que aquí no se hicieron.

El panel de ejecución, a su izquierda, muestra `COMPLETED` con `Start/Pause/Resume/Cancel`
deshabilitados — ilegales en estado terminal — y solo `Verify integrity` activo. Un estado
terminal no ofrece comandos que el servidor rechazaría.

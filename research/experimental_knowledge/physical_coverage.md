# Cobertura física y científica reconciliada

## Medición

La cifra inicial de ~3,65 GB fue una suma selectiva de ocho directorios
visibles de investigación. El árbol local completo medía aproximadamente 20 GB
en el momento de la inspección. La diferencia no prueba datos científicos
omitidos por sí sola: incluye entornos, cachés y registros de herramientas.

| Conjunto local | Tamaño aproximado | Clasificación | Publicación |
|---|---:|---|---|
| `.venv/` | 7,6 GB | dependencias regenerables | excluido |
| `.claude/` | 3,9 GB | caché/worktrees de herramienta | excluido por defecto |
| `.terrario/` | 2,5 GB | base/artefactos locales | sólo índice, pendiente de revisión por procedencia |
| `.sandbox/` | 2,4 GB | sandboxes de herramienta | local; no evidencia científica por nombre |
| `.sandbox-addressing`, `.sandbox-capability`, `.sandbox-closed-loop`, `.sandbox-screening` | 1,78 GB | JSON de engineering sandbox versionados | no extraer automáticamente: pueden contener contexto conversacional |
| `runs/` | 954 MB | mixto: piloto H-ADAPT, screening y fixtures | H-ADAPT individualizado; resto delimitado por tipo |
| `.git/` | 193 MB | historia, refs y objetos recuperables | no publicar objetos inalcanzables sin procedencia |
| `experiments/`, `docs/`, `research/`, `artifacts/` | ~16 MB | fuentes científicas y documentos versionados | indexados por ref/ruta |
| `node_modules/` | 19 MB | dependencia regenerable | excluido |

## Hallazgo de cobertura

Los directorios ocultos explican gran parte de la discrepancia de espacio. Una
muestra de los JSON `.sandbox-*` tiene `classification = ENGINEERING_SANDBOX`;
no se reclasifica como experimento científico sin contrato, mundo, agente y
procedencia específicos. Los rollouts de custodia de PRIMITIVO también pueden
contener contexto de sesión, por lo que no se exportan como “traza de conducta”
sin una revisión de divulgación independiente.

## Relación entre árboles

Terrario es el aparato experimental y el linaje A0–A5. Genesis/RNE/RNFE son
árboles vinculados por documentación y contratos, no subdirectorios que este
expediente pueda copiar o fusionar. Durante el inventario se verificaron árboles
externos disponibles para Genesis y RNE; su contenido queda fuera de esta
publicación salvo referencias ya documentadas por los Atlas 05–07. RNFE no fue
localizado en la ruta histórica indicada por el Atlas.

## Límite de cobertura

El recuperador publicado puede producir inventarios de metadatos por raíz sin
reescribir artefactos. La revisión de contenido individualizó las 32 corridas
H-ADAPT; los JSONL D4T son medidas agregadas y el ledger `.terrario` no
contiene resultados científicos. No se declara cobertura integral del resto.

# Expediente científico experimental de Terrario

## Alcance

Este directorio es un índice de recuperación, no una nueva cartografía, un
resultado experimental ni una integración de ramas. Fue construido en la rama
`docs/experimental-knowledge-recovery-01`, desde la base limpia
`d2824ba18f3c83003635fdb10304f08d002a76ec`.

Sus fuentes son: la cartografía y los Atlas existentes; referencias Git locales
y remotas recuperables; los dos worktrees locales existentes en el momento del
inventario; y artefactos locales no rastreados que se clasifican sin copiarlos.
No se ejecutaron campañas, no se regeneraron resultados y no se alteró ningún
worktree preexistente.

## Cómo leerlo

1. [`source_inventory.json`](source_inventory.json) indica qué patrimonio se
   inspeccionó, dónde se conserva y si es accesible remotamente.
2. [`experiment_registry.json`](experiment_registry.json) usa como unidad una
   ejecución/campaña identificable, no sólo un documento.
3. [`capability_matrix.md`](capability_matrix.md) separa mecanismo, evidencia,
   condiciones y estado epistemológico.
4. [`trace_evidence.md`](trace_evidence.md) identifica trazas y extractos
   disponibles, incluidas limitaciones de preservación.
5. [`coverage_and_limits.md`](coverage_and_limits.md) delimita exactamente qué
   puede auditar un investigador remoto y qué permanece local.
6. [`physical_coverage.md`](physical_coverage.md) reconcilia la medición física
   del laboratorio y separa datos científicos de entornos y caches.
7. [`executions/h_adapt_001_pilot_execution_catalog.json`](executions/h_adapt_001_pilot_execution_catalog.json)
   enumera las 32 ejecuciones recuperadas del piloto H-ADAPT-001.
8. [`executions/h_adapt_001_behavioral_extracts.json`](executions/h_adapt_001_behavioral_extracts.json)
   contiene tres ventanas conductuales: recuperada, negativa e inconclusa.
9. [`executions/h_adapt_001_behavioral_windows_all.json`](executions/h_adapt_001_behavioral_windows_all.json)
   permite abrir la ventana original alrededor del cambio causal de cualquier
   `run_id` del catálogo.

El recuperador [`scripts/inventory_experimental_sources.py`](../../scripts/inventory_experimental_sources.py)
produce un inventario de metadatos sin modificar los originales. Por defecto
escribe JSON a stdout; sólo calcula hashes completos con `--hash`.

## Reglas de lectura

* **Demostrado** significa sólo “demostrado bajo el contrato y mundo citados”.
* Un cierre negativo del mecanismo no falsifica automáticamente la familia de
  capacidad: véase 1.8 frente a L19.
* Un archivo local no rastreado no se atribuye a un SHA confirmado; se registra
  con su hash de archivo y su procedencia disponible.
* La ausencia de un artefacto primitivo se registra como limitación, no se
  reemplaza por una narración retrospectiva.

## Entrada para revisión remota

Las fuentes Git se pueden abrir por ref y ruta mediante GitHub. Para una fuente
local marcada `LOCAL_ONLY`, este expediente permite localizarla y verificar su
hash en el laboratorio, pero **no** la convierte en evidencia remotamente
auditable. Ningún secreto, ruta absoluta, base de datos completa, checkpoint
pesado ni traza masiva fue copiado a esta publicación.

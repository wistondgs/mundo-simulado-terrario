# Nivel 1.5 — paquete de diseño · versión supersedida/canónica v2

Estado: **solo diseño; sin rama, carpeta de implementación ni código de Nivel 1.5**.

Este paquete conserva byte-idénticos los cinco documentos del snapshot anterior y añade una supersesión explícita. El snapshot anterior NO se reescribe; queda histórico.

## Orden de autoridad

1. `LEVEL15_06_SUPERSESSION_2026-09-20.md`
2. `LEVEL15_01_ENTREGABLE_1_CONSTRUCTO.md`
3. `LEVEL15_02_ENTREGABLE_2_APRENDIBILIDAD.md`
4. `LEVEL15_03_ENTREGABLE_3_MECANISMO_CAMPANA.md`
5. `LEVEL15_04_AUDITORIA_FUGAS_Y_COORDINACION.md`
6. `LEVEL15_05_ESTADO_Y_DECISION_LOG.md`
7. `MANIFEST_LEVEL15_V1_FROZEN.md` — registro histórico solamente

Cuando exista conflicto, la supersesión tiene precedencia.

## Cambios canónicos de v2

Se retiran como expectativas vigentes:

- `31/40`, `28/40`, `31/40`;
- “30 fallos = 9 óptimos locales + 21 barreras de coordinación” como propiedad del problema;
- dificultad estructural de `R_P`;
- presupuesto de `100.000` seleccionado por saturación;
- bandas anteriores `15–21 %` o `20–35 %` como frecuencia canónica de fallo.

Evidencia visible con paso constante:

- a `10.000`: `R_G 59/60`, `R_P 55/60`, `R_J 60/60`, total `174/180`;
- a `100.000`: `R_G 60/60`, `R_P 59/60`, `R_J 60/60`, total `179/180`.

Sigue vigente:

- Entregable 1 y sus resultados matemáticos;
- endpoint primario = clase informacional;
- feedback de un bit;
- mecanismo de dos tablas;
- decoder sólo `(z,q)`;
- una actualización por tabla y por ensayo;
- tablas read-only durante el intervalo;
- H1/H2/H3 como regiones diagnósticas, no acciones.

## Discrepancia abierta

El reporte fuente afirma `540 corridas, tres presupuestos`, pero la tabla disponible contiene sólo `360 corridas, dos presupuestos`. El tercer presupuesto queda `PENDING_RECONCILIATION` y no se inventa en este paquete.

## Snapshot anterior

SHA-256 del paquete histórico:

`135d07ea36d13d554a200c59f31d3e866e2ce768212821e8606c06c9cfab9d78`

SHA-256 del manifiesto histórico:

`15444032a977f75b831b5ff12a365321e01374d9e02c34b81afecfcf07449c06`

`SHA256SUMS.txt` contiene las huellas de los archivos de esta versión v2.

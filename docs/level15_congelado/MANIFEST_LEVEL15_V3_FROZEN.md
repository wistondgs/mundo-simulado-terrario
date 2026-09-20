# Nivel 1.5 — paquete de diseño canónico v3

**Fecha:** 2026-09-20  
**Estado:** solo diseño; sin rama, carpeta de implementación ni código de Nivel 1.5.

## Orden de autoridad

1. `LEVEL15_07_SUPERSESSION_V3_2026-09-20.md` — autoridad canónica actual
2. `LEVEL15_06_SUPERSESSION_2026-09-20.md` — snapshot v2, supersedido donde exista conflicto
3. `LEVEL15_01_ENTREGABLE_1_CONSTRUCTO.md`
4. `LEVEL15_02_ENTREGABLE_2_APRENDIBILIDAD.md`
5. `LEVEL15_03_ENTREGABLE_3_MECANISMO_CAMPANA.md`
6. `LEVEL15_04_AUDITORIA_FUGAS_Y_COORDINACION.md`
7. `LEVEL15_05_ESTADO_Y_DECISION_LOG.md`
8. `MANIFEST_LEVEL15_V2_FROZEN.md` — registro histórico de v2
9. `MANIFEST_LEVEL15_V1_FROZEN.md` — registro histórico de v1

Ante conflicto, el documento de supersesión v3 tiene precedencia.

## Cambios canónicos de v3

Se cierra la reconciliación pendiente de v2 incorporando el tercer presupuesto:

- 10.000: `R_G 59/60`, `R_P 55/60`, `R_J 60/60`, total `174/180`;
- 20.000: `R_G 57/60`, `R_P 60/60`, `R_J 59/60`, total `176/180`;
- 100.000: `R_G 60/60`, `R_P 59/60`, `R_J 60/60`, total `179/180`;
- total piloto: `529/540 = 97,96 %`.

Se retira definitivamente:

- cualquier dificultad estructural o transitoria estable de `R_P`;
- la pregunta “por qué R_P es más difícil”;
- `100.000` como presupuesto justificado por saturación de la regla anterior;
- cualquier banda antigua de fallos como propiedad del experimento vigente.

Se fija para confirmación:

- `10.000` ensayos por corrida como **lowest demonstrated pilot budget**, no mínimo;
- 16 semillas nuevas `130000011 … 130000026`;
- 48 corridas confirmatorias emparejadas (`16 × 3 regímenes`);
- las semillas `20260920`, `777`, `31337` quedan **BURNED** y prohibidas en confirmación.

## Colisión histórica de semilla

`20260920` coincide numéricamente con la ventana de Nivel 1.0 `20260919…20260950`.

Se registra como colisión conocida y sin efecto científico identificado: se usó con generadores distintos y en papeles experimentales distintos. No se permite su reutilización confirmatoria.

## Formulación canónica de Nivel 1.5

> **La misma arquitectura aprende a preservar información diferente según lo que la experiencia hace útil.**

## Lo que sigue vigente

- Entregable 1 y resultados matemáticos;
- endpoint primario = clase informacional;
- feedback de un bit;
- encoder + decoder aprendidos mediante dos tablas;
- decoder sólo `(z,q)`;
- una actualización por tabla y ensayo;
- tablas read-only entre retención y respuesta;
- H1/H2/H3 como regiones diagnósticas, no acciones.

## Lo que sigue abierto

- magnitud exacta del paso constante;
- schedule exacta de exploración y sensibilidad;
- clasificador final de clases;
- gates/fixtures negativas finales;
- preregistro confirmatorio.

Hasta cerrar esas piezas: **NO IMPLEMENTAR**.

## Integridad histórica

SHA-256 paquete v2:

`ab7785bbe76acb421fe59a7fb77574d823e5bddfafd2b7cff91b7557e03bc7ab`

SHA-256 supersesión v2:

`3d5632d99b659565273b7f1b844152618ecd27fb5bf4a1605e3406f3f713ede6`

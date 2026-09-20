# Nivel 1.5 — paquete de diseño canónico v4

**Fecha:** 2026-09-20  
**Estado:** solo diseño; sin rama, carpeta de implementación ni código de Nivel 1.5.

## Orden de autoridad

1. `LEVEL15_08_SUPERSESSION_V4_2026-09-20.md` — autoridad canónica actual para reserva de semillas
2. `LEVEL15_07_SUPERSESSION_V3_2026-09-20.md` — autoridad canónica para piloto, presupuesto y decisiones de v3
3. `LEVEL15_06_SUPERSESSION_2026-09-20.md` — snapshot v2, supersedido donde exista conflicto
4. `LEVEL15_01_ENTREGABLE_1_CONSTRUCTO.md`
5. `LEVEL15_02_ENTREGABLE_2_APRENDIBILIDAD.md`
6. `LEVEL15_03_ENTREGABLE_3_MECANISMO_CAMPANA.md`
7. `LEVEL15_04_AUDITORIA_FUGAS_Y_COORDINACION.md`
8. `LEVEL15_05_ESTADO_Y_DECISION_LOG.md`
9. `MANIFEST_LEVEL15_V3_FROZEN.md` — registro histórico de v3
10. `MANIFEST_LEVEL15_V2_FROZEN.md` — registro histórico de v2
11. `MANIFEST_LEVEL15_V1_FROZEN.md` — registro histórico de v1

Ante conflicto, la supersesión más reciente tiene precedencia sólo sobre el ámbito que modifica.

## Cambio canónico de v4

Se corrige la reserva archivística de semillas confirmatorias:

- primarias: `130000011 … 130000026`;
- orientación derivada: `σ+7` → `130000018 … 130000033`;
- span completo reservado: `130000011 … 130000033`.

No cambia el número de primarias: 16. No cambia el total confirmatorio previsto: 48 corridas (`16 × 3 regímenes`).

Se registra además que primarias y derivadas se solapan numéricamente en `130000018 … 130000026`. El cierre archivístico queda hecho; la inocuidad estadística de ese solapamiento debe auditarse antes del preregistro final.

## Formulación canónica de Nivel 1.5

> **La misma arquitectura aprende a preservar información diferente según lo que la experiencia hace útil.**

## Evidencia piloto vigente

- 10.000: `R_G 59/60`, `R_P 55/60`, `R_J 60/60`, total `174/180 = 96,67 %`;
- 20.000: `R_G 57/60`, `R_P 60/60`, `R_J 59/60`, total `176/180 = 97,78 %`;
- 100.000: `R_G 60/60`, `R_P 59/60`, `R_J 60/60`, total `179/180 = 99,44 %`;
- total: `529/540 = 97,96 %`.

Las 540 corridas son `PILOT / DISCOVERY`.

## Semillas de diseño quemadas

- `20260920`;
- `777`;
- `31337`.

Quedan prohibidas en la campaña confirmatoria.

## Lo que sigue abierto

- magnitud exacta del paso constante;
- schedule exacta de exploración y sensibilidad;
- clasificador final de clases;
- gates/fixtures negativas finales;
- auditoría RNG del solapamiento interno de enteros entre `σ` y `σ+7`;
- preregistro confirmatorio.

Hasta cerrar esas piezas: **NO IMPLEMENTAR**.

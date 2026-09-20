# NIVEL 1.5 — SUPERSESIÓN v4 · RESERVA COMPLETA DE SEMILLAS CONFIRMATORIAS

**Fecha:** 2026-09-20  
**Estado:** diseño; Nivel 1.5 sigue sin rama, carpeta ni código de implementación.  
**Autoridad:** este documento supersede únicamente la declaración incompleta de reserva de semillas confirmatorias de v3. El resto de v3 permanece vigente.

## 0. Regla de archivo

La v3 permanece congelada y verificable. No se edita retroactivamente.

La corrección se añade como nueva supersesión para preservar las huellas ya verificadas de v3.

---

## 1. Primarias y flujo derivado `+7`

La campaña confirmatoria usa 16 semillas primarias:

`130000011 … 130000026`

Cada reconstrucción usa además:

`σ + 7`

para el flujo de orientación, según la receta heredada desde Nivel 1.1.

Por tanto, las semillas derivadas cubren:

`130000018 … 130000033`

La reserva archivística completa debe declarar la unión de ambos usos:

> **SPAN RESERVADO COMPLETO: `130000011 … 130000033`**

El span contiene 23 valores enteros distintos.

No se autoriza asignar ninguno de esos valores a futuros experimentos mientras esta campaña permanezca reservada.

---

## 2. Qué no cambia

Siguen siendo 16 semillas primarias y 16 tripletes emparejados:

- `R_G`;
- `R_P`;
- `R_J`.

Total previsto:

`16 × 3 = 48` corridas confirmatorias.

El hecho de reservar el span completo no aumenta el número de corridas ni transforma los valores `σ+7` en semillas primarias adicionales.

---

## 3. Colisiones externas

Chequeo reportado:

> **ninguna colisión con las semillas registradas previamente en el span completo `130000011 … 130000033`.**

La colisión histórica de la semilla piloto `20260920` con Nivel 1.0 permanece documentada como colisión archivística conocida y sin efecto científico identificado. Las semillas piloto `20260920`, `777` y `31337` siguen `BURNED` y prohibidas en confirmación.

---

## 4. Nota metodológica sobre solapamiento interno

La unión de primarias y derivadas tiene un solapamiento numérico interno:

`130000018 … 130000026`

Es decir, algunos enteros aparecen como `σ+7` de una primaria anterior y como `σ` de una primaria posterior.

Esta supersesión **no afirma por sí sola** que ese solapamiento sea estadísticamente inocuo. Su función es cerrar el libro de semillas y evitar reutilización externa accidental.

Antes del preregistro confirmatorio debe verificarse una de estas dos condiciones:

1. los usos `σ` y `σ+7` están separados por namespace/generador/rol de forma que compartir el entero no reutiliza el mismo flujo pseudoaleatorio; o
2. si no lo están, debe justificarse explícitamente por qué la dependencia determinista resultante no invalida el emparejamiento o, en su defecto, reservar primarias espaciadas para que primarias y derivadas sean disjuntas.

Este punto pertenece a la auditoría de RNG del preregistro, no al cierre archivístico.

---

## 5. Formulación canónica de la reserva

La formulación autorizada pasa a ser:

> **Semillas primarias confirmatorias: `130000011 … 130000026` (16). Flujo derivado de orientación: `σ+7`, alcanzando `130000018 … 130000033`. Span archivístico reservado completo: `130000011 … 130000033`.**

---

## 6. Estado de Nivel 1.5 tras esta supersesión

No cambia ninguna conclusión científica ni ningún resultado piloto.

Permanece vigente:

> **La misma arquitectura aprende a preservar información diferente según lo que la experiencia hace útil.**

Y permanecen abiertos antes de implementar:

- magnitud exacta del paso constante;
- programa exacto de exploración y sensibilidad;
- clasificador final de clases;
- gates y fixtures negativas;
- auditoría RNG del solapamiento interno `σ` / `σ+7`;
- preregistro confirmatorio final.

Hasta entonces:

`NO IMPLEMENTAR`.

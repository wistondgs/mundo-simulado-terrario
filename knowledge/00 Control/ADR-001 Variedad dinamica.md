---
kind: decision
status: PROPOSED
date: 2026-09-16
owner: human
---

# ADR-001 — Variedad dinámica

- **Estado:** PROPOSED
- **Fecha:** 2026-09-16
- **Alcance:** marco conceptual del objeto de estudio y, en consecuencia, qué puede afirmar el
  instrumento `viability-recovery-profile` antes de recibir firma.

## Decisión propuesta

> Nada relevante se supone estático salvo que un experimento lo congele deliberadamente **como
> control declarado**.

El estado del sistema deja de escribirse `E, 𝒱, D, R` y pasa a escribirse `Eₜ, 𝒱ₜ, Dₜ, Rₜ`, con
`Wₜ, Mₜ, Πₜ, Cₜ, Sₜ, Aₜ, Kₜ` igualmente indexados. Se distinguen seis clases de variedad:
exógena, endógena, **de la región de viabilidad**, relacional, temporal y **generada por el
propio ser**.

Consecuencias que el investigador deriva:

1. `Eₜ ∈ 𝒱ₜ` — la región viable se desplaza, se contrae o se deforma. La viabilidad es una
   geometría dinámica, no un umbral.
2. Recuperación **no** es restauración. `x₁ → x₂` con `x₂ ≠ x₀` y `E(x₂) ∈ 𝒱₂` es recuperación
   por reorganización, y puede ser científicamente más importante que el retorno.
3. La pregunta de Ashby se vuelve temporal: no `V_R ≥ V_D` sino `dV_R/dt`, y el Caso 3
   —`V_D > V_R(t₀)` seguido de `V_R(t₁) ≥ V_D` por reorganización— es el fenómeno buscado.
4. La unidad científica pasa del estado `xₜ` a la trayectoria `τ = (x₀,…,x_T)`.
5. `VARIEDAD Y CAMBIO` no es un bloque 65: es un eje transversal que indexa los 64.

## Motivo

La formulación anterior trataba la variedad como propiedad de `D`, lo que convierte al organismo
en una máquina congelada que recibe perturbaciones. El objetivo declarado —un ser cibernético
autopoiético, metacognitivo y autoevolutivo— es incompatible con esa lectura.

## Riesgos y límites científicos

Esta decisión **cae exactamente sobre el instrumento que estaba a punto de firmarse**. Verificado
en código, no inferido:

| Compromiso del ADR | Estado en Terrario | Archivo |
|---|---|---|
| `𝒱ₜ` variable | η = `viable_floor × max_energy`, evaluado por fila pero con `max_energy` fijado una vez por episodio | `viability_recovery_metric.py:161`, `world/state.py:33` |
| `dV_R/dt` | `variety_ratio` mide la variedad de **E** (la variable regulada), no la del regulador. `Π` no tiene canal | `viability_recovery_metric.py:178-183` |
| `P(Dₜ₊₁) ≠ P(Dₜ)` | `ChangeScheduler` toma una lista finita y ordenada de `(at_step, rules)`, cada una dispara una vez. No hay distribución sobre `D` | `world/scheduler.py:33-36` |
| variedad endógena y relacional | el marcador de perturbación es `cambio de world_revision`; ninguna de las dos lo produce, así que el detector devuelve `NO_DISTURBANCE_OBSERVED` | `viability_recovery_metric.py:148-153` |
| `τ` como unidad | **ya soportado**: `SCIENTIFIC_TRACE` sella la trayectoria completa por frame | — |
| `W ↔ O` | **parcial**: `destroy_object: true` y `opportunity_lifecycle` dan un lazo mínimo organismo→mundo; no hay construcción de nicho | `scenarios/d4_adaptation_scientific.yaml` |

**El riesgo concreto, y es de lectura, no de código.** `recovery_steps = None` ya tenía dos
causas separadas a propósito (`censored` distingue «nunca se recuperó» de «el episodio terminó
antes»). Este ADR introduce una **tercera**: *se recuperó dentro de una región viable distinta
que el instrumento no puede ver*. Un organismo que se reorganiza y queda estable en `E = 40` con
η fijado en `50` se reporta hoy como `viable_at_end = False, censored = True` — es decir, como el
caso «estaba bien al golpe y luego murió despacio» que el propio instrumento fue construido para
no confundir. **El Caso 3 no sólo no se mide: se informa como fracaso.**

**Ventana temporal.** `viability-recovery-profile` todavía **no** está congelado: existe
`freeze_construct_validation` para la métrica de CL-7 (`planning_trace_metric.py:163`) y no hay
equivalente para ésta. Mientras no haya preregistro que fije su `metric_spec_hash`, ampliar su
`reading_rule` y su `does_not_measure` es gratis. Después, no.

## Lo que este ADR **no** decide

No propone construir canal de `Π`, ni perturbaciones estocásticas, ni `𝒱ₜ` variable. Eso sería
añadir mecanismos, que es lo que PROCESO-DE-TRABAJO-01 §4 prohíbe hasta `scientific_results > 0`.
Reclasifica el mapa y nombra una lectura prohibida; no abre trabajo de construcción.

## Evidencia enlazada

- [docs/CORPUS_A_ALGORITMO_01.md](../../docs/CORPUS_A_ALGORITMO_01.md) — el triaje que este ADR
  reindexa.
- [docs/PROCESO_DE_TRABAJO_01.md](../../docs/PROCESO_DE_TRABAJO_01.md) — §4 moratoria, §7
  contrato de medición `R`.
- `terrario/lab/viability_recovery_metric.py` — el instrumento afectado.

## Reemplaza / es reemplazada por

Reemplaza la formulación estática `E, 𝒱, D, R` usada hasta el 2026-09-16. No reemplaza ninguna
decisión registrada.

## Decisión pendiente para el humano

Firmar `viability-recovery-profile` como detector de Caso 1 y Caso 2 **con la tercera causa de
`None` declarada**, o no firmarlo todavía. Son las dos únicas opciones compatibles con este ADR;
firmarlo sin declararla no lo es.

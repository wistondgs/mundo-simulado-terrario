---
kind: decision
status: PROPOSED
date: 2026-09-16
owner: human
---

# ADR-002 — El objetivo es desarrollo endógeno de capacidad

- **Estado:** PROPOSED
- **Fecha:** 2026-09-16
- **Alcance:** formulación del objetivo de la Teoría de la Inteligencia y, por tanto, qué puede
  contar como evidencia.

## Decisión propuesta

El objetivo deja de formularse como **mejora de desempeño** y pasa a formularse como **desarrollo
endógeno de capacidad en una relación organismo–mundo cambiante**.

> Buscamos un ser cuya experiencia transforme sus propias posibilidades de existencia y acción,
> mientras él y su mundo cambian; no solamente una máquina que aprende a obtener mejores
> resultados.

Cuatro fenómenos quedan explícitamente separados, y **ninguno de los dos primeros se llamará
inteligencia automáticamente**:

1. **Regulación** — mantener `E` con el repertorio ya disponible.
2. **Reorganización endógena** — modificar el propio regulador cuando su organización resulta
   insuficiente.
3. **Desarrollo de capacidad** — adquirir distinciones, representaciones o estrategias antes
   inexistentes.
4. **Mejora del proceso de adquisición** — que la historia transforme *cómo* se adquiere después.

La cadena a demostrar es `historia → reorganización propia → capacidad nueva → ampliación
verificable`, con persistencia y transferencia comprobadas, no deducidas del nombre de los
módulos.

## Motivo

Ni resolver tareas, ni mantener constantes unas variables, ni responder distinto por tener
memoria representan lo que se busca. Recompensas, tasas de éxito y errores predictivos siguen
siendo instrumentos auxiliares y dejan de determinar el veredicto por sí solos.

## Riesgos y límites científicos

**La trampa que el propio ADR nombra.** Si `𝒱` puede moverse (ADR-001), relajar umbrales para
declarar que el organismo sigue funcionando demuestra nada. Todo cambio de necesidades o límites
debe corresponder a una transformación justificada del organismo o del entorno y quedar
registrado. Sin ese registro, `𝒱ₜ` es un grado de libertad del experimentador, no del ser.

**El confundido de origen, verificado en código.** `VARIABLES_ESENCIALES_Y_REORGANIZACION_01`
establece que la variable esencial y la señal de refuerzo son la misma magnitud:

```
variable esencial  = agent.energy              core/types.py:87
señal de refuerzo  = consequence.energy_delta  a1:86 · a3:141 · a4:417
```

Por tanto el gate 1 —¿tiene la viabilidad autoridad causal sobre la reorganización, o depende
exclusivamente de recompensa externa o error predictivo?— **no puede decidirse hoy retirando la
recompensa externa**, porque no hay ninguna que retirar. `do(reward = 0)` es `do(energy_delta =
0)`, que suprime la variable esencial en lugar de aislarla.

Separarlas exige una segunda variable esencial no usada como refuerzo, o un disparador de
plasticidad anclado en la frontera de viabilidad. Ambas son construcción, y la moratoria de
PROCESO-DE-TRABAJO-01 §4 sigue vigente hasta `scientific_results > 0`.

**Tres viabilidades simultáneas.** Muerte del mundo (`energy <= 0`), umbral del organismo
(`0.5` normalizado) y η del observador (≈ `0.23`) responden distinto a la misma trayectoria.
Antes de afirmar nada sobre `𝒱ₜ` hay que decidir cuál de las tres es `𝒱`.

## Alcance sobre las implementaciones

La Teoría de la Inteligencia **no** queda limitada a lo que hoy implementen RNFE, Genesis o
Terrario. Esas implementaciones se contrastan con el objetivo y no lo redefinen por sus
limitaciones. En particular, el estado actual —`E` escalar, reorganización dirigida por
recompensa, cero mecanismos de desarrollo de capacidad— **no es un argumento para rebajar el
objetivo**, sino la distancia que este ADR hace medible.

## Evidencia enlazada

- [docs/VARIABLES_ESENCIALES_Y_REORGANIZACION_01.md](../../docs/VARIABLES_ESENCIALES_Y_REORGANIZACION_01.md)
  — las tres respuestas de código a la prioridad experimental vigente.
- [[ADR-001 Variedad dinamica]] — `Eₜ, 𝒱ₜ, Dₜ, Rₜ`, que este ADR presupone.
- [docs/PROCESO_DE_TRABAJO_01.md](../../docs/PROCESO_DE_TRABAJO_01.md) — §4 moratoria.

## Reemplaza / es reemplazada por

Reemplaza la formulación del objetivo como mejora de desempeño. Complementa ADR-001, que
no queda reemplazado: uno fija que las variedades cambian, éste fija qué se busca en ese cambio.

## Decisión pendiente para el humano

Aceptar o rechazar. Si se acepta, la consecuencia inmediata no es construir: es **elegir cuál de
las tres fronteras de viabilidad es `𝒱`**, porque ninguna afirmación sobre reorganización es
interpretable mientras haya tres.

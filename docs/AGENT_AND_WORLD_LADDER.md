# AGENT-AND-WORLD-LADDER-01

**Qué es:** la descripción de los dos ejes del experimento —qué distingue a cada agente y qué
exige cada mundo— reunidos en un solo sitio.

**Por qué existe:** `A0…A4` y `d0…d4` aparecen mencionados en siete documentos y no están
explicados en ninguno. Son la variable independiente y la demanda ambiental del proyecto entero.
Este documento no introduce nada nuevo: transcribe lo que ya declaran
`terrario/agent/agents/*.py` y `scenarios/*.yaml`, y lo ordena como la progresión que son.

**Estatus:** descriptivo. No es un preregistro, no autoriza ninguna ejecución y no afirma que
ninguna celda de la matriz haya sido medida científicamente.

## 1. El eje de los agentes — ablación anidada estricta

Cada nivel añade **exactamente un** componente cognitivo y conserva todo lo anterior. Ésa es la
propiedad que convierte la escalera en un instrumento de disección: la diferencia entre dos
niveles contiguos es un solo mecanismo.

| | Agente | Añade | No tiene |
|---|---|---|---|
| **A0** | `A0_RANDOM` | nada — acción uniforme al azar | aprendizaje, estado, memoria |
| **A1** | `A1_REACTIVE` | percepción + política (`REINFORCE`) · π(obs)→acción | estado temporal, memoria, modelo del mundo |
| **A2** | `A2_GRU_BASELINE` | **estado temporal** (GRUCore) | modelo del mundo, memoria |
| **A3** | `A3_WORLD_MODEL` | **modelo del mundo** (predice consecuencia) | memoria episódica y de largo plazo |
| **A4** | `A4_ADVANCED` | **memoria episódica + memoria de largo plazo + estimador de incertidumbre + planificador + homeostasis** (núcleo SSM) | — |

A4 es el único nivel que agrupa varios componentes a la vez. Por eso las ablaciones *dentro* de A4
(como `use_planner` en CL-7) son un segundo eje de disección, más fino que la escalera misma.

**Advertencia de pureza** — la registra el propio `docs/SCIENTIFIC_REVIEW.md`: al pasar de un
nivel al siguiente no solo cambia el mecanismo, también cambian **capacidad y cómputo**. Una
diferencia A2→A3 no es atribuible al modelo del mundo hasta que capacidad, cómputo, dinámica
temporal y distribución de representaciones estén igualadas. La escalera propone la comparación;
no la justifica sola.

## 2. El eje de los mundos — demanda ambiental creciente

| | Escenario | Qué exige | Estructura |
|---|---|---|---|
| **D0** | `d0_differences` | **discriminar** | objetos con firmas de canal distintas; reglas fijas |
| **D1** | `d1_objects` | **permanencia del objeto** | los objetos se mueven cada 20 pasos |
| **D2** | `d2_properties` | **propiedad funcional** | movible vs inamovible, señalado por canal |
| **D3** | `d3_causality` | **causa frente a correlación** | ch0 correlaciona con la recompensa; solo ch1 es causal |
| **D4** | `d4_change` | **adaptación a cambio causal** | las reglas se invierten en el paso 750 |
| D4′ | `d4_adaptation_scientific` | lo anterior, por fases | `ACQUISITION → CAUSAL_CHANGE → RECOVERY` |
| D4″ | `d4_adaptation_transfer` | transferencia | fase `TRANSFER`, 200 pasos |
| D4‴ | `d4_change_fast` | cableado de CI | inversión en el paso 10, 30 pasos |

### D3 merece una nota aparte

Es el escalón mejor construido de la escalera, y es una trampa deliberada:

```
ch0 alto  +  ch1 alto   →  energía  +8.0
ch0 alto  +  ch1 BAJO   →  energía  −4.0
```

Un agente que aprenda «ch0 predice recompensa» —la inferencia estadísticamente obvia— **es
castigado**. Solo tiene éxito el que aísla ch1. D3 no mide rendimiento: mide si el agente
construyó una representación causal o meramente correlacional. Es la pregunta del proyecto
reducida a un escenario de 10×10.

## 3. La matriz A×D

5 agentes × 8 escenarios = 40 celdas. El barrido diagnóstico del 2026-09-16 las ejecutó todas:
**40/40 arrancan y terminan** (40 pasos por celda, CPU, 2–5 s cada una). Eso establece
ejecutabilidad, **no** resultado científico: una celda puede correr y no medir nada interpretable.

Lo que la matriz permite preguntar, celda a celda: *¿en qué escalón de exigencia ambiental
empieza a ser necesario cada componente cognitivo?* Ésa es la forma experimental de la pregunta
«cómo se construye la cognición».

Lo que la matriz **no** puede responder por sí sola:

- no distingue *necesario* de *suficiente* sin las intervenciones I01–I12, hoy no implementadas
  (solo existen `C00` control, `C01_SHAM` y `TEST_ENERGY_DELTA`);
- no controla capacidad ni cómputo entre niveles (ver la advertencia de pureza);
- el fork causal exacto solo está soportado en `A0×D0`.

## 4. Cómo correr una celda

```bash
./.venv/bin/python scripts/phase1_sweep.py --sandbox .sandbox/mi-barrido --groups matrix
```

Para una sola celda, escriba una config con un agente y un escenario y use la CLI clásica. La
config de fábrica `configs/default.yaml` pide `device: cuda` y falla cerrado en esta máquina
(`AgentFactoryError: Requested device 'cuda' is unavailable`); use `device: cpu`.

Nada de esto produce evidencia: la ruta científica exige preregistro bloqueado y autorización
humana. Ver `docs/TUTORIAL_CADENA_CIENTIFICA.md`.

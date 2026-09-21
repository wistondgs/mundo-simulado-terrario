# `LEVEL1.6` · auditoría de integridad y lista de anomalías

**Fecha:** 2026-09-20 · **Auditor:** segundo pase, adversarial sobre trabajo propio
**Árbol:** `/home/wis/level16-sensory-change-01` · rama
`experiment/level16-developmental-sensory-change-01` · HEAD `0503874` · limpio

Cada afirmación va etiquetada:
**[C]** hecho de código verificable leyendo el árbol ·
**[M]** medido en esta auditoría ·
**[I]** inferencia mía, con su razonamiento a la vista.

---

## 1 · Genealogía

**[C]** Orden real de commits, con marca temporal:

```
9b0d39b 18:01:36  oráculo sellado
d0ce9f8 18:05:19  Enmienda 01 · consumo de semillas
8f8c85d 18:17:46  Enmienda 02 · parámetros del mundo
02b6e62 18:19:43  S0 + predicado + consumo            ← primer código
42f7b1a 18:20:29  A1
ad99b74 18:20:55  vida / freeze / banco POST
c8f66f1 18:22:07  los cuatro brazos
9909fc2 18:22:53  K-SOMBRA + intervención causal
23903fb 18:24:07  los doce gates + fixtures negativas
5c54848 18:24:29  Enmienda 03 · clasificación
9625aaa 18:25:39  campaña                              ← primera vez que se puede correr
0503874 18:26:39  informe
```

**[C]** Las tres enmiendas preceden a `9625aaa`, que es el primer commit capaz de
producir un resultado confirmatorio. **Ninguna se emitió después de ver números.**

**[C]** El oráculo es literalmente el mismo blob:

```
blob en 9b0d39b  59faa96d88b887eda836d0a47b7f5ff29d6e5c6a
blob en HEAD     59faa96d88b887eda836d0a47b7f5ff29d6e5c6a
git diff 9b0d39b HEAD -- docs/LEVEL16_ORACULO_PREREGISTRADO.md   →  vacío
```

## 2 · Aislamiento del linaje

**[C]** `level11`, `level12`, `level13`, `level14`, `organism`, `remembered`,
`level15`: **ninguno existe** en este árbol.

**[C]** Todo lo que `terrario/level16/` importa de fuera de sí mismo:

```
terrario.level1.world        · la física del Nivel 1.0, sin modificar
__future__ ast dataclasses enum hashlib numpy pathlib typing
```

Un solo módulo del proyecto. La independencia respecto de B, Q, H, M y ψ no es
una declaración: no hay nada que importar.

## 3 · Reproducibilidad

**[M]** Segunda corrida completa de la campaña, independiente de la primera:

```
corrida 1  fde8f10e2a3beda4
corrida 2  fde8f10e2a3beda4      idénticas bit a bit
IC95 inferior +0.6805 · veredicto POSITIVO · gates 12/12
```

**[M]** Semillas consumidas `140000011…140000026`, 16 vidas, **0 descartes
`N-MUNDO`**, 16 semillas sin consumir. Coincide con lo que la Enmienda 02
predijo antes de correr.

## 4 · Corroboración analítica del resultado primario

**[M]** Verificación que no vuelve a correr al organismo: la ganancia sobre
`TEMPORAL-SHUFFLED` debería aproximar la información mutua `I(o_t; o_{t+1})` del
mundo, calculable de la topología.

```
                 analítica   medida    sesgo      r
ΔL vs SHUFFLED     0.8536    0.8308   -0.0228   0.9935
ΔL vs FROZEN       1.6301    1.5947   -0.0354   0.9964
```

**[I]** El sesgo negativo constante es lo que se espera de un contador con prior
frente a la conditional verdadera: el estimador finito pierde un poco. Que la
correlación por vida sea 0.99 y el sesgo vaya siempre en el mismo sentido es
evidencia independiente de que el resultado mide la estructura del mundo y no un
artefacto del procedimiento.

## 5 · Gates y fixtures

**[C]** 12 gates implementados. **[C]** 12 fixtures negativas, cada una
falsificando por la vía real del verificador —ninguna levanta la excepción a mano:

| gate | qué hace fallar la fixture |
|---|---|
| L16-0 | un directorio `level13` junto al paquete |
| L16-1 | vida con `motor_emitted = 0` frente a pasos vividos |
| L16-1 | un segundo módulo que también llama `.integers` |
| L16-2 | `state()` que omite el estado del generador → `MotorContractError` |
| L16-3 | cinco fuentes fabricadas, una por forma de señal |
| L16-3 | **tres fuentes inocentes que deben PASAR** (prosa, `dict.values()`) |
| L16-4 | `temporal.py` fabricado que nombra `direction` |
| L16-5 | `life.py` fabricado que importa `TemporalModel` |
| L16-6 | `teachability` forzada a 0 |
| L16-7 | pérdidas sintéticas donde una vida no mejora |
| L16-8 | pérdidas sintéticas cuyo intervalo toca el cero |
| L16-9 | intervención sobre un modelo sin estado aprendido |
| L16-10 | `log_loss` instrumentada para actualizar el modelo |
| L16-11 | `probability` inyectada en el control |

**[C]** Las tres fixtures de L16-3 que deben **pasar** son lo que distingue este
gate de un detector de falsos positivos: prosa que menciona `reward`, `novelty` y
`value`, y `dict.values()`, no lo disparan.

**[M]** 84 contratos en verde en esta auditoría, con el árbol tal como está.

## 6 · Listas negras · sin excepciones silenciosas

**[C]**

```
UNAMBIGUOUS_SIGNALS   16 nombres, prohibidos como identificador Y como atributo
GENERIC_SIGNALS        4 nombres, prohibidos sólo como identificador propio
FORBIDDEN_IN_LEARNER  16 nombres, ninguno presente en temporal.py
```

**[C]** La única excepción es la partición documentada, cuya razón es que
`dict.values()` es Python y no una señal de valor. **No hay carve-outs añadidos.**

**[C]** Los tres renombres forzados (`value`→`candidate`, `target`→`destino`,
`advantage`→`temporal_gain`) siguen en pie. Las apariciones que quedan de esas
palabras están en `gates.py`, **todas como cadenas dentro de la lista negra o en
docstrings** —es decir, nodos `Constant`, que el escáner no mira. El guardián
sobrevive a su propio escaneo porque nombra lo prohibido como dato, no como
identificador.

## 7 · Frontera del aprendiz

**[C]** `A1.observe` acepta dos tuplas de cuatro bits y nada más. **[M]** Rechaza
en ejecución: `Direction`, un int, una posición `(3,3)`, tres bits, un no-bit, una
lista. **[C]** `temporal.py` no nombra `direction`, `action`, `efference`,
`moved`, `position`, `grid`, `cells` ni `changed`.

**[C]** `life.py` no importa `temporal`: el cuerpo no puede leer la tabla, y por
eso la paridad de trayectoria entre brazos es estructural y no impuesta.

## 8 · Resultado, reverificado

**[M]**

```
16/16 POSITIVO · 16/16 causal · 4096 updates por vida
ΔL vs FROZEN     +1.5947  sd 0.2639  mín +1.3533
ΔL vs SHUFFLED   +0.8308  sd 0.3067  mín +0.1290   IC95 inf +0.6805
brecha con el óptimo analítico  media 0.0288  máx 0.0450 nats
fracción capturada              media 0.9813  mín 0.9701
BS_change  FULL 0.2121 · BITCOUNT 0.2191 · el control gana 3/16
```

---

# Anomalías

**Ninguna ha sido corregida.** Se reportan, como pediste, antes de tocar nada.

## AN-1 · `SHUFFLE_NOT_DESTRUCTIVE` no tiene gate · **severidad alta**

**[C]** El oráculo §17 lo declara condición de parada. `audit_shuffle` calcula la
destrucción y `LifeOutcome.shuffle_destructive` la guarda por vida. **Ningún gate
lee ese campo.** El contraste crítico del nivel depende de que el barajado
destruya de verdad, y esa comprobación queda como dato del informe, no como
puerta.

**[M]** Se cumple en 16/16 vidas, de modo que **el resultado no está en
cuestión** —pero el procedimiento tiene un agujero: una baraja defectuosa en una
campaña futura pasaría los doce gates.

## AN-2 · `FROZEN_MODEL_CHANGED` no tiene gate · **severidad media**

**[C]** Lo impide el contrato de clase —`TemporalModel.freeze()` hace que
`observe` levante— y hay test unitario. **[C]** Pero ningún gate lo comprueba
sobre la campaña.

## AN-3 · L16-7 nombra dos contrastes que son uno · **severidad baja**

**[M]** Con `α₀ = 1` y cero actualizaciones, `PRE` y `FROZEN` son el mismo objeto:

```
huella PRE     ec9d9827912e6fc384605ff0
huella FROZEN  ec9d9827912e6fc384605ff0      idénticas
```

**[C]** El gate calcula sólo `frozen`. La etiqueta —y la frase del informe, «que
su estado inicial, que un organismo congelado»— enumera dos comparadores donde hay
uno. No es falso; es redundante y sugiere más controles de los que hay.

## AN-4 · El oráculo promete «una fixture por gate» y lista 11 para 12 · **baja**

**[C]** §13 enumera once fixtures. `L16-11` (BITCOUNT) no tiene fixture declarada.
**[C]** El código sí la implementa. El documento promete menos de lo que hay.

## AN-5 · Tres fixtures declaradas no son las implementadas · **media**

**[C]** §13 declara «cambiar una acción de un brazo» para L16-5. **[I]** Esa
fixture es **irrealizable en el diseño final**: los brazos no producen acciones —
la trayectoria la produce el cuerpo una sola vez y los brazos la comparten por
construcción. Se implementó la vía equivalente: hacer que el cuerpo pudiera leer
la tabla. Igual ocurre con «mundo estático» (L16-6) y «congelar FULL» (L16-7).

## AN-6 · §11 selló valores medidos sobre una población filtrada · **alta**

**[M]** Contrafactual exacto sobre esta campaña:

```
criterio estructural (16 vidas)   IC95 inferior  +0.6805
exclusión «≤6»       (13 vidas)   IC95 inferior  +0.8653
sellado en §11                                   +0.8858
```

**[I]** El valor sellado reproduce la exclusión, no el criterio estructural. Los
números del preregistro se midieron sobre una muestra ya filtrada sin declararlo.
La campaña definitiva es más adversarial y pasa igual, pero la lección
metodológica queda: **un valor preregistrado debe declarar sobre qué población se
midió.**

## AN-7 · La segunda cláusula de `N-MUNDO` está implicada por la primera · **baja**

**[M]** 0 casos en 30 000 mundos. **[I]** Demostración: en un componente conexo,
`|O| ≥ 2` obliga a que algún par adyacente difiera, y cruzarlo ya es una
transición que cambia. No admite fixture negativa propia. Ya documentado en el
código.

## AN-8 · Los valores de `BS_change` de §7 no se reproducen en magnitud · **baja**

```
sellado §7   tabla 0.222368 · bitcount 0.226245 · Δ -0.003877 · β 0.8363
campaña      tabla 0.212128 · bitcount 0.219067 · Δ -0.006938 · β 0.8798
```

**[I]** Mismo signo y misma conclusión —el control de un parámetro queda a
milésimas—, magnitudes distintas. Los sellados eran poblacionales; los de campaña
son la media de 16 vidas. No invalida nada, pero no es una reproducción.

## AN-9 · «182 de 256 transiciones» es un descriptor dependiente de la muestra · **muy baja**

**[M]** Medido 182–184 según la muestra de mundos. §4 lo presenta como valor fijo.

## AN-10 · `LATER_CAPABILITIES` omite `level15` · **cosmética**

**[C]** La lista del gate L16-0 tiene seis entradas y no incluye `level15`.
**[M]** Verificado a mano: `terrario/level15` tampoco existe. 1.5 está congelado y
nunca tuvo paquete, así que la omisión no deja pasar nada, pero la lista no es
exhaustiva respecto del linaje.

---

## Veredicto de la auditoría

**[I]** El resultado confirmatorio es **sólido y reproducible**, y ninguna anomalía
lo pone en duda: `AN-1` y `AN-2` son agujeros de procedimiento cuya condición se
cumple de hecho en las 16 vidas; `AN-3`, `AN-4`, `AN-5`, `AN-7`, `AN-9` y `AN-10`
son divergencias entre lo que el oráculo dice y lo que el código hace, todas en la
dirección de que el código hace **más** o **lo mismo por otra vía**; `AN-6` y
`AN-8` son defectos de calibración del preregistro que la campaña definitiva
supera en vez de esconder.

**[I]** El único que exigiría trabajo antes de una campaña futura es `AN-1`.

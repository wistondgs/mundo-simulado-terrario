# Mundos diagnósticos · replanteamiento

**2026-09-17 · Fase 1 de TCS-01**

## El problema con «un mundo por capacidad»

El plan original de la Fase 1 dice: cada capacidad recibe su propio mundo diagnóstico. Siete
mundos bespoke, siete controles, siete endpoints.

Eso tiene tres defectos que se ven en cuanto se intenta construir el primero:

1. **Los controles no son controles.** Si el mundo exigente de memoria y su control son dos
   escenarios escritos aparte, difieren en más de una cosa aunque nadie lo quiera. «Difiere en
   exactamente una dimensión» no se puede garantizar con dos YAML distintos; sólo con **un
   generador y un parámetro**.

2. **La composición se vuelve un tercer conjunto de mundos.** Fase 3 pregunta qué pasa cuando dos
   capacidades se juntan. Con mundos bespoke, «memoria + plasticidad» necesita un octavo mundo que
   nadie diseñó. Con un generador, es encender dos ejes.

3. **Casi ninguno es construible.** El motor de reglas sólo condiciona sobre `(canal del objeto,
   acción)`. Sin posición, sin tiempo, sin historia, sin estado del agente. Un mundo que «exija
   memoria» no puede escribirse con reglas que no recuerdan nada — **salvo que el mundo tenga
   información que el agente no ve**.

## La primitiva que lo hace posible

`get_observation` entrega `obs[1..3] = canales 0..2 del objeto`. El **canal 3 se trunca**:
`n_obj_ch = min(4, num_channels − 1) = 3`. Pero `RuleEngine` sí lo lee: una regla con
`object_channel: {index: 3, min: 0.8}` dispara.

Verificado:

```
objeto con canales [0.5, 0.5, 0.5, 0.9]
el agente ve:      [1.0, 0.5, 0.5, 0.5]     ← occupancy + canales 0..2; el 0.9 no aparece
regla sobre índice 3 ≥ 0.8 → dispara, delta +7.0
```

**El canal 3 es una variable oculta.** Es lo que permite que el mundo tenga una verdad que el
agente debe **recordar, integrar o inferir** en vez de leer. Sin eso, todo mundo «de elección»
degenera en «lee el canal de la puerta» — que es D4T otra vez, markoviano.

## El sustrato: `CUE → DEMORA → ELECCIÓN`

Un solo generador. Todos los mundos diagnósticos son parametrizaciones suyas.

```
t = 0        el agente ve un CUE: un objeto cuyos canales visibles (0..2) llevan una señal
t = 1..k     el agente se desplaza; el cue sale de la ventana 5×5   ← la demora es espacial
t = k        el agente llega a dos ELECCIONES perceptivamente idénticas en canales 0..2,
             que difieren SOLO en el canal 3 oculto
             la señal del cue dice cuál tiene el canal 3 bueno

reglas:      CONSUME sobre canal_3 ≥ 0.8  → +E
             CONSUME sobre canal_3 ≤ 0.2  → −E
```

Para elegir bien hay que **haber visto el cue y conservarlo hasta la elección**. Un organismo sin
memoria elige al azar: 0.5.

### Los ejes

| Eje | Parámetro | Qué capacidad exige al encenderlo | Control = eje apagado |
|---|---|---|---|
| **demora** | `k` = distancia cue→elección | **EPMEM** — con `k > 2` el cue sale de la ventana | `k = 0`: cue y elección visibles a la vez, no hace falta recordar |
| **distractores** | `d` = cues falsos entre medio | **LTMEM** — retener a través de interferencia | `d = 0` |
| **secuencia** | `s` = número de cues cuyo **orden** decide | **TEMP** — `s ≥ 2`: A→B elige izquierda, B→A derecha | `s = 1`: un solo cue, basta recuperar |
| **riesgo** | `r` = varianza oculta en una elección | **HOMEO** — una elección da +5 o −3 según canal 3, la otra +1 seguro; con energía baja la varianza mata | `r = 0`: ambas deterministas |
| **mapeo** | `m` = ¿cue→elección conocido? | **LEARN** — `m = desconocido`: hay que aprenderlo por experiencia | `m = fijo`: el oráculo lo sabe |
| **novedad** | `n` = fracción de cues con canales nunca vistos | **UNC** — familiares / ambiguos (canal entre umbrales, ninguna regla dispara) / novedosos | `n = 0` |
| **inversión** | `f` = paso en que el mapeo se invierte | **PLAST** — `changes: [{at_step: f, rules: …}]` | `f = ∞` |

Cada capacidad = **un eje encendido, los demás en base**. Su control = **ese eje apagado**.
Difieren en exactamente una dimensión **por construcción**, no por cuidado.

### Lo que el generador usa del motor, y nada más

- `procedural_layout` con plantillas de clase → cue, elecciones, distractores
- **canal 3** como verdad oculta
- `changes` para la inversión
- `opportunity_lifecycle` para regenerar episodios cue→elección dentro de una vida
- `num_channels = 4` — que es lo que oculta el canal 3. Con 5 se vería, y todo el diseño se
  vendría abajo. **Ese parámetro pasa a ser parte del contrato del mundo.**

### Lo que NO puede hacer, dicho ahora

- **Posición absoluta.** El agente no la ve. «Elección de la izquierda» tiene que ser relativa a
  su trayectoria de aproximación. El layout debe ser simétrico respecto al camino.
- **Condicionar sobre la energía del agente.** Las reglas no la ven. Pero el eje `riesgo` no lo
  necesita: el mundo no condiciona sobre energía, **el agente** debe hacerlo. Ésa es exactamente
  la demanda homeostática.
- **INSPECT no hace nada.** Un diseño que espere que «inspeccionar el cue» revele algo está
  usando una acción vacía. El cue se ve al estar en ventana, y punto.

## Lo que el replanteamiento revela sobre el orden

Cinco de los siete ejes necesitan que el organismo **aprenda** el mapeo cue→elección. Un agente
neuronal no «sabe» mapeos: los adquiere. Así que:

```
EPMEM, LTMEM, TEMP, PLAST   dependen de LEARN
LEARN                        medido: no se separa del azar con 1536 ejemplos puros
HOMEO, UNC                   NO dependen de LEARN — la modulación por energía está
                             cableada, y la varianza del ensemble existe desde el inicio
```

**LEARN-A1 está en el camino crítico de cuatro certificaciones, y es la capacidad con peor
evidencia medida.** Si no se certifica, la familia entera de memoria queda bloqueada — no porque
la memoria no funcione, sino porque no habría forma de saberlo.

Eso da el orden de la escalera sin discutirlo:

```
Nivel 1   HOMEO, UNC        certificables ahora, sin depender del learner
Nivel 2   LEARN             reparar o sustituir; sin esto nada más avanza
Nivel 3   EPMEM, LTMEM, TEMP, PLAST   una vez que el organismo pueda aprender un mapeo
```

Y la Fase 3 —composición— deja de necesitar mundos nuevos: **es encender dos ejes a la vez** en el
mismo generador, con los mismos controles.

## Lo que queda por decidir

1. **¿Se acepta el canal 3 como variable oculta de diseño?** Es un efecto colateral de
   `num_channels = 4` sobre objetos de 4 canales, no una decisión de diseño. Usarlo lo convierte en
   contrato. La alternativa es añadir al motor un campo `hidden_channels` explícito, que es más
   honesto y más caro.

2. **¿Qué se hace con LEARN?** El replanteamiento lo pone en el camino crítico. Reparar
   `OnlineLearner` toca A4, que está congelado. Sustituirlo por un learner mínimo de referencia
   —regresión sobre el canal visible, sin backbone compartido— daría un ORACLE de aprendizaje y
   diría si el problema es el mecanismo o el organismo.

3. **¿Un generador de escenarios, o siete YAML derivados de una plantilla?** El generador es lo
   correcto; siete YAML son lo que existe hoy. La diferencia es si `procedural_layout` crece para
   soportar cue/elección/distractor como clases con roles, o si se escriben a mano.

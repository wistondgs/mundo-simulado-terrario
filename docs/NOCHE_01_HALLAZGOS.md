# NOCHE-01 · el azar come más que la arquitectura cognitiva

**Fecha:** 2026-09-17, 02:00–04:00.
**Clasificación:** `ENGINEERING_SANDBOX_NOT_EVIDENCE`. Nada de esto es evidencia científica: sin
preregistro, sin métrica promovida, y el firewall lo rechazaría. Sirve para decidir qué merece un
experimento preregistrado.
**Encargo:** correr todo lo posible, arreglar lo roto, traer una pista de un perfil viable.

---

## El resultado

D4T, 1200 pasos, mismas semillas, mismo mundo:

| agente | pasos | vivo | comió | aciertos | variedad conductual |
|---|---:|---|---:|---:|---:|
| **A0 aleatorio** | 1034 | no | **10** | 0,600 | **2,319** |
| **A0 aleatorio** | 967 | no | **16** | 0,438 | **2,321** |
| A1 reactivo | 967 | no | 6 | 0,333 | 1,611 |
| A1 reactivo | 1000 | no | 14 | 0,500 | 2,016 |
| A4 completo | 1000 | no | 7 | 0,571 | 1,851 |
| A4 completo | 1000 | no | 6 | 0,500 | 1,701 |

**El agente uniformemente aleatorio come más que la arquitectura cognitiva completa.** A0 no
tiene aprendizaje, memoria, modelo del mundo, planificador ni homeostasis. A4 tiene 1,35 millones
de parámetros y los ocho módulos, y come la mitad.

Ninguno sobrevive. Todos mueren alrededor del paso 1000, que es exactamente `60 ÷ 0,06`: **la
línea base de no hacer nada.**

---

## El techo del mundo: sí es habitable

Controles escritos a mano, con acceso a la verdad que la política no tiene:

| política | pasos | vivo | comidas | aciertos |
|---|---:|---|---:|---:|
| quieto (piedra) | 1001 | no | 0 | — |
| paseo + come todo | 1135 | no | 32 | 0,62 |
| **paseo + come sólo lo bueno** | **1200** | **sí** | **15** | **0,93** |

**Un paseo aleatorio que discrimina sobrevive el episodio entero.** No hace falta navegar, ni
planificar, ni recordar: bastan **quince comidas acertadas** en 1200 pasos.

La habilidad que falta es **discriminar**, no navegar. Y es una habilidad barata.

---

## Por qué no la adquiere

```
1200 pasos · organismo completo
pasos con señal informativa      7      0,70 %
energía ganada por comer      +1,0
energía necesaria para vivir   +60
```

**Siete muestras útiles por vida.** Ningún algoritmo aprende una discriminación con eso. Y el
bucle se cierra sobre sí mismo:

```
la política colapsa sobre una acción
   → cae la variedad conductual (2,32 del azar → 1,7 de A4)
      → encuentra menos objetos
         → ~7 muestras informativas
            → no aprende a discriminar
               → come al azar, neto cero
                  → muere en la línea base
```

**Lo aprendido destruye la exploración que lo alimentaba, sin adquirir a cambio la
discriminación.** A eso se le llamaría ablación si lo hubiéramos hecho a propósito.

### La causa mecánica

```python
# core/types.py:139 -- 25 acciones = tipo × dirección, y nada más
def from_int(value):
    at = ActionType(value // NUM_DIRECTIONS)
    d  = Direction(value % NUM_DIRECTIONS)
    return Action(action_type=at, direction=d)      # target_id nunca se fija → −1

# sandbox_runtime.py:210 -- comer exige acertar 1 de 5 direcciones
pos = agent.pos + DIRECTION_DELTA[action.direction]
```

Medido sobre 400 pasos: comida adyacente el **55,5 %** del tiempo, eligió `CONSUME` el **43,2 %**,
y de las **70** veces que lo intentó con algo al lado acertó **8**. En una corrida apuntó `UP`
**215 de 236 veces**.

Y la rama que lo resolvería está escrita y es inalcanzable: `_find_target` acepta
`target_id >= 0` y consume cualquier objeto adyacente validando la adyacencia. La codificación de
acciones no tiene sitio para expresarlo.

---

## Lo que queda descartado

**No es motivación.** A4 ya tenía dos señales no-recompensa cableadas a la acción: presión
homeostática sobre la temperatura, y `logits + 0.1 * uncertainties`, comentado como *curiosity*.
Existían desde antes y nunca se habían probado.

**No es el colapso por sí solo.** Añadí el término de entropía que faltaba —`policy_loss` era
`-log_prob × advantage`, sin regularización— con bandera y coeficiente declarado, y lo barrí:

| coef | pasos | comió | aciertos | indecisión |
|---:|---:|---:|---:|---:|
| 0,0 | 995 | 6,7 | 0,49 | 0,087 |
| 0,003 | 1034 | 5,7 | **0,70** | 0,213 |
| 0,01 | 1006 | 7,3 | 0,53 | 0,350 |
| 0,03 | 967 | 4,3 | 0,28 | 0,288 |
| 0,1 | 1039 | 8,0 | 0,66 | 0,289 |

**Las quince mueren.** El acierto mejora y el número de comidas no. Arregla lo que apunta a
arreglar y no cambia el desenlace.

**No es escasez.** D4T · D4T16 · D4T08 · D4T04 (32, 16, 8 y 4 objetos, idénticos en todo lo
demás): balance −35,9 a −36,9 sobre 600 pasos, que son los 36,0 del decaimiento. Comer cuatro
veces o cero no cambia nada.

---

## Tres defectos, y uno era mío

**La semilla del agente no determinaba el agente.** `create_agent` siembra un `torch.Generator`
usado sólo para muestrear; los pesos los inicializa `nn.Module` con el RNG **global**, que avanza
en cada construcción. Tres agentes con semilla `1000045` dieron tres hashes distintos. **Cada
condición corría con un organismo diferente según su posición en el bucle.** Arreglado en el
arnés y verificado; **no** en la fábrica, porque eso movería la caracterización golden y el
manifiesto protegido, que son compuertas humanas.

**El `policy_loss` sin término de entropía.** Añadido con bandera, apagado por defecto.

**Y mi propia sonda del techo estaba rota.** El paseo elegía siempre la primera dirección libre
en orden fijo, así que el agente oscilaba entre dos casillas y nunca exploraba: un «comedor
perfecto» que no comía. Lo detecté porque contradecía el 55,5 % de adyacencia ya medido. La
primera versión habría titulado *«ni un comedor perfecto sobrevive»*, que es exactamente lo
contrario de lo que pasa.

---

## Lo que esto dice del perfil

La pregunta era qué configuración de conceptos da un ser viable. Esta noche dice tres cosas:

1. **Ninguna, todavía** — pero no porque falten conceptos, sino porque el evento que enseña
   ocurre el 0,7 % del tiempo.
2. **El listón es bajo**: quince comidas acertadas bastan, y un paseo aleatorio que discrimine las
   consigue. El ser que buscamos no necesita ser brillante para empezar a existir.
3. **El stack cognitivo actual va en contra**: reduce la variedad conductual por debajo del azar
   y no compra discriminación con lo que gasta.

Un perfil no se puede seleccionar mientras todas sus variantes rinden por debajo del control
aleatorio. **Primero el mundo tiene que poder enseñar, y la acción tiene que poder apuntar.**

---

## Lo que rompería el bucle, de menos a más intrusivo

1. **Hacer alcanzable `target_id`** — el mecanismo existe y está validado; falta que la acción
   pueda expresarlo. Es lo más barato y lo que menos inventa.
2. **Bajar el coste por paso** para alargar la vida y acumular más muestras.
3. **Recompensa más densa** — la peor, porque acerca el diseño a moldear la conducta que
   queremos descubrir.

Las tres cambian el contrato del mundo. **Ninguna es mía.**

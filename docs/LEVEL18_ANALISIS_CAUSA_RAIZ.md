# Nivel 1.8 · Análisis de causa raíz e hipótesis

Análisis técnico de por qué `LEARNER-18-v1` no pudo desarrollarse. No cambia
ningún veredicto ni toca el learner.

---

## 1 · Hipótesis

> **El estado del learner es una función de la secuencia de acciones. Las
> observaciones nunca entran en él.** El oráculo selló
> `Z_{t+1} = F(Z_t, A_t, O_{t+1})`; lo implementado es el caso degenerado
> `Z_{t+1} = F(Z_t, A_t)`. Todo lo demás —bimodalidad, churn, 1 % de información
> situacional, lavado con el presupuesto, incomensurabilidad crear/destruir— son
> consecuencias de haber elegido la familia de particiones equivocada.

### Evidencia de código

```
predictive_state.py:168   self._came_from = (self._here, command)      ← sin observación
predictive_state.py:336   for following in range(16):
                              self._routing[(sig[0], sig[1], following)] = born
                          ← las 16 rutas del hijo, idénticas para toda observación
```

La observación está en la clave de la ruta y nunca discrimina.

### Evidencia empírica · prueba hermética

Learner entrenado con estructura (4 estados recorridos). Mismas 400 acciones,
tres secuencias de observaciones distintas: **secuencias de `Z` idénticas, 0/400
diferencias.** Mismas observaciones, acciones distintas: 297/400 diferencias.

### Evidencia cuantitativa · cuánta información se deja fuera

Situación verdadera `C` como instrumento, 60.000 pasos, 5 mundos, `H(C)` = 2,98 nats:

| k | H(C \| últimas k acciones) | ctx | H(C \| últimos k pares (obs, acción)) | ctx |
|---:|---:|---:|---:|---:|
| 1 | 2,6393 | 4 | **0,6633** | 46 |
| 2 | 2,4008 | 16 | **0,2734** | 258 |
| 4 | 2,0322 | 256 | 0,0742 | 4.803 |
| 6 | 1,5435 | 4.096 | 0,0140 | 41.943 |

**Dos pares (obs, acción) con 258 contextos resuelven el 91 % de la situación.
Seis acciones solas con 4.096 contextos resuelven el 48 %.** La familia de
particiones del learner necesita dieciséis veces más estados para saber menos, y
cada uno de esos estados está hambriento de evidencia. (El estimador sesga a la
baja con más contextos; el hueco es demasiado grande para ser sesgo: `OA_2` tiene
menos contextos que `A_6` y aun así lo bate por 1,27 nats.)

---

## 2 · Por qué la hipótesis explica cada síntoma medido

| síntoma | medido | explicación |
|---|---|---|
| FD1 captura casi todo lo que captura el learner | margen +0,01–0,03 | FD1 **es** historia de acciones de profundidad 1; el learner es la misma familia, más honda |
| el learner casi no sabe dónde está | `I(C;Z\|O)` 1,0–1,6 % | la historia de acciones lleva un 11 % de la información situacional a k=1 |
| el oráculo está lejísimos | +0,53 vs +0,09 | la situación vive en la historia (obs, acción), que `Z` no ve |
| sobrefragmentación | 61→90 estados sin merge | los sufijos de acciones crecen 4^k y no colapsan por equivalencia de lugar |
| la ventaja se lava con datos | ΔL +0,107 → +0,058 | `C17` continuo ya condiciona en `O`; los sufijos de acciones no añaden nada condicionado en `O` |
| sin merge hay más información situacional | 0,053 vs 0,006 | los sufijos hondos SÍ correlacionan con el lugar (mundo determinista) pero no pagan: merge los retira |
| bimodalidad · muerte en 0 pasos | favor inicial 0,02 vs incremento 0,17 | la partición por `(estado, comando)` casi nunca paga de verdad, así que se acepta por márgenes ínfimos y muere al primer dato |

La incomensurabilidad crear/destruir es el mecanismo **próximo**. La familia de
particiones equivocada es la causa **distal**: con la partición correcta los
splits nacerían con favor grande.

---

## 3 · Los errores que cometimos

**1 · Veinte gates y ninguno miraba la forma de `F`.** Certificamos procedencia,
fuga de oráculo, conservación de masa, tiempo causal, pasividad del scoring,
reversibilidad, paridad de baseline. Nunca «¿entra `O` en `Z`?». La ecuación
sellada del estado no fue nunca un gate, y las veinte pasaron sobre una
implementación que la violaba en su núcleo.

**2 · El «learner mínimo» heredó el sesgo inductivo de 1.7 sin derivarlo del
oráculo.** Refinar por firma de entrada `(estado, comando)` es la extensión
natural de la tabla `(o, a)` de 1.7. Era la jugada tabular más cercana, y dejó
la observación fuera sin que nadie lo decidiera.

**3 · Los defectos de medición absorbieron la sesión y enmascararon el de
arquitectura.** Scoring que no avanzaba el estado, routing absorbente,
`organization` absorbente: cada vez que el learner salía mal, el instrumento
tenía la culpa, y repararlo era correcto. Pero cada reparación producía una señal
positiva que se trató como «el learner funciona; ahora elijamos presupuesto».
La señal era real —historia de acciones más honda que FD1— pero **no era**
desambiguación predictiva del aliasing. Calibramos tres rondas un mecanismo que
no podía, en principio, hacer la tarea sellada.

**4 · Crear y destruir escritos por separado, en escalas distintas.** Defecto
genuino, pero aguas abajo del anterior.

**5 · Una corrección que me debo.** Cuando preguntaste si estábamos cometiendo
el error de 1.5 —organizar antes de generar— te dije que sí. La tabla de §1 dice
otra cosa: bajo el mismo paseo aleatorio uniforme, dos pares (obs, acción)
resuelven el 91 % de la situación. **La política no es lo que bloqueó la
adquisición.** La ecuación del estado lo fue. El paseo aleatorio limita el *uso*
de `Z` —nada lo consume— pero no su *adquisición*. Acepté demasiado rápido una
lectura que encajaba con la narrativa del proyecto sin medirla.

---

## 4 · Predicciones falsables

Si la hipótesis es cierta, un learner cuya firma de entrada incluya la
observación —`(estado, comando, observación)`— debe, **sin tocar nada más**:

```
a  nacer con favor inicial un orden de magnitud mayor (la partición paga)
b  no ser bimodal: ninguna vida termina con 1 estado
c  I(C;Z|O) corregida por nula ≫ 1,6 %
d  batir a FD1 en las 16 vidas, no en 10
```

La refuta: que con `O` en la firma el favor inicial siga en ~0,02, o que la
bimodalidad persista, o que `I(C;Z|O)` no suba. Entonces la causa está en otro
sitio y esto era una correlación.

---

## 5 · Lo que no se hace

No se rescata `LEARNER-18-v1`: está cerrado como insuficiente y la calibración
que lo cerró es válida para el mecanismo que era. Una v2 con `O` en la firma es
**otro mecanismo**, y se sella antes de escribirse —con un gate nuevo que
certifique la forma de `F`, para que la ecuación del estado no vuelva a ser una
frase del oráculo que ningún gate lee.

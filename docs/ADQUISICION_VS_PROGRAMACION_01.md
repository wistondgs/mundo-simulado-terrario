# Adquirir una capacidad frente a recibirla programada

Respuesta a las doce preguntas.

Regla de este documento: **todo «MEDIDO» lleva fichero y línea, o el documento del
proyecto donde está el número.** Lo que es diseño mío va como **PROPUESTA** y puede
estar equivocado. No hay cifras de memoria.

> **Hallazgo que ordena todo lo demás.** El programa de adquisición causal
> ([PROGRAMA_ADQUISICION_CAPACIDAD_01.md](docs/PROGRAMA_ADQUISICION_CAPACIDAD_01.md))
> ya corrió este experimento y dio **negativo**, con la causa medida:
> el organismo recibe **mediana de 6 ejemplos informativos por vida** de 1200 pasos.
> La pregunta «¿cómo adquiere sin que se lo programe?» ya tiene una respuesta parcial
> del propio proyecto, y no es sobre la arquitectura: **es sobre la exposición.**

---

# 1 · La frontera operativa

No es filosófica y no depende de la intención del programador. Propongo ésta:

> **Una capacidad fue DADA si existe en la arquitectura una función cuya firma ya
> computa el constructo con las variables correctas ligadas. Fue ADQUIRIDA si el
> constructo sólo es computable después de la experiencia, desde un sustrato
> INDIFERENTE a qué constructo va a acabar computando.**

La palabra que trabaja es **indiferente**, y da una prueba barata:

> **El mismo mecanismo, sin tocar una línea, en un mundo distinto, tiene que producir
> una capacidad distinta.** Si sólo puede producir X, X estaba dada.

Aplicada al linaje, sin piedad:

| ser | qué se le dio | ¿indiferente? |
|---|---|---|
| el que cuenta contingencias **por caso** | la tabla indexada por observación completa × acción | **No.** El diseñador decidió cuáles son las variables relevantes |
| el que cuenta **por rasgos** | la factorización en rasgos | **No.** Decidimos nosotros por dónde se corta el mundo |
| el que **recuerda** | la ranura de memoria y su política de escritura | **No.** La ranura está ahí exista o no estructura temporal |
| el que **liga** | el mecanismo de correspondencia | **No.** Aprende qué se liga, no que haya que ligar |
| el de **memoria acotada sin semántica** | la cota, y nada más | **Parcialmente sí** — y por eso es el primero que se acerca |

El salto del último no es tener memoria. Es que **nadie dijo qué guardar**.

---

# 2 · El mecanismo mínimo general

**PROPUESTA.** Un solo sustrato:

```
m_t ∈ R^k                 estado interno ACOTADO, k pequeño y declarado
w(o_t, m_t) → m_{t+1}     compuerta de escritura, parámetros aprendibles
π(o_t, m_t) → a_t         la política LEE el estado interno
```

Tres restricciones, y las tres hacen falta:

1. **`k` acotado y menor que lo que el mundo exige retener.** Sin escasez no hay
   presión y no se organiza nada.
2. **Ninguna semántica asignada a las ranuras.** Ni por dirección, ni por tiempo,
   ni por atributo.
3. **La misma señal que evalúa la conducta entrena la escritura.** Sin pérdida
   auxiliar «de memoria»: eso sería programarla.

De ahí salen cinco capacidades, **diferenciadas por el mundo y no por el código**:

| capacidad | qué la hace aparecer |
|---|---|
| memoria | el mundo exige información de `t−k` |
| categorización | ranuras < situaciones distintas → obligado a fusionar |
| atención | entrada más ancha que el ancho de banda de escritura → obligado a elegir |
| binding | dos atributos deben quedar coindexados en la misma ranura |
| predicción | escribir *lo que espero* paga más que escribir lo que veo |

**La cota `k` es la fuente de toda la presión.**

---

# 3 · Cómo demostrar adquisición y no arquitectura escondida

**Tres de los cinco controles ya existen en el proyecto y ya dieron resultado.**
El diseño aprendiz / congelado / crédito-barajado es exactamente esta pregunta:

| nivel | condición | significa |
|---|---|---|
| 1 · adquisición paramétrica | `L_post > F_post` | la actualización produjo información funcional |
| 2 · crédito correcto | `L_post > S_post` | importa la correspondencia experiencia↔consecuencia |
| 3 · generalizable | sobrevive a entidades y valores nunca vistos | capacidad generalizada |

**MEDIDO** (8 semillas, 1200 pasos, 400 sondas por banco,
[PROGRAMA_ADQUISICION_CAPACIDAD_01.md §2.1](docs/PROGRAMA_ADQUISICION_CAPACIDAD_01.md)):

```
banco reservado     G_P = +0.0103  (+4/−3)      control barajado: +0.0250
banco decorrelado   G_P = +0.0097  (+3/−4)      control barajado: +0.0163
banco visto         G_P = +0.0238  (+5/−3)      control barajado: +0.0184
```

**El control de crédito barajado queda por encima del aprendiz en los tres bancos.**
No es que el aprendizaje fuera pequeño: es que lo poco que se mueve **no depende de
que la consecuencia esté bien asignada**. Es deriva. El instrumento funcionó y
devolvió un negativo limpio, que es lo que tiene que hacer un instrumento.

Faltan dos controles, y son los que propongo añadir:

**C4 · Escalado de capacidad.** Variar `k` y medir. **Una capacidad que vive en el
sustrato aprendido degrada de forma graduada al reducir `k`.** Si es indiferente a
`k`, vive en otro sitio — y ese otro sitio se lo pusimos nosotros. Es la firma más
limpia que conozco, y es barata.

**C5 · Intercambio de mundo.** Mismo código, mismas semillas, mundo sin la estructura.
Si la capacidad aparece igual, estaba en la arquitectura.

---

# 4 · Qué tiene que cambiar por dentro

El proyecto ya tiene el instrumento correcto, y es una cadena de tres eslabones, no un
número:

```
G_P  ganancia predictiva      ¿aprendió algo del mundo?
G_S  ganancia de decisión     ¿la decisión lo usa?
G_R  ganancia conductual      ¿llega a la conducta?
```

La tabla diagnóstica que separa los casos ya está escrita, y es lo que permite decir
*dónde* se corta la propagación en vez de decir «no aprendió».

**Y hay un defecto de medición ya nombrado que vale como advertencia general**:
`G_R ≡ 0` en todas las celdas **por construcción**, porque el examen de realización
resolvía la dirección favorable sin consultar al organismo. Medía una propiedad del
contrato, no del ser, y daba 1,0 para cualquier agente antes y después.

Esto es la pregunta 8 ocurriendo de verdad, en casa, y detectada. Guardarlo.

---

# 5 · ¿El mismo mecanismo, capacidades distintas?

Es la pregunta central y es la prueba del §1. Experimento mínimo: un sustrato, dos
mundos, cero cambios de código.

```
MUNDO A   la señal aparece en t y se necesita en t+1        → debe emerger MEMORIA
MUNDO B   16 situaciones, k=4 ranuras, sin demora temporal  → debe emerger CATEGORIZACIÓN
```

| | |
|---|---|
| **programado** | `m_t` con `k` ranuras, compuerta `w`, política `π`, una señal escalar |
| **aprendido** | qué se escribe y cuándo |
| **evidencia** | en A, la conducta correcta con demora y sólo con escritura activa; en B, las 16 situaciones se agrupan en ≤4 clases **y las agrupadas comparten consecuencia** |
| **control falsador** | correr A en B y B en A. Si aparece memoria en el mundo sin demora, la memoria estaba dada |
| **resultado negativo** | que en ambos mundos emerja la misma organización de `m` → el sustrato tiene un sesgo que no declaramos |

---

# 6 · Un mundo que cree la presión

> **La capacidad tiene que ser el camino más barato al pago, y el mundo tiene que
> encarecer los demás.** Nunca «aprendé X»: siempre «aquí, no-X te cuesta».

```
memoria          la pista desaparece antes de que haga falta actuar
categorización   más situaciones que ranuras
atención         más canales de entrada que ancho de banda de escritura
binding          dos atributos con las mismas marginales y distinta ligadura
predicción       actuar tarde cuesta; anticipar paga
```

**Y una condición que el proyecto ya pagó por no respetar: el mundo no puede
agotarse.** El diagnóstico de P1 lo dice con todas las letras: el cuello no es el
aprendiz, es la **hambruna de exposición informativa** — mediana de **6 ejemplos
informativos por vida de 1200 pasos** — y tiene dos fuentes ya medidas: el canal de
acción desperdicia el **98,5 %** referencialmente, y el mundo del banco es
**estrictamente agotable** porque el ciclo de oportunidades no se ejecuta.

Ninguna arquitectura adquiere una regularidad perceptiva con seis ejemplos.

**Esto reordena las prioridades: antes de diseñar el sustrato del §2 hay que arreglar
la exposición, o el sustrato nuevo dará el mismo negativo por la misma razón.**

---

# 7 · La menor señal de enseñanza

Ordenadas por cuánto regalan, de menos a más:

```
1. cambio de viabilidad     lo genera el cuerpo al chocar con el mundo;
                            el diseñador nunca la escribe por situación
2. éxito/fallo escalar      externo, pero de un bit
3. error predictivo         dice QUÉ estuvo mal, no sólo que lo estuvo
4. objetivo vectorial       ya es supervisión
```

Criterio operativo para saber cuándo una señal regala demasiado:

> **Comparar la dimensionalidad de la señal con la de lo que hay que aprender.** Si la
> señal tiene la misma forma que la respuesta, es supervisión disfrazada.

Por eso la viabilidad va primera: es escalar, es interna, y **no contiene información
sobre la solución** — sólo sobre si te estás muriendo.

---

# 8 · Evitar que la solución se cuele

Tres fugas, las tres verificadas, dos de ellas en casa.

**Fuga por el mundo.** En la réplica externa, la condición «binaria» declara entrada
visual; el código hace `eef = eef[2] #only z axis`, toma la norma del desplazamiento
respecto al paso anterior y la binariza con umbral `0.02`. La «novedad visual» **es el
desplazamiento vertical de la muñeca**. El mundo entregaba la respuesta por un canal
directo. **MEDIDO**, `singleModel.py:466-477`.

**Fuga por la métrica.** `G_R ≡ 0` por construcción (§4). El examen respondía solo.

**Fuga por el protocolo de medición.** Si cada brazo se mide sobre los estados que su
propia conducta visita, parte de la diferencia es desplazamiento de distribución, no
conocimiento. **MEDIDO** sobre 8.015 situaciones y 8 semillas
([measurement.py:11-16](terrario/level1/measurement.py:11)): el protocolo cambia el
marcador de **exactamente un brazo, y es el control negativo** —

```
permutado    trayectoria propia 0.3072    situaciones iguales 0.6673    delta +0.3600
```

Reproducido hoy a 32 semillas, el mismo brazo y sólo ese brazo:
`trayectoria 0.2682` contra `conducta 0.6150`.

— porque el permutado es determinista dada la observación: elige una dirección
bloqueada, no se mueve, vuelve a ver lo mismo y se atasca. Leer ese `0,30` como «el
control cae por debajo del azar» habría sido medir la trampa. Todos los demás brazos:
delta `0,0000`.

**Regla para el decodificador.** Tiene que ser **más débil que la política**, y el
mismo decodificador tiene que **fallar en el control**. Si recupera la variable
latente del estado de un agente congelado, el que trabaja es el decodificador.

---

# 8 bis · El fallo que no estaba en tus doce preguntas

Hay una tercera posibilidad entre «el mecanismo ayudó» y «el mecanismo no ayudó»:

> **el mecanismo nunca se ejecutó, y el resultado que medimos es el de su respaldo.**

No es hipotético. Ocurrió hoy, en casa, y lo encontré al reproducir el experimento de
curiosidad.

**MEDIDO** · 16 semillas × 8192 experiencias ·
`scripts/level1_curiosity.py --semillas 16`:

```
ser                                  Brier    conducta   celdas   sorpresas
aprende por casos                 0.001566      1.0000     63.0          —
curioso · flujo compartido        0.001566      1.0000     63.0        0.0
curioso · AUTO-DIRIGIDO           0.006824      1.0000     63.8        0.0

Brier: compartido − auto-dirigido    -0.005258   IC95% [-0.006665, -0.003847]   signo + 0%
```

Leído deprisa: elegir qué probar **empeora** la predicción, en las 16 semillas, sin
excepción. Pero la columna que importa es la última. **Sorpresas: 0,0.** Cero, en
131.072 experiencias.

El mecanismo del ser curioso es que *la sorpresa dirija la acción*. La sorpresa nunca
ocurrió. **Lo que corrió no fue curiosidad: fue su respaldo** — el interés decayendo
0,1 por visita, que es exploración por conteo.

## Por qué no podía ocurrir, verificado ejecutando y no razonando

La pérdida es `(q − y)²` con `q = α/(α+β)` y prior `(1,1)`, y el umbral se ancló en
`0.25` con un argumento que parecía bueno: es lo que produce un predictor ignorante,
así que «sorprenderse» significa «he fallado más que si no supiera nada».

El argumento tiene un agujero. En un mundo determinista, `0.25` no es un valor típico
del ignorante: **es el máximo alcanzable**, y se toca exactamente una vez, en la primera
visita, donde la comparación es `0.25 > 0.25` → falso. A partir de ahí `q` se mueve
hacia `y` de forma monótona y la pérdida sólo baja:

```
visitas sucesivas de una misma (observación, dirección), y constante:
  0.2500  0.1111  0.0625  0.0400  0.0278  0.0204  0.0156  0.0123
  máximo = 0.250000    ¿supera 0.25? False    sorpresas del propio objeto = 0
```

**El umbral estaba puesto en el techo.** Determinismo + prior simétrico + comparación
estricta ⇒ la sorpresa es imposible por construcción, no improbable.

## Corrige una conclusión anterior

Yo había cerrado esto como «el mundo de 64 celdas deterministas no puede albergar la
pregunta». Era la dirección correcta y la afirmación imprecisa. La versión exacta es
más fuerte y es mecánica:

> **En un mundo determinista, un umbral de sorpresa anclado en la pérdida del ignorante
> nunca puede dispararse.** No es que el mundo sea pequeño: es que el umbral y el techo
> coinciden.

El mundo pequeño sigue siendo un problema —y el §6 lo sostiene—, pero no era éste.

## La regla que se lleva a las doce preguntas

> **Todo mecanismo propuesto tiene que traer un contador que informe de si su
> componente distintivo llegó a ejecutarse alguna vez.**

Sin ese contador no se puede distinguir *no ayudó* de *no corrió*, y las dos producen
exactamente el mismo número. En la tabla de cada propuesta, junto a «resultado
negativo», va una fila más:

| | |
|---|---|
| **resultado nulo por inactividad** | el contador del componente distintivo marca 0 → el experimento no probó lo que dice probar, y no hay conclusión que extraer |

Aquí el contador existía —`self.surprises`— y por eso el defecto se ve. Es la única
razón por la que este párrafo puede escribirse. **Ese instrumento se replica en todo lo
que venga.**

---

# 9 · Representación contra memorización

La prueba no es dejar fuera **instancias**: es dejar fuera **combinaciones** cuyas
partes sí se vieron por separado. Y esto ya está medido, hoy, con el discriminador del
experimento de contingencia sensoriomotora: los mismos seres entrenados **sin ver
cuatro de las dieciséis situaciones**, y medidos **sólo sobre esas cuatro**.

**MEDIDO** · 32 semillas · `scripts/level1_sensorimotor_contingency.py --semillas 32`:

```
ser                             Brier (retirado)    conducta
aprende por casos                      0.250000      0.6646     ← el ignorante exacto
aprende por rasgos                     0.000021      1.0000
vecino más próximo (transferido)       0.094004      1.0000
congelado / techo externo                     —      0.6646
```

```
Brier retirado: casos − rasgos    +0.249979   IC95% [+0.249977, +0.249979]   signo + 100%
conducta retirada: rasgos − td    +0.335380   IC95% [+0.330807, +0.339868]   signo + 100%
```

El que cuenta por casos no queda *peor*: queda **exactamente en el ignorante**,
`0.250000`, el valor analítico de decir siempre 1/2. No degrada — no tiene nada. Y su
conducta en las situaciones retiradas es la del congelado, `0.6646`, clavada.

**Ésa es la separación que buscamos, y es la más limpia del banco:** mismo prior, misma
experiencia, mismo mundo; cuatro órdenes de magnitud de diferencia, con el 100 % de las
semillas del mismo lado y un intervalo de confianza de anchura `0.000002`.

El alcance honesto, sin embargo, está nombrado en el propio programa de adquisición:
pasar el banco reservado demuestra **generalización perceptiva fuera de prototipos**, no
inducción de la regla latente. Una superficie suave alrededor de dos prototipos acierta
fuera de ellos sin haber identificado el criterio.

La versión exigente para una capacidad adquirida: retirar una **combinación** cuyos dos
componentes aparecieron por separado. Si acierta, compuso. Si da el prior, memorizó.

# 10 · Integrar sin escribir una regla de composición cada vez

**PROPUESTA**, y creo que es de recursos, no de arquitectura:

> **Que todas las capacidades vivan en el mismo sustrato y compitan por el mismo
> recurso escaso.**

Si memoria, categorías y atención consumen ranuras del **mismo `k`**, la composición no
la escribimos: la fuerza el presupuesto. El organismo tiene que **repartir**, y el
reparto *es* la composición. Se vuelve medible: qué fracción de `k` toma cada función,
y cómo se redistribuye cuando el mundo cambia de exigencia.

Precedente verificado: el gestor homeostático que corrimos hace exactamente esto con
las pulsiones — `before-trigger ((freeze all))` / `after-trigger ((unfreeze all))`.
Un recurso, exclusión mutua, y el arbitraje emerge en vez de escribirse.

---

# 11 · Detectar por sí mismo que no le alcanza

Experimento mínimo, sin llamarlo metaaprendizaje: dar al organismo **una segunda acción
más cara** —preguntar, mirar mejor, esperar— y demostrar que la toma **selectivamente
cuando su error es alto Y no está bajando**.

La conjunción es todo. «Error alto» es *no saber*. «Error alto y estancado» es **no
poder**. Distinguirlas exige una derivada temporal del error.

**MEDIDO**: en los 12 ficheros Python de la réplica externa, buscar
`progress|derivative|slope|previous_loss|prevLoss|lossDelta` da **2 coincidencias, las
dos en `plotMyLog.py`**, y las dos dentro de `plot_progress()`, que sólo dibuja con
matplotlib. **Ninguna en la ruta de decisión.** El sistema traza su propio progreso
para el humano y no lo lee para sí mismo.

| | |
|---|---|
| **programado** | la acción cara existe y tiene coste |
| **aprendido** | cuándo usarla |
| **evidencia** | su frecuencia correlaciona con `dε/dn ≈ 0 ∧ ε alto`, no con `ε alto` solo |
| **control falsador** | un mundo donde el error es alto pero **sí** baja. Si pregunta igual, sólo reacciona al nivel |
| **resultado negativo** | la usa a tasa constante, o correlaciona sólo con `ε` |

---

# 12 · El primer experimento, si hubiera que elegir uno

**Categorización bajo presión de capacidad.** Es la más barata de instrumentar, tiene
un control negativo perfecto, y **la misma maquinaria con otro mundo da memoria** —
con lo que de paso demuestra la pregunta 5, que es la que importa.

```
DE FÁBRICA    k ranuras acotadas, compuerta de escritura con parámetros,
              una política que lee (o_t, m_t), y una señal escalar de viabilidad

DESCUBRE      QUÉ situaciones comparten ranura

EVIDENCIA     las situaciones agrupadas comparten consecuencia, y la agrupación
              NO es la que un diseñador habría elegido — medirlo como información
              mutua entre la partición emergente y la partición por consecuencia

CONTROL       k ≥ número de situaciones. Sin escasez no debe aparecer agrupación

FALSADOR      si con k holgado aparece agrupación igual, nuestra compuerta trae
              un sesgo que no declaramos

NEGATIVO      la partición emergente es independiente de la consecuencia → agrupa
              por algo irrelevante, y no hay categorización
```

**Requisito previo, no negociable, y viene del §6:** este experimento no se corre hasta
que la exposición informativa esté arreglada. Con seis ejemplos por vida el resultado
ya se conoce, y sería el mismo negativo de P1 atribuido por error al sustrato nuevo.

---

# El cambio de eje

Pasar de «¿cuál es la siguiente habilidad que le ponemos?» a «¿cuál es la menor
maquinaria para que aparezca?» tiene una consecuencia práctica concreta:

**cada fila del mapa de habilidades necesita una segunda columna** — no sólo *qué sabe
hacer*, sino **qué fracción de la solución tuvo que construir**. Esa fracción es
medible con el control C4: cuánto degrada la capacidad al reducir el recurso que le
dimos.

Con esa columna, los seres que ya corrieron no bajan de categoría: siguen siendo
resultados válidos. Pero quedan etiquetados como lo que son — demostraciones de **uso**,
no de **adquisición**. Y el de memoria acotada sin semántica pasa a ser el primero del
linaje que puede aspirar a la segunda etiqueta.

Conviene además nombrar que el backlog del programa ya tenía esta pregunta escrita
como trabajo futuro: **adquisición autónoma — «sin stream igualado: que el organismo
consiga su propia experiencia»**. Tu reformulación no abre una línea nueva. **La
asciende de backlog a objeto principal**, y el diagnóstico de la hambruna de
exposición explica por qué tiene que subir: mientras la experiencia se le entregue
igualada, el organismo no puede resolver su propia escasez.

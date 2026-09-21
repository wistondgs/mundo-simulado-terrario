# Handoff · Agente de Nivel 1.6

Adquisición de estructura temporal del flujo sensorial propio.
Para quien vaya a construir el decimal siguiente.

```
árbol   /home/wis/level16-sensory-change-01
rama    experiment/level16-developmental-sensory-change-01
base    d278f59   cierre del Nivel 1.0
estado  CONGELADO · A1 = DEMOSTRADA · RÉGIMEN = EXPOSICIÓN SATURADA
```

---

# 0 · Lee esto antes de escribir una sola línea

**Un decimal, una adquisición.** 1.6 añade exactamente una cosa: `P(o_{t+1} | o_t)`.
Todo lo demás del ser está congelado o no existe.

**El aislamiento es estructural, no declarado.** El árbol arranca del cierre del
1.0, así que `level11`, `level12`, `level13`, `level14`, `organism` y `remembered`
**no están en el disco**. Si tu decimal necesita alguna de esas capacidades,
ramifica de otro commit — no las importes aquí.

**Lo único que el paquete importa del proyecto es `terrario.level1.world`.**
Verificado por AST en `gate_lineage_isolation` y en la suite.

**El oráculo se sella antes del código y no se edita nunca.** Si al implementar
aparece una discrepancia, se emite una **enmienda fechada y separada**. En 1.6
salieron tres, todas antes de la campaña.

**Nunca `git add -A`. Cada trabajo nuevo es un commit aparte. No push, no merge.**

---

# 1 · El mundo · heredado, no elegido

Física del Nivel 1.0 importada sin modificar desde `terrario/level1/world.py`.
Los parámetros **se leyeron del experimento canónico**, no se ajustaron:

```
grid_size          7        terrario/level1/measurement.py:52
wall_probability   0.25     terrario/level1/measurement.py:55 · reversal.py:259
observación        4 bits, uno por dirección, 1 = celda contigua bloqueada
acciones           {UP, DOWN, LEFT, RIGHT}, rebote contra pared
determinista       sí · sin recompensa, comida, energía ni objetivo
```

**Estadística medida sobre 20 réplicas de 200 mundos × 4096 pasos:**

```
tasa de movimiento                     0.5923 ± 0.0087
tasa de CAMBIO sensorial  o' ≠ o       0.5155 ± 0.0065
se movió sin que cambiara la obs.      0.1297 ± 0.0060  de los movimientos
observaciones distintas alcanzadas     16 de 16
transiciones distintas alcanzadas      182 – 184 de 256
I(o ; o')                              0.8861 ± 0.0358 nats
```

> **Advertencia de precisión, que ya me hizo equivocarme una vez.** La unidad
> correlacionada es el **mundo**, no el paso. El `n` efectivo de estas cifras es
> el número de mundos (~200–400), no los 1 638 400 pasos. Usar el error por paso
> sobreestima la precisión por un factor de veinte. **Ningún gate puede exigir de
> estos descriptores más precisión de la que tienen.**

El `12 %` de movimientos sin cambio sensorial importa para la redacción:
`c = 1[o'≠o]` **no es «se movió»**. Dos celdas contiguas pueden compartir firma.

---

# 2 · La arquitectura · qué pusimos y qué nació

## 2.1 · S0 · sustrato suministrado

```python
class EndogenousMotor:
    def __init__(self, rng: np.random.Generator)   # exige Generator propio
    @property emitted -> int                        # prueba de procedencia
    def next() -> Direction                         # uniforme sobre 4
    def state() -> dict                             # {"rng": ..., "emitted": ...}
    def restore(state) -> None                      # MotorContractError si falta "rng"
```

**No cuenta como inteligencia adquirida.** Nace con el cuerpo, no cambia un bit en
toda la vida. Lo que importa de él no es su sofisticación —es uniforme a
propósito— sino tres propiedades:

- el generador **pertenece al organismo**: no hay cinta de acciones, ni maestro,
  ni currículo;
- su estado **forma parte de la serialización del ser**: misma foto ⇒ mismo futuro,
  incluidos los actos estocásticos;
- **cuenta lo emitido**, para que la procedencia se verifique contra los pasos
  vividos en vez de asumirse.

## 2.2 · A1 · la única adquisición

```python
PRIOR = 1.0
OBSERVATION_INDEX: dict[Observation, int]           # 16 firmas, índice fijo

class TemporalModel:
    def observe(previous, following) -> None        # LA ÚNICA operación plástica
    def predict(previous) -> np.ndarray             # 16 probabilidades
    def probability(previous, following) -> float
    def change_probability(previous) -> float       # q(o) = 1 − P(o|o), SECUNDARIA
    @property updates -> int
    @property frozen -> bool
    def freeze() -> None
    def fingerprint() -> str                        # sha256 del estado
    def snapshot() -> np.ndarray                    # para la intervención causal
    def load(counts) -> None
    @classmethod naive(prior=PRIOR) -> TemporalModel # M_0
```

Tabla 16×16, prior simétrico, una operación: ver dos observaciones consecutivas y
sumar uno. **No hay generalización entre observaciones, y es deliberado**: con 256
celdas independientes, cualquier competencia medida procede de haber vivido las
transiciones.

`α₀ = 1` no es una elección de gusto: hace que el ser sin experiencia prediga
uniforme y que la pérdida del brazo FROZEN valga exactamente `log 16 = 2.7726`.
Es un ancla analítica, no un hiperparámetro.

## 2.3 · La frontera · dónde está y por qué

**Está en la firma, no en una promesa.** `observe` acepta dos tuplas de cuatro bits
y `TemporalContractError` rechaza en ejecución: un `Direction`, un int, una
posición `(3,3)`, tres bits, un no-bit, una lista.

```
RECIBE      el par temporal (o_t, o_{t+1})
NO RECIBE   a_t · copia eferente · posición · c_t · Δ
            reward · novelty · progreso · valor · target · labels
```

La copia eferente **existe** en el cuerpo porque el cuerpo la tiene. Lo que el
contrato prohíbe es que el aprendiz la lea. Sin esa frontera A1 derivaría hacia
`P(o'|o,a)`, que ya es contingencia propia.

Reforzado por AST: `temporal.py` no nombra `direction`, `action`, `act`,
`efference`, `moved`, `movement`, `position`, `delta`, `changed`, `motor`, `grid`
ni `cells`.

## 2.4 · Cuarentena de flujos

Sin esto, «evaluar si un mundo sirve» alteraría la vida que ese mundo produce.

```python
world_stream(seed)          -> default_rng([seed, 0])   # rejilla + celda natal
motor_stream(seed)          -> default_rng([seed, 1])   # S0
shuffle_stream(seed)        -> default_rng([seed, 2])   # TEMPORAL-SHUFFLED
null_stream(seed, replica)  -> default_rng([seed, 3+k]) # nulas de la auditoría
```

**Corolario exigible y verificado por test:** la trayectoria de la semilla `s` es
idéntica se haya consultado el predicado estructural o no, y su hash lo demuestra.

---

# 3 · El ciclo experimental · adquirir, congelar, continuar, evaluar

```python
ACQUISITION_STEPS = 4096
POST_STEPS = 2048

def live(seed, steps=4096, post_steps=2048) -> Life
```

```
vida de adquisición (T pasos)
        │
        ▼  FREEZE
        │
        ▼  continuación en el MISMO mundo, mismo flujo motor, N_POST pasos
        │
        ▼  banco POST no visto, IDÉNTICO para los cuatro brazos
```

**`live()` no construye ni importa modelo alguno.** Ésa es la razón de que la
paridad de trayectoria entre brazos sea **estructural** y no impuesta: el cuerpo
no puede leer la tabla, luego la trayectoria no puede depender de lo aprendido.
El hash existe para demostrarlo, no para conseguirlo.

**El banco POST es del propio mundo, no poblacional.** Medido, el banco poblacional
invierte el signo del resultado:

```
T           banco de su mundo     banco poblacional
   256           1.7269               2.4628
 4 096           1.2654               2.7556
16 384           1.2379               3.0815      ← peor que FROZEN (2.7726)
```

`population_bank_diagnostic()` lo conserva como **diagnóstico exploratorio**, y un
test verifica que el módulo de gates ni siquiera lo nombra.

---

# 4 · Los brazos y el instrumento

```python
full(life)              -> TemporalModel   # S0 vive, A1 cuenta, se congela
frozen(life)            -> TemporalModel   # misma vida, tabla en el prior
temporal_shuffled(life) -> TemporalModel   # o_t con o_{π(t)+1}
StaticBitcount.fitted(life)                # q(o) = β·k(o)/4, un parámetro
AnalyticShadow(grid)                       # K-SOMBRA: instrumento, no brazo
```

## 4.1 · K-SOMBRA no estima: resuelve

Bajo política uniforme con rebote la cadena sobre celdas es **simétrica**
—`P(c→c') = 1/4` en ambos sentidos para cada par adyacente libre— luego su
estacionaria es **uniforme sobre el componente natal**. Eso permite escribir la
conditional exacta:

```
P(o'|o) = (1/|C_o|) · Σ_{c∈C_o} (1/4) · Σ_d 1[firma(aterriza(c,d)) = o']
```

Es el suelo de pérdida alcanzable. Contesta la pregunta que el organismo no puede
contestar sobre sí mismo: **¿había algo que aprender?** Sin ella, un nulo es
ambiguo entre «el mecanismo no tiene plasticidad» y «esta vida no daba para nada»,
y esas dos cosas son evidencia sobre partes distintas del ser.

`teachability(shadow, bank) = log 16 − L(sombra)` es el discriminante.

## 4.2 · El barajado, y los dos contadores que confundí

```python
@dataclass class ShuffleAudit:
    fixed_points            # π(t) == t · esperanza 1 · ES «pares supervivientes»
    value_coincidences      # following[π(t)] == following[t] · esperanza n·Σp²
    expected_coincidences
    full_distance_to_marginal
    shuffled_distance_to_marginal
    null_mean, null_sd
    @property tolerance     # null_mean + 4·sd  ← se autocalibra
    @property destructive
```

Contar coincidencias de **valor** da 431 de 4096 y no es un defecto: con dieciséis
observaciones el azar predice 410. El «0 supervivientes» sellado sólo podía
referirse a puntos fijos de la permutación.

**El umbral fijo fue un error mío y está corregido.** Una fracción `< 0.5·d_FULL`
depende del tamaño de muestra: a `T = 512` una baraja **honesta** llega a 0.573.
Ahora el criterio es la distribución nula de la propia trayectoria, generada con
ocho permutaciones de referencia:

```
T       razón de una baraja honesta        ¿servía 0.5?
        media     p95      máx
 512    0.3803  0.5216  0.5732             NO
1024    0.2476  0.3282  0.3551             sí
4096    0.1065  0.1397  0.1534             sí, margen 3×
```

---

# 5 · Métricas · cuál manda y por qué

```python
log_loss(model, bank)     -> float   # PRIMARIA · nats por transición
brier_change(model, bank) -> float   # SECUNDARIA · diagnóstica
free_directions(o)        -> int     # 4 − sum(o)
```

**Endpoint primario:** log-pérdida de la distribución completa `P(o'|o)`.

**Por qué `BS_change` es secundaria, medido antes de escribir el código:**
`q(o) = 1 − P(o|o)` correlaciona **0.9748** con el número de direcciones libres, y
una regla estática de **un solo parámetro** queda a 0.0039 de la tabla aprendida.
Confirmatorio: FULL 0.212128 vs BITCOUNT 0.219067, y **el control gana en 3 de 16
vidas**. Si el primario hubiera sido el bit de cambio, el nivel no habría
demostrado nada temporal.

`StaticBitcount` **no tiene método `probability`**. Pedirle el primario levanta
`PrimaryMetricNotApplicable`. Estructura, no una regla en una docstring.

---

# 6 · El oráculo y sus tres enmiendas

| commit | qué es |
|---|---|
| `9b0d39b` | oráculo sellado antes de existir código · **blob idéntico en HEAD** |
| `d0ce9f8` | Enmienda 01 · consumo de semillas |
| `8f8c85d` | Enmienda 02 · parámetros del mundo y prior |
| `5c54848` | Enmienda 03 · criterio de clasificación |

Las tres preceden a `9625aaa`, el primer commit capaz de producir un número.

## 6.1 · Enmienda 01 · la regla que el oráculo prometió y no escribió

El oráculo decía que las semillas `N-MUNDO` «se reemplazan por regla
preregistrada» y no daba ninguna. Eran dieciséis grados de libertad.

```
k ← 0
para s = 140000011 … 140000042 ascendente, sin saltos:
        construir el mundo · evaluar N-MUNDO   ← ANTES de vivir
        si N-MUNDO: registrar, publicar, NO correr la vida, siguiente s
        si no:      k ← k+1 · esta semilla es la vida k · correr
        si k = 16:  PARAR
```

**La mitad que importa es la segunda:** sólo `N-MUNDO` —estructural, anterior a la
vida— provoca reemplazo. `N-EXPERIENCIA`, `N-PLASTICIDAD`, `NEGATIVO VERDADERO` y
`POSITIVO` son posteriores y **permanecen entre las 16, en el denominador**.
Sustituirlas sería seleccionar vidas favorables.

`INVÁLIDO` no es categoría de semilla: es defecto de cableado y anula la campaña
entera.

## 6.2 · Enmienda 02 · los parámetros que el oráculo medía sin escribir

`size=7`, `wall_probability=0.25`, `α₀=1.0`. Ninguno se ajustó: los dos primeros se
leyeron del 1.0 y el tercero es verificable por `log 16`.

> **Cómo casi reporto una contradicción que no existía.** Mi primer barrido apuntó
> a `wp = 0.26`. El error era el modelo de error: traté el paso como unidad
> correlacionada cuando la unidad es el mundo. A 0.25 los estratos coinciden a tres
> decimales. **Leer el código del 1.0 antes de barrer el espacio me habría ahorrado
> todo.**

## 6.3 · Enmienda 03 · las seis categorías que el oráculo nombró sin definir

```
disponible = log 16 − L(K-SOMBRA)      nats que este mundo puede enseñar
logrado    = L(FROZEN) − L(FULL)       nats que el ser ganó
ventaja    = L(SHUFFLED) − L(FULL)     nats atribuibles a la temporalidad

1. updates == 0  ó  huella(M_T) == huella(M_0)   -> N-PLASTICIDAD
2. disponible <= 0.05 nats                       -> N-EXPERIENCIA
3. logrado < 0.25 · disponible                   -> N-EXPERIENCIA
4. logrado > 0 y ventaja > 0 y causal            -> POSITIVO
5. cualquier otro caso                           -> NEGATIVO VERDADERO
```

`0.05` = `exp(0.05) = 1.05`, un 5 % de verosimilitud sobre predecir uniforme.
`0.25` es **una elección declarada, no derivada**.

---

# 7 · Resultados medidos

## 7.1 · Campaña confirmatoria · una sola vez

Semillas `140000011…140000026`. **Cero descartes `N-MUNDO`.** 16 sin consumir.

```
ΔL vs FROZEN      +1.5947   sd 0.2639   mín +1.3533    16/16 positivas
ΔL vs SHUFFLED    +0.8308   sd 0.3067   mín +0.1290    16/16 positivas
IC95 inferior     +0.680501                  CRITERIO PRIMARIO CUMPLIDO
causal            16/16 · gates 12/12 · contratos 89 verdes
```

| semilla | FULL | SHUFFLED | K-SOMBRA | disponible | temporal | celdas |
|---|---|---|---|---|---|---|
| 140000011 | 1.4193 | 2.3655 | 1.3829 | 1.3897 | 0.9463 | 20 |
| 140000012 | 1.1405 | 2.1612 | 1.1078 | 1.6648 | 1.0207 | 16 |
| 140000013 | 1.2041 | 1.9764 | 1.1722 | 1.6003 | 0.7723 | 24 |
| 140000014 | 0.7123 | 1.1167 | 0.7011 | 2.0715 | 0.4044 | 3 |
| 140000015 | 1.2662 | 2.3467 | 1.2336 | 1.5390 | 1.0805 | 18 |
| 140000016 | 1.3118 | 2.3082 | 1.2668 | 1.5058 | 0.9964 | 20 |
| 140000017 | 1.4119 | 2.0837 | 1.4038 | 1.3688 | 0.6718 | 21 |
| 140000018 | 1.3188 | 2.1285 | 1.2856 | 1.4870 | 0.8097 | 22 |
| 140000019 | 1.2875 | 2.1520 | 1.2580 | 1.5146 | 0.8645 | 18 |
| 140000020 | 0.7311 | 1.0908 | 0.7217 | 2.0509 | 0.3597 | 3 |
| 140000021 | 1.3929 | 2.4237 | 1.3567 | 1.4159 | 1.0308 | 20 |
| 140000022 | 1.2535 | 2.5314 | 1.2120 | 1.5606 | 1.2778 | 18 |
| 140000023 | 1.2372 | 2.3330 | 1.1971 | 1.5755 | 1.0958 | 17 |
| 140000024 | 1.2925 | 2.1075 | 1.2616 | 1.5110 | 0.8150 | 13 |
| 140000025 | 0.5675 | 0.6965 | 0.5607 | 2.2119 | 0.1290 | 2 |
| 140000026 | 1.2993 | 2.3174 | 1.2645 | 1.5081 | 1.0181 | 18 |

## 7.2 · El techo analítico

```
brecha con el óptimo   media 0.0288 nats   máx 0.0450
fracción capturada     media 0.9813        mín 0.9701
```

## 7.3 · Intervención causal

```
congelar → guardar M_T → poner M_0 → reevaluar → restaurar M_T → reevaluar
```

Las tres evaluaciones sobre el **mismo banco POST inmutable** — volver a correr el
mundo haría del ruido de trayectoria una segunda variable.

```
16/16   la pérdida sube a exactamente log 16 = 2.7726 al ablacionar
16/16   vuelve exactamente a su valor al restaurar
16/16   huella idéntica antes y después
```

## 7.4 · El hallazgo adversarial · los mundos pequeños

```
semilla     celdas   disponible   ganado   temporal
140000014        3       2.0715   2.0603     0.4044
140000020        3       2.0509   2.0415     0.3597
140000025        2       2.2119   2.2050     0.1290

correlación tamaño ↔ ventaja temporal    +0.7520
```

En un bolsillo de dos celdas la secuencia es casi determinista: la ganancia sobre
el prior es enorme, pero la **marginal** ya está tan concentrada que barajar apenas
destruye nada.

**Contrafactual exacto sobre la misma campaña:**

| criterio | n | media | IC95 inferior |
|---|---|---|---|
| **estructural** | 16 | +0.8308 | **+0.6805** |
| exclusión «≤6 celdas» | 13 | +0.9538 | +0.8653 |

El oráculo traía sellado **+0.8858** — reproduce la **exclusión**, no el criterio
estructural. **Los números del preregistro se midieron sobre una muestra ya
filtrada sin declararlo.** Incluir los casos adversos bajó el intervalo de +0.87 a
+0.68 y el nivel pasa igual: la afirmación es más fuerte por incluirlos.

## 7.5 · La identidad analítica · doctrina B-4

En el límite poblacional, con `P(o'|o)` estacionaria:

```
L(FULL)      →  H(O_{t+1} | O_t)
L(SHUFFLED)  →  H(O_{t+1})
L(FROZEN)    =  log 16                    exacto, no asintótico

⇒  ΔL(FULL vs SHUFFLED)  →  I(O_t ; O_{t+1})
⇒  ΔL(FULL vs FROZEN)    →  log 16 − H(O_{t+1} | O_t)
```

Verificado contra la campaña:

```
                 analítica   medida    sesgo      r
ΔL vs SHUFFLED     0.8536    0.8308   -0.0228   0.9935
ΔL vs FROZEN       1.6301    1.5947   -0.0354   0.9964
```

**Consecuencia para el método:** donde el mundo admita solución cerrada, el tamaño
de efecto esperado debe calcularse **por semilla antes de ejecutar al aprendiz**.
Eso separa la dificultad del mundo del rendimiento del organismo.

---

# 8 · Los doce gates · qué falsifica realmente cada uno

```
L16-0   que exista en el disco cualquier paquete de un decimal posterior
L16-1   que los actos emitidos difieran de los pasos vividos, o haya más de un emisor
L16-2   que una foto del motor no baste para reproducir sus actos futuros
L16-3   que el paquete NOMBRE --como identificador, no en prosa-- una señal de
        recompensa, novedad, valor u objetivo
L16-4   que el aprendiz nombre o acepte acto, eferencia, posición o etiqueta de cambio
L16-5   que el cuerpo pueda leer la tabla, o que la trayectoria no se reproduzca
L16-6   que el mundo no ofrezca nats por encima del prior
L16-7   que alguna vida no mejore sobre su propio estado inicial
L16-8   que el intervalo toque el cero, que la baraja conserve temporalidad,
        o que no exista auditoría de la baraja
L16-9   que ablacionar el estado no cueste competencia, o restaurarlo no la devuelva
L16-10  que evaluar mueva la huella o la cuenta de actualizaciones
L16-11  que el control de un parámetro pueda puntuarse en el endpoint primario
```

**Ninguno escanea texto.** Cuatro veces en este linaje un guardián se disparó
contra su propia documentación. Se camina el AST: un comentario no es un nodo, y
una docstring que nombra lo prohibido es una `Constant`.

La lista negra está partida en dos a propósito:

```python
UNAMBIGUOUS_SIGNALS   # prohibidos como identificador Y como atributo
GENERIC_SIGNALS       # value, values, label, labels: sólo como identificador propio
FORBIDDEN_IN_LEARNER  # lo que temporal.py no puede nombrar
```

`dict.values()` es Python, no una señal de valor. Mantener el gate afilado costó
**tres renombres en mi propio código**: `value`→`candidate`, `target`→`destino`,
`advantage`→`temporal_gain`. Renombrar lo inocente, nunca aflojar el gate.

**Cada gate tiene fixture negativa por la vía real del verificador.** Tres de las
fixtures de L16-3 deben **PASAR** (prosa que menciona reward/novelty/value, y
`dict.values()`): es lo que lo distingue de un detector de falsos positivos.

**Dos fixtures prometidas por el oráculo son imposibles y se declararon
redundancia lógica en vez de inventarles sustituto:**

- **L16-5** «cambiar una acción de un brazo»: los brazos reciben una vida **ya
  vivida** y ninguno produce actos. La paridad no es un invariante que un brazo
  pueda romper.
- **L16-6** «mundo estático»: es `N-MUNDO` y la regla de consumo lo descarta
  **antes** de vivirlo, así que no puede llegar a un gate.

---

# 9 · Taxonomía

```
INVÁLIDO            cableado, fugas o pasividad rotos · anula la campaña entera
N-MUNDO             no había estructura que aprender · anterior a la vida
N-EXPERIENCIA       el mundo podía enseñar, la trayectoria S0 no bastó
                    ← evidencia negativa sobre S0, NO sobre A1
N-PLASTICIDAD       experiencia suficiente, mecanismo sin cambio
NEGATIVO VERDADERO  K-SOMBRA aprende, A1 se activa, y aun así no adquiere
POSITIVO            adquiere y pasa las intervenciones causales
```

**La asimetría de `N-EXPERIENCIA` es el punto de diseño más importante de la
taxonomía** y hay que conservarla en los decimales siguientes: distingue un fallo
del aprendiz de un fallo del sustrato que lo alimenta.

---

# 10 · Los defectos que se encontraron construyendo

Esta sección vale más que los resultados. Son las formas concretas en que este
método falla.

| defecto | cómo apareció | lección |
|---|---|---|
| **Umbral fijo en un criterio de control** | la baraja honesta lo superaba a T=512 | los umbrales no se heredan porque los tamaños de muestra no se heredan. Derivar de la nula de los propios datos |
| **Contador que mide otra cosa** | 431 «supervivientes» de 4096 eran coincidencias de alfabeto | nombrar el contador por lo que cuenta, no por lo que quisieras que contara |
| **Guardián que escanea texto** | cuarta recurrencia en el linaje | caminar el AST, siempre |
| **Gate con etiqueta más ancha que su medición** | L16-7 dice «PRE y FROZEN», y son el mismo objeto | la etiqueta de un gate es una afirmación: verificarla |
| **Aserción vacua** | `len({id(x)}) == 1`, quinta de la estirpe | leer qué falsifica el test, nunca confiar en su nombre |
| **`pytest.raises(Exception)`** | acepta cualquier fallo, incluido uno accidental | apretar al error concreto del verificador |
| **Valor sellado de población no declarada** | +0.8858 reproducía mi exclusión, no el criterio | un valor preregistrado debe declarar sobre qué población se midió |
| **Modelo de error equivocado** | traté el paso como unidad, y es el mundo | identificar la unidad correlacionada antes de calcular un sd |
| **Categoría inalcanzable certificada como «no observada»** | `N-EXPERIENCIA` con captura mínima 0.9539 frente a umbral 0.25 | comprobar que cada rama de una taxonomía **puede** dispararse en el régimen real |
| **Exagerar la propia limitación** | dije «no distingue al organismo de la aritmética» | enunciar la limitación de más también es un error de medición |

---

# 11 · La limitación del régimen · lo que 1.6 NO probó

```
T = 4096   cobertura de S0 sobre las transiciones alcanzables:  1.0000   sd 0.0000
```

**S0 visitó todas las transiciones posibles de las 16 vidas.** El problema de
exposición estaba resuelto antes de que A1 hiciera nada.

```
T        captura A1   cobertura S0    sd cobertura
  32        0.3048       0.4795          0.2774
  64        0.4375       0.6077          0.2046
 128        0.5856       0.7972          0.1493
 256        0.7216       0.9037          0.1176
1024        0.9164       0.9984          0.0063
4096        0.9796       1.0000          0.0000

correlación cobertura(S0) → captura(A1), 112 corridas:   r = +0.9274
```

**Qué significa, dicho con precisión:** FROZEN, SHUFFLED y la intervención causal
**sí** distinguen aprender de no aprender. Lo que el experimento **no** distingue
es al organismo de **un estimador tabular elemental suficientemente alimentado**.

Por eso el `98.13 %` **no debe citarse como indicador de sofisticación**: con
cobertura 1.0 mide principalmente convergencia del estimador.

**El régimen informativo existe y no se usó.** A `T = 64` el contraste sigue
positivo (IC95 inferior +0.2384) **y la taxonomía se enciende** — una vida cae en
`N-EXPERIENCIA`.

> Un presupuesto en saturación es magnífico para demostrar convergencia y pésimo
> para estudiar cómo aprende el ser. Cuando interese la adquisición como **proceso**,
> el régimen útil está en la pendiente, no en la asíntota.

---

# 12 · Superficie de código

```
terrario/level16/
    world.py       GRID_SIZE · WALL_PROBABILITY · los cuatro flujos · build_world
    motor.py       EndogenousMotor · MotorContractError
    structure.py   WorldStructure · describe_world · is_nonworld
    seeds.py       SEED_WINDOW · LIVES_REQUIRED · consume_seeds · SeedLedger
    temporal.py    TemporalModel · PRIOR · OBSERVATION_INDEX · TemporalContractError
    life.py        ACQUISITION_STEPS · POST_STEPS · Life · Instruments · live
    arms.py        full · frozen · temporal_shuffled · StaticBitcount · audit_shuffle
    metrics.py     log_loss · brier_change · PrimaryMetricNotApplicable
    shadow.py      AnalyticShadow · teachability
    causal.py      CausalProbe · probe
    gates.py       los doce · identifiers/attributes/imported_modules · listas negras
    campaign.py    LifeOutcome · classify · read_life · run_campaign

scripts/
    medir_dependencia_accion.py     I(A;O'|O) por mundo · gemelo A/B

tests/
    test_level16_substrate.py · _temporal.py · _life.py · _arms.py
    _shadow_causal.py · _gates.py · _campaign.py          89 contratos

2358 líneas de código y tests.
```

---

# 13 · Lo que 1.7 puede reusar tal cual

| pieza | por qué sirve |
|---|---|
| `world.py` completo | física, parámetros heredados y cuarentena de flujos |
| `motor.py` | S0 es el mismo sustrato; su serialización ya está resuelta |
| `structure.py` · `seeds.py` | el predicado estructural y la regla de consumo no dependen de la capacidad |
| `life.py` | el ciclo adquirir/congelar/continuar es agnóstico del modelo |
| `metrics.py` | `log_loss` es el endpoint correcto también para `P(o'|o,a)` |
| `causal.py` | la intervención `M_T → M_0 → M_T` sirve para cualquier estado |
| `gates.py` · el escáner AST | `identifiers`, `attributes`, `imported_modules` y las listas negras |
| `AnalyticShadow` | **hay que extenderla** a `P(o'|o,a)`: la estacionaria sigue siendo uniforme |

**Lo que NO se reusa:** `temporal.py` es la capacidad de 1.6 y queda congelada.
Un decimal que condicione por acción necesita su propio módulo.

---

# 14 · Medición hacia adelante · lo que el mundo ofrece a un decimal que use la acción

Producida con `scripts/medir_dependencia_accion.py`, sin aprendiz.

```
D_W(mundo) = I(A_t ; O_{t+1} | O_t) = H(O'|O) − H(O'|O,A)
```

bajo `p_ref(o,a) = p_estacionaria(o) · ¼`, que es exactamente lo que S0 produce.

```
D_W        media 0.8447   sd 0.1223   mín 0.5623   máx 1.0678
I(O;O')    media 0.8536   ← lo que 1.6 tenía disponible
```

**La acción aporta tanta información sobre la observación siguiente como todo el
pasado sensorial.** No hace falta rediseñar el mundo. El aliasing cuesta poco:
`D_W / H(O'|C) ≈ 0.88`.

## 14.1 · Los estratos se invierten

```
             D_W      I(O;O')    razón
<=3 celdas  0.6684    0.2950     2.708
 >6 celdas  0.8853    0.9825     0.916
```

Los mundos que eran **adversarios** de 1.6 son los **favorables** de un decimal que
use la acción: en un bolsillo de dos celdas el pasado no dice nada pero el comando
lo dice casi todo. En los de 2 y 3 celdas `D_W = H(O'|C)` exactamente — sin
aliasing, cada celda tiene firma única.

> **La estratificación adversarial de 1.6 no se hereda.** Un decimal que reuse el
> criterio de mundos sin recalcular sus estratos estaría corriendo en el régimen
> fácil. Recalcular `D_W` por semilla **antes** de sellar.

## 14.2 · Un par A/B exacto, no aproximado

```
T_B(s'|s,a) = ¼ · Σ_b T_A(s'|s,b)      para toda a
```

Verificado sobre la física real:

```
I_B(A;O'|O)                0.000e+00   exacto
dinámica marginal          idéntica    np.allclose = True
I_A(A;O'|O) del gemelo     1.0678
```

Algebraicamente: `P_B(o'|o,a) = P_A(o'|o)` ∀a ⇒ `I_B = 0` por construcción; y
`Σ_a π(a)T_A = T_B` ⇒ misma cadena marginal ⇒ misma estacionaria. **No preserva
«tanta estructura marginal como sea posible»: preserva toda.** A y B comparten
topología, dinámica temporal marginal, estacionaria y variedad sensorial, y
difieren **sólo** en si la identidad del comando informa sobre la consecuencia.

---

# 15 · Lo que NO está decidido

Ninguna de estas es mía. Requieren adjudicación humana.

1. **Qué significa heredar `M_0` en un mundo nuevo.** Una tabla `P(o'|o)` aprendida
   en otro mundo no es baseline limpio para otra topología. Hay al menos dos
   ontologías —*capacidad heredada* vs *baseline experimental*— y no son la misma.
2. **Si la cobertura pasa a ser instrumento obligatorio** en todos los decimales
   futuros o se decide nivel por nivel.
3. **El presupuesto del decimal siguiente:** pendiente, saturado, o la curva
   completa como endpoint.
4. **Si `AN-2` (`FROZEN_MODEL_CHANGED` sin gate) se repara** o se deja como
   contrato de clase.
5. **Qué capacidades pertenecen al Nivel 2.** El Nivel 1 no se modifica para
   anticipar esa decisión.

---

# 16 · Reproducción exacta

```bash
# la suite completa · 89 contratos
python -m pytest tests/test_level16_substrate.py tests/test_level16_temporal.py \
  tests/test_level16_life.py tests/test_level16_arms.py \
  tests/test_level16_shadow_causal.py tests/test_level16_gates.py \
  tests/test_level16_campaign.py -q

# la campaña confirmatoria · ~2 segundos
python -c "from terrario.level16.campaign import run_campaign; \
r = run_campaign(); print(r.verdict, r.interval_lower)"

# la dependencia acción-consecuencia del mundo, sin aprendiz
python scripts/medir_dependencia_accion.py
```

```
digest de las 16 salidas   cca758237cc43131d08cae70aa9f39d6fe78fa09e26f891dc2f5dcabec04e86e
IC95 inferior              +0.680501
```

---

# 17 · Inventario de commits

```
9b0d39b  oráculo sellado, intacto
d0ce9f8  Enmienda 01 · consumo de semillas
8f8c85d  Enmienda 02 · parámetros del mundo
02b6e62  S0 + predicado estructural + consumo
42f7b1a  A1
ad99b74  vida / freeze / banco POST
c8f66f1  los cuatro brazos
9909fc2  K-SOMBRA + intervención causal
23903fb  los doce gates + fixtures negativas
5c54848  Enmienda 03 · clasificación
9625aaa  campaña
0503874  informe
3bfc4cf  auditoría de integridad + diez anomalías
b9c0b4d  cierre formal
4592576  mapa causal
0c9e3d1  crítica y backlog
ffe97e8  cierre de deuda del verificador
2b5c6e6  congelación
```

---

# 18 · El claim, y su frontera

**Permitido:**

> El Agente Nivel 1.6 produjo endógenamente su trayectoria motora y, a partir del
> flujo de observaciones consecutivas generado durante esa vida, adquirió una
> representación predictiva de la estructura temporal de su propio flujo sensorial.
> La competencia supera controles congelados y con temporalidad destruida, se
> aproxima al óptimo disponible y depende causalmente del estado interno aprendido.

**Siempre acompañado de:** `RÉGIMEN = EXPOSICIÓN SATURADA`.

**Prohibido:** detección de cambio, contingencia acción→efecto, causalidad sobre el
mundo, exploración dirigida, curiosidad, motivación, valor, búsqueda, objetivo,
memoria selectiva, descubrimiento autónomo, generalización entre mundos, agencia
fuerte.

**Y sobre todo:** 1.6 **no** es evidencia de un ser que aprende con pocos datos. Es
evidencia de algo anterior y necesario: cuando su propia vida le proporciona la
estructura suficiente, puede convertir esa experiencia en una expectativa temporal
interna correcta.

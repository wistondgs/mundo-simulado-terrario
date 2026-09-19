# Agente de Nivel 1 · especificación técnica

**Identificador técnico:** `AGENT_LEVEL_1_SENSORIMOTOR_CONTINGENCY_01`
**Rama de construcción:** `bench/causal-capability-01`, commit `de9a3ba`
**Rama activa:** `experiment/level1-reversal-plasticity-01`, desde `97e8300`

Ser nuevo. No es una capa sobre ningún organismo anterior; el linaje previo es
documentación histórica y no participa.

---

# 1 · Alcance

Lo que el ser tiene, y nada más:

```
un cuerpo en una rejilla · cuatro actos motores · cuatro bits de sentido
```

Deliberadamente **fuera**: energía, hambre, valencia, objetos, recursos,
recompensa, memoria episódica, planificación, búsqueda simulada, red neuronal.
Cualquiera de ellos sería una explicación alternativa del primer resultado.

La pregunta, entera:

$$
\boxed{\;\text{¿puede descubrir, por experiencia propia, qué efecto motor produce cada acto?}\;}
$$

---

# 2 · El mundo

`terrario/level1/world.py`

## 2.1 · Geometría

$$
\mathcal C \in \{0,1\}^{7\times 7},\qquad
0 = \text{libre},\quad 1 = \text{bloqueada}
$$

Borde siempre cerrado; interior de $5\times5$ con paredes independientes:

$$
\mathcal C_{ij} \sim \mathrm{Bernoulli}(0.25), \quad 1\le i,j\le 5
$$

Posición $p_t=(r_t,c_t)$, inicial uniforme sobre celdas libres (`world.py:74`).

## 2.2 · Vocabulario motor

`world.py:26`, con los mismos índices y deltas que el motor del mundo grande:

$$
\mathcal A=\{\text{UP}=0,\ \text{DOWN}=1,\ \text{LEFT}=2,\ \text{RIGHT}=3\}
$$

$$
\Delta(\text{UP})=(-1,0)\quad
\Delta(\text{DOWN})=(1,0)\quad
\Delta(\text{LEFT})=(0,-1)\quad
\Delta(\text{RIGHT})=(0,1)
$$

## 2.3 · Observación

`world.py:91`. Cuatro bits y nada más:

$$
o_t=\big(b_t^{0},b_t^{1},b_t^{2},b_t^{3}\big)\in\{0,1\}^4,
\qquad
b_t^{d}= \mathbb 1\big[\mathcal C_{\,p_t+\Delta(d)}=1\big]
$$

$$
|\mathcal O| = 2^4 = 16 \quad\text{(`world.py:46`, todas alcanzables)}
$$

**No** recibe: posición absoluta, geometría global, distancia, tiempo, ni la
regla que relaciona el bit con el desplazamiento.

## 2.4 · Transición

`world.py:101`

$$
p_{t+1}=
\begin{cases}
p_t+\Delta(a_t), & \mathcal C_{\,p_t+\Delta(a_t)}=0\\[2pt]
p_t, & \text{en otro caso}
\end{cases}
\qquad
y_t=\mathbb 1[p_{t+1}\neq p_t]
$$

## 2.5 · Experiencia elemental

`world.py:52`

$$
\xi_t=(o_t,\;a_t,\;y_t,\;o_{t+1})
$$

---

# 3 · Contrato físico · GATE 0

`world.py:122`

$$
\boxed{\;y_t = 1 - o_t[a_t]\;}
$$

En este mundo el bit sensorial de la dirección elegida determina exactamente si
el desplazamiento es posible. Se **cuenta** contra el mundo en cada transición de
adquisición (`measurement.py:69`), no se supone. Medido: **0 violaciones en
262 144 transiciones** (32 semillas × 8 192).

Si deja de cumplirse, el experimento no mide aprendizaje sino instrumentación
rota, y se detiene antes de analizar nada.

---

# 4 · Los seres

`terrario/level1/models.py`

Los dos usan **el mismo conteo Beta-Bernoulli** y **el mismo prior**. Difieren
sólo en sobre qué cuentan.

## 4.1 · Aprende por casos · `ContingencyTable` (`models.py:24`)

Una creencia por situación completa:

$$
(\alpha_{o,d},\beta_{o,d}),\qquad
\alpha^{(0)}=\beta^{(0)}=1
\quad\Rightarrow\quad
\hat P_0(y=1\mid o,d)=\tfrac12
$$

$$
\hat P(y=1\mid o,d)=\frac{\alpha_{o,d}}{\alpha_{o,d}+\beta_{o,d}}
\qquad\text{(`models.py:53`, NO escribe)}
$$

$$
\alpha_{o,d}\leftarrow\alpha_{o,d}+y,\qquad
\beta_{o,d}\leftarrow\beta_{o,d}+(1-y)
\qquad\text{(`models.py:67`)}
$$

Celdas: $|\mathcal O|\times|\mathcal A| = 16\times4 = \mathbf{64}$, independientes.

**Límite estructural, declarado antes de leer resultados:** un par nunca visto
devuelve el prior. Este ser **no puede generalizar**, sólo memorizar.

## 4.2 · Aprende por rasgos · `FactoredContingency` (`models.py:147`)

El mismo conteo sobre **rasgos** en vez de sobre casos. Dos almacenes:

$$
(\alpha_d,\beta_d)\quad\text{por dirección}
\qquad
(\alpha_{d,j,v},\beta_{d,j,v})\quad\text{por (dirección, posición del bit, valor)}
$$

Con $\ \mathrm{logit}(\alpha,\beta)=\log\alpha-\log\beta\ $ (`models.py:189`), la
combinación es suma de log-momios de Bayes ingenuo (`models.py:193`):

$$
\ell(o,d)=\mathrm{logit}(\alpha_d,\beta_d)
+\sum_{j=0}^{3}\Big[\mathrm{logit}(\alpha_{d,j,o_j},\beta_{d,j,o_j})-\mathrm{logit}(\alpha_d,\beta_d)\Big]
$$

$$
\hat P(y=1\mid o,d)=\sigma\big(\ell(o,d)\big)=\frac{1}{1+e^{-\ell(o,d)}}
$$

Actualización (`models.py:203`): con $\xi=(o,d,y)$ se incrementan el almacén base
de $d$ y los **cuatro** rasgos $(d,j,o_j)$.

Celdas: $4 + 4\cdot4\cdot2 = \mathbf{36}$.

**No se le entrega la regla.** Tiene los cuatro bits y debe descubrir que tres
son mudos, porque los datos hacen que sus log-momios se cancelen contra la base.

## 4.3 · Selección de acto

Idéntica en los dos (`models.py:81`, `models.py:215`):

$$
a^\star=\arg\max_{d\in\mathcal A}\hat P(y=1\mid o,d)
$$

Empates rotos uniformemente. Es lectura diagnóstica, no deseo: pregunta si lo
adquirido **puede usarse para elegir**, no si el ser quiere moverse.

---

# 5 · Los techos

## 5.1 · Techo externo · `TabularQ` (`models.py:99`)

Q-learning tabular. **No es nuestra arquitectura**: contesta si un método
estándar y probado resuelve esta tarea con este instrumento.

$$
Q(o,a)\leftarrow Q(o,a)+\eta\Big[y+\gamma\max_{a'}Q(o',a')-Q(o,a)\Big]
$$

$$
\eta=0.20,\qquad \gamma=0.90,\qquad Q^{(0)}\equiv 0,\qquad r_t=y_t
$$

Indexa por observación completa: **también es una tabla**.

## 5.2 · Techo físico · `oracle_policy` (`models.py:135`)

No aprende; conoce la física. Elige uniformemente entre las direcciones libres.
Por construcción alcanza $1.0$ exacto en toda situación con salida.

---

# 6 · Los controles

**Congelado** — `ContingencyTable(frozen=True)`. `observe` es no-op
(`models.py:67`); `predict` devuelve $1/2$ siempre; como los cuatro valores
empatan, `act` es **exactamente una política aleatoria uniforme**. Bloquea la
escritura, no el cálculo.

**Permutado** — la misma cantidad de experiencia y la misma marginal de
resultados, con la correspondencia destruida:

$$
\{y_t\}\ \longrightarrow\ \{y_{\sigma(t)}\},\qquad
\sigma \text{ uniforme, semilla } \text{seed}+10\,000\,003
$$

Recibe los mismos $(o_t,a_t)$ con los resultados barajados globalmente.

---

# 7 · La medición

`terrario/level1/measurement.py`

## 7.1 · Parámetros

`measurement.py:51`

```
grid_size 7 · wall_probability 0.25
train_layouts 128 · train_steps_per_layout 64      → 8 192 transiciones/semilla
test_layouts 128  · test_positions_per_layout 32
repetitions 32 · prior_alpha 1.0 · prior_beta 1.0
q_learning_rate 0.20 · q_discount 0.90
```

## 7.2 · Actividad motora basal

`measurement.py:69`. Actos uniformes, sin objetivo ni recompensa:

$$
a_t\sim\mathcal U(\mathcal A),\qquad P(a_t=a)=\tfrac14
$$

No es motivación. Es lo que genera experiencia antes de que exista nada que la
dirija. El flujo es **independiente de la política**, así que todos los brazos
consumen exactamente la misma experiencia.

## 7.3 · Dos bancos, y no son el mismo

`measurement.py:94`. Construidos del mundo, nunca de la historia, con semilla
$\text{seed}+20\,000\,003$ — mundos disjuntos de los de adquisición.

| banco | `require_exit` | contenido |
|---|---|---|
| predicción | `False` | todas las situaciones |
| conducta | `True` | sólo las que tienen salida |

**Por qué separados:** la situación encerrada $(1,1,1,1)$ es la más rara y la
peor aprendida. Filtrarla del Brier lo baja de `0.000826` a `0.000070` —
**por selección, no por conocimiento**.

## 7.4 · Predicción

`measurement.py:126`. Contrafactual: se evalúan las cuatro direcciones **sin
ejecutarlas**, contra lo que la física produciría. La medida es pasiva.

$$
BS=\frac{1}{4N}\sum_{o\in\mathcal B}\ \sum_{d\in\mathcal A}
\Big(\hat P(y=1\mid o,d)-\big(1-o[d]\big)\Big)^2
$$

Referencias **analíticas**, no estimadas:

$$
\hat P\equiv\tfrac12\ \Rightarrow\ BS=0.25\ \text{exacto}
\qquad\qquad
\hat P\equiv y\ \Rightarrow\ BS=0
$$

## 7.5 · Conducta

`measurement.py:150`. Un acto por situación, **las mismas situaciones para todo
brazo**, y el azar de la política sale de un generador propio:

$$
R_{\text{move}}=\frac{1}{|\mathcal B|}\sum_{o\in\mathcal B}\mathbb 1\big[o[\pi(o)]=0\big]
$$

`measurement.py:161` conserva la variante por trayectoria propia, **sólo** para
poder informar la diferencia.

## 7.6 · Inferencia

`PairedResult` de `terrario/lab/causal_bench.py` — el mismo instrumento del resto
del proyecto, para que los intervalos sean comparables entre experimentos.

Bootstrap pareado por semilla, $20\,000$ remuestreos, semilla $20\,260\,918$,
percentiles $2.5$ y $97.5$. El gate exige $\ \mathrm{IC}_{95\%}^{\text{inf}}>0$,
nunca la media sola.

---

# 8 · El experimento

`scripts/level1_sensorimotor_contingency.py`

```
BASE_SEED      20260919        semillas = BASE_SEED + i,  i = 0 … n−1
EVAL_OFFSET    20 000 003      banco de evaluación
SHUFFLE_OFFSET 10 000 003      permutación del control negativo
```

## 8.1 · El discriminador

`script:57`. Cuatro de las dieciséis, **retiradas del entrenamiento**:

$$
\mathcal H=\{(1,0,0,0),\ (0,1,0,0),\ (1,1,0,0),\ (0,0,1,1)\}
$$

Sin esto el gate de generalización sólo puede aprobar por ausencia de prueba: con
$8\,192$ transiciones las dieciséis situaciones se ven todas. Las cuatro
retiradas tienen salida, así que sirven también para medir conducta.

## 8.2 · Flujo por semilla

`script:87`

1. Actividad motora basal → $8\,192$ transiciones, contando violaciones.
2. Con las dieciséis disponibles: casos, rasgos y techo externo consumen el flujo.
3. El control permutado consume los mismos $(o,a)$ con resultados barajados.
4. **Discriminador:** casos, rasgos y techo externo **parciales**, entrenados
   saltándose toda transición cuya observación esté en $\mathcal H$.
5. Evaluación sobre los dos bancos.

---

# 9 · Los gates

| gate | definición | contraste |
|---|---|---|
| **0** integridad física | $0$ violaciones **y** oráculo $=1.0$ exacto | — |
| **1** adquisición | $BS_{\text{congelado}}-BS_{\text{casos}}$ | IC inf $>0$ |
| **2** dependencia causal | $BS_{\text{permutado}}-BS_{\text{casos}}$ | IC inf $>0$ |
| **3** generalización | $BS^{\mathcal H}_{\text{casos}}-BS^{\mathcal H}_{\text{rasgos}}$ | IC inf $>0$ |
| **4** uso conductual | $R_{\text{casos}}-R_{\text{congelado}}$ | IC inf $>0$ |
| **5** control positivo | $R_{\text{td}}-R_{\text{congelado}}$ | IC inf $>0$ |
| **6** uso de la regla | $R^{\mathcal H}_{\text{rasgos}}-R^{\mathcal H}_{\text{td}}$ | IC inf $>0$ |

Estado: `FALLO_DE_MUNDO_O_INSTRUMENTO` si cae el 0 · `CONTROL_POSITIVO_FALLIDO`
si cae el 5 · `PASA` si todos · `FALLA` en otro caso.

---

# 10 · Resultados medidos

**Condiciones:** 32 semillas desde `20260919`, $128\times64$ pasos por semilla,
mundos de prueba disjuntos, `OMP_NUM_THREADS=2`.

## 10.1 · Con las dieciséis situaciones disponibles

| brazo | Brier | conducta | trayectoria propia |
|---|---|---|---|
| aprende por casos | `0.000826` | `1.0000` | `1.0000` |
| aprende por rasgos | `0.000001` | `1.0000` | — |
| congelado | `0.250000` | `0.6029` | `0.6036` |
| permutado | `0.243285` | `0.6150` | `0.2682` |
| td (techo externo) | — | `1.0000` | — |
| oráculo (techo físico) | — | `1.0000` | — |

## 10.2 · El discriminador — sólo sobre las cuatro retiradas

| brazo | Brier | conducta |
|---|---|---|
| aprende por casos | **`0.250000`** | `0.6646` |
| aprende por rasgos | **`0.000021`** | **`1.0000`** |
| td (techo externo) | — | `0.6646` |
| congelado | — | `0.6646` |
| oráculo (techo físico) | — | `1.0000` |

## 10.3 · Contrastes pareados · $n=32$

```
Brier: congelado − casos           +0.249174  [+0.248410, +0.249783]   100%
Brier: permutado − casos           +0.242459  [+0.240254, +0.244646]   100%
Brier retirado: casos − rasgos     +0.249979  [+0.249977, +0.249979]   100%
conducta: casos − congelado        +0.397074  [+0.393852, +0.400292]   100%
conducta: td − congelado           +0.397074  [+0.393852, +0.400292]   100%
conducta retirada: rasgos − td     +0.335380  [+0.330807, +0.339868]   100%
```

GATE 0: `0` violaciones en `262 144` transiciones, oráculo `1.000000`.
**Estado: PASA**, los siete.

## 10.4 · Los tres hechos

1. **Sobre lo retirado, casos y techo externo y congelado dan el mismo número:
   el azar.** Q tabular indexa por observación completa, luego también es una
   tabla, y falla por la misma razón estructural.
2. **Rasgos alcanza el techo físico exacto** sobre situaciones que nunca vivió.
3. **Con las dieciséis disponibles los cuatro de arriba empatan en `1.0000`.** La
   tarea no los separa; sólo el discriminador los separa.

---

# 11 · Interpretación permitida

**Autorizado, exactamente esto:**

> La experiencia sensorimotora produjo un cambio interno persistente que permite
> predecir y usar mejor las consecuencias de los propios actos, y **lo adquirido
> transfiere a situaciones nunca vividas**.

**No autorizado:**

- que el ser **inventara** la descomposición en rasgos — se le dio; lo que
  descubrió es cuál rasgo gobierna cada acto;
- navegación, orientación, motivación, regulación, flexibilidad cognitiva,
  aprendizaje continuo, metaaprendizaje, inteligencia;
- que el método probado sea inferior en general — lo es **en esta tarea**, por
  ser una tabla.

**Límites del alcance:** dieciséis situaciones, cuatro actos, mundo
determinista, sin ruido sensorial, sin consecuencias diferidas.

---

# 12 · Defectos hallados durante la construcción

Los cuatro se midieron; ninguno se dedujo.

| defecto | efecto medido | reparación |
|---|---|---|
| un banco reutilizado para dos medidas | Brier `0.000826` → `0.000070` por selección | dos bancos, `require_exit` |
| `predict` insertaba la celda que leía | ningún número movido; toda huella del estado contaminada | consulta con valor por defecto |
| conducta sobre trayectoria propia | el control negativo atrapado: `0.2682` frente a `0.6150` | situaciones iguales para todo brazo |
| gate de generalización vacío | sólo podía aprobar por ausencia de prueba | retirar cuatro observaciones |

El tercero tiene mecanismo: una política **determinista** con conocimiento
equivocado elige una dirección bloqueada, no se mueve, vuelve a ver lo mismo y
queda atrapada. El azar no se atasca porque vuelve a sortear. Medido con los
cinco brazos sobre las mismas $8\,015$ situaciones, **cambia un solo brazo**; los
otros cuatro coinciden hasta la cuarta cifra.

---

# 13 · Ficheros

```
terrario/level1/__init__.py                    15
terrario/level1/world.py                      130   rejilla, 4 bits, contrato físico
terrario/level1/models.py                     223   casos, rasgos, techo externo, oráculo
terrario/level1/measurement.py                182   bancos, Brier, conducta
scripts/level1_sensorimotor_contingency.py    257   el experimento y sus 7 gates
tests/test_level1_contingency.py              212   13 contratos
                                            -----
                                            1 019   líneas
```

**Dependencia externa única:** `from terrario.lab.causal_bench import PairedResult`.
Es un instrumento estadístico compartido, no una atadura al linaje histórico.
`terrario/level1/` no importa nada fuera de sí mismo salvo `numpy`.

## 13.1 · Los trece contratos

`tests/test_level1_contingency.py`

```
27   el bit sentido decide el desplazamiento exactamente          (GATE 0)
37   los deltas coinciden con el vocabulario del motor
52   el predictor ignorante puntúa exactamente 0.25
63   congelar bloquea la escritura, no el cálculo
72   el oráculo alcanza el techo exacto
81   un par nunca visto devuelve el prior y nada más
99   los dos bancos difieren exactamente en las encerradas
110  toda configuración sensorial es alcanzable
119  la sonda no deja huella en el modelo
133  reubicar nunca cae en una pared
148  rasgos llega a una situación no vista y casos no
174  ninguno de los tres escribe al predecir
197  el techo externo también es una tabla
```

---

# 14 · Reproducción exacta

```bash
cd /home/wis/causal-bench-01
PY="/home/wis/mundo simulado terrario/.venv/bin/python"

# el experimento completo, 32 semillas, ~1 minuto
OMP_NUM_THREADS=2 "$PY" -u scripts/level1_sensorimotor_contingency.py --semillas 32

# los trece contratos
OMP_NUM_THREADS=2 "$PY" -m pytest tests/test_level1_contingency.py -q --no-header -p no:cacheprovider

# la auditoría: parámetros, pasividad, conjunto de fallos, experimento
OMP_NUM_THREADS=2 "$PY" .claude/skills/run-terrario/checker.py all --semillas 4
```

Entorno verificado: `Python 3.12.3`, `numpy 2.5.2`, `torch 2.5.1+cu121`,
`pytest 9.1.1`. El `python3` del sistema **no** sirve: no tiene `numpy`.

`OMP_NUM_THREADS=2` no es opcional: sin él torch abre un hilo por núcleo y por
proceso.

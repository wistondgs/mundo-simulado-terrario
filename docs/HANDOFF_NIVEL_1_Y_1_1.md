# Handoff · Agente de Nivel 1 y Nivel 1.1

**Destinatario:** cualquier asistente o colaborador que vaya a trabajar sobre este
linaje. **Estado a 2026-09-19:** Nivel 1.0 cerrado, Nivel 1.1 cerrado y verificado.
Rama `experiment/level1-reversal-plasticity-01`, HEAD `ef67ee5`, árbol limpio,
46 contratos verdes.

---

# 0 · Lee esto antes de escribir una sola línea

Este linaje ya se descarriló una vez porque un colaborador **añadió capacidades que
no pertenecían al nivel**. El resultado fue medio año sin avance medible: cada
corrida mezclaba varias adquisiciones a la vez y ninguna era atribuible.

La regla que lo impide es una sola, y no es negociable:

> **Un decimal, una adquisición.** `1.0 → 1.1 → 1.2 …`, exactamente **una**
> capacidad nueva por decimal, y el nivel anterior **congelado**, no reescrito.

De ahí se siguen tres prohibiciones operativas:

1. **No se modifica un nivel cerrado para anticipar el siguiente.** Si el 1.2
   necesitara algo del 1.1, se forkea; no se edita.
2. **Quién decide qué capacidad entra en el decimal siguiente es el humano (Wis),
   no el asistente.** Proponer está bien; implementar sin adjudicación, no.
3. **No se «completa» trabajo que fue cerrado deliberadamente.** Hay un
   Experimento 2 construido y sin correr (§7). Está así a propósito.

Y una regla epistémica que gobierna todo informe de este repositorio: cada
afirmación se clasifica como **hecho medido** (hay un número y el guion que lo
produjo), **hecho de código** (hay `fichero:línea`) o **inferencia**. Las
inferencias se marcan como tales. Nada se infiere y se reporta como medido.

---

# 1 · El mundo · común a 1.0 y 1.1

Compartido por los dos niveles, byte a byte: `terrario/level11/world.py` es copia
literal de `terrario/level1/world.py` y hay un contrato que lo verifica
(`tests/test_level11_lineage.py`).

**Geometría.** Rejilla con paredes. **Vocabulario motor:** cuatro actos,
`U` `D` `L` `R`, con sus desplazamientos.

**Observación:** cuatro bits, uno por dirección — *«¿hay pared inmediatamente en
esa dirección?»*. Espacio completo: `2⁴ = 16` situaciones sensoriales, **todas
alcanzables** (hay contrato que lo verifica).

**Transición:** `Transition(observation, direction, moved, next_observation)`.

**Contrato físico · GATE 0:**

```
physics_contract(o, d) = 1 − o[d]
```

Es decir: el ser se mueve **si y sólo si** el bit sentido en esa dirección es
`0`. Determinista, sin ruido, sin consecuencia diferida. Cualquier violación de
esto es `FALLO_DE_MUNDO_O_INSTRUMENTO` y detiene todo — nunca se reinterpreta
como resultado.

Medido: `0` violaciones en `262 144` transiciones; oráculo `1.000000` exacto.

---

# 2 · Nivel 1.0 · contingencia sensorimotora

**La adquisición:** aprender la consecuencia de los propios actos —
`P(moverse | observación, acto)` — por experiencia, sin que nadie se la diga.

## 2.1 · Los dos seres

Ambos son Beta-Bernoulli con prior `Beta(1,1)`; la predicción es la media
posterior `α/(α+β)`.

| ser | indexación | acumuladores |
|---|---|---|
| **aprende por casos** `ContingencyTable` (`models.py:24`) | observación completa × acto | 64 |
| **aprende por rasgos** `FactoredContingency` (`models.py:147`) | base por acto + (bit, valor) por acto | 4 + 32 = 36 |

La composición de rasgos es **log-momio naive-Bayes**:

```
ℓ = L_d + Σ_j ( L_{d,j,o_j} − L_d )        p = σ(ℓ)
```

**La descomposición en rasgos se le dio al ser; no la inventó.** Lo que descubrió
es **qué rasgo gobierna cada acto**. Esto es una limitación declarada, no un
detalle.

## 2.2 · Techos y controles

- **Techo externo** `TabularQ` (`models.py:99`) — aprendizaje por refuerzo tabular.
- **Techo físico** `oracle_policy` (`models.py:135`) — conoce la física; `1.0000`.
- **Congelado** — mismo ser, escritura bloqueada, cálculo intacto.
- **Permutado** — la asociación acto↔consecuencia barajada.

## 2.3 · El discriminador · lo que hace falsable al gate 3

Con las 16 situaciones disponibles, **casos, rasgos, techo externo y oráculo
empatan los cuatro en `1.0000`**. La tarea no los separa. Sin un discriminador,
el gate de generalización sólo podía aprobar por ausencia de prueba.

El discriminador: **retirar cuatro observaciones del entrenamiento** y medir sólo
sobre ellas.

## 2.4 · Resultados medidos · 32 semillas desde `20260919`, 128×64 pasos

Con las dieciséis disponibles:

| brazo | Brier | conducta |
|---|---|---|
| aprende por casos | `0.000826` | `1.0000` |
| aprende por rasgos | `0.000001` | `1.0000` |
| congelado | `0.250000` | `0.6029` |
| permutado | `0.243285` | `0.6150` |

**Sobre las cuatro retiradas** — aquí sí se separan:

| brazo | Brier | conducta |
|---|---|---|
| aprende por casos | `0.250000` | `0.6646` |
| **aprende por rasgos** | **`0.000021`** | **`1.0000`** |
| techo externo (TD) | — | `0.6646` |
| congelado | — | `0.6646` |
| oráculo | — | `1.0000` |

Contrastes pareados, `n = 32`, todos al `100 %`:

```
Brier: congelado − casos           +0.249174  [+0.248410, +0.249783]
Brier: permutado − casos           +0.242459  [+0.240254, +0.244646]
Brier retirado: casos − rasgos     +0.249979  [+0.249977, +0.249979]
conducta: casos − congelado        +0.397074  [+0.393852, +0.400292]
conducta: td − congelado           +0.397074  [+0.393852, +0.400292]
conducta retirada: rasgos − td     +0.335380  [+0.330807, +0.339868]
```

**Los siete gates: `PASA`.**

**El hecho que importa:** sobre lo retirado, *casos*, *techo externo* y
*congelado* dan **el mismo número, el azar**. El techo externo tabular falla por
la misma razón estructural que casos: también es una tabla. Sólo rasgos alcanza
el techo físico exacto en situaciones que nunca vivió.

## 2.5 · Afirmación permitida para 1.0

> La experiencia sensorimotora produjo un cambio interno persistente que permite
> predecir y usar mejor las consecuencias de los propios actos, y **lo adquirido
> transfiere a situaciones nunca vividas**.

**No autorizado:** que el ser inventara la descomposición en rasgos; navegación,
orientación, motivación, regulación, flexibilidad cognitiva, aprendizaje continuo,
metaaprendizaje, inteligencia; ni que el método de casos sea inferior *en general*
— lo es **en esta tarea**, por ser una tabla.

---

# 3 · El fork · por qué existe el 1.1 y no un 1.0 revisado

Las semillas del Nivel 1.0 **están contaminadas**: sus resultados fueron leídos
durante la construcción, así que ya no pueden sostener una predicción
preregistrada. Una en concreto (`31415926`) se quemó verificando el mecanismo de
reversión y quedó registrada como Enmienda 1.

Por eso el 1.1 **no es una capa sobre el 1.0**: es un linaje nuevo con espacio de
semillas propio y verificadamente disjunto (`70000019 … 70000026`, con imágenes
bajo desplazamientos `+20 000 003` para el banco y `+10 000 003` para el barajado).

`terrario/level11/{world,models,measurement}.py` son **copia literal** del 1.0. Un
contrato de linaje lo comprueba: si alguien edita el cuerpo del 1.1, el test cae.

---

# 4 · Nivel 1.1 · orientación direccional

**La adquisición nueva, y es exactamente una:** una **señal direccional externa**
`g_t`, que el ser debe aprender a interpretar y **combinar con el conocimiento
corporal que ya tenía**, para elegir `a_t` a partir de `(o_t, g_t)`.

## 4.1 · Lo que impide el atajo

La señal llega como **token opaco** — `C0 C1 C2 C3` — y el significado vive en el
experimento (`CueSemantics`), no en el token. Sin esto, «cue == acción» resolvería
la tarea sin aprender nada. `g_t` es uniforme e independiente, con **su propio
RNG**, separado del RNG del mundo y del del barajado.

## 4.2 · La composición

```
J(o, g, a) = B(o, a) · Q(g, a)
```

`B` es el cuerpo FEATURES del 1.0, **congelado**. `Q(g,a)` es la única estructura
nueva y la única que cambia durante el 1.1.

**El congelado es estructural, no una bandera:** el cuerpo entrenado pasa a un
envoltorio `FrozenFactoredBody` que **no tiene método `observe`**. El método que
no existe no se puede llamar por descuido. Verificado: huella del cuerpo idéntica
antes y después en las ocho realizaciones.

**La factorización la suministramos nosotros.** El organismo no la descubrió. Es
una limitación declarada, igual que la descomposición en rasgos del 1.0.

## 4.3 · Los estratos · por qué la métrica primaria es la balanceada

Las 256 tripletas `(o, g, a)` se parten en tres:

- **A** — el acto que la señal indica, y está **libre** · 32 casos
- **B** — la señala y está **bloqueada** · 32 casos
- **C** — cualquier otro acto · 192 casos

`BS_balanced = (A + B + C) / 3`.

**Y hay una razón medida para no reportar el total.** En el total, `BODY-ONLY`,
`CUE-ONLY`, `FROZEN` y **un predictor constante que dice siempre cero** empatan
los cuatro en `0.125`, con perfiles de fallo **opuestos**: `CUE-ONLY` es perfecto
en A y catastrófico en B (`0.973`); `SIEMPRE-CERO` es exactamente lo inverso
(`1.000` en A). El promedio los cancela. La balanceada los separa: `0.125` contra
`0.333`.

## 4.4 · Resultados medidos · 8 semillas, `N_ORIENTATION = 2048`

```
brazo            total       A       B       C  balanced  oráculo       Δ
COMPOSITE       0.0001   0.000   0.000   0.000     0.000    0.000  +0.000
BODY-ONLY       0.1249   0.250   0.000   0.125     0.125    0.125  +0.000
CUE-ONLY        0.1218   0.000   0.973   0.000     0.324    0.333  −0.009
FROZEN          0.1249   0.250   0.000   0.125     0.125    0.125  +0.000
SHUFFLED        0.0957   0.564   0.000   0.034     0.199        —       —
JOINT-TABLE     0.0781   0.070   0.087   0.078     0.078        —       —
SIEMPRE-CERO    0.1250   1.000   0.000   0.000     0.333    0.333  +0.000
IGNORANTE       0.2500   0.250   0.250   0.250     0.250    0.250  +0.000
```

**La conducta no prueba integración, y estaba previsto.** `R_align`:
`COMPOSITE 1.0000` y `CUE-ONLY 1.0000` — **empatan exactamente**. Quien conoce la
señal acierta siempre donde la dirección señalada está libre, sepa o no si lo
está.

**Lo que prueba integración es el estrato B:** `COMPOSITE 0.000` contra
`CUE-ONLY 0.973`. Ahí el cuerpo es lo único que puede saber que el movimiento
señalado no es realizable.

**Probe 2×2 · intervención causal por situación** (variar `g` con `o` fijo, y al
revés; sin promedios ni intervalos):

```
brazo           sensib. cue   sensib. cuerpo
COMPOSITE             0.972            0.984
BODY-ONLY             0.000            0.499     ← ciego a la señal
CUE-ONLY              0.973           −0.000     ← ciego al cuerpo
```

**Holdout · 16 pares `(o,g)` nunca vistos juntos:** `COMPOSITE 0.000` ·
`FROZEN 0.125` · `SHUFFLED 0.206` · `JOINT-TABLE 0.250` (su prior: no tiene celda).

**Y esto está determinado por la arquitectura, no descubierto.** Ni `B(o,a)` ni
`Q(g,a)` indexan el par `(o,g)`, así que retirar combinaciones no le quita nada a
ninguno. Por eso la **fixture de factorización falsa** es obligatoria: sin ella el
gate composicional no puede rechazar nada. Existe, y funciona: con el significado
del cue dependiendo de la observación, `COMPOSITE` se degrada **por un factor de
veinte** y la tabla conjunta gana.

**Integridad:**

```
cobertura informativa mínima   46   (criterio ≥ 30)
cuerpo intacto en las 8        True
violaciones del contrato        0
fugas del holdout               0
mayor desviación del oráculo   0.0085   (tolerancia 0.020)
```

**`LEVEL11_STATUS = VERIFIED`.**

## 4.5 · Qué clase de resultado es · dicho sin adorno

**Esto no fue un experimento confirmatorio.** Antes de escribir código, cada gate
se calculó en cerrado y ninguno tenía resultado incierto. Correr 32 semillas con
bootstrap habría establecido que `0.0000 < 0.1250`. La pregunta que sí tenía
sentido era: **¿reproduce la implementación el mecanismo que diseñamos?** El
oráculo se selló en `docs/LEVEL11_ORACULO_PREREGISTRADO.md` **antes** de existir
el experimento.

**La adquisición nueva son menos de cinco bits:** cuál de cuatro comandos
corresponde a cada uno de cuatro tokens, `log₂(4!) = 4.58`. Frente a los 36
acumuladores del cuerpo, es diminuta. Eso fija de qué clase es el hito: **de
integración, no de descubrimiento**.

Las 32 semillas y el bootstrap quedan reservados para el primer decimal donde
exista una pregunta cuya respuesta **no podamos calcular antes de ejecutar el
organismo**.

## 4.6 · Afirmación permitida para 1.1

> El agente aprendió a utilizar una señal direccional externa y la combinó con su
> conocimiento sensorimotor previo para seleccionar movimientos compatibles con
> esa señal cuando eran físicamente realizables.

**Y NO «conducta adaptativa».** El corpus lo prohíbe explícitamente: Ashby rechaza
«responde correctamente a un estímulo» como definición de adaptación porque
*«no tiene significado "correctamente" salvo que signifique conformarse a lo que
el experimentador cree que el animal debería hacer»* (`R-HEA-014-001`). `R_align`
es **cumplimiento de una correspondencia especificada por el experimentador**, no
adaptación.

**Tampoco:** navegación, orientación con objetivo, búsqueda de rutas, memoria
espacial, representación de distancia, mapa, motivación, planificación, ni
cognición espacial general.

---

# 5 · Los defectos que se encontraron construyendo

No son anécdotas: son el método. Cada uno se **midió**, ninguno se dedujo, y cada
uno se delató por un patrón que conviene saber reconocer.

## Nivel 1.0

| defecto | efecto medido | cómo se delató |
|---|---|---|
| un banco reutilizado para dos medidas | Brier `0.000826 → 0.000070` **por selección** | el número mejoraba sin que el ser mejorara |
| `predict` insertaba la celda que leía | ningún número movido; **toda huella del estado contaminada** | la sonda modificaba lo sondeado |
| conducta medida sobre trayectoria propia | control negativo atrapado: `0.2682` frente a `0.6150` | el control **peor que el azar** |
| gate de generalización vacío | sólo podía aprobar por ausencia de prueba | los cuatro brazos empataban en `1.0000` |

El tercero tiene mecanismo: una política **determinista** con conocimiento
equivocado elige una dirección bloqueada, no se mueve, vuelve a ver lo mismo y
queda atrapada. El azar no se atasca porque vuelve a sortear. Medido con los cinco
brazos sobre las mismas `8 015` situaciones, **cambia un solo brazo**; los otros
cuatro coinciden hasta la cuarta cifra.

## Nivel 1.1

**El control negativo no era un control.** `SHUFFLED` daba `0.0001` contra
`0.0001` de `COMPOSITE`, y `R_align 1.0000` los dos. Yo barajaba la señal **junto
con su semántica**: un reetiquetado consistente, no un desacople. Un control que
empata con lo que controla es como se delató. La corrección, en `train_orientation`:

```python
referencia = semantics.direction_of(e.cue)      # el cue ORIGINAL, no el barajado
q.observe(cue_vista, e.action, moved=e.moved, physical=e.physical,
          semantics_direction=referencia if e.moved and e.physical is not None else None)
```

**`R_align` se muestreaba donde se puede calcular.** El oráculo promedia el
desempate y la implementación lo sorteaba: `0.5000` frente a una esperanza de
`0.4688`. La verificación habría levantado un `INTEGRATION_MODEL_MISMATCH`
**falso contra su propio oráculo**. Reparado con `alignment_rate_expected`, en
cerrado.

**El umbral de la factorización falsa lo había elegido yo:** `COMPOSITE` se
degradaba a `0.0469` contra un `0.05` inventado. Bajarlo a `0.04` habría sido
ajustar el test al resultado. Ahora compara `COMPOSITE` **consigo mismo** bajo
factorización verdadera: un factor, no un número.

**Y una corrección del informe por la propia corrida.** Dije que `SHUFFLED` cae al
azar, con base en una sola semilla donde dio `0.2500`. Sobre las ocho da `0.4531`,
y es lo correcto: barajar destruye el conocimiento de la señal pero **conserva el
cuerpo**, así que su conducta debe tender a la de `BODY-ONLY` (`0.4688`), no al
azar. El daño se ve en la predicción: estrato `A` en `0.564`, que es exactamente
`(1 − 0.25)²` con `Q` colapsada a su marginal de `0.25`.

## La clase de defecto que más veces apareció

Un **verificador cuyo caso degenerado es aprobar**. Tres ejemplares:

- el parser de la suite hacía `line.split(" ")[0].removeprefix("FAILED ")` — en ese
  orden registraba la cadena literal `"FAILED"`, y aprobaba cualquier cosa;
- tres guardas que escaneaban texto **cazaban su propia documentación** (reparadas
  recorriendo el AST: los comentarios no son nodos);
- el panel de campaña pintaba **«Viva»** con cero datos, porque `heartbeat`
  ausente daba `NaN` y `NaN > x` es falso para todo `x`.

**Regla:** todo verificador necesita una fixture negativa que lo haga fallar. Si no
puedes construirla, el verificador no verifica.

---

# 6 · Lo que está congelado · no tocar

- **`terrario/level1/`** — Nivel 1.0, cerrado. No se edita.
- **`terrario/level11/{world,models,measurement}.py`** — copia literal del 1.0,
  con contrato de linaje que lo comprueba.
- **El cuerpo entrenado dentro del 1.1** — sin método `observe`, por diseño.
- **Hashes protegidos y fixtures históricas** — no se regeneran.
- **Semillas ya usadas** — `20260919…` (1.0), `31415926` (quemada),
  `70000019…70000026` (1.1). Un decimal nuevo estrena espacio propio y disjunto.
- **Commits `854f8a1` y `8ee0e68`** — no se integran.
- **Los cinco fallos históricos de la suite** — no se reparan aquí.
- **El worktree `agent_composition`** — WIP ajeno, no se toca.

---

# 7 · Lo que está construido y NO se corrió · a propósito

**Experimento 2 · reversión** (`LEVEL1-SENSORIMOTOR-REVERSAL-01`).
`terrario/level1/reversal.py`, 568 líneas: `MAPPING_A/B`, `phased_babbling`,
`audit_mapping_switch`, `audit_freeze_control`, `EMATable`, referencias
analíticas, `FLOOR_TOLERANCE = 1e-9`. Preregistro sellado en
`docs/REV_PREREGISTRO_01.md`. Siete de sus 26 contratos están escritos; **quedan
19** (T01–T06, T08, T10–T16, T18, T19, T21, T22, T26).

**Wis cerró el Nivel 1 sin correrlo.** No se retoma sin que él lo diga. El código
queda como está: ni se borra ni se completa.

Piezas de método que ese preregistro dejó y conviene no reinventar:

- **Separación de orden de eventos:** `layout_refresh → snapshot → mapping_switch →
  fingerprint → freeze_control → primera transición B`. Sirve para probar que dos
  intervenciones son de **una sola variable** cada una.
- **Dos huellas distintas:** `statistics_digest` (sin la bandera de congelado) y
  `learner_digest` (con ella).
- **Paridad de flujo por SHA-256** del stream de babbling motor, que es
  independiente de la política.
- **Suelo analítico como contrato de implementación**, con `FLOOR_VIOLATED` como
  condición de parada — no como resultado a interpretar.

---

# 8 · Lo que NO está decidido

- **Qué capacidad es el Nivel 1.2.** Decisión de Wis, exclusivamente.
- **Cómo debe aprenderse internamente una capacidad nueva** — en el 1.1 se dejó
  deliberadamente sin decidir hasta tener la especificación.
- **Si el Experimento 2 se corre alguna vez.**

---

# 9 · Reproducción exacta

```bash
cd /home/wis/causal-bench-01
PY="/home/wis/mundo simulado terrario/.venv/bin/python"

# Nivel 1.0 · experimento completo, 32 semillas, ~1 minuto
OMP_NUM_THREADS=2 "$PY" -u scripts/level1_sensorimotor_contingency.py --semillas 32

# Nivel 1.1 · verificación de integración, 8 semillas
OMP_NUM_THREADS=2 "$PY" -u scripts/level11_integration_verification.py

# los 46 contratos
OMP_NUM_THREADS=2 "$PY" -m pytest \
  tests/test_level1_contingency.py tests/test_level1_reversal.py \
  tests/test_level11_lineage.py tests/test_level11_orientation.py \
  tests/test_energy_ceiling.py -q --no-header -p no:cacheprovider

# el comprobador: parámetros, pasividad, conjunto de fallos, experimento
OMP_NUM_THREADS=2 "$PY" .claude/skills/run-terrario/checker.py all --semillas 4
```

Entorno verificado: `Python 3.12.3`, `numpy 2.5.2`, `torch 2.5.1+cu121`,
`pytest 9.1.1`. El `python3` del sistema **no** sirve: no tiene `numpy`.
`OMP_NUM_THREADS=2` **no es opcional**: sin él torch abre un hilo por núcleo y por
proceso.

---

# 10 · Inventario

```
terrario/level1/                  1 118 líneas   Nivel 1.0 + reversión sin correr
  world.py            130   rejilla, 4 bits, contrato físico
  models.py           223   casos, rasgos, techo externo, oráculo
  measurement.py      182   bancos, Brier, conducta
  reversal.py         568   Experimento 2, construido y no ejecutado

terrario/level11/                 1 413 líneas   Nivel 1.1
  world.py / models.py / measurement.py   copia literal del 1.0
  cue.py               83   token opaco C0..C3 y su semántica
  orientation.py       78   Q(g,a); no escribe nada si moved == 0
  body.py              80   FrozenFactoredBody — sin método observe
  agent.py             79   predict = cuerpo × orientación
  metrics.py          155   Brier estratificado, R_align, probe 2×2
  stream.py           149   babbling con tres RNG separados
  experiment.py       178   tabla conjunta, entrenamiento, run_seed

scripts/level1_sensorimotor_contingency.py     el 1.0 y sus 7 gates
scripts/level11_integration_verification.py    el 1.1, semillas 70000019…70000026

tests/  46 contratos:  13 (1.0) + 8 (reversión) + 6 (linaje) + 12 (1.1) + 7 (techo energético)

docs/AGENTE_NIVEL_1_ESPECIFICACION.md   especificación técnica del 1.0
docs/LEVEL11_ORACULO_PREREGISTRADO.md   oráculo sellado ANTES del experimento
docs/LEVEL11_INFORME.md                 informe del 1.1
docs/REV_PREREGISTRO_01.md              preregistro del Experimento 2
```

**Dependencia externa única del 1.0:** `from terrario.lab.causal_bench import
PairedResult` — instrumento estadístico compartido, no atadura al linaje
histórico. Por lo demás `terrario/level1/` no importa nada fuera de sí mismo salvo
`numpy`.

---

# 11 · Reglas de trabajo de este repositorio

- **Nunca `git add -A`.** Nada de `push`, nada de `merge`.
- **Cada trabajo nuevo es un commit aparte.**
- **Base de datos viva en sólo lectura:**
  `sqlite3.connect(f"file:{path}?mode=ro", uri=True)`. Sin `VACUUM`, sin
  checkpoint, sin `journal_mode`, sin PRAGMA de escritura; **jamás** tocar `-wal`
  ni `-shm`.
- **No tocar WIP ajeno.**
- **Nombres descriptivos, no índices.** Dos capas: clave técnica en el código,
  frase legible para el humano. `A4`, `E2-A`, `OCF-G3` están prohibidos en
  informes.
- **El corpus se consulta**, y puede refutar una afirmación ya escrita — como hizo
  Ashby con «conducta adaptativa» en §4.6.

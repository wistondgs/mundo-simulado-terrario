# A4 en juicio · informe adversarial

**2026-09-18.** Clasificación: **[MED]** medido hoy · **[COD]** hecho de código con
fichero:línea · **[INF]** inferencia · **[HIP]** hipótesis · **[ESP]** especulación.

---

# 1 · HECHOS DUROS DEL ORGANISMO

| # | Hecho | Clase | Evidencia |
|---|---|---|---|
| H1 | `s_t = concat(latente, hidden, memoria_episódica, contexto_LTM)`. **64 dimensiones.** Sin término corporal, sin observabilidad, sin tiempo | **[COD]** | `a4_advanced.py:343`, `:177` |
| H2 | A4 consume **1 de 4** campos sellados de `Observation`. `mask`: 0 usos. `time_fraction`: 0 usos | **[COD]** | `grep` sobre `a4_advanced.py` |
| H3 | `agent_energy` llega a conducta **sólo** por la temperatura del softmax | **[COD]** | `a4_advanced.py:421`, y el docstring lo declara: *«the only site where the organism's viability pressure reaches behaviour»* |
| H4 | En un 5×5 vacío A4 produce **1 vista para 25 celdas**; con la máscara, 25 | **[MED]** | conteo exhaustivo de celdas |
| H5 | El world model predice `next_state` desde `(s,a)` con target real y **detached**; `loss_state` está en `loss_total` | **[COD]** | `world_model.py:111`, `a4:640-661` |
| H6 | El planner puntúa `total_energy − 10·done_prob` y **nada más** | **[COD]** | `policy.py:151` |
| H7 | La incertidumbre **sí** gobierna conducta: `logits = logits + 0.1 * uncertainties` | **[COD]** | `a4_advanced.py:438` |
| H8 | `M` está recortada a ±10 y **satura hacia el paso 74**: `‖M−M₀‖` pasa de 23.78 a 25.66 en los 225 pasos siguientes | **[MED]** | test de checkpoints, n=8 |
| H9 | Con `use_planner=False`: **0 CONSUME en 201 pasos y muerte**. Con planner: 210 consumos efectivos | **[MED]** | mundo con comida adyacente |
| H10 | El pareado contrafactual quitó sólo el **14%** de la varianza; correlación NORMAL~FULL = **+0.140** | **[MED]** | DISCOVERY-32 |
| H11 | `action_availability` se declara y valida; **ningún runtime la aplica** | **[COD]** | cero apariciones en `world/`, `experiment/`, `agent/` |
| H12 | El encoder fija su dimensión de entrada al construirse; mundo y agente **no negocian** el radio | **[COD]** | `encoder.py:38-39` |

---

# 2 · CINCO CUELLOS CAUSALES, por evidencia

## C-1 · LA BÚSQUEDA DESTRUYE EL CONOCIMIENTO QUE EL MODELO YA TIENE — **demostrado hoy**

**[MED]** Mismo world model entrenado, mismo estado, comida al lado. Dos formas de buscar:

```
planner actual      horizonte 5, 10 secuencias de 25⁵    elige CONSUME el  30%
exhaustivo H=1      las 25 acciones, todas evaluadas     elige CONSUME el 100%  (6/6 semillas)
```

**El modelo ya sabe que CONSUME paga. La búsqueda lo pierde.** Y no es falta de muestras: 25
candidatos de profundidad 1 baten a 10 secuencias de profundidad 5. **Es estructura, no cantidad.**

**[INF] Éste es el primer corte causal DEMOSTRADO del proyecto, y está en CUT-D (búsqueda), no en
percepción.** Contradice la tesis central de mi propio documento de arquitectura de hace dos horas.

## C-2 · El planner puntúa una magnitud que casi no varía
**[COD]** `total_energy − 10·done`. **[MED]** dispersión de scores ≈ 0.001 antes de que el modelo
aprenda que CONSUME paga. En un mundo donde la energía no depende de la acción, el score es plano
por construcción y el «mejor candidato» es el primero sorteado.

## C-3 · El organismo descarta 3 de 4 campos de su observación
**[COD]** H2. **[MED]** H4. **Pero degradado desde mi afirmación anterior**: una permutación
determinista de la máscara (SHAM) da **también 25 vistas**. La distinguibilidad no es lo escaso —
lo escaso sería la **correspondencia** con la geometría. Y eso no está medido.

## C-4 · `M` satura y deja de llevar información
**[MED]** H8. `‖M−M₀‖` alcanza el 93% de su valor final en el primer cuarto de la adquisición.
**[INF]** Una memoria con rango dinámico agotado no puede seguir codificando experiencia nueva,
y eso pone un techo a la acumulación que ningún mecanismo de mantenimiento arreglaría.

## C-5 · El estado corporal no entra en la decisión
**[COD]** H1, H3. **[INF]** Sin esto, B2 es media capacidad: una política que no ve el hambre
aprende una política promediada sobre estados de hambre.

---

# 3 · CINCO HIPÓTESIS RIVALES, con falsador

| # | Hipótesis | Falsador |
|---|---|---|
| **R1** | **[HIP]** El cuello es la estructura de búsqueda, no la información. Un `argmax` de profundidad 1 sobre el modelo actual produce mejor conducta que el planner | Sustituir el planner por exhaustivo-H1 y medir conducta. Si no mejora, R1 cae |
| **R2** | **[HIP]** El planner es un generador de exploración disfrazado de planificador: su valor es la aleatoriedad, no la evaluación | Comparar planner contra muestreo uniforme **sin** evaluación. Si empatan, R2 vive |
| **R3** | **[HIP]** `M` saturada es funcionalmente equivalente a `M` congelada | Contrastar `M` del paso 74 contra `M` del 299 en conducta. **[MED] Primer indicio a favor**: el desemparejado es plano |
| **R4** | **[HIP]** La conducta está dominada por transiciones de régimen y ninguna mejora arquitectónica se verá en conteos | Medir cualquier intervención con entrada-en-régimen. **[MED] apoyo**: régimen excluye el cero donde los conteos no |
| **R5** | **[ESP]** La curiosidad ya implementada (`+0.1·incertidumbre` en logits) **perjudica** al empujar hacia acciones mal modeladas en vez de útiles | Ablacionar `use_uncertainty` y medir conducta. Nunca se ha hecho |

---

# 4 · ARQUITECTURA vNEXT

```
                    ┌──────────── mundo ────────────┐
                    │                               │
              Observation(channels, mask, energy, time)
                    │            │        │      │
      ┌─────────────┘            │        │      └── [FALTA] tiempo en el estado
      │                          │        │
  EXTEROCEPCIÓN            OBSERVABILIDAD  INTEROCEPCIÓN
  channels → encoder        mask [FALTA]   energy [SÓLO temperatura]
      │                          │              │
      └──────────┬───────────────┴──────────────┘
                 ▼
            s_t  (64 dim, totalmente unido: 7 consumidores)
                 │
      ┌──────────┼──────────┬───────────┐
      ▼          ▼          ▼           ▼
  WORLD MODEL  POLICY   INCERTIDUMBRE  MEMORIAS
  (s,a)→s',e,d           →+0.1 logits   episódica · M (SATURA)
      │                       │
      ▼                       │
  ┌─────────────────────┐     │
  │ [CUELLO C-1]        │     │
  │ PLANNER             │     │
  │ 10 de 9.7M al azar  │     │
  │ score = e − 10·done │     │
  └─────────┬───────────┘     │
            └────────┬────────┘
                     ▼
                  ACCIÓN
```

**Lo que vNEXT añadiría, en orden de evidencia**: (1) búsqueda estructurada — al menos exhaustiva a
profundidad 1, guiada por política a profundidad mayor; (2) un score que varíe — desviación
homeostática en vez de energía cruda; (3) la máscara; (4) `M` con rango dinámico o normalizada;
(5) el cuerpo en `s_t`.

---

# 5 · PRIMER CAMBIO A PROBAR

**Sustituir la generación de candidatos del planner por `policy-guided search`: muestrear las
secuencias de la política en vez de uniformemente, manteniendo horizonte, número de candidatos y
score idénticos.**

Una línea conceptual: `torch.randint(0, TOTAL_ACTIONS, ...)` pasa a
`torch.multinomial(softmax(policy_logits), ...)`.

**[INF] Por qué ésta y no la máscara**: es el único cuello **demostrado** (C-1), y separa
limpiamente «faltan muestras» de «falta estructura» — porque el número de muestras no cambia.

---

# 6 · EXPERIMENTO

```
CONTROL      planner actual, muestreo uniforme
TRATAMIENTO  planner con muestreo guiado por la política · mismo H, mismos 10 candidatos
BRAZO EXTRA  exhaustivo profundidad 1 (techo del conocimiento que el modelo ya tiene)

NACIMIENTO   un organismo, tres clones, intervención declarada, equivalencia verificada

ENDPOINT PRIMARIO   P(acción apropiada | oportunidad) en el banco conductual congelado
ENDPOINT SECUNDARIO probabilidad de entrada en régimen
NO usar conteos totales como primario: [MED] cola pesada, 325 pares para 80% de potencia

FALSACIÓN    si el guiado no supera al uniforme Y el exhaustivo-H1 tampoco supera al planner
             en conducta, entonces C-1 es un artefacto de medir elección y no conducta,
             y el cuello está aguas abajo (política o expresión ecológica)
```

---

# 7 · QUÉ NO TOCAR TODAVÍA

Memoria, `M`, interocepción, B2, affordances, skills, meta-control, `action_availability`, y la
frontera adaptativa. Una intervención, una cadena, un veredicto.

---

# 8 · DÓNDE OS CONTRADIGO

1. **El planner no es «pequeño»: es del tipo equivocado.** [MED] 25 candidatos de profundidad 1
   baten a 10 de profundidad 5. Multiplicar rollouts ataca la variable que no es.
2. **La curiosidad no falta: ya está, y es infalsable.** [COD] `a4:438` suma
   `0.1·incertidumbre` a los logits — exactamente la trampa que el pasaporte de CURIO-A1 describe.
   Tenemos un pasaporte para una capacidad implementada de la forma que el propio pasaporte declara
   incertificable.
3. **La escalera E0–E9 asume que las capacidades son independientes y secuenciales.** [MED] `M`
   satura en el primer cuarto: el sustrato impone un techo antes de que la escalera llegue a E3.
4. **`InitialStateFingerprint` y el pareado prometían más de lo que dieron.** [MED] 14% de
   reducción de varianza. La clonación causal es correcta y **no resuelve** el problema que
   motivó construirla.
5. **Medimos conteos porque son fáciles.** [MED] La entrada en régimen excluye el cero con n=32
   donde el conteo necesitaría 325 pares. Llevamos toda la campaña midiendo la magnitud cara.

---

# 9 · DÓNDE ME CONTRADIGO A MÍ MISMO

1. **«El cuello vinculante es perceptivo».** Escrito hace dos horas con confianza. **Falso o al
   menos no primero**: el corte demostrado está en la búsqueda (C-1), y SHAM da las mismas 25
   vistas que TRUE, así que ni siquiera la premisa del aliasing separa lo que yo creía.
2. **«La anomalía es co-adaptación, tipo Dobzhansky–Muller».** **Muerta.** [MED] El daño del
   desemparejado no crece con la divergencia: es plano, y el contraste tardío−temprano da +2.62
   `[+0.12, +6.88]` — va en la dirección contraria. Y la razón es más interesante: `M` satura.
3. **«La incertidumbre no llega a la decisión».** Falso, dicho hace veinte minutos. Busqué la
   variable **registrada** en vez de la **computada**. `a4:438` la usa.
4. **Mi experimento de plasticidad residual no tenía control positivo.** La segunda adquisición
   produjo ganancia **cero** en todos los brazos, así que no había nada cuya degradación medir.
   Inválido tal como lo corrí.
5. **«97% del ruido lo aportan 2 pares».** Calculado sobre la varianza marginal de FULL y
   presentado como si fuera sobre la pareada. Sobre la pareada son el **39%**.

---

# 10 · LA PREGUNTA QUE NADIE ESTÁ HACIENDO

**¿Es el planner un planificador, o es el generador de exploración del organismo?**

**[MED]** Sin él: cero CONSUME en 201 pasos y muerte. Con él: 210 consumos. **[MED]** Pero elige la
acción correcta el 30% de las veces cuando su propio modelo la identifica el 100%. **[INF]** Un
mecanismo que es imprescindible para la conducta y que evalúa mal es la descripción de un
**generador de variedad**, no de un evaluador.

Si eso es cierto, casi todo nuestro marco está mal orientado: llevamos la sesión preguntando si el
organismo **usa** lo que aprende, cuando la pregunta sería si el organismo **actúa** por una vía
que no pasa por lo que aprende — y el aprendizaje sería un pasajero, no un conductor.

**Falsador, y es barato**: comparar el planner actual contra muestreo uniforme **sin evaluación
alguna**, con el mismo número de acciones emitidas. Si empatan, el planner no está planificando.
Nunca se ha corrido, y es el experimento que más información daría hoy de todos los que tenemos
sobre la mesa.

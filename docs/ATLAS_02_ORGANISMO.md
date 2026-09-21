# Atlas 02 · El organismo · runtime y linaje A0–A5

**2026-09-21** · `7051d7f` · depositado en `CARTOGRAFIA_TERRARIO_01.md` **§XL**
· 14 citas `fichero:línea`, todas verificadas contra el fuente.

Cubre los puntos 2 y 3 del contrato de conocimiento. Lo que no se pudo cerrar
queda como K1/K2/K3 y no se rellena.

---

## 1 · El lazo, en el único sitio donde el organismo toca el mundo

`run_step` en `world/transition.py:316`. Trece pasos, y tres que sólo se ven
leyendo:

**La acción se reescribe después de decidirla.** El paso 5 pasa lo decidido por
el contrato de acción y devuelve `action` **y** `provenance`. Lo intentado y lo
resuelto viajan separados, que es lo que impide que «eligió mal» y «eligió bien
y el actuador falló» vuelvan a ser el mismo fallo.

**El RNG de la física es `world_seed + step`.** Derivado del mundo, no del
agente: cambiar de agente no mueve los sorteos exógenos. Hoy es inerte porque
`Physics.step` no lo consume.

**El estado interno entra en la `Transition` como cadena** —
`str(agent.get_internal_state())`. Queda registrado y no queda consultable.

Y **hay un segundo lazo**: `lab/causal.py:134` monta su propio
perceive→decide→learn para el banco contrafactual. No es accidental —necesita
intervenir entre decidir y transicionar— pero **nadie compara su semántica con
la autoritativa**. Es la clase exacta de divergencia que ya costó tres
resultados. **K1.**

## 2 · A4, sin los nombres conceptuales

```
observación → encoder Conv×3+LayerNorm → e_t (128)
            → SSM → h_t (256)
            → s_t = concat(e_t, h_t, mem_episódica 128, mem_LP 128) = 640
            → policy_head 640→256→25 → logits
            → temperatura = 1 + exploration_bias
            → logits += 0.1 · varianza_del_ensemble
            → planner con probabilidad 0.5, si no muestreo
```

**Un módulo ablacionado contribuye ceros, no desaparece.** La forma de `s_t` es
invariante bajo ablación, y por eso ablacionar no cambia el tamaño de nada aguas
abajo. Es la decisión que hace comparables los brazos, y está bien tomada.

**La energía entra escribiendo un atributo privado:**
`self.homeostasis._energy = observation.agent_energy` (`:358`). Es el snapshot
PRE. El POST ocurre 88 líneas después, en `learn()`, y **nadie guarda el
primero**: el valor que la política usó y el que el aprendizaje usa no son el
mismo.

## 3 · El planner no planifica

`Planner.plan` muestrea **10 secuencias aleatorias** de largo 5, las despliega
por el modelo del mundo, puntúa `energía − 10·ΣP(done)` y devuelve la primera
acción de la mejor. Diez tiros sobre 25⁵ ≈ 9,8 millones de secuencias.

Y se usa **a cara o cruz**: `plan_prob = 0.5`. `use_planner=True` no significa
«planifica»; significa «planifica la mitad de las veces, con diez tiros».

Que éste sea, medido, uno de los dos únicos módulos que mueven la conducta
(+6,7 comidas) dice algo sobre el resto, no sobre la potencia del planner.

## 4 · Apagar el aprendizaje significa cuatro cosas distintas

| Interruptor | Qué suprime |
|---|---|
| `learning_enabled` (el llamante) | que `learn()` se llame siquiera |
| `use_online_learning` | todo el bloque de pérdidas |
| `learning_commit_enabled` | **sólo** `optimizer.step()` — el resto del estado adquirido sigue cambiando |
| `full_adaptive_freeze` | las cuatro piezas de la frontera adoptada |

La frontera está declarada en un solo sitio, con el fichero que escribe cada
pieza: `A = { θ, EpisodicBuffer, M, energy_baseline }`. Y **bloquea la escritura
antes de que ocurra** en vez de revertirla, porque `escribir → leer → revertir`
no equivale a `no escribir → leer` aunque terminen con el mismo hash. Además
**registra los intentos**: congelado sin que nadie intentara escribir no es
evidencia de nada.

Es, junto con el pasaporte de capacidades, lo mejor razonado del repositorio.

## 5 · La regulación homeostática se apoya en un solo canal

```
drive            = max(0, threshold − energy)     ← se calcula, se traza, NADIE LO CONSUME
exploration_bias = 1 − energy                     ← único contacto con la conducta
```

La presión de viabilidad no elige **qué** hacer: sólo **cuánto** desordena la
elección. Un organismo hambriento explora más; no busca comida.

Esto importa para la capacidad HOMEO-A1: su hipótesis se apoya hoy en un único
canal, la temperatura de muestreo.

## 6 · El linaje

| | Percep. | Temporal | Mundo | Mem. ep. | Mem. LP | Incert. | Planner | Aprende |
|---|---|---|---|---|---|---|---|---|
| **A0** | — | — | — | — | — | — | — | no |
| **A1** | sí | — | — | — | — | — | — | REINFORCE |
| **A2** | sí | GRU | — | — | — | — | — | REINFORCE |
| **A3** | sí | GRU | sí | — | — | — | — | + modelo |
| **A4** | sí | SSM | sí | sí | sí | ensemble 5 | sí | + ensemble |
| **A5** | *hereda A4 entero* | | | | | | | **+ recompensa intrínseca** |

**A0–A4 son hermanas, no una cadena.** Cada una reimplementa el lazo y hereda
sólo de `AgentInterface`. **A5 es la única herencia real** — `A5Cybernetic(A4Advanced)`
sobrescribiendo **un método**:

```python
extrinsic = super()._policy_reward(consequence)     # = energy_delta
if not self._use_curiosity: return extrinsic         # ⇒ A5 es A4, bit a bit
return extrinsic + self.curiosity.signal(self.last_prediction_error)
```

Es la intervención causal más limpia que este proyecto puede montar, y lo es por
construcción: A4 dejó `_policy_reward` inerte a propósito para que un
descendiente no duplicara 187 líneas y dejara derivar la copia.

## 7 · «Curiosidad» son dos cosas distintas

| | Dónde entra | Qué es |
|---|---|---|
| **A4** | en los **logits**: `+0.1·varianza` | bono por incertidumbre del ensemble, coeficiente fijo, comentado como «curiosity» |
| **A5 · CURIO-A1** | en la **recompensa** | error de la propia predicción menos una línea base corrida |

La distinción no es estética: el pasaporte de CURIO-A1 declara que sumar la
señal a los logits haría que `purity_check` la llamara PURE **por construcción**
y el gate pasaría en vacío. **A4 ya hace exactamente eso con otra cantidad.**

El mecanismo de A5 motiva **predecir peor de lo habitual**, no predecir mal en
general; sin el suelo corrido, un organismo que predice mal en todas partes
recibe la misma señal en todas partes, que es no tener dirección. Confusor
declarado y no resuelto en el propio módulo: sin dinámica inversa, un organismo
curioso en un mundo con ruido irreducible puede quedarse mirando la estática.

## 8 · Lo que no se sabe

1. **K1** · El segundo lazo de `lab/causal.py` frente al autoritativo.
2. **K2** · Degradación del modelo del mundo a lo largo del horizonte 5, con
   contextos de memoria que el rollout no puede actualizar.
3. **K2** · Qué fracción real de las acciones viene del planner en una corrida.
4. **K2** · Si `drive` cambiaría algo al consumirse.
5. **K3** · Cómo acotar la curiosidad frente al ruido irreducible sin dinámica
   inversa.

---

## Reconocimiento de los árboles recién abiertos

No es el volumen 05 ni el 06: es lo que hace falta para escribirlos bien.

**Genesis vive en `RNE_v16-genesis-v2/lab/genesis/`** — 19 861 líneas, con
`acquisition/` (synthesis, ranked_synthesis, complete_frontier, certification,
confirmation, composition, dsl, campañas v2 y v3, preregistration),
`causal/adapters/` (code, dependencies, environment, forkable, rng) y
`evidence/ledger.py`. 70 ficheros de prueba bajo `tests/genesis/`, incluidos
tres de retención: audit package, epistemic state, family budget.

**No aparecen** `CEGIS`, `SyGuS`, `Composer` ni `archive` como componentes: de
la lista del contrato, esos cuatro no existen con ese nombre en el árbol vivo.
Confirmarlo o desmentirlo es trabajo del volumen 05.

**El organismo (RNE) es `runtime/`**, 277 ficheros Python, y **la autoridad
documental es `canon/`**, partida en `normative`, `provisional`, `experimental`
e `historical`. El canon normativo son siete documentos, entre ellos
`CANON_RNFE_v3_2_rc1.md` y `RUNTIME_SSOT_v1.md`. Cuál manda ante contradicción
es exactamente la pregunta del volumen 07, y ahora se sabe dónde se contesta.

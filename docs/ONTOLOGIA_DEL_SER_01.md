# Qué ser estamos construyendo
## SER → FUNCIÓN → CONCEPTO → CIRCUITO → ALGORITMO → SUSTRATO → CAPACIDAD

**2026-09-18.** Sin código, sin instrumentación, sin gates nuevos.
**[CORPUS]** con locator · **[COD]** fichero:línea · **[MED]** medido hoy · **[INF]** · **[HIP]**

---

# 0 · El hallazgo, primero

Aplicando el orden que fijaste, el diagnóstico de todo el día se reordena:

> **[INF] A4 está a UN CABLE de ser un regulador, y ese cable es exactamente el que medí que
> falta.**

El circuito homeostático mínimo tiene seis piezas. A4 tiene **cinco**:

```
variable esencial        energía                                    [COD] AgentState.energy      ✔
límites de viabilidad    muerte en 0                                [COD] state.py:170           ✔
percepción del interior  observation.agent_energy                   [COD] state.py:121           ✔
COMPARADOR               drive = max(0, umbral − energía)           [COD] homeostasis.py:39      ✔
  └─ SU SALIDA NO LLEGA A NINGUNA PARTE                             [MED] cero consumidores      ✘
control correctivo       CONSUME                                                                 ✔
realimentación           la acción cambia la energía                                             ✔
```

**[MED]** `drive` se calcula cada paso y aparece **sólo en trazas** (`a4:513`, `a4:562`). La única
ruta de la energía a la conducta es `temperature = 1 + (1 − energía)` (`a4:427`), que **no usa el
umbral** — no compara contra nada.

**[INF] Por eso `use_homeostasis` no es homeostasis: no es que falte un módulo, es que falta una
arista.** El comparador existe, produce el número correcto, y nadie lo lee.

---

# 1 · El ser mínimo

**[CORPUS]** Ashby define supervivencia como *«a line of behaviour that takes no essential variable
outside given limits»* (HEA-014 S.3/15) y conducta adaptativa como *mantener las variables
esenciales dentro de límites fisiológicos* (S.5/3). **[CORPUS]** Di Paolo añade que la mera
persistencia no basta: hace falta *regulación respecto de las condiciones de viabilidad*
(HEA-007, `C-HEA-007-02`).

De ahí, y no de una lista de módulos, salen las condiciones mínimas:

| Condición | Función causal | ¿Existe hoy? | Qué la realiza | Qué falta |
|---|---|---|---|---|
| **Variable esencial** | algo que puede salir de límites y matar | **sí, UNA** | `AgentState.energy` | N=1; con N=1 el conflicto entre necesidades es **indefinible**, no sólo no medible |
| **Región viable** | define dentro y fuera | **parcial** | muerte en 0 | `low_energy=14` es un cubo de puntuación, no un umbral fisiológico **[MED]** |
| **Interocepción** | percibir el interior | **sí** | `observation.agent_energy` | no entra en el estado que decide **[COD]** |
| **Comparador** | distancia al referente | **sí** | `homeostasis.drive` | **su salida no se consume** **[MED]** |
| **Control correctivo** | acción que reduce esa distancia | **sí** | CONSUME vía planner | no está condicionado por el comparador |
| **Realimentación** | la acción cambia la variable | **sí** | reglas del mundo | — |
| **Exterocepción** | percibir el mundo | **parcial** | `channels` | descarta `mask` y `time_fraction` **[COD]** |
| **Efectores** | afectar el mundo | **sí** | 25 acciones | `action_availability` no se aplica **[COD]** |
| **Continuidad temporal** | historia | **sí** | GRU | — |
| **Memoria** | persistencia entre episodios | **sí** | episódica + `M` | sin consumidor demostrado **[MED]** |
| **Plasticidad** | cambio por experiencia | **sí** | learner | demostrada sólo internamente |

**[INF] Veredicto**: A4 **es** un organismo situado por casi todos los criterios. Lo que no es, es
un **regulador** — porque el único lazo que lo haría regulador está abierto.

---

# 2 · Funciones antes que módulos

**[HIP]** Seis funciones, cada una con su circuito cerrable. Ninguna presupone red neuronal.

| Función | Circuito que la cierra | Estado en A4 |
|---|---|---|
| **REGULAR** | variable esencial → error respecto a referente → acción correctiva → reducción del error | **ABIERTO** en el tercer eslabón **[MED]** |
| **PERCIBIR** | mundo → señal → representación que decide | **parcial**: 1 de 4 campos **[COD]** |
| **PREDECIR** | (estado, acción) → consecuencia anticipada → error → corrección del modelo | **CERRADO** **[COD]** |
| **RECORDAR** | experiencia → persistencia → recuperación → efecto posterior en la decisión | **abierto en el último eslabón**: nunca medido **[MED]** |
| **ANTICIPAR** | estado → alternativas → consecuencias → comparación → selección mejor que el control | **ROTO**: ordena mal el 71% **[MED]** |
| **EXPLORAR** | ignorancia → acción dirigida → información → reducción de esa ignorancia | **abierto**: no hay ganancia de información **[COD]** |

**[INF] Sólo PREDECIR está cerrado.** Y es el único concepto cuyo algoritmo la auditoría declaró
BIEN FUNDADO. Eso no es coincidencia: **el circuito cerrado y la fidelidad conceptual son la misma
propiedad vista dos veces.**

---

# 3 · Hipergrafo de dependencias

**[HIP]** Derivado del corpus, no copiado de tu ejemplo:

```
REGULACIÓN  requiere  variable_esencial · región_viable · interocepción ·
                      comparador · control_correctivo · realimentación
            [CORPUS] Ashby S.3/15, S.5/3 · Di Paolo C-HEA-007-02

ANTICIPACIÓN requiere representación_de_estado · modelo_acción_condicionado ·
                      generación_de_alternativas · valoración · selección
            [CORPUS] Conant&Ashby: buen regulador ⇒ modelo. NECESIDAD, no suficiencia

MEMORIA-GUIADA requiere codificación · persistencia · recuperación ·
                      ACOPLAMIENTO_A_DECISIÓN
            el cuarto es el que nunca medimos

EXPLORACIÓN requiere estimación_de_ignorancia · dirección · adquisición ·
                      REDUCCIÓN_de_esa_ignorancia
            sin el cuarto es ruido dirigido, no exploración

MOTIVACIÓN  requiere REGULACIÓN cerrada  ← no es ortogonal, es DERIVADA
```

**[INF] Consecuencias que el grafo hace visibles y la lista de flags ocultaba:**
- **MOTIVACIÓN no es un concepto hermano de REGULACIÓN: la presupone.** No se puede tener B2 sin
  cerrar el lazo regulador primero. E1 no es «añadir hambre», es **cerrar el circuito que ya está
  dibujado**.
- **ANTICIPACIÓN no requiere REGULACIÓN.** Son ortogonales, y eso explica que A4 coma sin regular.
- **EXPLORACIÓN requiere un estimador de ignorancia que no tenemos** — desacuerdo de dos MLP
  entrenadas idénticamente no lo es.

---

# 4 · Perfil ≠ ablación

**[INF] Ésta es la corrección más consecuente de todas.**

Un **perfil** es un subgrafo **completo**: todos los prerequisitos de sus conceptos presentes.
Una **ablación** rompe deliberadamente una arista para medir causalidad, y su resultado **no es
otro organismo válido**.

Aplicado al catálogo actual:

```
use_homeostasis=False   no produce «organismo sin homeostasis»: rompe una arista
use_homeostasis=True    TAMPOCO produce homeostasis: la arista comparador→control
                        falta en los DOS casos                            [MED]
```

**[INF] El flag es ortogonal a si el concepto está realizado.** Encenderlo y apagarlo mueve una
constante de temperatura. La matriz de ablaciones lleva todo el proyecto midiendo la diferencia
entre dos organismos que **ninguno de los dos** regula.

Y el conteo: de los 2¹¹ = 2048 perfiles que el catálogo admite, **[INF] ninguno realiza
REGULACIÓN**, porque ninguna combinación de flags añade la arista que falta.

---

# 5 · Criterio de certificación · C0–C7

Adopto tu escala y la fijo con observables. **C0–C5 = mecanismo funcional. C6–C7 = inteligencia.**

| Nivel | Qué exige | Observable |
|---|---|---|
| **C0** definición | variables indispensables y anti-definición declaradas | ficha con locator de corpus |
| **C1** correspondencia | el algoritmo contiene esas variables y esas relaciones | lectura de código |
| **C2** señal | las señales existen y no son constantes | traza |
| **C3** integración | alcanzan **por alguna ruta** una variable que decide — no necesariamente `s_t` | grafo causal |
| **C4** efecto sobre acción | `P(a | mecanismo) ≠ P(a | ¬mecanismo)` | gemelos de un nacimiento |
| **C5** efecto organísmico | la diferencia de acción produce el efecto **que el concepto predice** | para regulación: retorno a la región viable, no «come más» |
| **C6** adquisición | la competencia mejora por experiencia | probe congelado |
| **C7** retención y composición | persiste y se integra con capacidades posteriores | transferencia |

**[INF] C5 es el nivel que nos faltaba y el que evita certificar nombres.** Para homeostasis no
basta que comer suba; hace falta **desviación → acción correctiva → retorno**. Ningún experimento
del proyecto ha medido eso todavía.

---

# 6 · Reauditoría de pasaportes

| Pasaporte | Veredicto | Por qué |
|---|---|---|
| **HOMEO-A1** | `INVALID_CONCEPT_MAPPING` | el algoritmo no cierra el circuito homeostático; `drive` no gobierna **[MED]** |
| **UNC-A1** | `NEEDS_REDEFINITION` | «desacuerdo de ensemble no calibrado» es una afirmación defendible; «estimación de incertidumbre» no |
| **PLAN-A1** | `MECHANISM_ONLY` | existe y actúa, pero ordena mal el 71% **[MED]**; no es anticipación competente |
| **CURIO-A1** | `INVALID_CONCEPT_MAPPING` | término sumado a logits; el propio pasaporte declara esa forma incertificable |
| **WM-A1** | `VALID` en C0–C3 · `NOT_TESTED` en C4–C5 | el algoritmo es fiel; su contribución conductual no está medida |
| **EPMEM / LTMEM / TEMP** | `NOT_TESTED` | mecanismos fieles; el eslabón «efecto posterior en la decisión» nunca se midió |
| **PLAST-A1** | `TERM_NOT_MODULE` | y por defecto está apagado **[COD]** |

---

# 7 · E0–E9 reauditado

| Exp | Veredicto | Por qué |
|---|---|---|
| **E1 hambre** | **TARGET NEEDS REDEFINITION** | presupone que `use_homeostasis` es homeostasis. **No lo es.** E1 deja de ser «añadir interocepción» y pasa a ser **cerrar el lazo regulador** |
| **E2 forrajeo** | `VALID TARGET` pero **mal ordenado** | forrajear es una tarea; regular es la relación con la viabilidad. **[CORPUS]** Ashby pone la segunda primero |
| **E0 motor** | `CURRENT IMPLEMENTATION CANNOT TEST` | sin `mask`, una vista por 25 celdas **[MED]** |
| **E3 valencia** | `VALID TARGET` | el generador ya lo hace |
| **E4 memoria** | `VALID TARGET` | mundo existe; falta el eslabón de acoplamiento a decisión |
| **E5 curiosidad** | **TARGET NEEDS REDEFINITION** | requiere estimador de ignorancia que no existe |
| **E8/E9** | `CANNOT TEST` | sin regulación cerrada no hay nada que reorganizar |

---

# 8 · El organismo mínimo coherente

**[HIP] Un regulador. Ni más.**

```
        mundo ──────────────────────────────┐
          │                                 │
     exterocepción                    la acción cambia
          │                           la variable esencial
          ▼                                 │
    ┌─ variable esencial (energía) ─────────┘
    │         │
    │    interocepción
    │         │
    │         ▼
    │    COMPARADOR   error = referente − percibido
    │         │
    │         ▼   ← LA ARISTA QUE FALTA
    │    VALORACIÓN   el error condiciona el valor de las alternativas
    │         │
    │         ▼
    └──── SELECCIÓN ──────────────────────► acción correctiva
```

**Sin world model. Sin planner. Sin memoria. Sin curiosidad.** Y su primera capacidad a demostrar
**no es forrajear**: es **regular** — que tras una desviación de la variable esencial, la conducta
la devuelva a la región viable. **[CORPUS]** Ésa es la definición de Ashby, y es medible con lo que
ya existe.

**[INF] Lo notable: A4 ya contiene ese organismo como subgrafo.** No hay que construirlo — hay que
cerrarle una arista y **apagar todo lo demás** para poder atribuir el efecto.

---

# 9 · Las cinco decisiones a revertir, en orden

1. **Tratar los once conceptos como flags conmensurables.** Es la raíz. Produjo pasaportes sobre
   nombres, una matriz de ablaciones que compara organismos igualmente rotos, y un `purity_check`
   ciego a tres de los once.
2. **Poner E2 (forrajeo) antes que regulación.** Forrajear es una tarea; regular es la relación con
   la viabilidad que el corpus pone primero. Invertimos el orden que Ashby fija.
3. **Certificar por presencia de módulo en vez de por circuito cerrado.** HOMEO-A1 y CURIO-A1
   habrían pasado su gate sin realizar su concepto.
4. **Medir conducta por conteos de consumo.** **[MED]** Es una magnitud con cola pesada dominada por
   transiciones de régimen; el retorno a viabilidad es el observable del concepto.
5. **Construir instrumento antes que cerrar circuitos.** Mío en gran parte. Tenemos clonación
   causal, huellas versionadas y transplantes de portador sobre un organismo con un lazo abierto.

---

# 10 · Lo que esto cambia mañana

**[INF]** Si el diagnóstico es correcto, la primera intervención sobre el ser **no es el planner**.
Es más pequeña todavía y ya está localizada: **hacer que `drive` gobierne la valoración.** Una
arista. Y a diferencia de todo lo demás, su falsador es el criterio C5, que es del corpus y no
nuestro: desviación → acción correctiva → retorno a la región viable.

Si al cerrarla el organismo sigue sin regular, entonces el problema no es la arista y hay que
mirar el sustrato. Pero eso todavía no lo sabemos, y llevamos cuatro días sin haberlo probado.

# Perfiles causales del organismo
## Un orden que no es arbitrario, y qué hay que modificar del ser para cada uno

**2026-09-18.** **[CORPUS]** con locator · **[COD]** fichero:línea · **[MED]** medido · **[HIP]**

---

# 0 · El error que hay que dejar de cometer

```
perfil_actual = subconjunto(planner, memoria, homeostasis, incertidumbre, ...)
```

**[MED]** Eso admite 2¹¹ = 2048 combinaciones, y **ninguna realiza regulación**, porque ninguna
añade la arista que falta. El catálogo genera 2048 nombres para organismos que difieren en
constantes.

Un perfil no es un subconjunto de flags. **Es un subgrafo cerrado**: todos los prerequisitos de sus
conceptos presentes y todas sus aristas conectadas.

---

# 1 · El eje de orden, y por qué no es una preferencia nuestra

**[CORPUS]** Ashby no define la conducta adaptativa como una capacidad entre otras: la define como
*mantener las variables esenciales dentro de límites fisiológicos* (HEA-014 S.5/3), y la
supervivencia como *una línea de conducta que no saca ninguna variable esencial fuera de los
límites dados* (S.3/15).

**[INF] Eso convierte la regulación en el CRITERIO, no en un peldaño.** Predicción, memoria y
exploración no son capacidades hermanas de la regulación: son **maneras de ampliar qué
perturbaciones puede absorber un regulador**.

De ahí sale el orden, y es el de la **variedad requisita**: cada perfil se define por **la clase de
perturbación que puede absorber**, no por los módulos que lleva dentro.

```
            ¿qué clase de perturbación absorbe?
P0  ninguna — no hay variable esencial con autoridad
P1  la acción correctiva está disponible AQUÍ y AHORA
P2  ...requiere anticipar una consecuencia antes de actuar
P3  ...la información relevante YA NO ES VISIBLE
P4  ...la contingencia del mundo es DESCONOCIDA y hay que ir a buscarla
P5  ...la contingencia CAMBIÓ y lo aprendido ya no sirve
```

**[INF] Cada peldaño es una ampliación del envolvente de regulación.** Y cada uno tiene un falsador
que no inventamos nosotros: si el perfil P_n no absorbe la perturbación de su clase, no es ese
perfil, por muchos módulos que lleve encendidos.

---

# 2 · Los perfiles

## P0 · REACTIVO — el organismo nulo

```
mundo → exterocepción → política → acción → mundo
```

**Qué hay**: todo. **[COD]** `a4:544-547`: sin planner, `policy_head.sample(logits, temperature)`
es la vía por defecto. **[MED]** Y este perfil come 0 veces en 201 pasos y se muere — pero eso **no
es un fallo del perfil**: es su línea base correcta. Un reactivo sin nada que le diga qué hacer
debe morirse.

**Existe hoy**: sí. Es `use_planner=False` con todo lo demás apagado.
**Rol**: control negativo de todos los demás. No es un organismo a mejorar: es el suelo.

## P1 · REGULADOR ADAPTATIVO — el primero que interesa

```
              ┌──────────────── el mundo cambia la energía ──────────────┐
              ▼                                                          │
   variable esencial ──► interocepción ──► COMPARADOR (drive)            │
                                                 │                       │
                                                 ▼                       │
                            AUTORIDAD: cuánto pesa ahora la              │
                            consecuencia energética APRENDIDA            │
                                                 │                       │
   experiencia ──► E[Δenergía | acción] ─────────┤                       │
                   (se APRENDE)                  ▼                       │
                                          preferencia ──► acción ────────┘
```

**La frontera que define este perfil**, y es la corrección que fijaste:

```
INNATO       que existe una necesidad · el comparador · que la desviación tiene autoridad
APRENDIDO    QUÉ acción o qué objeto reduce esa desviación
```

**[INF] Si programamos `drive → CONSUME`, no hay perfil: hay un termostato con nuestro
conocimiento dentro.** El perfil sólo es P1 si la contingencia es permutable por semilla y el
organismo la adquiere.

**Qué hay que modificar del ser**: una arista, y es la más pequeña de todo el documento.
**[COD]** `a4:438` ya demuestra que una valoración por acción puede entrar en los logits
(`logits + 0.1*uncertainties`). La modificación es de la misma forma, con dos diferencias: la
magnitud la aprende el `energy_head`, y su peso lo pone el `drive`.

**[HIP] Y una advertencia que viene del material que trajiste**: si el valorador es el
`energy_head` —entrenado sobre `energy_delta`— y certificamos la regulación midiendo energía,
estamos usando el entrenador como verificador. **Valorador y verificador tienen que ser piezas
distintas**, o el perfil no se puede certificar aunque funcione.

**Perturbación que debe absorber**: desviación inducida con el recurso correctivo **al alcance**.
**Falsador**: invertir la contingencia. Si sigue prefiriendo lo que antes servía, no adquirió
regulación: memorizó.

## P2 · REGULADOR PREDICTIVO

P1 **más** modelo de acción condicionada usado para valorar consecuencias **no inmediatas**.

**Qué hay**: **[COD]** el world model es el único de los once conceptos que la auditoría declaró
fiel. **[MED]** Y su conocimiento es explotable: exhaustivo a horizonte 1 elige bien el 100%.
**Qué hay que modificar**: la búsqueda, no el modelo. **[MED]** La contaminación por continuación
es 8× el margen decisivo.
**Perturbación**: el recurso está a distancia; actuar bien exige anticipar.

## P3 · REGULADOR CON MEMORIA

P2 **más** recuperación **acoplada a la decisión**.

**[MED] El eslabón que falta no es la memoria: es el acoplamiento.** Codificación, persistencia y
recuperación existen y son fieles; «efecto posterior en la decisión» no se ha medido nunca.
**Perturbación**: la información relevante ya no está en la ventana. Es el mundo cue→demora→elección
que ya existe.

## P4 · REGULADOR EXPLORADOR

P3 **más** estimación de ignorancia **cuya reducción se verifica**.

**[MED] Bloqueado**: lo que tenemos es desacuerdo de dos MLP entrenadas con datos idénticos. No es
ignorancia. Este perfil **no es construible** hasta que exista un estimador que se pueda falsar.
**Perturbación**: la contingencia es desconocida y nadie la va a mostrar.

## P5 · REGULADOR ULTRAESTABLE

P4 **más** reorganización cuando la regulación ordinaria fracasa de forma persistente.
**[CORPUS]** Ashby S.10/10 describe la pieza: un **mecanismo de compuerta** gobernado por el valor
del parámetro. **Bloqueado** hasta P1: sin regulación cerrada no hay fracaso regulatorio que
detectar.

---

# 3 · Perfil contra ablación · la regla operativa

```
PERFIL      subgrafo CERRADO. Se le exige absorber la perturbación de su clase.
ABLACIÓN    una arista rota a propósito DENTRO de un perfil, para atribuir causalidad.
            Su resultado NO es otro perfil.
```

**[INF] Consecuencia sobre la matriz actual**: `use_homeostasis=False` no produce «P1 sin
homeostasis». Produce **P0 con una constante distinta** — y `use_homeostasis=True` produce lo mismo,
porque la arista falta en los dos casos **[MED]**.

Y la regla que hay que poder comprobar mecánicamente: **una composición cuyos prerequisitos no estén
todos presentes debe fallar ruidosamente**, igual que `PINNED` hace fallar a `demand_for` cuando dos
capacidades piden cosas incompatibles. Un organismo incoherente no debería poder construirse en
silencio.

---

# 4 · Qué se modifica del ser, en orden

| # | Modificación | Tamaño | Habilita | Bloqueado por |
|---|---|---|---|---|
| **1** | el `drive` da autoridad a la consecuencia **aprendida** | **una arista** | **P1** | separar valorador de verificador |
| 2 | la búsqueda deja de sumar continuaciones aleatorias | una función | P2 | nada |
| 3 | la recuperación de memoria alcanza la decisión | una arista | P3 | medir primero si ya la alcanza |
| 4 | un estimador de ignorancia falsable | **pieza nueva** | P4 | no existe concepto implementable hoy |
| 5 | compuerta de reorganización | pieza nueva | P5 | P1 |

**[INF] Sólo la primera es pequeña, y es la única que convierte a A4 en un organismo de una clase
distinta.** Las demás amplían el envolvente de un regulador que todavía no existe.

---

# 5 · Lo que esto cambia en el catálogo

El catálogo debería dejar de ofrecer **once conceptos** y pasar a ofrecer **seis perfiles**, cada
uno con sus prerequisitos declarados y su clase de perturbación. Las ablaciones seguirían
existiendo, pero como **intervenciones dentro de un perfil**, nunca como perfiles.

**[INF] Y el criterio para añadir un perfil P6 no sería «tenemos un módulo nuevo».** Sería: existe
una clase de perturbación que P5 no absorbe y que sabemos inducir y medir. Eso hace que el catálogo
crezca por **preguntas**, no por piezas.

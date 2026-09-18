# Plan · De la vasija al organismo

**2026-09-18.** Derivado del corpus, no de mi razonamiento. Cada capacidad cita claims auditados
con locator; donde no los hay, se dice.

## Por qué existe este plan

Tres medidas de hoy lo obligan:

1. **El corpus está sin usar.** 0.00 % de los 283 conceptos y 1.06 % de los 189 claims son
   alcanzables desde alguna capacidad. Ninguno de los nueve `concept_id` de los pasaportes existe
   en el corpus: los inventé yo.
2. **El organismo no tiene alma.** Tres variables que calcula sobre sí mismo y no usa para nada:
   `drive` (cero consumidores), `homeostasis.update()` (escrito y sobrescrito), y
   `last_prediction_error` (entregado al observador y a nadie más).
3. **El organismo no tiene mundo.** Percibe `{channels, mask, agent_energy, time_fraction}` —una
   ventana 5×5— y su «modelo del mundo» predice su propio latente. Sin objetos, sin espacio, sin
   permanencia, sin causalidad.

Consecuencia medida: en 68 pasos recorre 2 columnas de 34, alcanza 1 estación de 8, y muere de
inanición a los 133 pasos. No explora mal: **no tiene razón para ir a ningún sitio.**

## La fuente que ya lo dice

`CLM-0123` (Pathak 2017, TI-0090, abstract y §1, pp. 1–2):

> «Cuando la recompensa externa es escasa o ausente, la señal intrínseca impulsa la exploración.»

El corpus ya contenía el diagnóstico y el remedio de nuestro fallo de alcance. Y `CLM-0121`, tipado
`OPERATIONAL_DEFINITION`, da el mecanismo: *«La curiosidad se operacionaliza como error al predecir
las consecuencias de las propias acciones.»* A4 **ya calcula ese error** y lo tira.

---

# Parte 0 · Reparar la procedencia

Barato, real, y desbloquea el gate que hoy detiene a ocho de nueve capacidades.

| Capacidad | Claims disponibles **hoy**, auditados y con locator |
|---|---|
| **HOMEO-A1** | `CLM-0056` regulation PRODUCE stability · `CLM-0052` regulation REQUIERE requisite variety · `CLM-0053` requisite variety DEPENDE_DE disturbance variety — Ashby 1956, TI-0049, part II ch. 11, pp. 108–110 |
| **WM-A1** | `CLM-0116` world model PRODUCE compressed spatiotemporal representation · `CLM-0117` compact policy USA esa representación — Ha & Schmidhuber 2018, TI-0087 |
| **UNC-A1** | `CLM-0126` uncontrollable noise PRODUCE prediction error · `CLM-0125` action-conditioned features INHIBE uncontrollable noise — Pathak, TI-0090, §2 p. 3 |

Cada una necesita un `OperationalizationRecord` con claim primario más uno de apoyo, y el bloque
`HumanOperationalization` — que es **acto humano, no derivable**.

**No se toca** `TEMP-A1` ni `PLAST-A1`: sus propias notas admiten que sus conceptos no están en el
corpus. Se marcan como tales en vez de inventarles procedencia.

---

# Parte 1 · El alma · CURIO-A1

```
CLM-0121  curiosity ASOCIADO_CON prediction error      OPERATIONAL_DEFINITION   ← primario
CLM-0122  prediction error PRODUCE intrinsic reward                             ← apoyo
CLM-0123  intrinsic reward FACILITA exploration                                 ← apoyo
```

**Operacionalización:** el error de predicción del organismo sobre las consecuencias de su propia
acción se le devuelve como señal de valor. `last_prediction_error` deja de ir solo al observador y
entra en la selección de acción.

**Lo que NO puede hacer, y es la línea que no se cruza:** la señal no puede saber dónde está la
comida. Dice «andá donde tu predicción falla», nunca «las puertas son buenas». Si supiera el mapeo,
habríamos construido la respuesta dentro del organismo — el problema del oráculo entrando por la
puerta de atrás, y con él la muerte de G4 y G8.

**Confusor declarado por adelantado:** `CLM-0126` advierte que predecir píxeles mantiene alto el
error por ruido incontrolable, y `CLM-0125` que la dinámica inversa lo reduce. Además `UNC-A1` ya
consume señal con forma de error de predicción y ya posee el eje `novelty`: hay colisión de
superficie de intervención y hay que resolverla antes de registrar nada.

---

# Parte 2 · A5 · el organismo que desciende de A4

A4 está congelado por decisión explícita, y debe seguirlo: es la línea base de toda la evidencia
existente. Así que **ni trasplante ni reforma: descendencia.**

`A5` = A4 con los lazos cerrados. Mismo sustrato, mismos módulos, misma física. La diferencia es
que las tres variables muertas llegan a la conducta. A4 permanece intacto como ancestro y como
brazo de control: la comparación A4 vs A5 es, por construcción, la intervención causal más limpia
que este proyecto puede hacer.

Criterio, fijado por la premisa del proyecto —esto es un organismo cibernético—:

> Una variable vital es fisiología si y solo si quitarla cambia lo que el organismo **hace**. Si
> solo cambia lo que el informe **dice**, es contabilidad.

Cada pasaporte de capacidad fisiológica debe declarar **por dónde cierra el lazo**, igual que hoy
declara `required_world_property`. Si no puede nombrar la ruta, no es fisiología todavía.

---

# Parte 3 · El mundo · de ventana a mundo

Aquí está «la comprensión de por qué lo hace, para qué lo hace y qué gana», y el corpus la reparte
en tres claims:

| Pregunta | Claim | Qué exige |
|---|---|---|
| **¿qué es el mundo?** | `CLM-0116` world model PRODUCE representación espaciotemporal comprimida | que el modelo prediga el **mundo**, no su propio latente |
| **¿para qué lo hace?** | `CLM-0138` policy selection DEPENDE_DE expected outcome (Friston, TI-0099, §2.3–2.6) | que la acción se elija por resultado esperado |
| **¿qué gana?** | `CLM-0140` belief updating INHIBE variational free energy | una cantidad que la acción reduce |

`CLM-0118` añade algo que este proyecto puede usar de inmediato: *«El modelo genera trayectorias
hipotéticas que funcionan como experiencia.»* Un organismo que no alcanza las estaciones podría
alcanzarlas imaginándolas — y eso es medible contra el mismo mundo real.

**Esta parte no se ejecuta todavía.** Se documenta ahora para que las Partes 0–2 no la contradigan.

---

# Parte 4 · Reparar la sonda y cerrar la frontera

Pendiente y conocido, con cuatro defectos confirmados por verificación adversarial: contaminación
de `_hidden` (infla LSB.19 ×18.6 y LSB.20 ×10), lectura de logits sin el canal de incertidumbre,
gates cableados en vez de calculados, y umbrales de 1e-9 sobre efectos de 1e-6. Además el inventario
omitía `_offered_targets` y `_generator`.

Se repara **después** de la Parte 1, porque la frontera solo puede medirse sobre historias que de
verdad difieran, y hoy en 2 de 3 semillas el organismo no toca ninguna puerta.

---

# Orden y dependencias

```
Parte 0  procedencia        ── independiente, empieza ya
Parte 1  CURIO-A1           ── necesita 0 para el pasaporte
Parte 2  A5                 ── necesita 1 para tener algo que cerrar
   └─ desbloquea exposición informativa
Parte 4  sonda y frontera   ── necesita exposición real
Parte 3  mundo              ── documentada, no ejecutada
```

# Lo que este plan NO hace

- No toca A4, ni `learner.py`, ni la física, ni G0/G4/G8, ni los hashes protegidos.
- No edita el snapshot sellado: es inmutable y su hash es constante de módulo.
- No usa X01–X16 (percepción de objetos, sensoriomotor, física intuitiva, X06 motivación
  intrínseca). **Ninguna tiene claims en la capa auditada** y la capa v0.3 que los contiene está
  declarada no canónica por el propio informe de expansión, con `definicion_del_autor` vacío en los
  59 conceptos y `validate()` rechazando su único claim. Usarlos exige una extracción humana nueva.
- No inventa procedencia para `TEMP-A1` ni `PLAST-A1`.

# Verificación

1. `scripts/passport_check.py` pasa de 1/9 con procedencia a 4/9, y ninguna procedencia nueva es
   inventada: `CorpusClaimReference.validate()` resuelve las seis contra el snapshot sellado.
2. CURIO-A1 registra y su estado se **calcula**, no se declara.
3. A5 existe, A4 no cambia: `git diff` sobre `terrario/agent/agents/a4_advanced.py` vacío.
4. El lazo cierra: quitar la señal intrínseca de A5 cambia su conducta; medido con el aparato de
   gemelos, no afirmado.
5. Exposición: A5 alcanza más estaciones que A4 en el mismo mundo y con la misma economía.
6. Suite completa con código real de pytest; los dos fallos baseline conocidos y ninguno más.

# El árbol C1/C2/C3 contra el corpus

**2026-09-18.** Qué dice el corpus sobre cada rama del árbol de decisión, antes de que la campaña
confirmatoria lo resuelva. Todo con locator en `corpus_v2/extracted_text/`.

---

## C1 · «competencia latente en θ, bloqueada por otro estado adquirido»

**El corpus la nombra, y dice que es un dilema, no un defecto.** Ashby S.16/15
([HEA-014.txt:19394-19404](corpus_v2/extracted_text/HEA-014.txt)):

> *«the demands that a brain model should show both **retroactive inhibition** and the ability to
> **accumulate adaptations** are opposed; for retroactive inhibition demands that later adaptations
> shall be destructive to earlier adaptations, while the power to accumulate adaptations demands
> that the later shall not be destructive to the earlier.*
>
> *The Homeostat showed retroactive inhibition at maximal intensity, for any later adaptation
> destroyed the earlier totally. A set of iterated systems, with some suitable **gating-mechanism**,
> shows the maximal power of accumulating adaptations. A multistable system of some intermediate
> degree can show both features partially, and will thus **resemble the living organism**.»*

Tres cosas que esto aporta y que no teníamos:

1. **La anomalía de DISCOVERY-32 tiene nombre.** `θ` inicial servido con estado adaptativo no
   paramétrico aprendido saliendo **peor** que el nacimiento —`Δ PARAMETRIC − FULL = −3.47,
   IC95% [−8.66, −0.34]`, 6% de pares a favor— es la forma que toma la inhibición retroactiva
   cuando lo adquirido tarde destruye lo adquirido temprano. No es un bug del transplante.
2. **Es un eje graduado, no un binario.** El Homeostato en un extremo (destrucción total), los
   sistemas iterados con gating en el otro (acumulación máxima), y el organismo vivo **en medio**.
   Si encontramos inhibición retroactiva, la pregunta deja de ser «cómo la eliminamos» y pasa a ser
   «dónde estamos en ese eje».
3. **El remedio tiene nombre**: S.10/10 ([HEA-014.txt:13185-13205](corpus_v2/extracted_text/HEA-014.txt))
   describe un **mecanismo de compuerta** `r` que decide qué conjunto de step-mechanisms está en el
   circuito de realimentación, gobernado por el valor del parámetro. Eso es una pieza de diseño
   concreta, no una metáfora.

Y la condición estructural, S.11/10 ([HEA-014.txt:14189-14190](corpus_v2/extracted_text/HEA-014.txt)):

> *«for the accumulation of adaptations to be possible the system must not be **fully joined**.»*

Nuestro `s_t = concat(latente, hidden, memoria, LTM)` alimenta **siete** módulos a la vez. Está
bastante joined. Esa frase es una predicción sobre nuestra arquitectura, no una observación sobre
la de Ashby.

## C2 · «conocimiento adquirido, puente a la acción roto»

Dos fuentes dicen lo mismo con vocabulario distinto, y las dos avisan de la **misma falacia**:
confundir tener la estructura con tener la función.

**Conant & Ashby**, título y tesis ([HEA-015.txt:3](corpus_v2/extracted_text/HEA-015.txt)):
*Every good regulator of a system must be a model of that system.* Es una **necesidad**, no una
suficiencia. Que el organismo tenga un modelo del mundo —y DISCOVERY-32 sugiere que lo adquiere—
**no implica** que regule. El teorema va en la dirección contraria a la que nos serviría.

**Di Paolo** ([HEA-007.txt:168-171](corpus_v2/extracted_text/HEA-007.txt)):

> *«autopoiesis implies only the former [robustness] while sense-making needs the latter
> [adaptivity]. Thus, autopoiesis simpliciter cannot provide the intended grounding for
> sense-making.»*

La misma forma lógica: la estructura presente no basta para la función deseada. Si C2 sale, el
corpus ya tiene indexado ese modo de fallo como `R-HEA-007-001`, con la implicación escrita:
*«Do not call a system agentic/autonomous from autopoietic language alone; require
adaptivity/viability regulation evidence.»*

## C3 · «competencia distribuida o sinérgica»

S.11/10 otra vez, leído al derecho esta vez: si el sistema **no** está totalmente unido, las
adaptaciones se acumulan. Un resultado donde `THETA_M` o `FULL_LEARNED` transporten conducta y
ninguno aislado lo haga sería exactamente un sistema parcialmente unido, que es lo que Ashby dice
que se parece a un organismo vivo.

---

## Lo que el corpus NO nos da

- **No dice qué esperar de un modelo del mundo entrenado por gradiente**, porque Ashby no tiene
  gradiente: sus step-mechanisms cambian por búsqueda aleatoria al salir la variable esencial de
  límites. La analogía entre `optimizer.step()` y un step-mechanism es **nuestra**, y no está
  sostenida por el corpus.
- **No dice nada sobre planificación por muestreo aleatorio.** El puente
  `world model → planner → acción` que C2 pondría en duda no tiene antecedente en el corpus: es
  arquitectura nuestra.
- **No predice el signo de nuestro resultado.** La inhibición retroactiva de Ashby es sobre
  adaptaciones sucesivas a **problemas distintos**; la nuestra sería entre piezas de estado dentro
  de **una sola** adquisición. Es la misma familia de fenómeno, no el mismo fenómeno.

## Lo que cambia en el plan si C1 sale

Si `THETA` transplantada produce conducta y `NORMAL` no alcanza F3, el corpus convierte la
conclusión «el planner no usa lo aprendido» en algo mucho más preciso y con literatura detrás:

```
el organismo SÍ adquirió competencia, y otro estado adquirido la está destruyendo
  → es inhibición retroactiva (Ashby S.16/15)
  → el eje es cuán unido está el sistema (S.11/10)
  → la pieza que falta tiene nombre: mecanismo de compuerta (S.10/10)
```

Y el objetivo siguiente dejaría de ser «entrenar más» para pasar a **localizar qué subcomponente
del bundle no paramétrico destruye**, que es justo lo que la matriz de portadores está midiendo:
`M` sola, `R` sin θ compatible, o la interacción.

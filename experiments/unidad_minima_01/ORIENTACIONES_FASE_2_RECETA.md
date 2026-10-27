# La receta · Fase 2 · un ser que elige qué vivir y hereda lo que aprendió

**Fecha:** 2026-10-27 · **Para:** Opus 5.5 · **De:** Fable, integrando el informe de literatura (46 fuentes) con lo medido en las Fases 0 y 1 · **Adjudica:** Wis.

**Qué es esto.** No una orientación más sobre cómo medir: la **composición** de la unidad siguiente, pieza por pieza, con la fuente de cada pieza y lo que es nuestro. La Fase 1 dejó un identificador correcto que no elige y no hereda. La Fase 2 construye el ser que hace las dos cosas, en mundos de 3 y 4 estados donde todo corre en milisegundos, y mide si **lo vivido se acumula**: si después de una vida la unidad puede, en la siguiente, algo que una unidad fresca no puede con la misma vida. Todo determinista, sin GPU, sin maestro, sin reset, sin marca (la marca queda como fase aparte).

**Corrección de Wis (27-oct), que rige todo el documento:** el criterio **no es economía**. No buscamos que gaste menos; buscamos que se desarrolle, como una célula: que de poco en poco sepa más, alcance más, y llegue a poder ser instruida. El cómputo y el tiempo se **registran** siempre y **no deciden nunca**. Donde una versión anterior decía «abarata», léase «amplía».

---

## 1 · Los seis órganos y de dónde viene cada uno

| órgano | qué hace | de dónde viene | qué es nuestro |
|---|---|---|---|
| **Identificar** | la máquina mínima consistente con la vida | 02 (nuestro); Gold/Angluin acotan su coste; en mundos ≤ 4 estados es instantáneo | ya existe, no se toca |
| **Releer** | reconstruir la hipótesis desde la memoria cuando deja de explicarla | Fase 0 (03): disparo **por consistencia**, no por vacío | ya existe; se generaliza el disparo |
| **Elegir** (nuevo) | cuando dos hipótesis mínimas empatan sobre la vida, ejecutar la **continuación más corta que las separa** en vez de seguir el itinerario | Kearns–Valiant 1994 (elegir rompe la barrera), Holmes–Isbell 2006 (la historia suficiente no llega al azar), Bender 1998 (procedimientos distinguidores), CALM 2007 («acción de prueba»), LIVE 1989 (genera sus propios experimentos) | la forma mínima: sin oráculo, sin marca, sobre la propia máquina |
| **Heredar la máquina** (nuevo) | al cambiar el mundo, empezar con la máquina anterior como **hipótesis inicial** y repararla localmente, en vez de aprender de cero | Groce–Peled–Yannakakis 2002 (adaptive model checking), Damasceno 2019 (learning to reuse), Ferreira–van Heerdt–Silva 2022 (adaptive L#) | adaptado a vida continua sin reset: el mundo cambia y la unidad no lo sabe |
| **Heredar las palabras** (nuevo) | las palabras de efecto constante (resets) y de permutación de W₁ entran al repertorio de acciones de W₂ como **macroacciones** | Korf 1985 / Tadepalli–Natarajan 1996 (tablas de macros), Soar 1986 (chunking), Egri-Nagy–Nehaniv (macroacciones = palabras que fijan una coordenada), Cropper 2020 (una biblioteca sin podar deja de servir) | la poda: una palabra heredada que no se usa en k vidas se retira (olvido sintáctico, no estadístico); se poda por no servir, no por costar |
| **Generar el mundo siguiente** (nuevo) | W₂ = **cascada** de W₁ y un bit nuevo cuya dinámica depende del estado de W₁ (dependencia feedforward); control: la dependencia al revés | Krohn–Rhodes / DeDeo 2011 (todo autómata es cascada; la novedad irreducible exige componente nuevo), Egri-Nagy–Nehaniv (producto corona restringido) | la familia enumerada y sus dos clases |

Lo que **no** entra, y por qué: PST con bucles y firmas (son para 1-bis, la escala); `hW` (necesita oráculo); la marca de Bender (cambia la interfaz; fase aparte); nada estocástico.

---

## 2 · Las piezas nuevas, especificadas

### 2.1 Elegir (acción epistémica mínima)

En cada paso la unidad tiene su hipótesis H (la mínima consistente). Si existe **otra** máquina mínima H′ consistente con la misma vida (01 ya la cuenta con `count_cap=2`; aquí se guarda), calcula la palabra más corta w tal que H y H′ predicen reacciones distintas tras w desde el estado actual de cada una (búsqueda en anchura sobre el producto H×H′, acotada a longitud ≤ 2·|Q|). Ejecuta w en vez del siguiente trozo del itinerario. Si no hay H′ (hipótesis única) o no hay w (empate indistinguible desde aquí), sigue el itinerario. Contadores: `empates`, `palabras_discriminantes_ejecutadas`, `empates_resueltos`, `empates_indistinguibles`.

Es exactamente lo que ataca la clase recurrente de la Fase 1, y lo que **no puede** atacar la transitoria (si el estado que separa ya no es alcanzable, w no existe: se cuenta como `indistinguible` y es dato).

### 2.2 Heredar la máquina

Al terminar la vida en W₁, la unidad **no sabe** que el mundo cambia. Sigue viviendo; W₂ empieza a responder. Su hipótesis H₁ empezará a fallar. En vez de retroceder al estado 0 de la búsqueda, la reparación es **local**: se conservan los estados y transiciones de H₁ que la traza de W₂ no ha refutado, y sólo se reabre la búsqueda sobre las transiciones refutadas (es el núcleo de Groce–Peled–Yannakakis: reutilizar la conjetura y reparar donde falla). Contador: `transiciones_heredadas_que_sobrevivieron`, `refutaciones_en_W2`.

Brazo «fresco»: misma unidad, memoria y máquina borradas al cambiar el mundo (el cambio lo hace el experimentador y queda declarado como tal: E-02). Brazo «lesionado»: se **funde** la distinción heredada que W₂ necesita (dos estados en uno, salidas por mayoría) y se conserva todo lo demás; el disparo de relectura por consistencia decide qué pasa.

### 2.3 Heredar las palabras

De H₁ se extraen las palabras de longitud ≤ 3 con efecto constante (escriben) y las permutaciones no triviales; entran al repertorio de W₂ como acciones compuestas disponibles para **elegir** (2.1) y para el itinerario (se intercalan en el shortlex como letras nuevas). Contador: `palabras_heredadas_usadas`. Poda: una palabra no usada en una vida completa se retira.

### 2.4 Generador de la familia (W₁, W₂)

Para cada W₁ del banco de n ∈ {3, 4} con n_min ≥ 2 e identificado por 02:
- **Componible:** W₂ tiene estados (x, b) con x ∈ W₁ y b ∈ {0,1}; las letras actúan sobre x **igual que en W₁** y sobre b con una regla que depende de x (b′ = f_a(x, b), enumeradas canónicamente; se toma la primera que hace a b distinguible desde la salida). La partición por x es congruencia de W₂: la distinción de W₁ sigue valiendo. Salida: bit de cambio del par.
- **Control no componible:** W₂ con la dependencia invertida: el efecto de las letras sobre x depende de b (la congruencia de W₁ se rompe). Mismo tamaño, misma salida.

Es una cascada en el sentido de Krohn–Rhodes: en la clase componible la novedad es un componente nuevo **encima** del viejo; en el control, la novedad reescribe el viejo. La predicción de la literatura (DeDeo) es que heredar sólo puede ayudar en la primera.

---

## 3 · El diseño: 2×2, como pidió el revisor externo

| | itinerario fijo | **elegir** (2.1) |
|---|---|---|
| **conserva** (máquina + palabras) | C1 | C3 |
| **lesionado** (distinción fundida) | C2 | C4 |
| fresco (sin nada) | F1 | F3 |

Mismo código congelado en las seis celdas; mismo W₁, misma vida en W₁ (así todos llegan a W₂ con la misma historia), mismo presupuesto en W₂. La distinción objetivo (el bit b) está **ausente** al empezar W₂ en todas las celdas, por construcción.

**Medidas de desarrollo en W₂, separadas (ninguna es de coste):**
- (a) **Alcance:** cuántos mundos W₂ del banco llega a identificar cada brazo con el **mismo presupuesto de vida**. La heredera que identifica mundos que la fresca no alcanza ha ganado alcance; eso es desarrollo.
- (b) **Exactitud:** fracción bien predicha de un futuro fijo de W₂, como curva por paso, no como punto final.
- (c) **Repertorio:** palabras que sabe y usa al final de W₂ frente al final de W₁: crece, se mantiene o se pierde. Un ser se desarrolla si crece.
- (d) **Instruibilidad:** dado un objetivo externo en W₂ (como en 04: «llevá el mundo al estado q»), ¿lo cumple, y lo cumple usando palabras heredadas? Es la primera forma de «se le va a poder instruir».
- Registro, no criterio: interacciones, trabajo computacional, tamaño de la biblioteca.

Contadores de actividad de cada órgano nuevo; contador en 0 ⇒ NULO-POR-INACTIVIDAD.

**Controles:** la clase no componible, donde heredar no debe ayudar y puede estorbar; el brazo lesionado, que separa «tener historia» de «tener la distinción»; y el intercambio A↔B en itinerario y desempates (control de asimetría pendiente de la Fase 1).

---

## 4 · Predicciones, escritas antes de correr

1. **Acumulación:** en la clase componible, C1 > F1 en alcance (la heredera identifica mundos W₂ que la fresca no alcanza con la misma vida) y en exactitud; en la clase no componible, C1 ≤ F1 (lo heredado estorba o no sirve).
2. **Elegir:** C3 > C1 y F3 > F1 en alcance, concentrado en los mundos donde W₂ era «recurrente» para el itinerario fijo; cero efecto en los «transitorios» (w no existe).
3. **Separación de efectos:** C3 − C1 (elegir) y C1 − F1 (heredar) son distintos y **se suman o mejor** en la clase componible; si C3 ≈ C1 ≈ F1, ni heredar ni elegir hacen crecer nada y lo que tenemos es un aprendiz, no un ser.
4. **Lesión:** C2 ≈ F1 (lo que se hereda es la distinción, no la historia).
5. **Repertorio e instrucción:** el repertorio crece de W₁ a W₂ en la clase componible y no en la otra; los brazos C cumplen objetivos externos en W₂ que los brazos F no cumplen con la misma vida.

**Falsador de programa:** C1 ≈ F1 en alcance y repertorio, y C3 ≈ F3, en la clase componible, con los contadores activos (si están en 0, es nulo, no negativo). Que la heredera gaste **más** cómputo que la fresca **no** es falsador: es registro.

---

## 5 · Lo que sigue siendo suministrado, declarado

La familia (W₁, W₂) y su regla de generación; el itinerario base; el criterio de poda; el tope de longitud de w; la salida observable; el cambio de mundo lo hace el experimentador (la unidad no recibe aviso). La valoración («se desarrolló») es nuestra, no de la unidad: la Fase 2 mide desarrollo, no lo motiva. Motivarlo (que la unidad busque ampliar su alcance) es la Fase 2-bis, después de saber si existe.

---

## 6 · Orden de trabajo

1. Gate de antecedentes de la Fase 2 con lo de arriba más Tripuraneni 2020, Agarwal 2023 y Lagriffoul 2022 (lo que la revisión externa trajo). Dos columnas, como siempre.
2. Ficha sobre la plantilla, punto 0 con guardas; mutantes **antes** de darla por final: un «hereda» que ignora lo heredado debe dar ≈ fresco; un «elige» que ejecuta palabras al azar está prohibido (sin azar): el mutante es «elige la palabra más larga», que debe empeorar.
3. `unidad_minima_08_fase2.py`: la unidad de 02 + 03 con los tres órganos nuevos; el generador de familias; las seis celdas; filas con la máquina serializada (E-21); reanudable; sin `random` **usado** (guarda corregida).
4. Banco: todos los W₁ de n = 3 identificados (≈ 368) y una fracción canónica sin retículo de los de n = 4; dos clases cada uno. Milisegundos por celda: cabe entero.
5. Cierre con las cinco predicciones marcadas cumplida/refutada, las cuatro medidas separadas, los contadores, y **una pregunta para Wis**.

Lo que no se hace: nada en n ≥ 6 (eso es 1-bis), nada con marca, nada estocástico, ningún documento más que los tres.

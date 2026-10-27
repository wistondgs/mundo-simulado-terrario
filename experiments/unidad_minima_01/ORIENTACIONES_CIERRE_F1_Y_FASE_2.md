# Orientaciones · cerrar la Fase 1, abrir la Fase 2, y qué hacer con n=8 y 1-bis

**Fecha:** 2026-10-26 · **Para:** Opus 5.5, en `/home/wis/Aplicaciones/worktrees/unidad-minima-01` · **De:** Fable, con la decisión delegada por Wis («eso depende de vos») · **Adjudica:** Wis en una sola cosa, al final.

**La decisión, en una línea:** el cierre se corrige y se commitea hoy; n=8 limpio corre **chico y en segundo plano**; 1-bis y la Fase 2 **no se encadenan**: la Fase 2 empieza ya, en mundos pequeños donde 02 no explota, porque es la pregunta que decide el programa y nada de lo pendiente la bloquea.

---

## 1 · Cerrar la Fase 1 (hoy, una hora, un commit)

Tres correcciones al `CIERRE_FASE_1.md`, en el sitio y con fecha:

1. **§3.** «La cobertura la fija el mundo» → «la fija el par **mundo × itinerario**». Las tres pruebas de vida larga alargan el *mismo* itinerario shortlex; el mutante de vida invertida ya mostró que **otro** itinerario identifica otros mundos (54 cambiaron). Así §3 pasa de «el mundo es inaprendible» a «la unidad no elige qué vivir», que es el argumento de la Fase 2.
2. **§7.** El criterio transitorio/recurrente pasa a ser **estructural**: un estado es transitorio si la parte alcanzable no es fuertemente conexa por debajo de él (hay ida sin vuelta). Sin umbral. Reproducido en n=4: «admite una menor» = **100 %** con transitorios estructurales en todo n_min; «dos del mismo tamaño» 94 / 58 / 33 %; identificados 24 / 11 / 5 %. El conteo de visitas queda como descriptor secundario.
3. **§5.** Los 24 mundos: con L = 7 se identifican **6 de 24**. La lección, escrita: *una palabra separadora presente en la vida no es experiencia si no se ejecuta desde el estado que discrimina*. Es la definición operativa de la clase recurrente.

Además: la frase «lesionada y reactiva no pueden» → «la lesionada no puede; la reactiva cumple desde su estado y falla desde el otro». Y el cierre lista **qué guardas saltaron** (§5 de este paquete). Commit.

## 2 · n=8 limpio: sí, pero contabilidad, no descubrimiento

- Tope duro **5 000** sistemas (no 30 000); parada por información con el criterio consciente del ruido como regla principal.
- Guardar por fila la máquina aprendida y las tablas (E-21) y **el índice**, para que 1-bis corra después **sobre los mismos mundos** y la comparación sea pareada sin pagar 02 dos veces.
- Mutantes M-4/M-5/M-6 corridos y **escritos en la ficha** antes de la corrida real (la vez anterior murieron sin dejar nada: E-29/E-30).
- Corre solo mientras se trabaja en lo demás. Nadie lo mira hasta que pare. Si no cambia ninguna de las tres conclusiones de la Fase 1, se dice en una línea y se archiva.

## 3 · 1-bis: la reparación única, reencuadrada por la literatura

El gate de 1-bis (`PRIOR_ART_FUSION_POLINOMICA.md`) no cita los dos candidatos con teorema para nuestro objeto exacto. Antes de construir, añadir y decidir:

- **Brazo principal: PST con bucles** (Holmes & Isbell, ICML 2006; PDF del autor en faculty.cc.gatech.edu/~isbell). Teorema de existencia finita para todo POMDP determinista fuertemente conexo; algoritmo LLT determinista, sin maestro ni reset; resuelve las repeticiones largas (u0)* que rompen cualquier ventana fija (nuestras corridas de A). Es batch: se implementa de las 8 páginas y se vuelve incremental sólo si hace falta.
- **Brazo secundario: fusión de estados sobre un camino** (lo que ya está en la ficha), para tener la comparación.
- **Instrumento, no brazo:** las firmas de profundidad 2·lg(n²/δ) de Freund et al. 1993 como criterio barato de identidad de estado y como cota de «caso típico»: medir qué fracción de nuestro coste vive en mundos atípicos.
- Mismo banco estratificado por n_min y por estructura de permutación; **pareado por índice** contra las filas de 02; mismo tope de 900 s y misma clase `sin terminar por reloj`.
- Predicciones a escribir antes: la pérdida de identificación se concentra en mundos **con transitorios estructurales** (el aprendiz irrevocable pierde donde el mundo no devuelve); coste polinómico; ambos brazos excluyen transitorios igual que 02.
- `hW` de AALpy queda fuera, como ya decidió Opus: actuar para preguntar es la Fase 2.

1-bis es la reparación que la regla exige para la Fase 1; **no es prerrequisito de la Fase 2**.

## 4 · La Fase 2 empieza ahora, y en mundos pequeños

La pregunta: **¿una distinción adquirida abarata la siguiente?** Se contesta en mundos de 3 y 4 estados, donde 02 identifica en milisegundos; no hace falta esperar a 1-bis.

**Lo que esta orientación fija:**
- **Banco de pares (W₁, W₂)** enumerado, en dos clases: **componible** (la máquina mínima de W₂ contiene la partición de W₁ como congruencia: la distinción de W₁ sigue valiendo) y **control no componible**. Generación: W₂ = extensión mínima de W₁ por un estado y una transición, canónica; el control, por una extensión que rompe la congruencia. Sin azar.
- **Tres brazos, mismo código:** conserva (máquina + palabras + política de relectura declarada), fresco, conserva-lesionado (lesión que **funde** estados, no que vacía: por eso el disparo de relectura tiene que ser **por consistencia** — «mi hipótesis no explica mi memoria» — y no «hipótesis vacía», como quedó dicho en la revisión de la Fase 0).
- **Endpoints:** curva de errores y paso del último error en W₂; contadores: predicciones que usaron estados heredados, elecciones que usaron palabras heredadas.
- **Elegir qué vivir, versión mínima:** la unidad, cuando dos hipótesis mínimas empatan sobre su vida, ejecuta la **continuación más corta que las separa** en vez de seguir el itinerario. Es la acción epistémica de Bender/Freund/Kearns–Valiant en su forma más chica, y es lo que ataca la clase recurrente. Se mide contra el itinerario fijo y contra el invertido.
- **Puerta:** conserva < fresco con margen preregistrado sobre la curva en la clase componible; lesionado ≈ fresco; conserva ≈ fresco en el control; elegir reduce la clase recurrente respecto del itinerario fijo. Falsador de programa: conserva ≈ fresco en la clase componible.
- Gate de antecedentes primero: Guerin 2008 (nadie lo demostró), Groce–Peled–Yannakakis 2002 y Damasceno 2019 (reutilizar un modelo aprendido), Bender 1998 (procedimientos distinguidores), Kearns–Valiant 1994 (elegir es salto de clase), Prospective Compression 2026.

**Lo que esta orientación NO fija y es de Wis (una sola pregunta):** si la unidad dispone de **una letra que escribe una marca y la vuelve a leer** (la «piedra» de Bender). Sin marca, elegir sólo puede escoger continuaciones; con marca, puede verificar que volvió. Es la decisión de diseño que separa dos Fases 2 distintas y no se puede preregistrar sin ella.

## 5 · El registro: dos mejoras de Opus, mejoradas

Opus propuso (a) una sección de «errores de banco de trabajo» y (b) que el cierre diga qué guardas saltaron. Las dos van, con un cambio cada una:

- **(a) Las guardas de banco de trabajo no se leen: se importan.** Un módulo `guardas.py` de cinco funciones que **todo** script del árbol usa: `no_vacio(lista, nombre)` (falla si se va a verificar sobre cero elementos; E-30), `matar_por_pid(pid)` (nunca por patrón; E-26), `muestreo_verificado(idxs, base, posiciones)` (cada dígito recorre todos sus valores; E-27), `salida_a_fichero(ruta)` (nunca una tubería que un tope pueda cortar; E-29), `estrato_de(fila)` (pertenencia por campo, nunca por posición; E-23). La guarda que vive en código actúa aunque nadie abra la libreta. La libreta señala al módulo.
- **(b) Medir las guardas, y también su silencio.** Cada entrada lleva un contador `veces que saltó` que el cierre actualiza. Y una regla: una guarda que no ha saltado en dos fases **se revisa**: o el error ya no es posible (se cierra la entrada como «resuelta por construcción») o la guarda no detecta (E-15). Así la libreta no sólo se llena: se poda.
- **(c) Tres clases de error en cada entrada:** *criterio* (mal pedido), *instrumento* (mide otra cosa), *banco* (comando suelto). De los 30 de hoy, la mayoría son de instrumento y banco: eso dice que el método de fichas y mutantes funciona para el criterio y que el agujero está en lo que ocurre entre fichas. Clasificarlos es lo que permite ver si la proporción mejora.

## 6 · Lo que no se hace

No correr n=8 a 30 000. No esperar a n=8 ni a 1-bis para abrir la Fase 2. No preregistrar la Fase 2 sin la decisión de la marca. No tocar RNE ni Genesis. No commitear a mitad; un commit por cierre.

## 7 · Entregables y orden

1. `CIERRE_FASE_1.md` corregido + commit (hoy).
2. `guardas.py` + registro con clases y contadores (una hora).
3. n=8 limpio lanzado (5 000, parada por información), desatendido.
4. `PRIOR_ART_FUSION_POLINOMICA.md` actualizado; 1-bis con dos brazos, pareado.
5. `PRIOR_ART_FASE_2.md` y, **tras la respuesta de Wis sobre la marca**, `APERTURA_FASE_2_COMPOSICION.md` sobre la plantilla.
6. Un cierre por cosa, una pregunta para Wis por cierre.

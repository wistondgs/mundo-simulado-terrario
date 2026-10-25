# FICHA DE APERTURA · elección por conveniencia bajo orientación externa (ítem 0.3)

**Fecha:** 2026-10-25 · **Veredicto: `OPEN`** (autoriza código) · **Gate previo:** `SOLVED` para el objeto, `OPEN_UNDER_CURRENT_SEARCH` para el uso, ver `PRIOR_ART_ELECCION_BAJO_ORIENTACION.md`

1. **Pregunta.** Dada una meta impuesta desde fuera —«que la próxima reacción a B sea 1»—, ¿la unidad la satisface eligiendo una palabra de su propio repertorio adquirido, en el mínimo de pasos, allí donde sus controles no pueden?

2. **Constructo y medida.** Constructo: *uso instrumental de la distinción propia*. Medidas: longitud de la palabra elegida; si al ejecutarla en el mundo la reacción real a B es 1; si la palabra es la más corta que cumple; y en cuántos pasos de la elección la distinción fue lo que decidió.

3. **Hipótesis.** La distinción adquirida no sólo predice: sirve para actuar. Una unidad con dos estados puede elegir una palabra que ninguna de sus letras realiza; una sin la distinción no tiene con qué elegir.

4. **Dos criterios, declarados por separado, porque no son la misma pregunta.**
   - **Desde el estado actual** (la unidad usa el `q` que cree ocupar): si cree estar en el estado donde B reacciona 1, la palabra es `ε`; si no, `A`.
   - **Robusto a la ignorancia del estado** (la palabra debe cumplir desde *todos* los estados): es una palabra de reset con imagen prescrita, y es `BA`, de longitud 2. Éste es el criterio que discrimina, porque es el que ninguna letra sola satisface.

5. **Predicciones, escritas antes de correr.** Mundo aliasado: criterio robusto → la unidad elige `BA`, longitud 2, y la reacción real a B es 1; no existe palabra de longitud 1 que cumpla (`A` conmuta, `B` escribe 0), así que 2 es el mínimo y la unidad lo alcanza. Criterio desde el estado actual → longitud 0 o 1 según dónde termine la vida. Lesionada: ninguna palabra certifica la meta (con un estado, su predicción de B es la mayoritaria y es 0) → **no encuentra**. Reactivo: no tiene estados sobre los que recorrer palabras; sólo puede mirar (reacción previa, letra) → **no encuentra** o acierta por casualidad sin poder certificarlo. Mundo visible: el reactivo **sí** cumple (el test discrimina). Mundo del bit inerte: la meta es **insatisfacible** y la unidad debe decir que no hay palabra, no inventar una.

6. **Falsador.** Que la unidad lesionada o el reactivo cumplan la meta en el mundo aliasado. También: que la unidad elija una palabra más larga que el mínimo, o que elija `BA` y la reacción real no sea 1 (su máquina estaría mal y 01 estaría mal).

7. **Banco.** Los tres mundos de 01 congelados. Palabras de longitud ≤ 4 en orden shortlex, exhaustivo. El gate anota que esta exhaustividad es legítima a esta escala y no escala: hallar la palabra de reset más corta es inaproximable dentro de n^(1−ε) (arXiv 1408.5248).

8. **Tres capas.** *Programado*: la meta, el alfabeto, el tope de longitud 4, y que se ejecute la primera palabra que cumple. *Disposición*: el orden shortlex como desempate entre palabras de igual longitud, y la predicción 0 por defecto cuando no hay ruta. *Adquirido*: la máquina, las palabras, y cuál se eligió.

9. **Contadores de actividad.** Palabras evaluadas antes de hallar la elegida; pasos de la simulación en que estados distintos predecían reacciones distintas (la distinción decidiendo). Contador de decisión en **0** en el mundo aliasado ⇒ nulo por inactividad: la elección no usó la distinción y el experimento no prueba lo que dice.

10. **Mutantes del gate, antes de lo real.** (i) Una unidad cuya máquina se colapsa a un estado —la lesionada— debe FALLAR el criterio robusto; si pasa, el criterio no mide la distinción. (ii) Un «elector» que devuelve `BA` fijo sin consultar su máquina debe FALLAR en el mundo del bit inerte, donde la meta es insatisfacible y responder `BA` es inventar. (iii) El mundo visible, donde el reactivo debe pasar: si FALLA, el test no discrimina y mide otra cosa.

11. **Puerta.** PASS si, en el mundo aliasado: la unidad cumple el criterio robusto con `BA` de longitud 2 y la reacción real es 1; no hay palabra más corta que cumpla (comprobado por enumeración); lesionada y reactivo no cumplen; en el mundo visible el reactivo cumple; y en el mundo del bit inerte las tres declaran insatisfacible. FAIL si se cumple cualquier parte del punto 6.

12. **Custodia.** `unidad_minima_04_eleccion.py`, resultado a `artifacts/unidad_minima_04_eleccion.json` con el sha256 del código, dos corridas un hash, sin `random`. No se commitea sin que Wis lo diga.

---

## Enmienda prospectiva · 2026-10-25, antes de escribir el código

El punto 5 prometía que «en el mundo visible el reactivo sí cumple», como control de que
el test discrimina. Con la meta «que la próxima reacción a B sea 1» eso **no se puede
medir**: en el mundo visible B reacciona 0 siempre, y en el del bit inerte también, así que
allí la meta es insatisfacible y el reactivo no falla por incompetencia sino porque no hay
nada que cumplir. Un control que no puede pasar no controla nada.

Se corre por tanto **cada mundo con dos metas**, declaradas como suministradas:

- «que la próxima reacción a **B** sea 1» — en el mundo aliasado exige la distinción (`BA`); en los otros dos es insatisfacible, y las tres partes deben declararlo;
- «que la próxima reacción a **A** sea 1» — en el mundo visible se cumple con `B` de longitud 1 y el reactivo **sí** puede hallarla, que es el control que faltaba; en el aliasado es trivial (A reacciona 1 siempre) y lo esperado es `ε`.

Una meta trivial y una insatisfacible no son ruido: son los dos extremos que acotan la
única interesante, y el experimento informa las tres.

**Robustez medida por fuera, no por declaración.** Que un agente «certifique» una palabra
no prueba nada: se ejecuta la palabra elegida en el mundo real desde **los dos** estados
ocultos posibles y se comprueba si la meta se cumple en ambos. El reactivo puede acertar
desde un estado por suerte; esa es justamente la diferencia que hay que medir.

### Segunda enmienda prospectiva · 2026-10-25, en el paso de mutantes

El mutante «reactivo mudo» mostró que el criterio del mundo visible estaba mal pedido: se
le exigía al reactivo que su palabra cumpliera **desde los dos estados ocultos**, es decir,
robustez frente a la ignorancia del estado. Pero en el mundo visible la reacción previa
*es* el bit, así que el reactivo no es ignorante y esa exigencia le pide resolver un
problema que allí no existe; el control no podría pasar nunca y por tanto no controlaba.

El criterio pasa a ser: en el mundo visible el reactivo **cumple la meta desde el estado en
que de hecho está**. Eso es lo que discrimina, porque en el mundo aliasado no puede
garantizarlo. La columna robusta se sigue informando para los cuatro electores, pero sólo
se le exige a la unidad.

**Nota honesta sobre el método.** Tres criterios de estas dos fichas salieron mal escritos
y los tres los encontró el paso de mutantes antes de correr lo real, que es exactamente
para lo que sirve. Pero tres en una sesión dice que los criterios se están escribiendo
demasiado rápido, y conviene que quede anotado en vez de disimulado.

# FICHA DE APERTURA · fusión de estados polinómica sin maestro y sin reset (1-bis)

**Fecha:** 2026-10-25 · **Veredicto: `OPEN`** (autoriza código) · **Gate previo:** `SOLVED` para el mecanismo / `OPEN_UNDER_CURRENT_SEARCH` para el acoplamiento, en `PRIOR_ART_FUSION_POLINOMICA.md`

**Qué es esto.** La reparación única de la Fase 1, declarada antes de correrla. La fase midió que el mecanismo de 02 **identifica bien y tiene una cola de coste catastrófica**. 1-bis no arregla 02: cambia el mecanismo por uno polinómico y mide **qué se pierde**. Mismo banco, misma salida observable, misma puerta de identificación.

---

## 0 · Guardas de `ERRORES_Y_GUARDAS.md` que aplican

| entrada | cómo se cumple aquí |
|---|---|
| **E-01** entorno sin ejecutar | el artefacto registra `python` con el comando que lo probó; nada de bibliotecas nuevas |
| **E-02** cero comprado con señal suministrada | punto 8: nadie de fuera dispara nada; la fusión la decide la unidad con lo que lee |
| **E-03** criterio sin unidad | punto 11: cada número con su unidad y su campo del JSON |
| **E-05** control que no controla | punto 7: por cada mundo, la afirmación exacta que controla |
| **E-06** la ecuación sellada no era la implementada | mutante «ciego a la observación»: la fusión **tiene** que usar la salida leída |
| **E-07** irreproducible | sin `random`; hash sobre filas ordenadas por `(n, idx)`; todo parámetro al JSON |
| **E-08** presupuesto donde ya saturó | se informa la curva frente a n y la **cobertura** aparte de la captura |
| **E-09** mecanismo que no corrió | contador `fusiones_intentadas` y `fusiones_aceptadas`; 0 ⇒ NULO-POR-INACTIVIDAD |
| **E-15** mutantes que no ejercitan el instrumento | punto 10: dos mutantes **de instrumento**, con resultado conocido por construcción |
| **E-16** calibrar sobre la mediana | el reloj se calibra sobre los deciles del orden canónico, y el coste está acotado por construcción (punto 2) |
| **E-17** gate sin la complejidad del problema | el gate trae la fila de complejidad: Gold 1978, Angluin 1978, Pitt & Warmuth 1993. **Es la razón de ser de 1-bis** |
| **E-11** iniciativa fuera del encargo | punto 1, segundo párrafo |

**Qué cubre ya un experimento previo:** el banco, la verdad de referencia, la comparación salvo isomorfismo y el clasificador están medidos y congelados en `unidad_minima_05_banco.py`. 1-bis **no los reescribe**: cambia sólo el aprendiz.

---

## 1 · Pregunta

**¿Cuánta identificación cuesta acotar la cola?** Es decir: un aprendiz de fusión de estados polinómico, sin maestro y sin reset, que nunca deshace una fusión, ¿con cuántos puntos menos de identificación paga el haber cambiado una cola de ×132 573 por una cota estructural?

**Qué estoy construyendo que la pregunta no pide** (E-11): nada de `hW`, nada de AALpy instalado, ningún comparador nuevo, ninguna métrica nueva. La propuesta que queda **aparte y no se construye**: comparar contra la rama pasiva de AALpy con sus propios cortes de traza. Se propone, no se hace.

---

## 2 · Constructo y medida

Constructo: **identificación bajo coste acotado**. Las dos mitades se informan **siempre juntas**, nunca una sin la otra.

| medida | campo del JSON |
|---|---|
| identificación salvo isomorfismo | `igual_salvo_isomorfismo` |
| clase del no coincidente | `clase` |
| trabajo real por paso de vida | `trabajo` / `vida_len` |
| fusiones intentadas y aceptadas | `fusiones_intentadas`, `fusiones_aceptadas` |
| paso del último error prediciendo antes de actuar | `ultimo_error` |
| estados finales frente al mínimo verdadero | `estados_aprendidos`, `n_min` |
| reloj | `reloj_s` |

**La cota de coste es por construcción, y eso se dice.** Cada paso de vida intenta a lo sumo una fusión contra cada estado ya existente, y una fusión aceptada no se deshace nunca; el trabajo total está acotado por `T · n_max`. Verificar esa cota no es descubrirla: es comprobar que la implementación cumple su propia promesa. **Lo que de verdad no se sabe es cuánta identificación cuesta**, y eso es la medida de esta ficha.

---

## 3 · Hipótesis

Renunciar al mínimo exacto no cuesta casi identificación en este banco, porque la vida shortlex da muchas más restricciones que las que hacen falta para forzar las fusiones correctas en la mayoría de los sistemas. Donde cuesta, costará en los mismos sistemas que 02 ya no identificaba.

---

## 4 · Criterios, declarados por separado

- **Coste acotado**: trabajo/vida acotado en todo n, en p99 **y** en máximo.
- **Identificación**: la tasa sobre la clase n_min ≥ 2, comparada con la de 02 **en el mismo n y el mismo conjunto de sistemas**.
- **No sobrefragmentación**: la clase inerte (n_min = 1) sigue con cero distinciones. No negociable.

---

### Predicción añadida el 2026-10-27 · dónde hay que medir a 1-bis

Si la muestra limpia de n=8 confirma que la identificación **cae a igual `n_min`** respecto de n=6 —hoy va en esa dirección con 1 669 de 5 000 mundos, aunque varias diferencias caben todavía en el ruido—, entonces la Fase 1 corrige su §3 a **«no degrada entre 3 y 6; degrada en 8»**, y eso fija dónde se mide 1-bis.

**La consecuencia para esta ficha:** el aprendiz polinómico **no se juzga en n=3 ni n=4**, donde 02 identifica bien y en milisegundos y cualquier mecanismo razonable empata. Se juzga **en el estrato exacto donde 02 empieza a perder**, que es donde un intercambio de exactitud por coste acotado puede ganar o perder de verdad. La comparación pareada por índice contra las filas de 02 se concentra ahí, y la pérdida de identificación admitida (≤ 15 puntos) se evalúa **por estrato** y no sobre el agregado.

Si en cambio la caída de n=8 resulta ser composición —el falsador declarado en la ficha de n=8—, entonces 02 no degrada con el tamaño del mundo en ningún punto medido, y 1-bis se juzga sólo por la cola de coste, que es el FAIL que sí está establecido.

## 5 · Predicciones escritas antes de correr

- Coste: trabajo/vida con **máximo ≤ 50** y **p99 ≤ 10** en los cuatro n. Frente a 02: p99 de 1 308 y máximo de 132 573 en n=6.
- Identificación: **pérdida de entre 5 y 15 puntos** respecto de 02 en cada n.
- La pérdida **no** será uniforme: caerá sobre los sistemas de n_min alto, donde la primera fusión compatible tiene más probabilidad de ser la equivocada.
- Clase inerte: **cero** distinciones abiertas, igual que 02.
- Los sistemas que 02 no identificaba seguirán sin identificarse: la ambigüedad del itinerario no la arregla cambiar de aprendiz (medido en la variante de cobertura: alargar la vida resolvió 6 de 19 182).

---

## 6 · Falsador, como número

**La pérdida de identificación supera los 15 puntos porcentuales en cualquier n.** Entonces el intercambio se rechaza y la fase informa que, en este banco, exactitud y coste acotado **no son compatibles** — lo que sería consistente con Pitt & Warmuth 1993 y es un resultado, no un fracaso.

Segundo falsador, de instrumento: que el máximo de trabajo/vida pase de 50. Eso significaría que la implementación no cumple la cota que su propio diseño promete, y es un defecto a arreglar antes de leer nada más.

---

## 7 · Banco y controles · por mundo, la afirmación exacta que controla

El banco de la Fase 1 en su definición —n ∈ {3,4,6,8}, L(n) = n+2, salida `o = [x′ ≠ x]`, orden canónico— pero **con la cobertura que prescribe E-18 en su «Aplicada en»**, no la 1-de-k de la Fase 1:

- **n=3 y n=4 completos** (729 y 65 536 sistemas). Son baratos y dan la comparación exacta contra 02 sobre el mismo conjunto.
- **n=6 y n=8 por muestra estratificada**, chica y declarada, **recorrida en orden esparcido** (E-18) y con **parada por información** cuando las curvas coste(n_min) e identificación(n_min) se estabilicen. No se repite el error de la Fase 1 de perseguir una muestra 1-de-k entera en n=8.
- **Estratos declarados, dos ejes.** El primero es `n_min`, como pide E-18. El segundo lo añade el hallazgo de la Fase 1 y es más informativo que `n_min`: **si cada letra es una permutación de lo alcanzable**. Medido sobre 143 458 sistemas, con las dos letras permutación la identificación de 02 es **100 %, cero excepciones en 2 037 sistemas**, y el gradiente a igual `n_min` es monótono (ninguna 46–70 %, sólo B 61–71 %, sólo A 68–80 %, las dos 100 %). Una muestra que no equilibre ese eje mide la mezcla, no el mecanismo.
- **Comparación pareada, no agregada.** Cada sistema medido por 1-bis se compara **contra la fila de 02 del mismo `idx`**, que ya está grabada. La pérdida de identificación se informa como diferencia pareada por estrato, no como diferencia de dos promedios sobre conjuntos distintos.

| mundo / clase | qué puede hacer el aprendiz ahí | qué afirmación controla ese mundo |
|---|---|---|
| **n_min = 1** (inerte bajo esta salida) | nada que distinguir: todo fusiona en un estado | que **no se inventan distinciones**. Si 1-bis abre una, sobrefragmenta y el resto no se lee |
| **n_min = 2** | identificar es fácil; 02 lo hace casi siempre | que el aprendiz **tiene la capacidad**: si falla aquí, no mide pérdida por fusión, mide que está roto |
| **n_min ≥ 4** | aquí la primera fusión compatible puede ser la equivocada | que la pérdida medida **viene de la fusión irrevocable** y no de otra cosa |
| **los no identificados por 02** | nada: la vida no determina la verdad | que la ambigüedad **es del itinerario y no del aprendiz** (ya medido en la variante de cobertura) |

---

## 8 · Tres capas, y quién dispara cada paso

- *Programado*: el banco, la verdad de referencia, la comparación salvo isomorfismo, la prueba de compatibilidad de fusión.
- *Disposición*: el **orden canónico de fusión** (se intenta contra los estados existentes en orden de creación, y gana la primera compatible), el que una fusión aceptada **no se deshace**, L(n), el tope n+1, el segmento de futuro, y la predicción 0 cuando no hay ruta.
- *Adquirido*: la máquina, qué se fusionó con qué, y cuándo dejó de errar.

**¿Quién dispara cada paso y qué sabe este brazo que el organismo no sabría?** (E-02) Nadie de fuera. La fusión se intenta en cada paso de vida, la decide la unidad con la salida que acaba de leer, y no recibe ninguna señal que el organismo no tenga: ni aviso de lesión, ni la máquina verdadera, ni cuántos estados hay. El único número que entra de fuera es el tope de seguridad n+1, que ya era disposición declarada en la Fase 1 y cuyo uso se registra.

---

## 9 · Contadores de actividad

`fusiones_intentadas` y `fusiones_aceptadas`. Si las aceptadas son **0** en la clase n_min ≥ 2, el resultado es **NULO-POR-INACTIVIDAD**: el mecanismo distintivo no corrió y el experimento no prueba lo que dice (E-09).

---

## 10 · Mutantes del gate, antes de lo real

**De capacidad** (deben fallar): *memorizador* (un estado por paso, nunca fusiona) debe fallar la identidad en todo sistema con n_min ≥ 2; *ciego a la observación* (fusiona sin mirar la salida leída) debe fallar en todo sistema con n_min ≥ 2 y terminar con un solo estado.

**Que debe pasar**: *oráculo* (se le da la máquina verdadera) debe pasar identidad y futuro al 100 %.

**De instrumento, con resultado conocido por construcción** (E-15, la guarda que esta fase añadió porque le faltó):
- **tope ejercitado**: la misma campaña con `n_max = 1` debe tocar el tope en **todos** los sistemas con n_min ≥ 2 y en **ninguno** de la clase inerte. Si no, el tope declarado no se está aplicando — que es exactamente lo que pasó en la Fase 1.
- **contador ejercitado**: un sistema de coste conocido de antemano —la clase inerte, donde no hay ninguna fusión que rechazar— debe dar `trabajo` exactamente igual a la longitud de la vida y `fusiones_aceptadas` exactamente igual al número de pasos menos uno. Si el contador se aparta de un número calculable a mano, es el contador el que está roto.

**Resultado de cada uno: se escribe aquí antes de la corrida real.** La ficha no es final hasta que sus mutantes hayan corrido (E-05).

---

## 11 · Puerta, con unidad y campo

- **(A) Coste** · `max(trabajo / vida_len) ≤ 50` y `p99(trabajo / vida_len) ≤ 10`, en los cuatro n. Es la cota que el diseño promete; se verifica, no se descubre.
- **(B) Identificación** · la tasa de `igual_salvo_isomorfismo` sobre `n_min ≥ 2` no cae más de **15 puntos porcentuales** respecto de la de 02 **en el mismo n**, tomada del artefacto cerrado de la Fase 1 (`unidad_minima_05_banco.json`, campo `por_n.<n>.identificadas_con_distincion` sobre `por_n.<n>.con_distincion`). No se congela aquí un número que todavía depende de que n=8 termine: se congela **la regla**.
- **(C) No sobrefragmentación** · `distinciones_en_inertes == 0` y `inertes_con_mas_de_un_estado == 0`, en todo n.
- **(D) Actividad** · `fusiones_aceptadas > 0` en la clase n_min ≥ 2.
- **(E) Clasificación** · cero casos `SIN EXPLICACIÓN`, con el mismo clasificador por comparación de tamaños de la Fase 1.
- **Informe obligatorio y conjunto**: identificación y cola **en la misma tabla**, por n. Una sin la otra no es un resultado (es lo que la Fase 1 casi hizo al poner el criterio de muerte sobre la mediana).

El veredicto lo calcula el programa leyendo esos campos, nunca a mano (E-03).

---

## 12 · Custodia

`unidad_minima_06_fusion.py`; filas a `artifacts/unidad_minima_06_fusion.jsonl`, una por sistema, volcadas en el momento y **reanudables**. **Cada fila guarda la máquina aprendida serializada** —lista de `(estado, letra) → (estado, salida)` más el estado final— y las tablas A y B del mundo, por E-20: si re-derivar cuesta más que guardar, se guarda. En la Fase 1 esto faltó y por eso el futuro de n=8 no se puede recalcular con otra ventana sin repetir el cómputo. resumen en `artifacts/unidad_minima_06_fusion.json` con sha256 del código, versión exacta del intérprete y el hash de las filas **ordenadas por `(n, idx)`**. Sin `random`. Paralelizable con el mismo corredor, con la misma prueba de identidad. Un commit al cerrar, cuando Wis lo autorice.

---

## Enmiendas prospectivas

*(vacío; se rellena si un mutante refuta un criterio antes de la corrida real)*

## Resultado

*(vacío; se rellena al correr)*

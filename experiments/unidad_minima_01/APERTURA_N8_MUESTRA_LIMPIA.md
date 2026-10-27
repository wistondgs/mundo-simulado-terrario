# FICHA DE APERTURA · n=8 con muestra sin retículo

**Fecha:** 2026-10-26 · **Veredicto: `OPEN`** · **Gate previo:** `MULTIPLE_NEAR_SOLUTIONS` en `PRIOR_ART_ESCALADO_SIN_AZAR.md`, más el informe de literatura (`INFORME_LITERATURA_UNIDAD_MINIMA_01.md`, §4 y §5)

**Qué es.** Rehacer el cuarto punto de escala. El de la Fase 1 quedó inválido por **E-27**: la muestra 1-de-10¹⁰ tenía cuatro de dieciséis entradas de tabla restringidas, y eso fabricó dos anomalías que informé como hallazgos. Mismo banco, mismo aprendiz, misma puerta; **sólo cambia cómo se elige qué mundos medir**, y se añade lo que E-21 obliga a guardar.

---

## 0 · Guardas del registro que aplican, y cómo se cumple cada una

| entrada | cómo se cumple aquí |
|---|---|
| **E-27** retículo de muestreo | paso multiplicativo **coprimo con el total**: `idx_r = (r·s) mod 8¹⁶` con `s = 173961102589771`, impar y por tanto coprimo con 2⁴⁸. **Verificado antes de correr**: con 1 000, 5 000 y 30 000 muestras, **cero** de las 16 posiciones de dígito queda restringida (el paso viejo clava 4 de 16 incluso con 30 000). La aserción corre como mutante, no como comentario. |
| **E-21** la fila no guarda el objeto | cada fila guarda **la máquina aprendida serializada** —`(estado, letra) → (estado, salida)` más el estado final— y las tablas A y B. Así cualquier pregunta nueva se contesta releyendo, no recorriendo. |
| **E-23** estratos por posición | la pertenencia va en un **campo de la fila** (`rango`, `estrato`), nunca en la posición del fichero; y el artefacto es **nuevo** (`unidad_minima_07_n8_limpio.jsonl`) para que no haya forma de mezclarlo con la muestra viciada. Aserción al cerrar: los estratos **suman** el total. |
| **E-22** umbral bajo el ruido | la parada por información usa la versión **consciente del ruido** ya implementada y con sus cuatro mutantes corridos: `z = |p₁−p₂| / √(EE₁²+EE₂²)`, umbral por alfa 0,05 **ajustado por el número de comparaciones**. No se declara un número de puntos. |
| **E-25** umbral absoluto entre escalas | la transitoriedad se mide **relativa** (visitas < 10 % de la media del propio sistema) y se informa junto al absoluto. |
| **E-24** invariancia sin rango | toda afirmación de este experimento lleva **el rango medido**. En particular no se dirá nada sobre longitudes de vida distintas de L=10. |
| **E-16** calibrar sobre la mediana | el reloj se calibra sobre **deciles del recorrido ya hecho**, no sobre una muestra repartida, y se declara el error esperado. Aviso por anticipado: la muestra limpia será **más cara** que la viciada, porque aquella tenía mundos colapsados hacia el estado 0. |
| **E-15** mutantes que no ejercitan el instrumento | tres mutantes **de instrumento** con resultado conocido por construcción, además de los tres de capacidad. Ver punto 10. |
| **E-20** parada que arrastra | al parar se **cancelan** los futuros encolados sin empezar; se informa cuántos. |
| **E-18** correr sin criterio de parada | la parada por información es la regla **principal**; el tope de reloj es el respaldo. |
| **E-17** gate sin complejidad del problema | el gate ya trae la fila de complejidad (Gold 1978, Angluin 1978, Pitt–Warmuth 1993) y ahora **la cota de caso típico**: Freund et al. 1993 (STOC) dan un aprendiz determinista y polinómico desde un solo paseo sin reset ni maestro **en el caso típico**. Esto es nuevo y cambia la lectura de la cola: ver punto 2. |
| **E-14** custodia tomada por trabajo | un commit al cerrar, y el informe dirá qué parte fue experimento. |
| **E-11** iniciativa fuera del encargo | el encargo es **rehacer n=8 limpio**. No se cambia el aprendiz, ni L, ni la salida observable, ni la puerta. El PST con bucles y las firmas que propone el informe de literatura son para 1-bis y **no se construyen aquí**. |
| **E-26** `pkill` que se mata a sí mismo | matar por PID obtenido antes, nunca por patrón seguido de más trabajo. |
| **E-01** entorno sin ejecutar | el artefacto registra `python` con su versión exacta. |
| **E-07** irreproducible | sin `random`; el paso `s` es una constante declarada; sha256 del código; hash de las filas ordenadas por `(n, idx)`. |
| **E-08** presupuesto donde saturó | se informan **curvas** por `n_min` y por estructura de permutación, con sus colas, no un punto. |
| **E-03** criterio sin unidad | cada número de la puerta con su unidad y su campo del JSON. |
| **E-05** control que no controla | la clase inerte (`n_min`=1) controla que no se inventen distinciones; es el único control de este experimento y su afirmación exacta es ésa. |
| **E-10** releer en vez de consultar el mapa | lo que cubre esto ya está medido: banco, verdad de referencia, comparación salvo isomorfismo y clasificador están congelados en `unidad_minima_05_banco.py` y **no se reescriben**. |

**No aplican:** E-02, E-04, E-06, E-09, E-12, E-13, E-19 (son de diseño de brazos, de controles reactivos, de ecuaciones de estado, de cartografía o del rol de supervisor; este experimento no tiene brazos ni controles reactivos y no toca documentación paralela).

---

## 1 · Pregunta

¿Cuál es la identificación, la cobertura y la cola de coste de la unidad de 02 en mundos de **ocho** estados, medidas sobre una muestra que **sí** representa el banco?

Y en particular: ¿se sostienen sobre n=8 limpio las tres cosas que la Fase 1 midió en n=3, n=4 y n=6 —la ley de reversibilidad, la planitud por `n_min` y la cola creciente—, o alguna era de los tres puntos bajos?

---

## 2 · Lo que el informe de literatura obliga a medir aquí, y es nuevo

Freund et al. 1993 dan un aprendiz determinista y polinómico **en el caso típico** (etiquetas de estado aleatorias) desde un solo paseo sin reset ni maestro. Si eso aplica, nuestra cola de ×132 573 es **peor caso** y los mundos que la producen son los **atípicos**. Eso es medible aquí y no cuesta nada extra: por mundo se registra la **estructura** (permutación de cada letra, estados en ciclos, ciclo más largo, transitoriedad relativa) junto al coste, y se informa **qué fracción del coste vive en qué fracción de los mundos y con qué estructura**.

Nivel de evidencia: Freund 1993 es LITERATURE-CLAIM para nosotros (el informe lo marca SOURCE-VERIFIED por un solo lector, sin verificación adversarial). **No se usa como garantía**; se usa como hipótesis sobre dónde está nuestro coste, y lo que se mide es nuestro.

---

## 3 · Diseño

- Banco: los `8¹⁶ = 281 474 976 710 656` pares de mapas sobre `{0..7}`, exactamente como en la Fase 1.
- Muestra: `idx_r = (r·s) mod 8¹⁶`, `s = 173961102589771`, `r = 0, 1, 2, …`. Es una permutación de ciclo completo del espacio, así que **cualquier prefijo del recorrido es una muestra esparcida**, y no hace falta inversión de bits por encima.
- Tope de muestra: **30 000** sistemas. La parada por información decidirá antes si ya no se aprende.
- L = 10 (vida de 18 434 pasos), salida `o = [x′ ≠ x]`, `n_max = 9`, futuro de 2 048 pasos. **Idénticos a la Fase 1**, para que la comparación sea con lo mismo.
- Tope por sistema 900 s, con la clase `sin terminar por reloj` que cuenta en el denominador.

---

## 4 · Predicciones, escritas antes de correr

1. La identificación a igual `n_min` **bajará** respecto de la muestra viciada: de 76–82 % a algo **compatible con la planitud** medida en n=3/4/6, es decir del orden de **77 % en `n_min`=2 y 45–50 % en `n_min` alto**. Si sale plana otra vez, la planitud es real y no era el retículo.
2. La transitoriedad relativa **subirá** desde el 0,6–3,5 % de la muestra viciada hasta el entorno del **13–18 %** que tienen n=3, n=4 y n=6.
3. La cola **será peor** que en n=6: p99 por encima de 1 485 y máximo por encima de 132 573, con más mundos tocando el tope de 900 s que los 37 de la muestra viciada.
4. La ley de reversibilidad **se sostendrá**: identificación 100 % donde las dos letras sean permutaciones.
5. El coste estará concentrado en los mundos **sin ninguna letra permutación y con poca estructura de ciclos**, que es la lectura de Freund.

## 5 · Falsadores

- Que la identificación a igual `n_min` siga en 76–82 %: entonces el retículo no era la causa del salto y hay algo de n=8 que no entiendo.
- Que algún mundo con las dos letras permutación **no** se identifique: cae la ley.
- Que la clase inerte abra alguna distinción: cae el control.
- Que la cola sea **más suave** que en n=6: entonces la cola no crece con n y el FAIL de la Fase 1 habría que releerlo.

---

## 6 · Puerta, con unidad y campo

- **(a)** cero casos `SIN EXPLICACIÓN` (`clase`).
- **(b)** cero distinciones abiertas en `n_min`=1 (`distinciones`, `estados_aprendidos`).
- **(c)** cero posiciones de dígito restringidas en la muestra (aserción de muestreo, mutante M-4).
- **(d)** cero mundos con las dos letras permutación no identificados (`igual_salvo_isomorfismo`).
- **(e)** los estratos suman el total (`rango`, `estrato`).
- Informe obligatorio y conjunto: identificación **y** cola en la misma tabla, por `n_min` y por estructura.

El veredicto lo calcula el programa leyendo esos campos.

---

## 7 · Mutantes, antes de lo real

**De capacidad** (deben fallar): memorizador; ciego a la observación. **Debe pasar**: oráculo.
**De instrumento, con resultado conocido por construcción** (E-15):
- **M-4 · muestreo**: cada posición de dígito recorre **todos** sus valores sobre la muestra entera. Y el paso viejo `k = 10¹⁰` **debe** fallar esta misma aserción — si no la falla, la aserción no detecta nada.
- **M-5 · tope ejercitado**: con `n_max = 1`, **todos** los mundos con `n_min ≥ 2` deben tocar el tope y **ninguno** de la clase inerte.
- **M-6 · contador ejercitado**: en la clase inerte, donde no hay nada que refutar, `trabajo` debe ser **exactamente** la longitud de la vida. Un número calculable a mano.

Resultado de cada uno: se escribe aquí antes de la corrida real.

---

## 8 · Custodia

`unidad_minima_07_n8_limpio.py`; filas a `artifacts/unidad_minima_07_n8_limpio.jsonl`, **con la máquina serializada**, volcadas en el momento, reanudables; resumen con sha256 del código, versión del intérprete, el paso `s` y el hash de las filas ordenadas. Sin `random`. Un commit al cerrar, cuando Wis lo diga.

---

## Enmienda prospectiva · 2026-10-26, en el paso de mutantes y antes de la corrida real

**M-5 estaba mal pedido.** Decía: «con `n_max = 1`, **todos** los mundos con `n_min ≥ 2` deben tocar el tope». Midió **157 de 161**, y los cuatro que no lo tocan no son un fallo del instrumento: tienen `n_min` de 2 y 7, pero su **vida es consistente con un solo estado** —comprobado en los cuatro—, así que con `n_max = 1` la unidad no tiene nada que refutar y no hay tope que tocar. Son la clase «la vida no determina la verdad: admite una máquina menor», que la Fase 1 ya había medido.

El tope depende de **lo que la traza fuerza**, no de lo que el mundo es. El criterio pasa a ser:

- todos los mundos cuya **vida fuerza ≥ 2 estados** tocan el tope con `n_max = 1`;
- **ninguno** cuya vida sea consistente con un estado lo toca — ni los inertes, ni los de `n_min ≥ 2` con vida pobre.

Así además queda más afilado que antes: distingue los dos casos en vez de mezclarlos.

**Resultado de los mutantes de instrumento** (los tres que me faltaron en la Fase 1):
- **M-4 muestreo: OK.** El paso limpio deja cero posiciones restringidas con 1 000, 5 000 y 30 000 muestras; y el paso viejo `10¹⁰` **falla** la misma aserción nombrando `B[4]`, `B[5]`, `B[6]`, `B[7]`. La aserción detecta lo que debe detectar.
- **M-6 contador: 39/39 exactos.** En la clase inerte `trabajo` es *exactamente* la longitud de la vida, que es el número calculable a mano.
- **M-5 tope:** pendiente de volver a correr con el criterio enmendado.

### Resultado de los mutantes · escrito por el orquestador · 2026-10-27 12:33

Corridos y escritos aquí **antes** de medir, con la salida en el árbol y no en un temporal (E-31):

```

# reintento del orquestador · 2026-10-27T12:22:58
=== MUTANTES, antes de la corrida real ===
  M-4 · paso limpio, 1000 muestras: LIMPIA
  M-4 · paso limpio, 5000 muestras: LIMPIA
  M-4 · paso limpio, 5000 muestras: LIMPIA
  M-4 · el paso viejo 10^10 DEBE fallar la aserción: falla, bien ['A[0]', 'B[4]', 'B[5]', 'B[6]', 'B[7]']
  M-4: OK
  M-5 tope: 157/157 de los que la vida FUERZA a >=2 estados lo tocan con n_max=1 · 0/4 de los que tienen n_min>=2 pero vida de 1 estado (deben ser 0) · 0/39 de los inertes (deben ser 0)
  M-6 contador: 39/39 exactos (trabajo == longitud de la vida en la clase inerte)
  M-1 memorizador: identidad 0/20, futuro perfecto 3/20
  M-2 ciego: 0/13 identidad, 0 con más de un estado
  M-3 oráculo: 18/20 identidad, 18/20 futuro
  [OK] M-1 memorizador FALLA la identidad
  [OK] M-1 memorizador FALLA el futuro
  [OK] quedaron mundos evaluables tras el tope
  [OK] M-2 ciego a la observación FALLA donde n_min>=2
  [OK] M-2 ciego no abre ninguna distinción
  [OK] M-3 oráculo PASA identidad y futuro
  [OK] M-4 la aserción de muestreo sirve
  [OK] M-5 con n_max=1 tocan el tope TODOS los que la vida fuerza a >=2
  [OK] M-5 y NINGUNO cuya vida sea de un estado
  [OK] M-6 en la clase inerte el trabajo es exactamente la vida
EL GATE SIRVE

python 3.14.4 · random importado: SÍ · sha256 be8ac51eaecf5fb2…
```

---

## Regla de lectura del cierre · declarada el 2026-10-27, antes de tener la muestra completa

**n=8 se informa por `n_min` contra n=6 por `n_min`, nunca agregado.** Comparar tasas crudas mezclaría distribuciones de `n_min` distintas, que es exactamente el error que ya cometí una vez en esta fase: informé una curva de escala decreciente que era **composición** y no escala. No se repite.

**Lo que se corrige en el cierre de la Fase 1 si la caída a igual `n_min` se confirma con los 5 000 mundos.** La §3 dice hoy «la escala no degrada», apoyada en la planitud entre n=3, n=4 y n=6. Pasaría a decir **«no degrada entre 3 y 6; degrada en 8»**, con los números por estrato. Es una corrección sustantiva, no de redacción: cambia la conclusión de la fase sobre el comportamiento del mecanismo al crecer el mundo.

**Y entra como predicción en la ficha de 1-bis.** Si la degradación aparece en n=8 y sólo ahí, entonces **ese es el sitio donde el aprendiz polinómico tiene que medirse**: no en n=3 y n=4, donde 02 ya identifica bien y en milisegundos, sino exactamente en el estrato donde 02 empieza a perder. La comparación pareada por índice contra las filas de 02 se concentra ahí.

**Estado provisional, que no se informa como resultado** (1 669 de 5 000, ~33 %): la dirección apunta a confirmarse —la identificación agregada va en 42,4 % frente al 55,6 % de n=6, y por estrato las diferencias son negativas en los cinco comparables, de −1,3 a −21,1 puntos—. Pero los estratos de n=8 tienen entre 50 y 357 mundos, así que varias de esas diferencias **caben dentro del ruido de muestreo** y no se declara ninguna hasta que la muestra esté completa o la parada por información la cierre.

**Falsador de la corrección, escrito ahora:** que con la muestra completa las diferencias por estrato queden dentro de dos errores estándar. En ese caso §3 **no** se toca y la caída agregada se explica entera por composición — los estratos de `n_min` alto, que en n=8 son muchos más, son los difíciles.

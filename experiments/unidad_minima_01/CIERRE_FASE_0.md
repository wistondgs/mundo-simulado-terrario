# CIERRE DE LA FASE 0 · fijar y completar lo que ya corre

**Fecha:** 2026-10-25 · **Árbol:** `experiment/unidad-minima-01` en `/home/wis/Aplicaciones/worktrees/unidad-minima-01` · **Base:** `master` = `bc05def`

| Ítem | Veredicto |
|---|---|
| 0.1 · Custodia | **hecho**, dos commits, un árbol cada uno |
| 0.2 · Regeneración tras lesión | **FAIL** de la hipótesis original; **PASS** de la reparación única |
| 0.3 · Elección por conveniencia bajo orientación externa | **PASS** |
| 0.4 · Determinismo y entorno | **hecho**, abajo, con dos hechos del plano corregidos |

---

## 0.1 · Custodia

- `f25552f` en `experiment/unidad-minima-01`: los dos experimentos del 24-oct, sus artefactos y el plano. Antes de sellarlos los regeneré: los dos JSON salieron **idénticos** a los de ayer, bajo un intérprete distinto. Nivel de evidencia COMPUTATIONALLY-REPRODUCED, ahora con custodia.
- `f69815f` en `experiment/level18-predictive-state-01`: `LEARNER-19-v1` tal como terminó. Llevaba desde el 23-oct sin trackear en un worktree que git daba por *prunable*. No se desarrolla más ahí.
- Borrado el `docs/LEVEL18_ANALISIS_CAUSA_RAIZ.md` vacío del checkout principal, comprobado antes en 0 bytes y sin trackear, con el documento real de 131 líneas vivo en `9b7bdb0`. `.agents/` y `.codex/` no se tocaron.

**Aviso que no estaba en el plano:** la lista de worktrees tiene **18 entradas marcadas `prunable`**, no sólo la de L19. Un `git worktree prune` se llevaría también los de la ETP, la autopsia causal y la enmienda A1b. L19 ya está a salvo; los demás no los he tocado.

---

## 0.2 · Regeneración tras lesión · FAIL de lo escrito, PASS de la reparación

Lesión de la hipótesis en t ∈ {64, 128, 256, 512, 1024} del mundo aliasado, con el resto de la
misma vida como corriente de recuperación. Pasos de **vida nueva** hasta el último error:

| brazo | 64 | 128 | 256 | 512 | 1024 |
|---|---|---|---|---|---|
| sham (no se borra nada) | 0 | 0 | 0 | 0 | 0 |
| con traza, repaso disparado desde fuera | 0 | 0 | 0 | 0 | 0 |
| **con traza, sin repaso** | **7** | **8** | **14** | 10 | 2 |
| **sin traza** | **7** | **8** | **14** | 17 | 6 |
| con traza, relectura disparada por sí misma | 0 | 0 | 0 | 0 | 0 |

**Lo que falló, y es un resultado, no un defecto de instrumento.** El falsador escrito en la
ficha §5 se cumplió: conservar la experiencia no abarató la vida nueva. En 3 de los 5 momentos
los dos brazos gastaron **exactamente lo mismo**; sólo en 2 el brazo con traza fue mejor.

**Por qué.** La traza no es inerte: cuando por fin llega una refutación, el repaso reconstruye
la máquina correcta y lo paga en repaso, hasta 6137 pasos. Lo que no hace es evitar los errores
**anteriores** a esa refutación. La unidad de 02 sólo relee su vida cuando se queda sin
alternativas; hasta entonces se equivoca igual que si no recordara nada. **El valor de lo
retenido depende de que algo dispare la relectura, y la unidad no tenía ese disparo.**

El brazo que cuesta 0 y venía en el plano como «con traza → 0 pasos» tiene un problema que hay
que decir: su disparo viene de fuera, porque soy yo quien sabe que hubo lesión. Un organismo no
recibe ese aviso, así que ese 0 estaba comprado con una señal suministrada, no era capacidad de
la unidad.

**La reparación única** (la que permite la regla de cierre; no se aflojó ningún criterio) añade
un disparador **interno** que la unidad puede ejecutar con lo que ya tiene: al ir a predecir, si
su hipótesis está vacía y su memoria no, se relee antes de responder. No es un detector de daño;
es notar que no tiene modelo y sí tiene recuerdos. Resultado, contra la predicción escrita antes:
0 pasos de vida nueva en los cinco momentos, máquina idéntica a la previa, futuro de vuelta en
1,0000, y el coste pagado entero en relectura (1 autorelectura, 6 refutaciones, 79 pasos de
repaso: exactamente lo que costó el nacimiento). Su falsador no se cumplió.

**Dos hallazgos laterales que conviene no perder.**

1. Sin traza, en t=512 y t=1024 la máquina recuperada **no es** la de antes y aun así el futuro
   de 6656 pasos vuelve a 1,0000: misma conducta, otras etiquetas. Es identificabilidad salvo
   isomorfismo, que es justo lo que la puerta de la Fase 1 ya tiene previsto exigir.
2. El control reactivo **no admite** el brazo «con traza», y no por omisión mía: su tabla es a la
   vez su hipótesis y su experiencia. La separación entre lo que se cree y lo que se ha vivido es
   precisamente lo que la unidad tiene y él no, y es la que esta lesión deja ver.

**Segundo criterio en FAIL**, y lo dejo en FAIL en vez de reescribirlo: en el mundo del bit
inerte pedí «sin traza, no más de 2 pasos» y midió 4, 1, 3, 2, 3. El error es de unidades, mío:
acoté un *número de pares letra→reacción* por reaprender y lo que mide el programa es el *paso*
del último error, que depende de cuándo aparecen A y B en lo que queda de vida. Lo que ese mundo
sí controla —que no se reabra ninguna distinción— pasó: 1 estado en los cinco momentos y los
cinco brazos.

---

## 0.3 · Elección por conveniencia bajo orientación externa · PASS

Meta impuesta desde fuera, palabras recorridas en orden shortlex hasta longitud 4, exhaustivo.
La robustez se mide **ejecutando** la palabra elegida en el mundo real desde los dos estados
ocultos, no preguntándole al agente si cree haber acertado.

Mundo aliasado, meta «que la próxima reacción a B sea 1» (mínimo real del mundo: `BA`, 2 pasos):

| elector | elige | cumple desde el estado actual | desde los dos estados |
|---|---|---|---|
| unidad, criterio robusto | **`BA`** (2, mínima) | sí | **sí** |
| unidad, desde el estado que cree ocupar | `A` (1) | sí | no |
| unidad lesionada | — declara insatisfacible | — | — |
| reactivo | `A` (1) | sí | **no** |

La unidad halla la palabra más corta que cumple la meta **desde cualquier estado**, que ninguna
letra sola realiza. La lesionada no encuentra ninguna: con un solo estado su predicción de B es
la mayoritaria y es 0. El reactivo elige `A`, que le funciona desde donde está por donde acabó
su vida y falla desde el otro estado: acierta sin poder garantizarlo, que es la diferencia que
había que medir.

Los dos extremos acotan el caso interesante y se informan: con la meta «reacción a A = 1» en el
mundo aliasado todos responden `ε` porque A reacciona 1 siempre (trivial), y en el mundo del bit
inerte con la meta sobre B los cuatro declaran **insatisfacible** en vez de inventar una palabra.
En el mundo visible con la meta sobre A el reactivo **sí** cumple desde su estado: el test
discrimina y la ventaja de la unidad en el mundo aliasado es del aliasing, no de ser mejor.

---

## 0.4 · Determinismo y entorno

Los cuatro programas: sin `random` importado, dos corridas un hash, resultado a JSON con el
sha256 del código. Comandos exactos, desde `experiments/unidad_minima_01/`:

```
python3 unidad_minima_01.py              # sha256 13c8870eb040918c…
python3 unidad_minima_02_incremental.py  # sha256 b4b67a111fc632a1…
python3 unidad_minima_03_regeneracion.py # sha256 510eee7620e3eb2c…
python3 unidad_minima_04_eleccion.py     # sha256 a437d5167a986931…
```

**Dos hechos del plano son falsos y hay que corregirlos antes de la Fase 1.** El plano §1 dice
usar `"/home/wis/mundo simulado terrario/.venv/bin/python"` como Python 3.12 con torch y numpy:

1. Ese `.venv` se construyó el 8-sep para **3.12.3** con `/usr/bin/python3.12`, y ese intérprete
   **ya no existe** en la máquina: `/usr/bin/python3` es ahora **3.14.4**. El `python` del venv es
   un enlace a `python3`, así que resuelve al 3.14 y sus paquetes, compilados para cp312 y vivos
   en `.venv/lib/python3.12/site-packages`, quedan invisibles.
2. Por tanto ese intérprete **no tiene numpy ni torch**, y `scripts/cartografia_check.py` muere
   con `ModuleNotFoundError: numpy` al importar `terrario.experiment.controller`. El gate de
   cartografía está caído en esta máquina ahora mismo.

Nada de las fases 0 a 3 lo necesita —los cuatro programas son sólo biblioteca estándar y corren
en el 3.14.4—, y la reproducción de hoy bajo un intérprete distinto del de ayer es, de hecho,
evidencia más fuerte del determinismo. Y la receta que sí funciona ya estaba en el árbol de L19,
sin declarar: `PYTHONPATH=.deps-level19 python3` carga numpy 2.5.4 sobre el 3.14. Ese es el
patrón que rescata también el gate de cartografía, si se decide rescatarlo.

---

## Decisiones de Wis aplicadas en esta fase

1. Trabajo en el árbol de la unidad; L19 commiteado sólo para custodia, sin desarrollo. **Hecho.**
2. Solucionador SAT admisible con semilla y versión fijas, como disposición suministrada, con
   cruce obligatorio contra el retroceso propio en |S| ≤ 4. **Anotado para la Fase 1**; aquí no
   hizo falta ninguno.
3. Salida observable del banco: sólo el bit de cambio. **Anotado para la Fase 1.**
4. Borrar el fichero vacío. **Hecho**, con la comprobación previa que pediste.

## Lo que la Fase 0 deja escrito para la Fase 1

- **Minimalidad exacta no es gratis al escalar.** Hallar la palabra de reset más corta es
  NP-difícil y coNP-difícil, completa para DP, e inaproximable dentro de n^(1−ε) para todo ε>0
  (Gawrychowski & Straszak, arXiv 1408.5248, resumen leído). El BFS exhaustivo de 0.3 es legítimo
  con 2 estados y palabras de longitud ≤ 4, y deja de serlo con |S| hasta 8. La ficha de apertura
  de la Fase 1 tiene que elegir: algoritmo voraz declarado (y que no da el mínimo) o cota de
  longitud declarada. No se hereda el criterio de 0.3.
- **El disparo de la relectura es ahora parte del organismo**, no del andamio, y la Fase 2
  («que una distinción abarate la siguiente») depende de él: si conservar sólo sirve cuando algo
  dispara la relectura, el brazo «conserva» de la Fase 2 debe declarar **cuál** es su disparo, o
  medirá una capacidad que viene de fuera.
- **Tres criterios de estas fichas salieron mal escritos** y los tres los encontró el paso de
  mutantes antes de correr lo real, que es para lo que sirve. Tres en una sesión dice que los
  criterios se están escribiendo demasiado rápido; queda anotado en vez de disimulado.

## Una sola pregunta para Wis

¿Commiteo 0.2, 0.3 y 0.4 —los dos programas, sus dos artefactos, los dos gates, las dos fichas
con sus enmiendas y este cierre— en `experiment/unidad-minima-01`?

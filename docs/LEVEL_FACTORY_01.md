# `LEVEL-FACTORY-01` · la parte mecánica del ciclo, y sólo ésa

Rama `factory/level-factory-01`, árbol propio, base `7ac43fb` --el mismo commit
del que forkean 1.3, 1.4 y la fusión, así que la fábrica es hermana de las
campañas y no descendiente de ninguna.

> **Regla de admisión.** A esta fábrica sólo entra lo que ya falló al menos una
> vez, con su instancia nombrada. Nada entra por simetría.

---

## 1 · Lo que se construyó, y el defecto que lo obliga

| comprobador | defecto medido que lo origina | dónde consta |
|---|---|---|
| `plan`    | 1.5 exige `binding` y `one_tick_memory`, que viven en árboles hermanos; se descubrió a mano después de cerrar 1.4 | la fusión `141df74` existe precisamente por eso |
| `seeds`   | cada linaje reescribe a mano la unión de todo lo gastado, offsets derivados incluidos | `test_level14_lineage.py`, seis términos que crecen por nivel |
| `gates`   | el guion evaluaba 7 gates donde el preregistro sellaba 11, y gastaba `L14-11` en las sondas cuando ese número es de la pasividad | `68d852d` |
| `vacuity` | `assert sin_asignar == sin_asignar` · y «un `str(s) in fuente` caza su propia documentación; ya ocurrió dos veces hoy» | informe 1.4 §7 · `test_level11_lineage.py` |

```bash
python -m factory plan          # qué está listo, qué exige componer antes
python -m factory gates         # inventario sellado contra inventario evaluado
python -m factory seeds --reserve 8
python -m factory vacuity <ruta>…
```

## 2 · El grafo · dos relaciones que no son la misma

`requires` son **capacidades**: lo que el organismo necesita tener para que el
experimento signifique algo. `inherits` son **nodos**: de qué árbol se forkea.
`holds` se calcula por `inherits`, nunca por `requires`.

Confundirlas es lo que esconde una fusión. Con la distinción puesta, el
planificador deduce sin que nadie se lo diga:

```
COMPOSICIÓN PRIMERO · las dependencias existen, pero en árboles distintos
      change_detection    exige [binding, direction, one_tick_memory, proximity, sensorimotor]
                          reunir [fusion_hm, level14] · no consume decimal
```

Las cinco capacidades están verificadas. Ninguna instancia las tiene todas.
`verificado` y `disponible en el mismo organismo` son cosas distintas, y ésa es
la que hace falta antes de un decimal 1.5.

## 3 · Lo que encontró al encenderlo

**Tres campañas verificadas tienen el inventario de gates divergente.** El
mismo defecto que 1.4 reparó en `68d852d`, y que en las otras tres nunca se
reparó porque nadie volvió a contarlos:

| campaña | sellados | evaluados | ausentes del informe | número gastado en otro gate |
|---|---:|---:|---|---|
| 1.2 | 12 | 10 | `L12-1` observabilidad · `L12-9` falsabilidad | --  (7 abreviaturas) |
| 1.3 | 14 | 11 | `L13-1` observabilidad temporal · `L13-2` aislamiento de la presentación · `L13-10` falsabilidad de atajos | -- (3 abreviaturas) |
| 1.4 | 11 | 11 | -- | reparado en `68d852d` |
| fusión | 10 | 9 | `F-2` `M` sin deriva | **`F-9` sellado «pasividad», evaluado «el tick hace falta»** |

**Ningún valor medido se mueve.** Lo comprobado: los gates ausentes del informe
**sí están verificados en contratos** --`F-2` en
`test_la_memoria_es_copia_literal_del_original_congelado` con su fixture
negativa; `L13-1` en `test_la_consulta_no_acepta_cue_externo`; `L13-2` en
`test_la_presentacion_no_puede_actuar`--. Lo que diverge es la taxonomía: el
informe de ejecución y el oráculo sellado dan números distintos de gates para
el mismo experimento, y quien lea después hereda uno de los dos.

El caso de la fusión es el grave, porque es el de 1.4 otra vez: `F-9` está
sellado para pasividad y el guion lo gasta en la necesidad del tick. La
pasividad está verificada --`test_las_huellas_no_se_mueven_al_consultar`--,
pero no bajo su número.

**El diseño de cada nivel nunca existió como artefacto.** `plan` lo reporta
como hueco en 1.1, 1.2, 1.3, 1.4 y la fusión: hay auditoría, hay oráculo y hay
informe, pero el diseño vivió en la conversación. Y 1.1 y la fusión se
verificaron sin auditoría adversarial registrada.

## 4 · La validación de los comprobadores

Un comprobador que sólo puede aprobar es exactamente el defecto que esta
fábrica dice cazar, así que cada uno lleva su fixture negativa. Dos llevan algo
mejor que una fixture inventada: **la regresión histórica**.

```
contra a4eef15 (el commit real, antes de reparar)
  FALTA      L14-1 · atributos
  FALTA      L14-4 · marginales
  FALTA      L14-6/7 · preservación
  FALTA      L14-9 · necesidad
  RENOMBRADO L14-11 · sellado «pasividad» · evaluado «probes exactos»

contra 68d852d (el commit que lo reparó)
  inventario conciliado · 11 gates, mismos identificadores y mismos nombres
```

El linter de vacuidad se afinó dos veces contra el repositorio real, porque su
primera versión daba 56 hallazgos y la mayoría eran falsos:

* `fingerprint(mk()) == fingerprint(mk())` **no** es una tautología: construye
  dos organismos y exige la misma huella. Se separa como informativo.
* leer texto **es** correcto cuando lo leído no es fuente Python: del HTML
  servido no hay árbol sintáctico que mirar. Sólo se señala si el ámbito lee
  ficheros `.py`.

Sobre el linaje vivo da **cero**, que es el resultado correcto: los dos
defectos reales se encontraron y se repararon antes de commitear. Su valor es
prospectivo, y decirlo así es parte del resultado.

## 5 · Lo que deliberadamente no se construyó

La propuesta pedía además siete agentes con una máquina de estados y ocho
artefactos por nivel. Eso ya existe en este repositorio:

```
terrario/lab/   103 módulos · 23 284 líneas
                hypothesis factory · experiment design compiler
                preregistration state machine · evidence admission
                capability passport · execution state machine
```

Y el linaje 1.0 → 1.4, que es la ciencia real de los últimos tres días, toma
de ahí **un solo símbolo**: `PairedResult`, un contenedor de resultados
emparejados, en el guion de 1.0. De la fábrica de hipótesis, el compilador de
diseños, la máquina de estados de preregistro y la admisión de evidencia no
importa nada, en ninguna de las cinco campañas.

No es un argumento contra automatizar: es la medida de qué se automatiza. Lo
que se construyó aquí son cuatro consultas sobre artefactos que las campañas ya
producen. Lo que no, es una segunda maquinaria que las campañas tendrían que
adoptar --y la primera demuestra que no las adoptan.

**Y el cuello de botella no está donde la propuesta supone.** Cinco campañas en
un día, `11:57 → 18:24`: 1.1, 1.2, 1.3, 1.4 y la fusión. La más lenta fue 1.4,
`17:24 → 18:24`, y lo fue por la auditoría adversarial que encontró que el
banco de evaluación no estaba especificado y que ahí vivía el atajo. Ése es el
paso que produce el valor, y es el que exige leer el repositorio real y hacer
la aritmética exacta. Automatizar alrededor de él está bien. Automatizarlo a él
es cambiar la pregunta sin darse cuenta.

## 6 · Lo que queda en la mesa

* **Reconciliar tres inventarios.** 1.2, 1.3 y la fusión, con un commit como
  `68d852d` cada uno. No cambia ningún número medido.
* **Sustituir las uniones de semillas escritas a mano** por una consulta al
  registro, en el próximo linaje que se abra --no reescribiendo hacia atrás.
* **`python -m factory gates` en el cierre de cada campaña**, antes de escribir
  el informe. Es la comprobación que habría evitado los cuatro casos.

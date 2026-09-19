# `LEVEL1.3-ONE-STEP-REFERENCE-PERSISTENCE-01` · informe

**`LEVEL13_STATUS = VERIFIED`** · los once gates en las ocho semillas.

Rama `experiment/level13-one-step-reference-persistence-01`, nacida de `ef67ee5`
--el cierre exacto del Nivel 1.1--. Oráculo sellado en `09c1d80`, **antes** de
existir una sola línea de código. Semillas `90000011 … 90000018`.

---

## 1 · Qué clase de hito es · dicho antes de enseñar números

**El mecanismo de memoria lo suministró la arquitectura.** El organismo no
descubrió que necesitaba memoria, ni cuándo escribir, ni qué guardar, ni cuánto
tiempo. Todo eso son capacidades distintas y ninguna se midió aquí.

Y **no hay aprendizaje**: el nivel no tiene `N_TRAIN`, ni dosis, ni cobertura, ni
un solo parámetro estimado. Eso elimina de raíz toda la clase de errores que
dominó el Nivel 1.2 --umbrales, tolerancias heredadas, ruido de muestreo--.

Lo que sí es nuevo respecto del 1.1 es la pregunta: **¿puede el organismo
mantener una variable relevante fuera de la entrada durante un intervalo y seguir
usando correctamente sus capacidades previas?**

## 2 · Genealogía · 1.3 es hermano de 1.2, no su hijo

```
1.0 → 1.1 → 1.2      proximidad cualitativa
1.0 → 1.1 → 1.3      persistencia de un paso
```

La rama nace de `ef67ee5` y no de `3697c5f`, aunque el árbol de código de los dos
sea **idéntico** (verificado: `git diff --stat ef67ee5 3697c5f -- terrario tests
scripts` sale vacío). `3697c5f` pertenece documentalmente a la campaña 1.2, y
aquí se preserva también la genealogía experimental.

En este árbol `terrario/level12/` **no existe en disco**. Por eso «1.3 no depende
de 1.2» es propiedad estructural y no aserción, y hay dos contratos que lo
comprueban: el directorio no existe, y ningún módulo lo importa.

## 3 · Uso de la historia · banco crítico

```
o_present = (1,0,0,0)   →   tick   →   o_query = (0,0,0,0)

brazo                 R_history    vs suelo
FULL_13                  1.0000     +0.7500
PRESENT_CUE              1.0000     +0.7500      ← techo y control positivo
SHUFFLED_HISTORY         0.2500     +0.0000
NO_MEMORY                0.2500     +0.0000
FROZEN_13                0.2500     +0.0000
TICK_OMITIDO             0.2500     +0.0000
```

**Mismo presente, distinta historia.** Las cuatro filas del banco comparten
observación de consulta; lo único que las distingue es qué se vio un tick antes.

**Los cuatro empates en `0.25` estaban preregistrados** y no son hallazgos: son
la misma ausencia de canal por cuatro vías distintas. Y el suelo es exacto por
una razón que conviene no olvidar: para cualquier política que ignore la
historia, `R = ¼ Σ_a P(a|o) = ¼` **sea cual sea la forma de `P`**. Da igual que
los cuatro scores se declaren empatados o que haya un máximo único. **Es un suelo
inmune al umbral de detección de empates** — en el Nivel 1.1 hizo falta
`alignment_rate_expected` precisamente porque allí los empates sí movían el
número.

## 4 · El canal temporal

```
fidelidad del contenido   F_M        1.0000
información en memoria    I(G;M)     2.0000 bits
paridad de política       D_π        0.0e+00      ← bit a bit, sobre 64×4 puntos
fuga del presente         I(G;o_q)   0.0000 bits  ← identidad del banco
fuga de la presentación   I(G;o_p)   0.0000 bits
```

`I(G;o_query) = 0` no es una estimación con un estimador: las observaciones son
constantes en el banco, así que es una **identidad**. Lo mismo `I(G;o_present)`.

`D_π = 0` es exacto por composición: si `peek` devuelve exactamente el token,
`J_memory(o,g,a)` y `J_present(o,g,a)` son la misma llamada con los mismos
argumentos.

**Sonda del presente**, con el cue recordado fijo y cambiando sólo `o`:

```
score con la dirección recordada LIBRE       0.9860
score con la dirección recordada BLOQUEADA   0.0010
movimiento de Q al cambiar o                 0.0e+00      ← exacto
```

El cuerpo participa: la memoria dice qué dirección, y `B` dice si es realizable.
Cuando no lo es, el score se hunde y el agente **no inventa una segunda ruta** —
eso sería pathfinding, que no pertenece a este nivel.

## 5 · El gate que certifica el constructo

**L13-13 · omitir el `tick()` hunde al brazo completo hasta el suelo.**

Sin él, lo demostrado sería «hay un registro consultable», no «hay persistencia a
través de un intervalo». La auditoría previa encontró que `R(c,0)` --leer antes
del tick-- **no estaba definida** en la especificación, y que si devolviera el
cue, un arnés que se saltara el tick pasaría L13-4 y L13-5 igual de verde.

Adjudicado `R(c,0) = NONE`. Y hay fixture negativa: `ImmediateMemory`, un
registro consultable al instante, obtiene `1.0000` con el tick omitido y por
tanto **suspende** ese gate. Es el registro que este nivel explícitamente no
demuestra.

## 6 · Integridad

```
linaje 1.1 intacto en las 8            True
retención exacta en los 4 cues         True
horizonte contenido tras 2 ticks       True
ensayos que empiezan EMPTY             1.00
leer no consume                        True
```

**Cero azar nuevo.** El banco se enumera --4 ensayos, 64 combinaciones, 16 pares--
y ninguna métrica consume RNG. El núcleo heredado no expone `act`, así que ni
siquiera existe la vía por la que en 1.1 el muestreo del desempate devolvió
`0.5000` frente a una esperanza de `0.4688`.

## 7 · Lo que la auditoría previa encontró, antes del código

Cinco hallazgos. **Dos habrían producido un experimento que aprueba en silencio.**

| hallazgo | consecuencia si no se repara |
|---|---|
| §7 y §10 contra §30 y §31: ¿la consulta borra? | tres métricas leen el mismo slot; la primera lo vaciaría y **la pasividad caería contra el uso de historia en la misma corrida** |
| `R(c,0)` sin definir | un `tick()` omitido pasaría todos los gates: el nivel entero sin probar |
| `write` con una no-entrada | `MEMORY_EARLY_ERASURE`, que ya estaba en la lista de paradas |
| L13-2 vacío en el camino nominal | el banco no instancia mundo: el gate vigila objetos que no existen |
| `o_present` sin especificar | un registro indexado por la observación pasaría sin que nadie lo notara |

El cuidado de `write` no era teórico: **`CueToken` y `Direction` son los dos
`IntEnum` con los mismos valores**, así que `CueToken.C0 == Direction.UP` es
cierto al comparar. Sólo `isinstance` los distingue, y hay contrato que lo deja
escrito.

## 8 · Defecto hallado construyendo · y es una reincidencia

**Dos de mis contratos cazaron su propia documentación.**

- `test_ningun_fichero_del_13_menciona_al_12` hacía `grep level12` y caía contra
  el docstring de `inherited.py`, que dice justamente que el Nivel 1.2 no existe
  en este árbol.
- `test_la_presentacion_no_puede_actuar` buscaba `"act"` en el texto de la
  función y lo encontró dentro de la palabra **«actúa»** del docstring.

Es **exactamente** la clase que el handoff del linaje ya documenta —«tres guardas
que escaneaban texto cazaban su propia documentación»— y la reparación era la ya
conocida: recorrer el AST, porque **un import es un nodo y una frase no**. Que
haya vuelto a ocurrir teniéndolo escrito dice algo útil: una guarda basada en
texto es frágil por construcción, no por descuido, y conviene tratarla como
prohibida y no como desaconsejada.

## 9 · Qué está permitido afirmar

> El Agente Nivel 1.3 conservó durante exactamente un tick información sobre una
> referencia direccional previamente percibida y utilizó esa información durante
> una consulta en la que la referencia ya no estaba disponible externamente y la
> entrada sensorial había cambiado, manteniendo intactas sus adquisiciones
> sensorimotoras y direccionales anteriores.

**Obligatorio junto a ella:**

> El mecanismo de persistencia fue suministrado por diseño. El experimento no
> demuestra que el agente inventara autónomamente memoria.

**Precisión temporal:** «un paso» significa **un tick del registro con cambio de
la entrada sensorial**. El banco no instancia mundo, no hay dinámica intermedia y
no hay interferencia. No es un paso motor.

**No autorizado:** memoria de trabajo general, memoria episódica, memoria
espacial, representación del tiempo, conciencia temporal, continuidad de
objetivos, planificación, navegación, selección de recuerdos, almacenamiento
aprendido, olvido aprendido, consolidación, memoria multietapa.

## 10 · Ficheros y reproducción

```
terrario/level13/     memory · inherited · agent · trials · metrics · experiment
scripts/level13_one_step_persistence.py
tests/test_level13_lineage.py     14 contratos
tests/test_level13_memory.py      33 contratos

suite del linaje 1.0 → 1.1 → 1.3:  93 contratos verdes
terrario/level1/ y terrario/level11/: sin un solo cambio desde ef67ee5
terrario/level12/: no existe en este árbol
```

```bash
cd /home/wis/level13-persistence-01
PY="/home/wis/mundo simulado terrario/.venv/bin/python"
OMP_NUM_THREADS=2 "$PY" -u scripts/level13_one_step_persistence.py
OMP_NUM_THREADS=2 "$PY" -m pytest tests/test_level13_*.py -q --no-header -p no:cacheprovider
```

## 11 · De qué tamaño es la adquisición

Cuatro cues equiprobables: `H(G) = log₂4 = 2 bits`, más el estado de control
`EMPTY`/`HELD`. Ésa es la escala exacta, y es la más pequeña del linaje --el 1.1
adquirió `log₂(4!) = 4.58` bits de correspondencia, el 1.2 cuatro parámetros
continuos--.

Pero el tamaño no es lo que distingue a 1.3. Lo que distingue es que **por
primera vez el organismo usa algo que ya no está delante**. Los tres decimales
anteriores computaban sobre la entrada del instante; éste computa sobre una
variable que sobrevivió a un intervalo y a un cambio de la entrada sensorial.

Que el registro se lo diéramos nosotros es precisamente lo que hay que seguir
diciendo en voz alta.

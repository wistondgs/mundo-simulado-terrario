# Cierre del backlog operativo · tres trabajos

**2026-09-21** · `experiment/cognitive-live-observatory-01`

Los tres pendientes que quedaron nombrados al cerrar la fase de cartografía.
Ninguno era una pregunta abierta de diseño: los tres eran afirmaciones del mapa
que nadie había puesto a prueba.

---

## Resumen

| # | trabajo | veredicto | commit |
|---|---|---|---|
| 1 | catálogo de composición roto | reparado · el catálogo era de A4 y lo pedía A5 | `bbaa3e5` y anteriores |
| 2 | paridad `run_step` ↔ `CausalRuntime.step` | **coinciden** · cuarenta pasos, cero divergencias | `7b25815` |
| 3 | tres inventarios de gates divergentes | **saldado** · nada estaba sin verificar; divergía la taxonomía | `3ef016c` · `32d400f` · `a1f180b` · `570478f` |

---

## 1 · El catálogo de composición

Cerrado antes de este tramo. Queda aquí por completitud del backlog: el
catálogo ofrecía `use_curiosity` —una adquisición de A5— dentro de la
configuración de A4, y `catalogue()` levantaba `KeyError` con tres pruebas en
rojo.

La reparación siguió la ontología del linaje en vez de parchear la clave:
A0–A4 son clases hermanas y A5 es la única herencia real, así que el catálogo
pasó a ser **por organismo**
([agent_composition.py:40](terrario/lab/agent_composition.py:40)), con
`config_for` cerrando en falso ante un agente desconocido
([:149](terrario/lab/agent_composition.py:149)) y `concepts_for` devolviendo
sólo lo que ese organismo lee de verdad
([:163](terrario/lab/agent_composition.py:163)).

Efecto lateral que importa: una clave conocida pero **ajena** ya no se ignora
en silencio, se rechaza nombrando a su dueño.

---

## 2 · Paridad de las dos superficies del paso

### La pregunta

El Atlas 03 nombró tres puntos donde el paso del banco experimental podía
separarse del autoritativo —el contrato de acción, el RNG exógeno y el
lifecycle— y registró como desconocido si de hecho se separan. Nada forzaba la
respuesta: el fichero de paridad que existía comparaba `run_step` **consigo
mismo**.

### Cómo se respondió

Misma condición inicial, mismo organismo guionizado, mismo T0, el escenario
sobre el que el banco **declara** ser exacto —`d0_differences`, sin lifecycle—,
y comparación paso a paso de la verdad del mundo: tiempo, versión de reglas,
posición, energía, vivo, conjunto y posiciones de objetos, `state_hash` y
terminación
([test_world_runtime_parity.py:311](tests/test_world_runtime_parity.py:311),
con las dos rutas en
[:273](tests/test_world_runtime_parity.py:273) y
[:288](tests/test_world_runtime_parity.py:288)).

### El resultado

**Cuarenta pasos, cero divergencias.** No hay primer campo divergente que
reportar.

Las tres divergencias que el Atlas 03 nombró son **inertes bajo estas
condiciones**: el contrato de acción es no-op en T0, el RNG exógeno no se
consume, y el lifecycle está apagado en las dos rutas porque el banco no lo
soporta.

### Lo que esto NO dice

No demuestra equivalencia general. El caso con lifecycle queda **controlado
fuera, no igualado** —el banco no lo soporta, así que no hay con qué
compararlo—.

### El agujero de T1, que resultó inalcanzable

El Atlas 03 marcó como hueco latente que `capability` no mira el modo de
direccionamiento. Sigue siendo cierto, y resulta que el hueco está cerrado por
**dos puertas independientes**, ahora fijadas en prueba
([:328](tests/test_world_runtime_parity.py:328)):

1. `ScientificTrialIdentity` sólo admite claves `use_*` **booleanas**, así que
   `addressing_mode` no cabe en la identidad de la corrida —levanta
   `ValueError`—;
2. el controlador construye el organismo con su propio `agent_config`, que en
   el banco está **vacío**, más `num_channels` y `view_size`.

El modo resultante es `T0_DIRECTIONAL`. Si alguna puerta se abre, la prueba se
rompe ruidosamente en vez de producir un brazo T1 paralizado que se leería como
«T1 rinde mal».

### Lo que apareció al escribirlo

`CausalRuntime.step` llama a `agent.get_trace_events()`, que `run_step` no
exige. El banco pide del organismo una pieza de interfaz que la ruta
autoritativa no pide.

---

## 3 · Los tres inventarios de gates

### La pregunta

1.2, 1.3 y la fusión tenían el inventario de gates divergente entre el oráculo
sellado y el informe de ejecución. Sólo 1.4 había sido reconciliado. La deuda
llevaba declarada desde el Atlas 04 sin que nadie hubiera abierto los ficheros
para ver **de qué clase** era.

### El resultado, y es el mismo en los tres

**Nada estaba sin verificar.** Todas las filas selladas se comprobaban en algún
sitio. Lo que divergía era la taxonomía: el diccionario `gates()` —que es lo
que el informe imprime y lo que un lector cuenta— mostraba un subconjunto.

| campaña | sello | guion antes | dónde estaban | ahora |
|---|---|---|---|---|
| 1.2 | 12 | **10** | `L12-1` y `L12-9`, en contratos | 12 |
| 1.3 | 14 | **11** | `L13-1`, `L13-2` y `L13-10`, en contratos | 14 |
| fusión | 10 | **9** | `F-2` en contratos; `F-9` en contratos **sin número** | 10 |

En 1.2 había además una **cuarta** cifra: la cabecera del guion decía «once
gates», el diccionario tenía diez y el informe los llamaba «los diez gates
**evaluables**» —una palabra que reconocía la brecha sin cerrarla—.

### La fusión no era una ausencia, era una usurpación

El guion usaba **`F-9` para «el tick hace falta»**. El sello le asigna ese
número a la **pasividad**, y lista omitir el tick entre las seis fixturas
negativas obligatorias.

Ascender una fixtura a gate numerado no añadió rigor: le quitó el sitio a otra
cosa y dejó la pasividad fuera del inventario **con su número aparentemente
cubierto**. Quien contara nueve filas y viera `F-0`…`F-9` habría concluido que
faltaba una sola. El número robado había llegado también a los contratos.

Es la lección que más vale la pena guardar: **un recuento que cuadra menos uno
puede esconder una sustitución más una omisión.** Lo que hay que comparar es el
conjunto de identificadores, no el tamaño del conjunto.

### Lo que apareció al abrirlos

* La mitad de `F-9` que nada comprobaba era **«cero RNG nuevo en las
  métricas»**. El factorial y el Brier son cerrados por diseño, así que un
  generador dentro de `organism/metrics.py` convertiría la medición en una
  realización más y el informe seguiría llamándola exacta. Hoy se comprueba por
  AST, en `organism-fusion-hm-01 · terrario/organism/experiment.py:196`.
* La fixtura falsa de `L12-9` estaba **duplicada**: una copia en el fichero de
  contratos y ninguna en el guion. Dos definiciones del mismo mundo falso son
  dos gates con el mismo número; ahora vive en `stream.py` y las dos la
  importan.

### El invariante, verificado y no afirmado

**Ningún número medido se movió en ninguna de las tres.** Comprobado por diff
de la salida completa contra la corrida previa:

```
1.2       +2 líneas   (L12-1, L12-9)          resto idéntico
1.3       +3 líneas   (L13-1, L13-2, L13-10)  resto idéntico
fusión    +1 línea (F-2), F-9 renombrado, bloque nuevo de fixturas
```

En 1.2, los cuatro valores de cabecera —mayor desviación `0.0612`, peor
`BS_pop` `0.146614`, separación sensor↔δ `0.1437`, cobertura `40`— salen
idénticos.

### Cada fila añadida trae su mutante

Un gate que sólo puede pasar no es un gate. Las ocho filas incorporadas llevan
su fixtura negativa: un campo de más en la vista, un parámetro de más en
`predict_near`, el mundo nominal en vez del falso, una `query` que acepta cue,
una presentación con `act`, un banco de fuga que no filtra, un blob distinto, y
unas métricas que sortean.

---

## Lo que queda abierto, dicho como tal

1. **El caso con lifecycle de la paridad.** Controlado fuera, no medido. Medirlo
   exige que el banco lo soporte, que hoy no.
2. **El cruce informe ↔ oráculo fuera de los gates.** Acotado, no cerrado: se
   cruzó la **taxonomía** de gates en las cuatro campañas del linaje A y ningún
   **valor** resultó contradicho. Umbrales, tamaños de banco, semillas
   declaradas y afirmaciones de alcance siguen sin cruzarse.
3. **El desplazamiento de citas.** El gate de cartografía detecta una cita a
   línea en blanco o fuera de rango, no una que aterrizó sobre otra línea
   válida. La reparación propuesta —guardar en el manifiesto una huella de la
   línea citada— sigue sin hacerse.
4. **Los árboles de campaña heredan el defecto del catálogo de composición** de
   su commit base. Tres pruebas en rojo en `organism-fusion-hm-01`, verificado
   que son previas a este trabajo. **No es deuda**: congelar cada árbol desde su
   base es deliberado, y propagar una reparación ajena a su pregunta rompería
   esa garantía.

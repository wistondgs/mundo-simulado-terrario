# La capa de conocimiento, leída · corpus, teoría, hipergrafos, memoria y composición

**2026-09-21** · `bbaa3e5` · **sustituye a `INFORME_CAPA_CONOCIMIENTO_01.md`**, que
contaba la capa en vez de leerla.
Depositado en `docs/CARTOGRAFIA_TERRARIO_01.md` **§XXXIX** · 23 citas
`fichero:línea`, todas verificadas.

Clasificación según el contrato de conocimiento del 2026-09-21: **K0** lo
establecido, **K1** lo documentado que había que verificar en código, **K2** lo
no resuelto —que no se rellena por intuición—, **K3** lo que exige evidencia
externa.

---

## 1 · Lo primero, porque está roto ahora mismo

**El catálogo de composición del organismo revienta, y tres pruebas llevan tres
días en rojo.**

```
$ python -c "from terrario.lab.agent_composition import catalogue; catalogue()"
KeyError: 'use_curiosity'

$ pytest tests/test_agent_composition.py
FAILED test_every_offered_concept_is_a_key_the_agent_actually_reads
FAILED test_the_catalogue_carries_what_a_person_needs_to_choose
FAILED test_the_mix_reads_as_a_sentence_not_as_flags
```

`GET /api/agent-concepts` —lo que alimenta la pantalla de composición— devuelve
`catalogue()`, así que **el endpoint está caído**. Y `validate_selection`
**acepta** `use_curiosity` y se la pasa a un A4 que no la lee: exactamente el
modo de fallo que la cabecera del propio módulo declara «el peor que puede tener
una pantalla de composición».

**La causa es una categoría, no una errata.** `fd725e3` construyó la curiosidad
como **A5**, un descendiente —«A5 is A4's descendant, not A4 with a flag»— y la
clave la lee A5. El catálogo modela **un** organismo; el linaje ya tiene **dos**.

Dos salidas, ninguna mecánica, y por eso no la tomé yo:

1. **Catálogo por agente:** cada concepto declara a qué configuración pertenece.
   Correcto si van a existir A5, A6…
2. **Sacar `use_curiosity` del catálogo de A4** y ofrecer la composición de A5
   aparte. Más pequeño, y deja el catálogo mintiendo por omisión.

## 2 · Estado científico real de las capacidades

Calculado, no declarado: `status_of` deriva el estado de precondiciones
comprobables en orden.

```
$ python scripts/passport_check.py
  procedencia   falla en 5 de 10
  pureza        falla en 3 de 10
  mundo         falla en 3 de 10
  instrumento   falla en 8 de 10
  listas para certificar: 1 de 10 — LEARN-A1
```

**La restricción que manda es el instrumento, y no por falta de instrumentos:**
los 8 del registro están los 8 en `REPORTABLE`. Ocho de las diez capacidades
declaran un endpoint `PENDIENTE-*`, un nombre que el registro no puede resolver.

Eso no es un fallo: es **lo contrario** del modo de fallo «defaults que
convierten fallos en números plausibles». En vez de sustituir el endpoint que
falta por una métrica parecida, se declara un hueco que la máquina ve. Es la
mejor decisión de diseño de toda la capa.

## 3 · Dónde se decide lo epistemológico · tres subcadenas

| Decisión | Mecanismo real |
|---|---|
| ¿claim del autor o inferencia del analista? | `"ANALYST" in value.upper()` |
| fuerza de una relación (5 niveles) | subcadenas mezclando español e inglés: `REQUIERE`, `DEPENDE`, `FACILITA`, `MODULA`, `INHIBE` |
| ¿la fuente vale como evidencia? | `QUARANTIN` / `MISMATCH` / `UNAVAILABLE` en el texto de integridad |

La frontera autor↔analista es la distinción más cargada del corpus y se decide
con `in`. Un claim que diga «inferred» sin la palabra `ANALYST` entra como claim
del autor.

**K2 declarado:** cuántos de los 189 claims están mal clasificados por esto no
está medido, y es medible.

## 4 · El grafo de teoría · 956 aristas que existen si dos cadenas coinciden

`build_graph` no declara el grafo: lo **infiere emparejando texto**. Claim→fuente
por título en casefold, si no por id exacto, si no por una regex que busca
`[TI-xxxx]` dentro del campo. Relación→concepto y componente→concepto, por
nombre en casefold.

Los **1 035 nodos y 956 aristas** son las coincidencias que hubo, no las
relaciones que el corpus afirma. Una diferencia de grafía produce **silencio**,
no error.

**K2 declarado:** la tasa de aristas perdidas por no-coincidencia no está medida,
y se mide comparando `RELATIONS_AUDIT` contra las aristas creadas.

## 5 · La fábrica de hipótesis · qué calcula de verdad

Ejecutada hoy sobre el snapshot real:

```
8 hiperaristas → 8 familias → 232 rivales
todas:  identificabilidad = DESCRIPTIVE_ONLY
        prioridad = (0.7, 0.5, 1.0, 0.3, 0.4, 0.6)
        umbrales preregistrados = {}
validate() = ('critical confounders unaddressed')   en las ocho
```

* Los rivales son `itertools.combinations`: **todos los subconjuntos no vacíos**
  (2ⁿ−1) más una nula. El «mecanismo propuesto» de cada uno es literalmente
  `" + ".join(componentes)`.
* La identificabilidad **no se mide**: el compilador llama a la auditoría con un
  diccionario escrito a mano con dos checks en `True` y cinco ausentes. 2 de 7 ⇒
  `DESCRIPTIVE_ONLY` para todo diseño que la fábrica produzca, por construcción.
* La prioridad son **seis constantes literales**, idénticas en las ocho familias.
  No es una puntuación; es una tupla.
* Cada confusor nace `critical=True, mitigation=None`, así que el validador
  siempre falla: **la fábrica no puede emitir una especificación ejecutable,
  nunca, sin intervención humana.** Eso es un gate, no un defecto —pero hay que
  decirlo como lo que es.
* `build_portfolio` sella la familia como aprobada **él mismo** para superar el
  `PermissionError` del compilador, y devuelve el diseño otra vez en `GENERATED`.

## 6 · La «revisión científica» es un registro, no un analizador

`review_portfolio` es determinista, y eso es cierto. Pero lo que evalúa está
escrito a mano: un diccionario indexado por `HYPERCAND-01 … 08` con el estado del
constructo, los proxies y la métrica de cada uno, y una **tabla literal de nueve
enteros por candidato** sobre la que se calcula el frente de Pareto.

Un noveno candidato **levanta `KeyError`**. La revisión no procesa una
hiperarista que no sea una de las ocho. `pseudo_falsifiable` está fijado a `True`
para todas.

No es deshonesto —codifica un análisis humano y lo hace reproducible— pero
llamarlo revisión invita a leerlo como un analizador.

## 7 · Hipergrafos · son tres, no uno

| Sistema | Qué modela | Aridad | Servido en |
|---|---|---|---|
| **Teórico** | mecanismos científicos con procedencia al corpus | **n-aria real** | `/api/theory-operational-*` |
| **Operacional** | el plano de ejecución: hipótesis → borrador → preregistro → plan → intento → … → blob CAS | tipada | `/api/operational-hypergraph` |
| **Intercambio** | ingesta JSON/YAML de artefactos derivados | **binaria** | `/api/hypergraph` |

El endpoint que se llama `hypergraph` a secas sirve el **binario**. El de
hiperaristas reales se llama de otra manera.

**El teórico es lo mejor construido del repositorio**, y su mecanismo es una
cadena de verificación: cada ligadura se resuelve contra el claim **y** la fuente
importados, se comprueban las revisiones de ambos, **el locator**, que el claim
resuelva a la fuente declarada, y si la versión empieza por `sha256:` **se abre
el PDF real y se compara el hash**. `materialize` prohíbe promover el estado
epistemológico. `from_payload` recalcula la identidad semántica y rechaza si no
coincide: la deserialización es a prueba de manipulación.

## 8 · La memoria · dos sistemas, dos mecanismos

**La del organismo.** `EpisodicMemory` es un buffer circular de 1 000 entradas
con recuperación por coseno y `softmax` **sobre las similitudes top-k**. Detalle
que importa: el softmax se aplica a cosenos en `[-1,1]`, así que cuando las k
similitudes son parecidas los pesos salen casi uniformes — la recuperación pesa
poco aunque encuentre el vecino correcto.

`LongTermMemory` es una matriz de 64×128 escrita **fuera del optimizador**, bajo
`no_grad`, con tres guardas: `nan_to_num_` antes de escribir, la actualización
sólo se copia si es finita, y se recorta a `[-10,10]`, registrando
`write_accepted` en la traza. Es estado que cambia la conducta sin pasar por el
gradiente, protegido a propósito.

**La del laboratorio.** `canonical.py` es la columna de identidad: un canonizador
total y fail-closed que **prohíbe los flotantes no finitos** en un artefacto
científico. Cada `semantic_id` del repositorio cuelga de esa función. Las 42
tablas vacías de 72 no son un almacén roto: son el esquema de una capa que nunca
ingirió.

## 9 · Lo que sigue sin saberse · K2 y K3, declarados

1. **K2** · Cuántos claims están mal clasificados por el test de subcadena
   `ANALYST`. Medible sobre los 189 con una muestra revisada a mano.
2. **K2** · Cuántas relaciones no llegaron al grafo por no coincidir la grafía.
3. **K2** · Si los 57 PDFs que el snapshot no conoce aportan claims nuevos o son
   duplicados. No es inferible sin ingerirlos.
4. **K3** · Qué mide cada `PENDIENTE-*`. Para al menos dos —calibración de
   incertidumbre y elección no miope— el proyecto no tiene evidencia interna para
   fijar el criterio.
5. **K2** · Si la recuperación episódica tiene efecto conductual, dado el
   aplanamiento del softmax. Medible con una lesión: fijar los pesos a uniformes
   y comparar.

## 10 · Divergencia entre el contrato de conocimiento y el disco

El documento de necesidades declara un corpus de **152 registros bibliográficos,
65 textos completos y 16 categorías**. Lo que hay en disco hoy:

```
101 PDFs en 10 subdirectorios
 44 fuentes ingeridas por el snapshot vigente
187 nombres de concepto normalizados, 56 citables por un claim
```

No digo cuál es la cifra correcta: digo que **son dos inventarios distintos** y
que el proyecto no puede tratarlos como el mismo. Reconciliarlos es trabajo de
corpus, no de código, y es K1 hasta que alguien lo haga.

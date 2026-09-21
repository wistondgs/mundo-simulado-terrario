# La capa de conocimiento, cartografiada · y la puerta puesta en automático

> **Superado por `INFORME_CAPA_CONOCIMIENTO_02.md`** (mismo día): este informe
> contó la capa; el 02 la lee. Los números de aquí siguen siendo correctos.

**2026-09-21** · rama `experiment/cognitive-live-observatory-01` · base `bbaa3e5`
Depositado en `docs/CARTOGRAFIA_TERRARIO_01.md` §XXXVIII · 237 líneas nuevas.

---

## 0 · Lo que se pidió y lo que se hizo

Dar uso a la cartografía en vez de tenerla de adorno: cartografiar el corpus, el
análisis de la teoría, los hipergrafos, la memoria y la combinación de
habilidades; y activar los hooks para que el mapa se compruebe solo.

Las tres cosas están hechas. La cartografía pasó de vigilar **107 ficheros a
127**, y de esos 20 nuevos, 19 son de esta capa.

---

## 1 · El hallazgo que justifica todo lo demás

**El corpus creció ×2,4 y el guardián del mapa no podía verlo.**

```
2026-09-17   §XXXII contó   42 PDFs
2026-09-21   hay           101 PDFs en 10 subdirectorios
el snapshot ingirió          44 fuentes
```

No fue un descuido de nadie: el patrón de referencias de
`scripts/cartografia_check.py` sólo reconocía rutas bajo `terrario`, `tests`,
`scripts`, `scenarios`, `configs` y `knowledge`. Ni `theory_snapshots/`, ni
`docs/handoff/`, ni ficheros `.csv`. **El corpus estaba fuera del campo de
visión de G1 por construcción**, así que podía duplicarse sin que ninguna
sección quedara obsoleta.

Corregido. Al ampliar el patrón, el gate detectó de inmediato una cita que
§XXXII llevaba haciendo desde el 17-09 y que nunca se había vigilado
(`SOURCE_PROVENANCE_v0.3.csv`).

---

## 2 · Qué se encontró al releer, por dominio

### Corpus · dos sistemas paralelos, ahora también divergentes en tamaño

`referencegraph/import_corpus.py` consume `manifest/CORPUS_MANIFEST.jsonl`, que
**sigue sin existir en el disco**. Por eso las 22 tablas `ref_*` siguen a cero
filas. El catálogo real vive en otro formato y otro sitio: el snapshot
`theory-f59dbb6d6ee3850c`, con 44 fuentes, 189 claims y 283 conceptos.

### Conceptos · el corpus es más pobre de lo que su cuenta sugiere

Los 283 conceptos son dos capas que conviene no sumar:

| Capa | Filas | Nombres distintos | Con definición del autor | Citables por claim |
|---|---:|---:|---:|---:|
| `CONCEPTS_RAW_v0.1` | 224 | 187 | 224 | **56** |
| `CONCEPTS_RAW_PATCH_v0.3` | 59 | 59 | **0** | 17 |

Las 59 filas del parche no tienen ni una definición del autor: son nombres, no
conceptos citables. Y de los 187 nombres de la capa buena, sólo **56** aparecen
en algún claim. El techo de la citabilidad es escasez de corpus, no de código.

### Citabilidad · el contrato existe y nadie lo ha estrenado

`d1485b4` construyó `CorpusConceptReference`: una cadena
`concepto → claim con locator → fuente`, con validación que rechaza un concepto
ausente de su claim y uno sin definición del autor. Es correcto y está probado.

**Y no lo usa nadie.** Las únicas apariciones en todo el árbol son su
declaración y su test. Las operacionalizaciones reales siguen citando sólo
claims.

### Hipergrafo · sin cambios, y el diagnóstico se sostiene

```
relation_type         2 valores
corroboration_status  2 valores, uno de ellos para declarar que NO hay corroboración
empirical_evidence            0 filas
empirical_evidence_links      0 filas
```

Es un almacén de estructura, no de conocimiento acumulado.

### Memoria · son dos cosas distintas con el mismo nombre

La del organismo está en §XI y no cambió. La del laboratorio está partida en
tres sitios que no se hablan:

| Dónde | Qué guarda | Formato |
|---|---|---|
| `.terrario/terrario.db` | ejecución y preregistro | SQLite · 72 tablas, **42 vacías** |
| `theory_snapshots/` | el conocimiento: 1 035 nodos, 956 aristas | CSV + JSON |
| `docs/handoff/*.csv` | 176 claims y 115 conceptos extraídos a mano | CSV sin esquema |

`TheoryGraphStore` **no persiste en base de datos**: es un objeto en memoria con
`save()`/`load()` a JSON. La base reservó 31 tablas para esta capa y las 31
están vacías.

### Composición de habilidades · la costura más corta del proyecto

`agent_composition.py` es la única pieza de esta capa conectada al ciclo
experimental —cuatro consumidores reales de `validate_selection`— y ahora tiene
**once** conceptos, no diez: `fd725e3` añadió `use_curiosity`.

Cada concepto lleva un `corpus_block: int` que **ningún fichero lee**. Las otras
dos apariciones del símbolo en todo el árbol son prosa que dice precisamente
eso. Es decir:

> Once conceptos con un entero huérfano como enlace al corpus, y a dos ficheros
> de distancia, `CorpusConceptReference`: exactamente la cadena verificable que
> les falta, construida y sin conectar.

Ésa es la reparación de mayor rendimiento por línea que hay ahora mismo en esta
capa.

---

## 3 · La puerta, ahora automática

`scripts/cartografia_hook.py`, atado en `.claude/settings.json`:

| Momento | Qué hace | Coste |
|---|---|---|
| `SessionStart` | ejecuta el gate real y mete su veredicto en el contexto | ~1,8 s, una vez |
| `PostToolUse` sobre `Edit`/`Write` | mira sólo el manifiesto y nombra la sección que ese fichero acaba de dejar obsoleta | milisegundos |

Probado con fixtura negativa: al modificar `terrario/world/physics.py` el hook
nombró las tres secciones afectadas —I, II y VII—; con el fichero intacto, y con
un fichero fuera del mapa, calla. La modificación de prueba quedó revertida.

La autoridad sigue siendo `cartografia_check.py`. El hook no decide nada y nunca
rompe el turno: cualquier excepción sale como silencio, porque un hook que rompe
el turno se desactiva y entonces no comprueba nada.

**Aviso de instalación:** el arnés vigila `.claude/` sólo si había un fichero de
ajustes al arrancar la sesión, y aquí no lo había. Los hooks quedan activos a
partir de la próxima sesión.

---

## 4 · Lo que este mecanismo NO arregla

El manifiesto se regenera con `--write`, y `--write` no puede comprobar que
alguien haya releído. Si se regenera después de cambiar el código sin reescribir
el texto, **el gate se pone verde sobre prosa vieja**. El hash prueba que el
fichero no ha cambiado desde la última vez que se dijo «lo leí»; no prueba que
se leyera.

Eso no es hipotético: al empezar esta sesión el gate daba verde sobre 107
ficheros, y §XXXII llevaba tres días afirmando cosas que el disco ya no
sostenía.

---

## 5 · Lo que queda en la mesa

1. **Conectar `corpus_block` a `CorpusConceptReference`** — once conceptos, un
   contrato ya escrito, ningún trabajo de corpus nuevo.
2. **Ingerir los 57 PDFs que el snapshot no conoce**, o declarar por escrito que
   el snapshot está congelado en 44 fuentes a propósito.
3. **Decidir qué es `docs/handoff/*.csv`**: si es corpus, le falta esquema y
   debería entrar al snapshot; si es material de trabajo, debería decirlo.
4. **Extraer claims para los 131 nombres no citables**, que es lo único que
   sube el techo de la citabilidad.

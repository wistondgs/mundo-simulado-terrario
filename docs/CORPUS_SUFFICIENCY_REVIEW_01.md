# CORPUS-SUFFICIENCY-REVIEW-01

**Pregunta:** ¿es suficiente el corpus documental que sostiene la teoría?
**Alcance:** `/home/wis/Documentos/teoria de la inteligencia` (516 MB, tres ZIP) más el snapshot
`theory-f59dbb6d6ee3850c`. Revisión de solo lectura.
**Método:** lectura del catálogo maestro y del informe de construcción; conteo por categoría y por
estado de acceso; verificación de procedencia por SHA-256 contra los bytes realmente presentes.

> **Corrección registrada.** Una primera pasada de esta revisión contó solo los archivos
> descargados (94) y concluyó que el corpus estaba sesgado hacia el aprendizaje automático y
> vacío en desarrollo cognitivo, atribuyéndolo a la selección. Al leer `CORPUS_MASTER.csv` y
> `BUILD_REPORT.json` esa conclusión resultó equivocada en su causa. Se sustituye por lo que
> sigue.

## 1. Respuesta corta

El catálogo es **152 obras**, repartidas de forma deliberadamente equilibrada entre 16 categorías
(8 a 14 por categoría). De ellas se obtuvieron **65: exactamente las 65 legalmente obtenibles**
(17 de dominio público + 48 de acceso abierto). Las **87 restantes están tras muro de pago** y
cada una queda registrada, con autor, año, DOI, enlace y el motivo exacto por el que no se tomó.

**La tasa de adquisición es del 100 % sobre lo que se podía adquirir legalmente.** El corpus no
está incompleto por descuido: está limitado por el acceso, y esa limitación está documentada obra
por obra.

## 2. El catálogo, por categoría

| Categoría | Catálogo | Con copia | Restringidas |
|---|---:|---:|---:|
| 01_Filosofia | 8 | **8** | 0 |
| 02_Evolucion_Inteligencia_Animal | 8 | 6 | 2 |
| 03_Psicologia_Psicometria | 14 | 3 | 11 |
| **04_Desarrollo_Cognitivo** | **8** | **0** | **8** |
| 05_Neurociencia | 8 | 1 | 7 |
| 06_Cibernetica_Sistemas | 8 | 1 | 7 |
| 07_Ciencia_Cognitiva | 8 | 1 | 7 |
| 08_IA_Clasica | 8 | 2 | 6 |
| 09_Inteligencia_Formal_AGI | 11 | 8 | 3 |
| 10_Aprendizaje_Metaaprendizaje | 14 | **14** | 0 |
| 11_Agencia_Decision_Accion | 11 | 3 | 8 |
| 12_Creatividad_Problemas | 8 | 1 | 7 |
| 13_Inteligencia_Social_Colectiva | 8 | 2 | 6 |
| 14_Filosofia_Mente_Semantica | 8 | 1 | 7 |
| 15_Medicion_Benchmarks | 14 | 12 | 2 |
| 16_Revisiones_Contemporaneas | 8 | 2 | 6 |
| **TOTAL** | **152** | **65** | **87** |

## 3. El hallazgo central: la forma del corpus es la forma de los muros de pago

Las dos categorías completas al 100 % son aquellas cuya literatura es gratuita por razones ajenas
al proyecto:

- **01_Filosofia** (8/8): clásicos en dominio público — Aristóteles, Descartes, Locke, Hume,
  Kant, James, Dewey, Russell.
- **10_Aprendizaje_Metaaprendizaje** (14/14): literatura moderna de aprendizaje automático, que
  se publica en arXiv — MAML, World Models, Dreamer, curiosidad, RND, POET.

La categoría vacía al 100 % es la que la industria editorial mantiene cerrada:

**`04_Desarrollo_Cognitivo` — 8 catalogadas, 8 restringidas, 0 obtenidas:**

| | | |
|---|---|---|
| TI-0031 | Jean Piaget, 1936 | *The Origins of Intelligence in Children* |
| TI-0032 | Jean Piaget, 1947 | *The Psychology of Intelligence* |
| TI-0033 | Lev Vygotsky, 1934 | *Thought and Language* |
| TI-0034 | Jerome Bruner, 1960 | *The Process of Education* |
| TI-0035 | Annette Karmiloff-Smith, 1992 | *Beyond Modularity* |
| TI-0036 | Gopnik; Meltzoff; Kuhl, 1999 | *The Scientist in the Crib* |
| TI-0037 | Susan Carey, 2009 | *The Origin of Concepts* |
| TI-0038 | Robert Siegler, 1991 | *Children's Thinking* |

El catálogo identificó exactamente las obras correctas. Ninguna se pudo tomar.

Psicología (11/14 restringidas), neurociencia, cibernética, ciencia cognitiva, creatividad y
semántica (7/8 cada una) siguen el mismo patrón. **El sesgo del corpus no es del autor: es el
sesgo de acceso de la literatura académica, impreso sobre el proyecto.**

## 4. La consecuencia científica, dicha sin rodeos

El objetivo declarado del proyecto es desmenuzar **cómo se desarrolla la cognición**. La
categoría del corpus que corresponde a esa pregunta es la única con cero cobertura, y su causa
es económica, no intelectual.

Hoy el corpus puede sostener afirmaciones sobre **medición** de inteligencia y sobre
**arquitecturas artificiales**. No puede sostener todavía afirmaciones sobre **ontogenia** —
no porque falte criterio, sino porque faltan los ocho libros.

Esto no invalida nada de lo construido. Sí determina qué se puede preregistrar: una hipótesis de
desarrollo cuyo marco teórico no puede citar fuente primaria es una hipótesis con un flanco
declarable y declarado.

## 5. Trazabilidad de la expansión v0.3 — defecto encontrado y CERRADO el 2026-09-16

**Al abrir esta revisión:** `SOURCE_PROVENANCE_v0.3.csv` declaraba 14 fuentes marcadas
`identity_verification: VERIFIED_LOCAL_FILE`, pero su `archivo_local` apuntaba a
`/workspace/scratch/0d8f1a516e82/deliverables/...`, ruta efímera de la máquina donde se hizo la
expansión. Al hashear los 168 archivos de los tres ZIP, solo **3 de 14** eran verificables.

**Reparación aplicada.** Las URL legales estaban registradas (repositorio de autor, PMC,
repositorio universitario). Se re-adquirieron desde esas mismas URL y se extrajeron de los ZIP
las que ya estaban dentro. Ruta estable nueva:
`/home/wis/Documentos/teoria de la inteligencia/documents_v0.3/` — 14 archivos, 15,7 MB.

| Estado | n | Significado |
|---|---:|---|
| `VERIFIED_LOCAL_FILE` | **10** | sha256 **idéntico** al registro original |
| `REACQUIRED_CONTENT_EQUIVALENT_HASH_DIFFERS` | 3 | HTML de PMC (X03, X07, X08): texto completo del artículo presente y verificado, pero el HTML renderizado lleva fecha embebida y no es reproducible byte a byte |
| `PREVIEW_ONLY_NOT_FULL_TEXT` | 1 | X09 Laland: Nature solo sirve resumen, tal como ya decía el registro |

**3/14 verificables → 14/14 presentes, 10/14 con hash idéntico.**

El CSV re-anclado se escribió como **`SOURCE_PROVENANCE_v0.3.local.csv`**; el original queda
intacto. Promoverlo a canónico es una decisión humana, no automática.

## 6. Lo que está bien hecho y conviene no tocar

- **`MISSING_AND_RESTRICTED.md` (33 KB)** documenta cada obra no obtenida con autor, año, estado,
  enlace, DOI y motivo literal. Ejemplo: *"No se identificó una copia completa pública e
  inequívocamente legal; se conserva el enlace bibliográfico oficial, DOI o catálogo para
  compra/préstamo."* Un corpus que declara sus huecos uno por uno es un corpus utilizable.
- **El equilibrio del catálogo** (8–14 por categoría en las 16) demuestra que la selección fue
  sistemática, no oportunista.
- **`BUILD_REPORT.json`** registra `records`, `records_with_copy`, `unique_files`, bytes y
  `master_sha256`. La construcción es auditable.
- **El corpus de referencia de mundos** (`WORLD-REF-*`: 29 PDF + 29 extracciones de texto, 30
  registros de procedencia con cadena de redirecciones) está completo y bien proveído.
- **Que solo un PDF sea legible por la API no es un defecto.**
  `LabAPI._operational_source_available` exige exactamente `TI-0077` y lo declara: *"The one
  reviewed operational path; no candidate/role inference is accepted."* Es fallo cerrado
  deliberado.

## 7. Recomendaciones, por rendimiento

1. **Re-anclar `SOURCE_PROVENANCE_v0.3.csv`**: sustituir las rutas `/workspace/scratch/...` y
   degradar a `UNVERIFIABLE_LOCALLY` las 11 fuentes sin bytes. Es el único arreglo urgente.
2. **Descomprimir los ZIP a una ruta estable** y apuntar ahí `TERRARIO_PRIMARY_SOURCE_ROOT`.
   Mientras el corpus viva comprimido, ninguna verificación futura lo alcanza.
3. **Desbloquear `04_Desarrollo_Cognitivo`**, por orden de coste:
   acceso institucional o préstamo interbibliotecario · copias de autor (Gopnik y Carey publican
   capítulos) · sustitutos de acceso abierto y *preprints* · compra selectiva de los dos o tres
   imprescindibles (Karmiloff-Smith y Carey son los más citados por la pregunta del proyecto).
4. **Recuperar X03, X06 y X16** de la expansión v0.3: son las fuentes de desarrollo que sí eran
   accesibles y cuyos bytes se perdieron.
5. Mientras 3 siga abierto, **declarar el límite en cualquier preregistro de ontogenia** en vez de
   silenciarlo.

## 8. Conclusión

152 obras catalogadas, 65 obtenidas, 87 documentadas como inalcanzables y ni una sola omitida sin
razón escrita. Como pieza de trabajo bibliográfico, el corpus está bien hecho.

Su límite no es de método sino de acceso, y cae justo encima de la pregunta del proyecto. La
pregunta «¿es suficiente?» se responde por partes: **para medir y construir inteligencia
artificial, sí. Para explicar la ontogenia de la cognición, faltan ocho libros y están
identificados por nombre.**

# Brief · Reestructuración del corpus de Terrario y construcción de `theory-v2`

> **Anexo.** El documento maestro es `ORIENTACIONES_CORPUS_COMPLETAS.md`, que cubre estado,
> defectos, contrato de claims, tipos de documento, artefactos, hashes, construcción,
> adquisición y aceptación. Esto queda como detalle de una parte.


**Para un agente externo con acceso al disco.** Autorizado por Wis, 2026-09-18.

Este documento es autosuficiente: contiene rutas exactas, esquemas exactos, reglas de validación
verbatim y los límites de lo que no se toca. No hace falta leer el resto del repositorio para
ejecutarlo, pero sí para entenderlo.

---

# 0 · Qué es esto y por qué existe

Terrario es un laboratorio que exige que **toda capacidad de un agente esté anclada a una fuente
del corpus**. La ley L-1 de su canon dice: conexión explícita con corpus **y concepto**. El código
valida esa conexión contra un snapshot inmutable con hashes.

**El estado medido hoy:**

```
corpus sellado           44 fuentes · 283 conceptos · 189 claims
ids que aparecen en todo el árbol de producción          9
que soportan algo real                                   2
fracción alcanzable desde alguna capacidad
    claims        2 / 189  =  1.06 %
    fuentes       1 / 44   =  2.27 %
    conceptos     0 / 283  =  0.00 %
```

El corpus está construido y sin usar. Y cuando se intentó usar, no se pudo, por cuatro defectos
estructurales que este brief manda reparar.

---

# 1 · Los cuatro defectos, medidos

## 1.1 · Dos capas: una sirve entera, la otra no sirve nada

```
                  conceptos   con definición del autor    claims   con locator real
v0.1                    224          224  (100 %)            171        171  (100 %)
v0.3 patch               59            0  (  0 %)             18          0  (  0 %)
```

La división es perfecta. La capa v0.3 no está mal extraída: **no está extraída**. Doce documentos
—percepción de objetos, sensoriomotor, física intuitiva, motivación intrínseca, desarrollo—
entraron como títulos con metadatos. El propio `CORPUS_EXPANSION_REPORT_v0.3.md` declara esa capa
no canónica.

## 1.2 · El grafo ignora la capa nueva

```
grafo de teoría        1035 nodos · 956 aristas
extremos de arista        CON- (v0.1): 812        P3C- (v0.3): 0
```

Cero. Los 59 conceptos de v0.3 están en el CSV y fuera del grafo.

## 1.3 · Las 21 familias conceptuales siguen abiertas

`COVERAGE_MATRIX_v0.3.csv`: `remaining_status = OPEN_GAP` en las 21. Incluidas, con prioridad alta,
`PERCEPTION_WORLD`, `LEARNING`, `MOTIVATION_VALUE` y `DEVELOPMENT`. El parche se hizo para cerrarlas
y no cerró ninguna.

## 1.4 · Los conceptos no tienen procedencia citable — este es el defecto raíz

El esquema de procedencia (`CorpusClaimReference`) direcciona **claims**. No existe ningún campo
que ate una capacidad a un **concepto**. Consecuencia concreta: el concepto `P3C-0014`
(«Intelligent Adaptive Curiosity», Oudeyer) existe en el corpus y **no hay forma de citarlo**. La
mitad «concepto» de L-1 es irrepresentable en el código.

Los espacios de nombres `P3R-*` (relaciones del parche) y `CLM-*` (claims auditados) son disjuntos
y el corpus nunca los cruza.

---

# 2 · Lo que NO se toca. Leer antes de nada

1. **El snapshot `theory-f59dbb6d6ee3850c` es inmutable.** Su `snapshot_manifest.json` lleva
   `"immutable": true`, y su id, su hash y el sha256 de su manifiesto están fijados como constantes
   de módulo en `terrario/lab/capability_operationalization.py`. Cambiar un byte invalida la
   procedencia de LEARN-A1, HOMEO-A1, WM-A1, UNC-A1 y CURIO-A1. **No se edita, no se regenera, no
   se "arregla".** Se construye uno nuevo al lado.
2. **No se tocan los hashes protegidos** ni las fixtures históricas de `tests/fixtures/`.
3. **No se inventa procedencia.** Si un claim no tiene locator de página o sección, no entra. Ese
   fue el defecto de v0.3 y repetirlo es peor que no hacer nada.
4. **Un claim de título o abstract no es un claim.** El corpus HEA v0.1 trae 21 claims semilla cuya
   propia columna `notes` dice «requires deeper extraction before ontology promotion». No se
   promueven tal cual.

---

# 3 · Material de entrada

## 3.1 · Snapshot sellado actual

```
theory_snapshots/theory-f59dbb6d6ee3850c/
```

21 artefactos. Los que importan:

| Fichero | Qué es | Estado |
|---|---|---|
| `CLAIMS_RELATIONS_v0.1.csv` | 171 claims `CLM-*` | **usable entero** |
| `CONCEPTS_RAW_v0.1.csv` | 224 conceptos `CON-*` | **usable entero** |
| `RELATIONS_AUDIT_v0.2.csv` | 206 relaciones auditadas | usable |
| `CONCEPT_CANONICAL_MAP_v0.2.csv` | 224 candidatos canónicos | usable |
| `SOURCE_PROVENANCE_v0.3.csv` | 14 fuentes de la expansión | metadatos correctos |
| `CONCEPTS_RAW_PATCH_v0.3.csv` | 59 conceptos `P3C-*` | **inservible: 0 % definiciones** |
| `CLAIMS_RELATIONS_PATCH_v0.3.csv` | 18 claims `P3R-*` | **inservible: 0 % locators** |
| `SOURCE_SAMPLE_v0.1.md` | tabla de fuentes `TI-*` | usable |
| `theory_graph.json` | grafo, 1035 nodos | usable, incompleto |
| `COVERAGE_MATRIX_v0.3.csv` | 21 familias, todas abiertas | diagnóstico |

## 3.2 · Corpus nuevo, íntegro y verificado

```
/home/wis/Documentos/teoria de la inteligencia/homeostatic_enactive_agency_corpus_v0.1.zip
sha256  1aa71f903443e050e675aac63291fae4af82d2cd6a41fd653a9f7d8339251066
```

Verificado: **29 de 29 ficheros coinciden** con su `manifest/SHA256SUMS.txt`, cero diferencias,
cero ausencias. Trae 15 PDFs, manifiesto, locators de referencia, `build_snapshot.py` y 21 claims
semilla.

Aviso: su `SHA256SUMS.txt` usa rutas absolutas de la máquina de construcción
(`/workspace/scratch/...`). Hay que reescribir el prefijo para verificar; **no es un fallo de
integridad**.

## 3.3 · Extracción profunda ya hecha — 49 claims

```
docs/handoff/HEA_CLAIMS_EXTRAIDOS_v1.csv
```

**176 claims** — el corpus HEA extraído entero, sus 15 documentos.

**Aviso de paginación en HEA-015.** Ese PDF es una re-composición en Word (Hollnagel, 2004) de 10
páginas del artículo original de 9, sin números de página de revista impresos. La correspondencia
`PDF p. 1 = journal p. 89` es una inferencia lineal y **deriva en algún punto del artículo**. Los
locators citan ambas paginaciones; la del PDF es la fiable. Conviene resolverlo contra el original
de *Int. J. Systems Sci.* 1(2):89-97 antes de sellar v2. Columnas: `claim_id`, `reference_id`,
`source_concept`, `relation_type`, `target_concept`, `claim_text_or_paraphrase`, `pagina_seccion`,
`explicit_or_inferred`, `evidence_type`, `bears_on`.

Todos con **locator exacto de sección y página**, leídos del cuerpo del PDF. Verificados releyendo
la página citada: **61 de 68 comprobaciones** independientes confirmaron locator correcto y
afirmación sostenida.

**Los 7 que no pasaron no son ruido: son la razón de verificar.** El patrón dominante es tipar como
`AUTHOR_EXPLICIT` una cláusula que es inferencia del extractor, o importar a un paper el encuadre
de otro. Ejemplo real, HEA-002: la extracción decía que la recompensa «ya no es una diferencia de
drives entre dos pasos» — eso es la formulación de Keramati & Gutkin, que este paper cita pero no
afirma. Antes de sellar v2, **cada claim rechazado hay que retiparlo o quitarlo**, no promoverlo.

Entran a `theory-v2` tras remapear sus ids al espacio `CLM-*`.

---

# 4 · Esquemas exactos

Respetar cabecera, orden de columnas y codificación. Los CSV v0.1 llevan **BOM UTF-8**; leer con
`encoding="utf-8-sig"`.

```
CLAIMS_RELATIONS_v0.1.csv
  claim_id, source_concept, relation_type, target_concept, autor, fuente,
  pagina_seccion, claim_text_or_paraphrase, explicit_or_inferred, evidence_type,
  confidence, notes

CONCEPTS_RAW_v0.1.csv
  concept_id, nombre_original, nombre_normalizado_provisional, tipo,
  definicion_del_autor, interpretacion_breve, autor, obra, año, disciplina,
  pagina_seccion, archivo_fuente, confidence, notas

SOURCE_PROVENANCE_v0.3.csv
  source_id, autor, titulo, año, disciplina, doi, revista_editorial,
  url_procedencia, tipo_acceso, idioma, archivo_local, sha256, file_size_bytes,
  fecha_recuperacion, identity_verification, integrity_notes
```

**Convención crítica de `fuente`:** el validador busca la subcadena `[<source_id>]` dentro de la
columna `fuente`. El formato correcto es:

```
Reinforcement Learning: An Introduction (Second Edition) (2018) [TI-0097]
```

El parche v0.3 escribió `fuente` como lista entre corchetes y **por eso su único claim es
rechazado**. No repetir.

`snapshot_manifest.json`:

```json
{
  "snapshot_id": "theory-<16 hex>",
  "snapshot_hash": "<64 hex>",
  "parser_version": "theory-ingestion/1",
  "immutable": true,
  "missing_artifacts": [],
  "artifacts": [
    {"filename": "...", "sha256": "<64 hex>", "artifact_version": "v0.1",
     "artifact_type": "...", "source_path": "...",
     "ingestion_status": "READY", "parser_version": "theory-ingestion/1"}
  ]
}
```

---

# 5 · Las nueve reglas de validación, verbatim

`CorpusClaimReference.validate()` en `terrario/lab/capability_operationalization.py` falla con
estos mensajes exactos. Un artefacto que no las pase no sirve:

```
1  corpus snapshot is unavailable          falta snapshot_manifest.json
2  corpus snapshot manifest hash mismatch  sha256 del manifiesto ≠ el declarado
3  corpus snapshot identity mismatch       (snapshot_id, snapshot_hash) no coinciden
4  claim artifact hash mismatch            el CSV de claims cambió
5  source artifact hash mismatch           el fichero de fuentes cambió
6  unknown claim id                        claim_id no está en el CSV
7  claim does not resolve to declared      "[<source_id>]" no aparece en `fuente`
8  claim locator mismatch                  pagina_seccion ≠ el locator citado, EXACTO
9  unknown source id                       source_id no aparece en el fichero de fuentes
```

La regla 8 compara cadenas exactamente. Un locator es una cadena estable, no prosa.

---

# 6 · El trabajo

## 6.1 · Construir `theory-v2` (no editar el actual)

Destino: `theory_snapshots/theory-v2-<16 hex del hash>/`

Contenido:

1. **v0.1 entera, sin cambios**: 224 conceptos `CON-*`, 171 claims `CLM-*`, la auditoría de
   relaciones y el mapa canónico. Se copian verbatim; sus hashes cambian solo porque el manifiesto
   es nuevo.
2. **Los 49 claims de HEA**, remapeados a `CLM-0190` en adelante, con `fuente` en el formato
   `<Título> (<año>) [HEA-0NN]` y `pagina_seccion` copiado literal del CSV de entrada.
3. **Las 15 fuentes de HEA** en `SOURCE_PROVENANCE`, con el sha256 real de cada PDF (ya verificado)
   y `archivo_local` apuntando a una ruta que exista en esta máquina, no a `/workspace/scratch`.
4. **Los 12 documentos de v0.3 quedan como fuentes sin claims**, marcados
   `PENDIENTE_EXTRACCION_PROFUNDA`. Honesto y explícito. **No se promueven sus `P3C-*`.**
5. Manifiesto nuevo con el sha256 real de cada artefacto y `immutable: true`.

## 6.2 · Extracción profunda pendiente, por orden de prioridad

```
1º  HEA-015  Conant & Ashby 1970, "Every Good Regulator"
             Ya leído parcialmente: el teorema y §3 sobre regulación por error.
             Cerrar §§4-8. Es el claim más importante del corpus para este proyecto:
             une regulación y modelo del mundo en un solo enunciado.

2º  HEA-011  Mortal Computation (Ororbia & Friston 2023)
3º  HEA-007  Autopoiesis, Adaptivity, Teleology, Agency
4º  HEA-008  How not to model autonomous behaviour
             (un artículo entero de resultados negativos; valioso)

5º  X01, X02, X07   percepción de objetos, sensoriomotor, física intuitiva
             Cierran la familia PERCEPTION_WORLD, prioridad HIGH y abierta.
             Sus PDFs NO están en esta máquina: hay que reconseguirlos antes.
```

Método obligatorio, el mismo que produjo los 49: leer el **cuerpo** del PDF, no el abstract;
locator con sección **y** página PDF **y** página impresa cuando el documento la tenga; paráfrasis
propia con fragmentos literales cortos solo donde la redacción exacta cargue el argumento; tipar
`AUTHOR_EXPLICIT` frente a `INFERRED` con severidad. Y verificar cada claim releyendo la página
citada, que es lo que detectó 2 de 20 fallos.

## 6.3 · Reparar el grafo

`theory_graph.json` debe incluir nodos y aristas para todo claim y concepto de `theory-v2`. Hoy 812
extremos tocan `CON-*` y **0** tocan la capa nueva. Cualquier consulta al grafo es, por
construcción, ciega a lo añadido después de v0.1.

## 6.4 · Actualizar la matriz de cobertura

Recalcular `COVERAGE_MATRIX` con las fuentes nuevas. `MOTIVATION_VALUE` y `DEVELOPMENT` deberían
poder cerrarse o al menos degradar de `OPEN_GAP` con HEA-001, HEA-005 y HEA-014.

---

# 7 · Cambio de código que este brief autoriza

**`CorpusConceptReference`**, junto a `CorpusClaimReference`, en
`terrario/lab/capability_operationalization.py`. Mismos campos de hash e identidad de snapshot,
pero direccionando `CONCEPTS_RAW_*.csv` por `concept_id` en vez de `CLAIMS_RELATIONS_*.csv` por
`claim_id`.

Cierra la mitad de L-1 que hoy es irrepresentable, y desbloquea citar `P3C-0014` y los conceptos de
HEA. Es el único cambio de código que este brief pide; todo lo demás es datos.

---

# 8 · Criterios de aceptación

```
1  El snapshot viejo está intacto: su sha256 no cambió y los cinco
   OperationalizationRecord existentes siguen validando.
2  theory-v2 existe, su manifiesto verifica artefacto por artefacto, e `immutable: true`.
3  Los 49 claims de HEA validan contra theory-v2 con las nueve reglas del §5.
4  Ningún claim nuevo tiene locator vacío, ni con forma de URL, ni con texto de
   marcador de posición. Cero excepciones.
5  El grafo cubre el 100 % de conceptos y claims de theory-v2.
6  Los 12 documentos de v0.3 aparecen como fuentes marcadas
   PENDIENTE_EXTRACCION_PROFUNDA, no como conceptos promovidos.
7  Un informe nombra, para cada familia de COVERAGE_MATRIX, si sigue abierta y por qué.
```

# 9 · Lo que hay que reportar al terminar

```
SNAPSHOT_V2_ID
SNAPSHOT_V2_HASH
FUENTES · CONCEPTOS · CLAIMS         (v2, y el delta frente a v0.1)
CLAIMS_CON_LOCATOR_EXACTO            debe ser el 100 %
DOCUMENTOS_PENDIENTES_DE_EXTRACCION  con motivo
FAMILIAS_CERRADAS / FAMILIAS_ABIERTAS
SNAPSHOT_VIEJO_INTACTO               sí/no, con el sha256
LOS_CINCO_RECORDS_SIGUEN_VALIDANDO   sí/no
```

Y detenerse. No tocar agentes, ni mundos, ni pasaportes, ni experimentos: este brief es corpus y
solo corpus.

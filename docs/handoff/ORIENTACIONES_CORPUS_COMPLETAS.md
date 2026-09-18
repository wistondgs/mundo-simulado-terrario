# Orientaciones completas · Corpus de Terrario

**2026-09-18.** Documento único. Sustituye a `BRIEF_CORPUS_V2.md` y
`BRIEF_ADQUISICION_DOCUMENTOS.md`, que quedan como anexos de detalle.

Cubre: estado medido, defectos, contrato de calidad de un claim, tipos de documento, artefactos del
corpus, disciplina de hashes, procedimiento de construcción, adquisición pendiente, criterios de
aceptación e informe final.

---

# PARTE I · ESTADO MEDIDO

## I.1 · Qué hay

```
snapshot sellado   theory-f59dbb6d6ee3850c   inmutable, 21 artefactos
    44 fuentes · 283 conceptos · 189 claims
    224 candidatos canónicos · 206 relaciones auditadas · 8 hiperaristas
    1035 nodos de teoría · 956 aristas · 141 nodos de evidencia

corpus nuevo       homeostatic_enactive_agency_corpus_v0.1
    sha256 1aa71f903443e050e675aac63291fae4af82d2cd6a41fd653a9f7d8339251066
    integridad 29/29 · 15 PDFs · 21 claims semilla (título/abstract)
    extraído en profundidad por este trabajo: 176 claims con locator
```

## I.2 · Cuánto se usa

```
ids del corpus que aparecen en todo el árbol de producción     9
de esos, que soportan algo real                                2

alcanzable desde alguna capacidad
    claims        2 / 189  =  1.06 %
    fuentes       1 / 44   =  2.27 %
    conceptos     0 / 283  =  0.00 %
```

Ninguno de los nueve `concept_id` de los pasaportes existe en el corpus. Los mundos diagnósticos
tienen **cero** referencias: `grep -cin 'corpus|claim|CLM-|TI-0|P3C'` devuelve 0 en
`world_generator.py` y `world_oracles.py`. El subsistema de grafo —unas 5.700 líneas— está
construido y **vacío** en el almacén vivo.

---

# PARTE II · LOS DEFECTOS

## II.1 · Dos capas, y la división es perfecta

```
                  conceptos   con definición del autor    claims   con locator real
v0.1                    224          224  (100 %)            171        171  (100 %)
v0.3 patch               59            0  (  0 %)             18          0  (  0 %)
```

La capa v0.3 no está mal extraída: **no está extraída**. Doce documentos entraron como títulos con
metadatos. El propio `CORPUS_EXPANSION_REPORT_v0.3.md` la declara no canónica.

## II.2 · El grafo ignora la capa nueva

`theory_graph.json`: de 956 aristas, **812 extremos tocan `CON-` (v0.1) y 0 tocan `P3C-` (v0.3)**.
Cualquier consulta al grafo es ciega a todo lo añadido después de v0.1.

## II.3 · Las 21 familias conceptuales siguen abiertas

`COVERAGE_MATRIX_v0.3.csv`: `remaining_status = OPEN_GAP` en las 21. El parche se hizo para
cerrarlas y no cerró ninguna. Prioridad `HIGH` y abiertas: `PERCEPTION_WORLD`,
`PHYSICAL_STRUCTURE`, `LEARNING`, `NUMBER_QUANTITY`, `CREATIVITY_GENERATION`, `MOTIVATION_VALUE`,
`DEVELOPMENT`, `TRANSMISSION_CULTURE`, `EVOLUTION`, `ANIMAL_COGNITION`.

## II.4 · Los conceptos no son citables — defecto raíz

El esquema de procedencia direcciona **claims**. No existe campo que ate una capacidad a un
**concepto**. La ley L-1 exige «conexión explícita con corpus **y concepto**»: la mitad «concepto»
es irrepresentable en el código.

Consecuencia concreta: `P3C-0014` (Intelligent Adaptive Curiosity, Oudeyer) existe en el corpus y
**no hay forma de citarlo**. Los espacios `P3R-*` y `CLM-*` son disjuntos y nunca se cruzan.

## II.5 · Solo el 29 % de los conceptos es enlazable

De 187 nombres normalizados distintos, **56 aparecen en algún claim**. Los otros 131 no podrán
citarse ni con el arreglo de II.4, porque no hay claim que los mencione. Es límite del corpus, no
del código.

---

# PARTE III · CONTRATO DE CALIDAD DE UN CLAIM

Esta parte es la más importante. Un corpus vale lo que vale su claim más flojo.

## III.1 · Qué es un claim válido

Una tripleta `concepto --RELACIÓN--> concepto` que **un autor afirma**, con dirección a la página
donde lo afirma.

```
claim_id                  CLM-NNNN
source_concept            nombre normalizado, minúsculas
relation_type             REQUIERE · PRODUCE · DEPENDE_DE · INHIBE · FACILITA
                          PARTE_DE · ACTUALIZA · MODULA · ASOCIADO_CON
target_concept            nombre normalizado
autor                     como figura en el documento
fuente                    <Título> (<año>) [<source_id>]      ← formato exacto, ver III.4
pagina_seccion            sección + página. Ver III.3
claim_text_or_paraphrase  paráfrasis propia + fragmento literal corto si es imprescindible
explicit_or_inferred      AUTHOR_EXPLICIT · AUTHOR_EXPLICIT_PARAPHRASE · INFERRED
evidence_type             OPERATIONAL_DEFINITION · FORMAL_DERIVATION · EMPIRICAL_RESULT
                          THEORETICAL_CLAIM · REVIEW_SUMMARY
confidence                HIGH · MEDIUM · LOW
notes                     matices, exclusiones, advertencias de no fusionar
```

## III.2 · El fallo real, medido

De 68 verificaciones independientes de los 176 claims extraídos, **7 fallaron. Los 7 con
`locator_correct = True` y `claim_supported = False`.**

**Ningún locator estaba mal. Los siete sobre-afirmaban.** Ahí es donde hay que apretar, y no en la
citación. Los tres modos observados:

**a) Inferencia tipada como explícita.** El extractor añade una cláusula de cierre —«lo cual
implica que…»— y la ficha entera queda `AUTHOR_EXPLICIT`. Regla: si una frase de la ficha no está
en el documento, **la ficha es `INFERRED`**, o se parte en dos.

**b) Encuadre importado de otro paper.** HEA-002: la ficha decía que la recompensa «ya no es una
diferencia de drives entre dos pasos». Eso es Keramati & Gutkin, a quien ese paper cita pero no
afirma. Regla: **lo que el paper cita no es lo que el paper afirma.**

**c) Definición que el propio artículo no usa.** En el mismo caso, el verificador notó que el
algoritmo del paper **nunca usa esa recompensa como señal de aprendizaje** — entrena sobre el nivel
del drive. Regla: antes de tipar `OPERATIONAL_DEFINITION`, comprobar que **el artículo opera con
esa definición**, no solo que la enuncia.

## III.3 · Locator

```
CORRECTO      §3, PDF p. 5, journal p. 93
              part II, ch. 11, PDF pp. 108–110
              §4.0.1, ecuación (7), PDF p. 10, p. impresa 10
              Figura 5, pie de figura, PDF p. 31

PROHIBIDO     https://arxiv.org/pdf/2507.04998        ← URL, no locator
              "secciones indicadas en SOURCE_PROVENANCE"
              "locator exacto requiere lectura de PDF"
              vacío
```

`validate()` compara `pagina_seccion` **como cadena exacta**. Un locator es un identificador
estable, no prosa.

**Paginación divergente.** Si la numeración del PDF no coincide con la impresa, **decirlo** y marcar
cuál es fiable. Caso real: HEA-015 es una recomposición en Word de 2004, 10 páginas contra las 9
del artículo, sin folios impresos; la correspondencia `PDF 1 = journal 89` es inferencia lineal y
**deriva**.

## III.4 · La convención de `fuente` que rompió una capa entera

```
CORRECTO   Reinforcement Learning: An Introduction (Second Edition) (2018) [TI-0097]
INCORRECTO ["Intrinsic Motivation Systems...", "Oudeyer et al."]
```

`validate()` busca la subcadena `[<source_id>]` dentro de `fuente`. El parche v0.3 escribió una
lista entre corchetes, y **ése es el único motivo** por el que su único claim es rechazado. Ese
detalle inutilizó doce documentos.

## III.5 · Método de extracción obligatorio

```
1. Leer el CUERPO del PDF. Título y abstract NO bastan — es lo que este trabajo reemplaza.
2. Locator con sección + página PDF + página impresa cuando exista.
3. Paráfrasis propia. Literal corto (<15 palabras) solo donde la redacción cargue el argumento.
4. Tipar AUTHOR_EXPLICIT frente a INFERRED con severidad. Ante la duda, INFERRED.
5. Verificar cada claim releyendo la página citada. Detectó 7 de 176; sin ese paso,
   los 7 habrían entrado.
6. Rendir poco es legítimo. Un comentario de una página sostiene tres claims, no doce.
   Rellenar es cómo se fabrica un corpus decorativo.
```

## III.6 · Los 7 claims rechazados

Están en `HEA_CLAIMS_EXTRAIDOS_v1.csv` mezclados con los buenos. Antes de sellar v2 hay que
**retiparlos o quitarlos**, nunca promoverlos. Afectan a HEA-001 (2), HEA-002 (1), HEA-009 (2) y
HEA-020 (2).

---

# PARTE IV · TIPOS DE DOCUMENTO

No todos aportan lo mismo, y confundirlos es parte del problema.

| tipo | qué aporta | qué NO aporta | cómo tiparlo |
|---|---|---|---|
| **Fuente primaria teórica** — Ashby, Maturana, Conant | definiciones operacionales, derivaciones formales | resultados empíricos | `OPERATIONAL_DEFINITION`, `FORMAL_DERIVATION` |
| **Paper empírico** — Dulberg, Pathak | mediciones con condiciones | definiciones canónicas | `EMPIRICAL_RESULT` |
| **Review** — HEA-001, HEA-011 | mapa del campo, vocabulario | autoridad sobre lo que resume | `REVIEW_SUMMARY`. **Un review no es fuente del claim que resume** |
| **Position paper** — HEA-010 | huecos declarados, agenda | evidencia | `THEORETICAL_CLAIM`, y severidad con `AUTHOR_EXPLICIT` |
| **Comentario / abstract de congreso** — HEA-003, HEA-020 | el dato que el autor destaca | detalle metodológico | pocos claims, y decirlo |
| **Resultado negativo** — HEA-008 | qué NO funciona y por qué | — | tan valioso como uno positivo. Capturar **el motivo**, no el veredicto |

**Regla transversal:** un claim derivado de un review debe apuntar al review como `fuente`, no al
trabajo original que el review cita. Si hace falta el original, se adquiere el original.

---

# PARTE V · ARTEFACTOS DEL CORPUS

## V.1 · Los que existen y sirven

| artefacto | contenido | estado |
|---|---|---|
| `CLAIMS_RELATIONS_v0.1.csv` | 171 claims | usable entero |
| `CONCEPTS_RAW_v0.1.csv` | 224 conceptos con definición | usable entero |
| `RELATIONS_AUDIT_v0.2.csv` | 206 relaciones con fuerza de evidencia | usable |
| `CONCEPT_CANONICAL_MAP_v0.2.csv` | 224 candidatos canónicos | usable |
| `SOURCE_PROVENANCE_v0.3.csv` | 14 fuentes con DOI y sha256 | metadatos correctos |
| `SOURCE_SAMPLE_v0.1.md` | tabla de fuentes `TI-*` | usable |
| `ONTOLOGY_v0.2.md`, `AMBIGUITIES_v0.2.md`, `CONCEPT_CONFLICTS_v0.1.md` | tipos, homónimos, conflictos | usable, y **poco consultado** |
| `COVERAGE_MATRIX_v0.3.csv` | 21 familias | diagnóstico |
| `theory_graph.json` | grafo | usable, incompleto (II.2) |
| `snapshot_manifest.json` | hashes | correcto |

## V.2 · Los que faltan

**1 · Índice concepto → claims.** Hoy el enlace es por nombre normalizado y hay que reconstruirlo
cada vez. Con él, II.5 se responde en una consulta.

**2 · Registro de exclusión.** Qué se leyó y se decidió NO incorporar, con motivo. Hoy un documento
descartado es indistinguible de uno nunca visto.

**3 · Índice de refutación.** Qué claim contradice a cuál. El corpus tiene `CONCEPT_CONFLICTS` para
conceptos y **nada para claims**. Hace falta: Ashby §5/2 rechaza el criterio de «respuesta
correcta»; HEA-005 refuta la escalarización; HEA-008 refuta el agente auto-instruido. Sin este
índice, un corpus puede sostener una tesis y su contraria sin que salte nada.

**4 · Trazabilidad claim → capacidad.** El corpus no sabe qué claims está usando el laboratorio.
Por eso el 1.06 % se descubrió auditando y no consultando.

**5 · Versión del extractor por claim.** Los 176 salieron de un método concreto y verificado; los
21 semilla, de otro. Hoy un CSV no distingue con qué rigor se produjo cada fila.

---

# PARTE VI · DISCIPLINA DE HASHES

## VI.1 · La regla

> **Una URL sola no cuenta como incorporación.** Un documento adquirido exige fichero local,
> procedencia, metadatos mínimos, validación y sha256.

Es del README del paquete HEA y es correcta. Un PDF sin hash es un PDF, no una fuente.

## VI.2 · Los cuatro niveles

```
1. sha256 del DOCUMENTO      cada PDF. Verifica que es el que el corpus dice.
2. sha256 del ARTEFACTO      cada CSV/MD. Verifica que la extracción no cambió.
3. sha256 del MANIFIESTO     cubre todos los artefactos. Es la raíz.
4. snapshot_hash             identidad del snapshot entero.
```

`CorpusClaimReference` los comprueba **todos** en cada validación. Por eso el snapshot no puede
editarse: un byte invalida los cuatro niveles hacia arriba.

## VI.3 · Las nueve reglas de `validate()`, verbatim

```
1  corpus snapshot is unavailable            falta snapshot_manifest.json
2  corpus snapshot manifest hash mismatch    sha256 del manifiesto ≠ el declarado
3  corpus snapshot identity mismatch         (snapshot_id, snapshot_hash) no coinciden
4  claim artifact hash mismatch              el CSV de claims cambió
5  source artifact hash mismatch             el fichero de fuentes cambió
6  unknown claim id                          claim_id no está en el CSV
7  claim does not resolve to declared source "[<source_id>]" no aparece en `fuente`
8  claim locator mismatch                    pagina_seccion ≠ el citado, EXACTO
9  unknown source id                         source_id no aparece en el fichero de fuentes
```

## VI.4 · Formato del manifiesto

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

## VI.5 · Trampas conocidas

**Rutas absolutas.** El `SHA256SUMS.txt` de HEA usa rutas de la máquina de construcción
(`/workspace/scratch/...`), así que `sha256sum -c` falla con «no existe el fichero». **No es fallo
de integridad**: hay que reescribir el prefijo. Verificado así, da 29/29.

**BOM.** Los CSV v0.1 llevan BOM UTF-8. Leer con `encoding="utf-8-sig"` o la primera columna se
llamará `﻿claim_id` y ninguna búsqueda por `claim_id` encontrará nada.

**El snapshot actual es inmutable.** Su id, su hash y el sha256 de su manifiesto son **constantes
de módulo** en `terrario/lab/capability_operationalization.py`. Cambiar un byte invalida la
procedencia de las cinco capacidades que hoy la tienen. **No se edita. Se construye uno nuevo al
lado.**

---

# PARTE VII · CONSTRUIR `theory-v2`

Destino: `theory_snapshots/theory-v2-<16 hex>/`

```
1. v0.1 ENTERA, verbatim
       224 conceptos CON-* · 171 claims CLM-* · auditoría · mapa canónico

2. LOS 176 CLAIMS DE HEA
       remapear a CLM-0190 en adelante
       fuente en formato  <Título> (<año>) [HEA-0NN]
       pagina_seccion copiado literal
       LOS 7 RECHAZADOS: retipar o quitar. No promover.

3. LAS 15 FUENTES HEA en SOURCE_PROVENANCE
       sha256 real de cada PDF, ya verificado
       archivo_local a una ruta que exista en ESTA máquina

4. LOS 12 DOCUMENTOS DE v0.3 como fuentes SIN claims
       marcados PENDIENTE_EXTRACCION_PROFUNDA
       sus P3C-* NO se promueven

5. CONCEPTOS NUEVOS de los 176 claims
       con definicion_del_autor NO VACÍA. Si no se puede extraer, no entra.

6. ARTEFACTOS NUEVOS de la Parte V.2
       índice concepto→claims · registro de exclusión · índice de refutación

7. GRAFO cubriendo el 100 % de conceptos y claims

8. COVERAGE_MATRIX recalculada

9. MANIFIESTO con sha256 real de cada artefacto e immutable: true
```

**Cambio de código autorizado, y solo uno:** `CorpusConceptReference` junto a
`CorpusClaimReference`. Mismos campos de hash e identidad, direccionando `CONCEPTS_RAW_*.csv` por
`concept_id`. Debe encadenar **concepto → claim con locator → fuente `[TI-XXXX]`**, y exigir
`definicion_del_autor` no vacía. Cierra la mitad de L-1 que hoy no existe.

---

# PARTE VIII · DOCUMENTOS A ADQUIRIR

## VIII.1 · Doce ya aprobados, solo falta el fichero

Tienen `source_id`, DOI y **sha256 declarado**. Su `archivo_local` apunta a `/workspace/scratch/`.
Como el hash está declarado, la adquisición es **verificable**: si no coincide, **no es el
documento** y hay que reportarlo, no usarlo.

```
PRIORIDAD 1 · el mundo        (familia PERCEPTION_WORLD, HIGH, abierta)
  X01  Spelke, Principles of Object Perception, 1990      10.1207/s15516709cog1401_3
  X02  O'Regan & Noë, Sensorimotor account, 2001          10.1017/S0140525X01000115
  X07  Piloto et al., Intuitive physics learning, 2022    10.1038/s41562-022-01394-8

PRIORIDAD 2 · desarrollo y linaje     (DEVELOPMENT + LEARNING, HIGH, abiertas)
  X16  Smith & Thelen, Development as a dynamic system    10.1016/S1364-6613(03)00156-6
  X03  Adolph & Hoch, Motor Development, 2019             10.1146/annurev-psych-010418-102836
  TI-0085-PATCH  Kirkpatrick et al., Catastrophic forgetting, 2017
  TI-0092-PATCH  Wang, Lehman, Clune & Stanley, POET, 2019

PRIORIDAD 3 · motivación y memoria
  X06  Oudeyer, Kaplan & Hafner, Intrinsic Motivation, 2007   10.1109/TEVC.2006.890271
  X08  Squire et al., Memory Consolidation, 2015              10.1101/cshperspect.a021766

PRIORIDAD 4 · no bloquean hoy
  X09, X11, X12, X13, X14   cultura, evolución cultural, adaptación colectiva
```

## VIII.2 · Sin `source_id`: hay que elegir el documento, no solo conseguirlo

**B.1 · Ultraestabilidad implementada y medida** en un agente artificial. Ashby la define
(`HEA-014 §7/26`) y Di Paolo & Iizuka la operacionalizan parcialmente. Sin una fuente que la
implemente, el segundo lazo se diseñaría por criterio propio.

**B.2 · Medición de agencia bajo perturbación.** `HEA-009` puede bastar — da protocolo de
deformación estructural única, puntuación de adaptividad espacial y temporal, y firma adaptativa
exigiendo ambas. Si basta, cerrado; si no, hace falta otra.

**B.3 · Emociones funcionales.** Sofroniew et al., Anthropic 2026, `arXiv:2604.07729`. **No está en
ninguna máquina de este proyecto.** Si va a fundamentar conceptos, se ingiere con sha256 como
cualquiera. Advertencia: sus emociones funcionales son **heredadas del preentrenamiento sobre texto
humano**; un organismo que no lee no las hereda. De ahí se toma el método, no el mecanismo.

## VIII.3 · Qué devolver por documento

```
source_id · fichero local · sha256 · COINCIDE_CON_CORPUS (sí/no/no aplica)
url y fecha de recuperación · tipo de acceso legal
```

Si no se consigue: `NO_ADQUIRIDO` con motivo. **Un hueco declarado es corpus; uno tapado no.**

---

# PARTE IX · CRITERIOS DE ACEPTACIÓN

```
 1  El snapshot viejo intacto: su sha256 no cambió y los 5 OperationalizationRecord validan.
 2  theory-v2 existe, su manifiesto verifica artefacto por artefacto, immutable: true.
 3  Los 176 claims validan con las nueve reglas de VI.3.
 4  CERO claims con locator vacío, con forma de URL o con marcador de posición.
 5  Los 7 rechazados están retipados o ausentes. Ninguno promovido tal cual.
 6  Todo concepto nuevo tiene definicion_del_autor no vacía.
 7  El grafo cubre el 100 % de conceptos y claims de v2.
 8  Los 12 documentos de v0.3 figuran como fuentes PENDIENTE_EXTRACCION_PROFUNDA.
 9  Existen los tres artefactos nuevos de V.2 (índice concepto→claims, exclusión, refutación).
10  Un informe dice, por familia de COVERAGE_MATRIX, si sigue abierta y por qué.
```

# PARTE X · INFORME FINAL

```
SNAPSHOT_V2_ID · SNAPSHOT_V2_HASH
FUENTES · CONCEPTOS · CLAIMS          (v2, y delta frente a v0.1)
CLAIMS_CON_LOCATOR_EXACTO             debe ser 100 %
CLAIMS_RETIPADOS · CLAIMS_DESCARTADOS con motivo
CONCEPTOS_CITABLES                    los que tienen claim que los menciona
DOCUMENTOS_ADQUIRIDOS                 con COINCIDE_CON_CORPUS
DOCUMENTOS_NO_ADQUIRIDOS              con motivo
FAMILIAS_CERRADAS / FAMILIAS_ABIERTAS
SNAPSHOT_VIEJO_INTACTO                sí/no, con sha256
LOS_CINCO_RECORDS_SIGUEN_VALIDANDO    sí/no
```

Y detenerse. **Esto es corpus y solo corpus**: no tocar agentes, mundos, pasaportes ni experimentos.

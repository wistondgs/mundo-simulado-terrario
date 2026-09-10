# CORPUS_EXPANSION_REPORT_v0.3

Estado final: **CORPUS EXPANSION INCOMPLETE**.

Este parche reconstruye T1.2 como auditoria de cobertura y ampliacion controlada del corpus. No define inteligencia, no construye grafo/hipergrafo y no traduce hallazgos a RNFE, Genesis ni Terrario.

## Estado de partida auditado

Se revisaron los artefactos historicos disponibles: T1 v0.1, ONTOLOGY_v0.2, CONCEPT_CANONICAL_MAP_v0.2, RELATIONS_AUDIT_v0.2, AMBIGUITIES_v0.2, HYPEREDGE_CANDIDATES_v0.2, CORPUS_INTEGRITY_PATCH_v0.1, DEVELOPMENTAL_COGNITION_PATCH_v0.1 y COVERAGE_MATRIX_v0.2. Los artefactos historicos no fueron modificados.

El corpus base contiene cobertura fuerte para varias tradiciones clasicas y de IA formal, pero el alcance nuevo de T1.2 exige granularidad distinta: no basta con tener fuentes sobre inteligencia general si faltan subfamilias como object individuation, affordances, cultura acumulativa, consolidacion, numerosidad o evolucion cognitiva.

## Areas realmente poco cubiertas

Antes del parche estaban debiles o ausentes: percepcion/construccion del mundo, materia y estructura fisica, numero y cantidad, creatividad/generacion, transmision cultural, evolucion biologica de capacidades cognitivas y varios subtemas de animal cognition. Tambien estaban solo parcialmente cubiertos memoria, aprendizaje activo, desarrollo historico de capacidades, cognicion social y adaptacion colectiva.

## Fuentes incorporadas

Se incorporaron 12 documentos nuevos con archivo local y hash cuando la descarga legal fue posible: Spelke 1990, O'Regan & Noe 2001, Adolph & Hoch 2019, Oudeyer/Kaplan/Hafner 2007, Piloto et al. 2022, Squire et al. 2015, Laland/Odling-Smee/Myles 2010 como preview, Mesoudi & Thornton 2018, Derex et al. 2019, Derex et al. 2025, Galesic et al. 2023 y Smith & Thelen 2003. Ademas se extrajeron dos fuentes ya presentes en el corpus original para cubrir continual learning y open-ended development: Kirkpatrick et al. 2017 y Wang et al. 2019.

## Conceptos RAW nuevos o reforzados

El parche agrega 59 entradas RAW. No deben leerse como conceptos canonicos. Muchas son formas nuevas, subtipos o vocabulario disciplinar que toca familias ya existentes: object perception, cohesion, boundedness, rigidity, sensorimotor contingencies, affordances, learning progress, object-centred representations, systems consolidation, cumulative cultural evolution, canalized exploration, collective adaptation, self-organization, elastic weight consolidation y open-ended learning.

Conceptos existentes que ganan cobertura: percepcion, representacion, aprendizaje, memoria, adaptacion, exploracion, causalidad, cultura, inteligencia colectiva, desarrollo y olvido catastrofico. El ganho es documental y conceptual, no una fusion semantica.

## Contradicciones nuevas

1. Vision como representacion de objetos vs vision como dominio sensorimotor activo.
2. Core/object priors o estructura object-centric suministrada vs desarrollo como autoorganizacion historica multicausal.
3. Mejora tecnologica cultural con comprension causal explicita vs mejora cultural sin comprension causal paralela.
4. Cultura acumulativa como mecanismo de mejora vs transmision social como canalizacion que tambien conserva teorias inutiles.
5. Inteligencia/adaptacion colectiva como rendimiento estatico vs adaptacion colectiva como proceso dinamico bajo cambio ambiental.

## Candidatos a relaciones de orden superior

No se promueve ninguna hiperarista. Quedan marcadas como candidatas: percepcion de objetos dependiente de cohesion + limites + rigidez + no accion a distancia; CCE dependiente de modificacion + transmision social + mejora de rendimiento + cambio secuencial repetido; collective adaptation dependiente de estrategias de integracion social + ambiente social + estructura del problema; POET como combinacion de generacion de ambientes + optimizacion de soluciones + transferencia.

## Documentos no obtenidos o no usados plenamente

No se declara saturacion. Laland et al. 2010 quedo como preview/abstracto y no cierra evolucion. Quedaron pendientes fuentes plenas para Piaget, Vygotsky, Karmiloff-Smith, Dehaene/ANS, teoria de la mente comparada, herramientas en animales, distributed cognition de Hutchins, swarm intelligence, creatividad humana/animal, active perception/predictive processing como tradiciones independientes y embodied AI/artificial life.

## Gate

**CORPUS EXPANSION INCOMPLETE**.

La expansion mejora tres huecos prioritarios: sustrato perceptivo/core knowledge, desarrollo historico de capacidades y transmision social-cultural. Sin embargo, permanecen huecos de alta prioridad en numero/cantidad, creatividad, evolucion biologica de la cognicion, animal cognition y desarrollo clasico completo. Por tanto no corresponde usar `CORPUS COVERAGE SATURATED FOR CURRENT SCOPE`.

# CORPUS_INTEGRITY_PATCH_v0.1

## Resultado

Este parche no modifica ni sobrescribe el corpus ni los cinco artefactos T1. Aísla siete registros defectuosos, establece la identidad bibliográfica correcta y documenta el efecto sobre las afirmaciones. Los seis PDF erróneos y el HTML incompleto quedan en estado **QUARANTINED_DO_NOT_CITE** dentro de la interpretación de v0.2.

| ID | Registro catalogado | Contenido encontrado | Defecto | Resolución | Fuente verificada | Base de autoridad | Impacto en claims |
|---|---|---|---|---|---|---|---|
| TI-0046 | Aron K. Barbey — Network Neuroscience Theory of Human Intelligence (2018) | Asymptotic structure of spacetime and the Newman-Penrose formalism | PDF y URL arXiv equivocados | REPLACEMENT_LOCATED_VERIFIED | https://www.decisionneurosciencelab.org/wp-content/uploads/2013/08/Barbey_20171.pdf | copia del laboratorio del autor + DOI 10.1016/j.tics.2017.10.001 | 0 claims T1; sin contaminación |
| TI-0098 | Karl Friston — The Free-Energy Principle: A Unified Brain Theory? (2010) | documento de comunicaciones de banda ancha | PDF y arXiv equivocados | REPLACEMENT_LOCATED_VERIFIED | https://www.fil.ion.ucl.ac.uk/~karl/NRN.pdf | página del autor en UCL + DOI 10.1038/nrn2787 | 0 claims T1; sin contaminación |
| TI-0116 | Danielle S. Bassett; Olaf Sporns — Network Neuroscience (2017) | documento sobre patrones puntuales | PDF y arXiv equivocados | REPLACEMENT_LOCATED_VERIFIED | https://cenl.ucsd.edu/CompNeuro/Readings/Week1/Bassett-Sporns%2BNetwork-Neuroscience%2BNN%2B2017.pdf | repositorio docente UCSD + DOI 10.1038/nn.4502 | 0 claims T1; sin contaminación |
| TI-0126 | José Hernández-Orallo et al. — Measuring Intelligence through Games (2010) | documento de complejidad estadística | PDF, arXiv, año y autoría conflados | BIBLIOGRAPHY_CORRECTED_AND_SOURCE_VERIFIED | https://arxiv.org/abs/1109.1314 | arXiv 1109.1314: Tom Schaul, Julian Togelius, Jürgen Schmidhuber (2011) | 0 claims T1; el ID debe conservar historial de corrección |
| TI-0127 | José Hernández-Orallo; David L. Dowe — The Anytime Universal Intelligence Test (2010) | Multi-latin squares | PDF y arXiv equivocados; título catalogado no coincide con la publicación primaria | BIBLIOGRAPHY_CORRECTED_AND_SOURCE_VERIFIED | https://users.monash.edu.au/~dld/Publications/2010/HernandezOrallo%2BDowe2010ArtificialIntelligenceJArticle.pdf | página del coautor: Measuring universal intelligence: Towards an anytime intelligence test | 0 claims T1; no usar el título previo como procedencia |
| TI-0144 | Demis Hassabis et al. — Neuroscience-Inspired Artificial Intelligence (2017) | documento de física de protonterapia | PDF y arXiv equivocados | REPLACEMENT_LOCATED_VERIFIED | https://www.columbia.edu/cu/appliedneuroshp/Papers/out.pdf | copia universitaria; DOI 10.1016/j.neuron.2017.06.011 | 0 claims T1; sin contaminación |
| TI-0064 | John McCarthy — Programs with Common Sense (1959) | HTML índice de 535 caracteres | texto incompleto | FULL_PDF_LOCATED_VERIFIED | https://www-formal.stanford.edu/jmc/mcc59.pdf | sitio histórico oficial de John McCarthy en Stanford | 0 claims T1; elegible para extracción futura |

## Hallazgos de control

- En los siete registros había **0 afirmaciones T1**. Por tanto, no fue necesario retirar claims existentes y no hay propagación documental hacia los 171 registros de relaciones.
- Un SHA-256 correcto sólo acredita estabilidad de bytes, no que el archivo corresponda al título. La validación v0.2 exige coincidencia independiente de título, autoría, año y, cuando existe, DOI.
- TI-0126 no era sólo una descarga equivocada: el registro mezclaba el título de Schaul–Togelius–Schmidhuber (2011) con la autoría de Hernández-Orallo.
- TI-0127 mezclaba una etiqueta no canónica con un arXiv ajeno. La fuente primaria verificada es *Measuring universal intelligence: Towards an anytime intelligence test*.
- McCarthy queda recuperado mediante el PDF oficial de Stanford; el HTML previo no se acepta como texto completo.

## Regla de uso

Hasta que los binarios del corpus maestro sean reemplazados y re-hasheados en una versión posterior, cualquier análisis debe citar las URL verificadas de esta tabla y no las rutas locales defectuosas. Este parche es una capa de reparación trazable, no una reescritura silenciosa del pasado.

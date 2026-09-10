# AMBIGUITIES_v0.2

## Regla

La tabla canónica es una vista reversible. `concept_id` conserva el nodo RAW; `canonical_candidate_id` permite comparar ocurrencias sin declarar identidad ontológica.

| Término o familia | Lecturas incompatibles/solapadas | Decisión v0.2 |
|---|---|---|
| intelligence | propiedad latente, rendimiento, adquisición, organización o etiqueta operacional | mantener instancias por teoría; nunca fusionar por palabra |
| learning | cambio conductual, adquisición representacional, ajuste paramétrico o proceso cultural | separar producto, proceso, mecanismo y escala temporal |
| adaptation / adjustment / accommodation / plasticity / flexibility | resultado funcional, ajuste, mecanismo piagetiano, capacidad de cambio o cambio de estrategia | RELATED_BUT_DISTINCT; prohibida la fusión automática |
| memory | almacén, recurso de trabajo, recuperación, memoria compartida o estado persistente | tipar por función y frontera del sistema |
| representation | contenido, vehículo, modo, modelo o relación semántica | conservar teoría, formato y función |
| reason / reasoning | facultad, proceso inferencial, desempeño psicométrico o explicación | separar capacidad, mecanismo y medición |
| goal / value / utility / reward | estado deseado, criterio normativo, señal escalar o función matemática | no tratarlos como sinónimos |
| action / intervention / exploration | salida motora, manipulación causal, búsqueda informativa o elección | distinguir acción epistémica de acción instrumental |
| selection | atención, elección de política, selección natural, selección de estrategia | HOMONYM_DIFFERENT_MEANING salvo prueba contextual |
| precision | exactitud empírica, parámetro bayesiano o resolución representacional | HOMONYM_DIFFERENT_MEANING |
| creativity / imagination | proceso, fase, capacidad, producto o exploración contrafáctica | no identificar imaginación con logro creativo |
| association | dependencia estadística, enlace aprendido o mera coocurrencia textual | nivel de evidencia obligatorio; nunca elevar a causa |

## Estadística de normalización

- Entradas RAW preservadas: **224**.
- Candidatos canónicos léxicos: **187**.
- Ninguna fila RAW fue eliminada ni reescrita.
- `EXACT_SYNONYM` sólo expresa identidad ortográfica dentro de la vista; no autoriza fusionar teorías.
- Términos polisémicos se marcan `RELATED_BUT_DISTINCT` o `UNRESOLVED` incluso cuando comparten spelling.

## Falsas equivalencias que deben evitarse

- frecuencia alta ≠ centralidad causal;
- desempeño alto ≠ capacidad de adquirir nuevas habilidades;
- conocimiento almacenado ≠ inteligencia;
- control inhibitorio ≠ inteligencia general;
- acción ≠ intervención informativa;
- correlación con g ≠ mecanismo producido por g;
- coordinación social ≠ suma de inteligencias individuales.

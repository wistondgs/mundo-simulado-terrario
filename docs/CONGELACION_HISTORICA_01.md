# Congelación del programa experimental histórico

**2026-09-21** · frontera entre el programa histórico y el nuevo programa de
microcapacidades. Manifiesto legible por máquina en
[CONGELACION_MANIFIESTO.json](docs/CONGELACION_MANIFIESTO.json), generado por
[congelacion_manifiesto.py](scripts/congelacion_manifiesto.py).

## Por qué

**Cambió la pregunta experimental.** El programa antiguo preguntaba si un
organismo concreto adquiría una capacidad concreta. El nuevo preguntará qué
ocurre al acumular capacidades mínimas contra mundos variados sistemáticamente.
Mezclarlos contaminaría la interpretación, y reinterpretar los experimentos
viejos para que parezcan haber probado la teoría nueva sería retrospectividad.

**Congelar significa** preservar, identificar, clasificar, cerrar
interpretación y separar.

**No significa** borrar, depreciar, declarar incorrecto, migrar, reescribir
resultados ni poner verdes los tests históricos.

## La frontera

```
último commit del programa histórico   97f13a136e36  experiment/cognitive-live-observatory-01
primer commit del régimen nuevo        el que introduce este manifiesto
```

**No se creó tag.** El repositorio tiene **cero** tags, así que no hay
convención que seguir e inventar una es una decisión de repositorio, no mía. La
frontera autoritativa es el manifiesto. Si querés el tag, se añade en un minuto.

## Qué queda congelado · 16 entradas

Los commits **se leen de cada worktree**, no se teclean. El modo de fallo
catalogado de este proyecto es una campaña que sella transcribiendo valores a
constantes sin que nada compruebe la transcripción contra el documento; un
manifiesto que lo repitiera sería el mismo defecto vestido de frontera.

| campaña | revisión | resultado | motivo |
|---|---|---|---|
| 1.0 contingencia sensorimotora | `3ef016c` | demostrada en su mundo | programa superado |
| — reversión del mapa motor (sonda) | `3ef016c` | sonda, no adquisición | referencia |
| 1.1 orientación direccional | `3ef016c` | demostrada | programa superado |
| 1.2 proximidad cualitativa | `3ef016c` | demostrada y reconciliada · techo 8/55 | programa superado |
| 1.3 persistencia un paso | `32d400f` | verificada y reconciliada | programa superado |
| 1.4 ligadura conjuntiva | `68d852d` | verificada y reconciliada | programa superado |
| fusión B+Q+H+M | `a1f180b` | interacción superaditiva | programa superado |
| **1.5 memoria selectiva** | `02d5c43` | congelado · sólo diseño | **anomalía sin resolver** |
| 1.6 regularidad temporal | `c2b808b` | POSITIVO | programa superado |
| 1.7 contingencia de la acción | `6cf55a4` | POSITIVO | programa superado |
| **1.8 estado predictivo** | `9b7bdb0` | `FAMILY_MISMATCH` · sin presupuesto | **anomalía sin resolver** |
| 1.8 adjudicación | `eaf9d26` | `UNKNOWN` · no auditada | referencia |
| **EXP-ADAPTIVE-FORAGING-01** | `6d41a95` | ambos veredictos `INSUFFICIENT_INFORMATION` | **limitación de instrumento** |
| OCF-G1 / OCF-G3 | `25fd0d0` | G1 no pasó tal como se midió; G3 cerrado | referencia |
| D5 copia de experiencia | `c394a82` | disociación se sostiene | referencia |
| los 10 pasaportes A4/A5 | `97f13a1` | 1 certificable, 0 con experimento | referencia |

**Tres campañas no se dejan contar como éxitos y no se las cuenta:** 1.5 con su
piloto irreproducible, 1.8 con la familia mal elegida, y el forrajeo con dos
veredictos de información insuficiente. La congelación las preserva tal como
acabaron.

## Los UNKNOWN que no se rellenan

**1.5.** El confirmatorio nunca corrió; hubo **dos pilotos** y el segundo dio
`529/540 = 97,96 %`. El piloto es `NON_REDERIVABLE`: ningún `.py` de ningún árbol
contiene sus semillas —`20260920`, `777`, `31337`, **quemadas**— ni marca alguna
de `level15`, y la magnitud del paso «no consta en la evidencia textual
preservada aquí». Entre los dos pilotos cambiaron además la rejilla de
presupuestos, la estructura de repetición **y** las semillas, así que atribuir el
salto al optimizador no está identificado. La **retirada** de los 21 fallos como
propiedad del problema se sostiene sola. `α`, el calendario de exploración y el
clasificador siguen `UNKNOWN`.

**1.8 adjudicación** y **D5**: sus hechos no están cubiertos por las secciones
auditadas de la cartografía y **no los reverifiqué** para esta congelación. Van
con alcance `UNKNOWN` y provenance que lo dice, en vez de con una descripción
plausible que nadie comprobó.

**Forrajeo**: el punto estimado se apoya en una sola semilla por condición.

## Orden histórico ≠ orden developmental

Que 1.6 ocurriera antes que 1.7 **no** significa que sea la secuencia óptima de
microcapacidades. Los números de nivel son cronología, no escalera.

Y hay una razón medida para insistir: el **linaje B es un reinicio deliberado**.
`9b0d39b` lo dice en el asunto y está verificado — `level16` importa de
`level1.world` sólo primitivas del cuerpo y del mundo, y **nada** de
`level11…level14`. Se hereda el cuerpo; no se hereda la cognición. Dos linajes
con numeración continua y sin continuidad cognitiva entre ellos.

Los resultados históricos pueden usarse como evidencia, contraejemplo,
antecedente, pista, fuente de mecanismos o de modos de fallo. **No** como
autoridad automática para decir que la capacidad A va antes que la B. Esa
secuencia se estudia de nuevo.

## Qué cruza la frontera y sigue vivo

```
WORLD INSTANCE  · configuración histórica concreta   → CONGELADO
WORLD DESIGNER  · maquinaria generadora              → ACTIVO
```

Activos: el **World Designer** (`world_generator`, `world_authoring`,
`world_contracts`, `world_oracles`), la **fábrica de niveles**
(`/home/wis/level-factory-01 · factory/`), los **hipergrafos**, el **corpus** y
la capa de conocimiento, la **infraestructura experimental genérica** —el carril
de archivo direccionado por contenido, construido, verificado, ejercitado 141
veces y usado por **cero** campañas— y el **motor developmental** `A1`–`A3b.1`,
construido después de que cambiara la pregunta y para servirla.

## Estado de los tests históricos

La suite completa, medida el 2026-09-21 en `1:13:26`:

```
2 failed · 1058 passed · 1 skipped
```

Ambos fallos en `tests/test_system_baseline_characterization.py`, y ninguno se
toca:

**`test_protected_source_and_historical_artifact_hashes_match_baseline`** →
`EXPECTED_HISTORICAL_DRIFT`. El manifiesto protegido se selló en `f105eb2`
(14-sep) y desde entonces **22 commits** tocaron el árbol protegido: 5 ficheros
nuevos y 9 con hash distinto, todos de commits del 17 y 18 de septiembre. El
gate golden está haciendo exactamente su trabajo.

**`test_d2_d3_d4_a0_a1_a4_match_checked_in_behavior`** →
`EXPECTED_HISTORICAL_DRIFT`, con **causa nombrada**: `44380b9` reclavó el sorteo
exógeno sobre linaje y generación, lo que cambia la corriente por construcción;
`43ee4e0` dejó que el gradiente sobreviva al paso de aprendizaje; `f72d225` metió
la frontera de congelado adaptativo en A4. El determinismo **sobrevive** —
`test_same_case_repeats_semantically_byte_for_byte` pasa—, así que no es
indeterminismo.

**El residuo honesto:** verifiqué que la causa existe, no que explique el diff
entero. Nadie ha comparado la fixtura línea a línea. Eso, y resellar el
manifiesto protegido, son adjudicación tuya: la pregunta no es de hashes sino de
si esos catorce cambios son deriva aceptada o regresión.

## Lo que no se hizo, y consta

No se reescribió ningún resultado. No se migró ninguna campaña a
`CapabilityPassport` v2 ni a esquemas nuevos. No se actualizó ningún golden. No
se cambió ningún hash. No se inventó provenance. No se ejecutó ninguna campaña.
Las semillas confirmatorias `130000011`–`130000026` siguen reservadas y **sin
ejecutar**.

# La identidad científica dejó de derivarse del registro

**2026-09-21** · medido sobre `.terrario/terrario.db` · veredicto y contrato.

---

## Veredicto

**Salida (b): la discontinuidad se declara y se le pone un guardián. La salida
(a) —congelar un códec por `schema_version`— no está disponible, y la razón
importa más que la decisión.**

No está disponible porque **`schema_version` no distingue las generaciones**.
Las 285 versiones de preregistro llevan la misma cadena
`terrario.lab.preregistration/v1`, y el contrato cambió al menos tres veces
por debajo de ella. Un códec por versión necesita una versión que se mueva; aquí
el único discriminante disponible es *el conjunto de claves que el payload trae*,
que no es una versión: es el payload. Y aunque se inventara el discriminante,
**(a) no alcanza a la segunda causa**, porque la entrada que derivó no está
guardada en ningún sitio (§2).

El alcance también es mayor que el enunciado: no son 285 registros de
preregistro, son **347 de 433 versiones almacenadas con códec**, y el
preregistro no es el único contrato enfermo.

---

## 1 · El alcance exacto

```
                              se re-deriva   no    bloqueados
  Preregistration  borrador         0        144        —
  Preregistration  bundle           0        141       141
  ExperimentDraft  borrador        85         62         —
  WorldDraft       borrador         1          0         —
                                 ────       ────
                                   86        347
```

`TrialMatrix` (146 versiones) queda fuera del perímetro por un hecho del árbol,
no por omisión: no tiene códec en
[codecs.py](terrario/lab/persistence/codecs.py), nunca se relee a objeto, y por
tanto no puede sufrir esta clase de deriva.

**Los 141 bloqueados son todos los que hay.** De 144 preregistros, 141 están en
`preregistration_locks` y **ninguno** de sus 141 manifiestos raíz se re-deriva
de su propio borrador. Los tres sin bloquear son
`PREREGISTRATION-CL7-20b807bf16cf7ff4`, `prereg-ux-walkthrough-01` y
`prereg-ux-walkthrough-02`, los tres en estado `DRAFT`.

### Claves que el códec materializa y el registro no tiene

```
  285 versiones   metrics[].instrument_ref            (no está guardada en NINGÚN registro)
  116 versiones   metrics[].specification_hash
  116 versiones   metrics[].calibration_report_id
  116 versiones   metrics[].calibration_report_hash
  116 versiones   metrics[].calibration_seed_set
  116 versiones   metrics[].confirmatory_seed_set
   60 versiones   hypothesis_mapping                  (ExperimentDraft)
    2 versiones   hypothesis_mapping.conditions[].agent_config
```

De los 144 borradores de preregistro, **86 pierden sólo `instrument_ref`** y
**58 pierden las seis**. Todas las divergencias son claves *añadidas*: ni un
solo valor almacenado discrepa del reconstruido. El contenido científico de los
registros está intacto; lo que se perdió es la **función de identidad**, no el
dato.

---

## 2 · Son dos causas, no una, y la segunda decide el veredicto

### Causa A · campos añadidos a un contrato

`MetricCommitment` ([domain.py:179](terrario/lab/preregistration/domain.py:179))
ganó seis campos con valor por defecto después de que esos registros se
escribieran. El códec los materializa al releer, `plain()` los emite, y el
payload canónico cambia.

Alcanza al borrador (`scientific_payload()`) y al bundle (el componente
`metrics_and_endpoints` es `plain(draft.metrics)`).

### Causa B · el manifiesto raíz no se deriva sólo del registro

El décimo componente del bundle, `validation_policy`, **no sale del borrador**:
sale de `policy_snapshot()`
([commitments.py:69](terrario/lab/preregistration/commitments.py:69)), que lee
el conjunto de reglas del código vivo.

Y ese conjunto se movió sin que su versión se moviera. Los 141 sellados llevan
**tres conjuntos de reglas distintos bajo la misma cadena
`preregistration-policy-1.0`**:

```
   58 bundles   sin PR-CL7-001 ni PR-INSTRUMENT-001
   83 bundles   sin PR-INSTRUMENT-001
  hoy           las dos
```

Los 141 bundles fallan por **las dos causas a la vez** —`metrics_and_endpoints`
*y* `validation_policy`—, así que reparar la causa A no devolvería ni uno solo
de ellos.

**Esto es lo que descarta la salida (a).** Un códec congelado reconstruye lo que
está guardado. `validation_policy` no está guardado en el registro: es una
entrada externa que el sellado consulta al correr. No hay códec que pueda
reconstruir lo que nunca se escribió.

---

## 3 · Por qué tampoco sirve podar los ausente-equivalentes

El patrón correcto —el que se aplicó al añadir `gates`: quitar la clave del
payload científico cuando vale `None`, de modo que un borrador sin ella hashee
como antes de que existiera— es correcto **hacia adelante** y equivocado **hacia
atrás**, y se puede medir:

```
  si scientific_payload() podara None y {} dentro de metrics[]
     59 borradores volverían a re-derivarse   (no tenían la clave)
     85 borradores dejarían de re-derivarse   (la tienen, guardada con null)
    141 bundles seguirían rotos               (causa B, intacta)
```

De los 169 registros de métrica que sí guardan las cinco claves, **168 las
guardan con `null` o `{}` y exactamente uno con valores reales**: el borrador
CL-7, que es además uno de los tres sin bloquear. Podar movería la rotura de
sitio en vez de quitarla, y lo haría **redefiniendo la función que produjo los
hashes almacenados**. Eso es reescribir la provenance aunque no se toque un solo
byte del disco.

La diferencia con `gates` es exacta y vale la pena dejarla escrita: `gates` es
un campo que **ningún registro guarda todavía**, así que podarlo cuando vale
`None` no puede contradecir nada ya escrito. `specification_hash` lo guardan 169
registros. La poda es segura el día que se añade el campo, y deja de serlo en
cuanto un registro lo escribe.

---

## 4 · El daño concreto: la enmienda hereda lo que el protocolo nunca comprometió

`service.verify()` no lo detecta, y no por descuido: compara
`content_hash(root_manifest ALMACENADO)` contra el `scientific_hash`
**almacenado** ([service.py:188](terrario/lab/preregistration/service.py:188)),
y `CommitmentBuilder.verify` compara los blobs del CAS contra los hashes del
índice ([commitments.py:106](terrario/lab/preregistration/commitments.py:106)).
Ambas comparaciones son almacenado-contra-almacenado y ambas son correctas: la
integridad de lo guardado es perfecta. Lo que ninguna comprueba es que lo
guardado pueda **volver a producirse**.

El camino donde eso deja de ser teórico es la enmienda:

```python
# service.py:340 — add_postlock_record; exige que el padre esté BLOQUEADO (service.py:313)
source = plain(self._draft_from_record(parent))   # ← materializa los seis campos
source.update(delta)
child = preregistration_draft_from_payload(source)
```

El hijo de una enmienda nace con seis campos que el protocolo bloqueado nunca
comprometió, y el `AmendmentRecord` que documenta el cambio **no los menciona**:
el `delta` sólo lleva lo que pidió quien enmendó. El registro de gobernanza del
cambio es incompleto por construcción, y los 141 bloqueados están en ese camino.

El caso más cercano es CL-7: es el único registro con calibración real, está sin
bloquear, y `derive()` sobre él escribiría hoy un hijo con `instrument_ref: null`
sin que nada lo declare.

---

## 5 · Qué se hizo

**No se tocó ningún hash almacenado, ningún registro histórico y ningún módulo
de producción.** La discontinuidad se declara; no se repara.

### El acta · `tests/fixtures/reconstruccion_ledger.json`

Las 347 versiones que no se re-derivan, una fila cada una, con su hash
almacenado, su hash recomputado hoy, su forma de divergencia y si está
bloqueada. Más la **superficie de contratos**: los 30 contratos que participan
en una identidad científica almacenada, con su conjunto exacto de campos, y el
hash de todo ello.

No es una lista de excepciones perdonadas. Es el estado congelado contra el que
se compara, y por eso sigue teniendo dientes.

### El guardián · `scripts/reconstruccion_check.py` y `tests/test_reconstruccion_contrato.py`

Dos mitades, porque una sola no cubre dónde ocurre el fallo:

| mitad | necesita datos | salta cuando |
|---|---|---|
| superficie de contratos clavada | no | se añade un campo a cualquiera de los 30 contratos |
| conjunto de reglas clavado a su versión | no | se añade una regla sin mover `POLICY_VERSION` (causa B) |
| un preregistro escrito hoy se re-deriva | no (raíz temporal) | la ruta de sellado deja de reproducirse |
| cada registro almacenado coincide con el acta | sí | la historia se mueve |

La mitad sin datos es la importante: **los árboles de trabajo no llevan
`.terrario/`**, y es en ellos donde se escriben los contratos. Un guardián que
sólo vive donde está la base de datos habría estado dormido exactamente el día
en que se añadió `instrument_ref`. La superficie clavada salta ese día, con el
mensaje que dice qué hacer: podar como `gates` si el campo es
ausente-equivalente, o re-declarar la discontinuidad y explicarla aquí.

### Los mutantes

Un criterio que sólo pasa tampoco es un criterio. Los siete modos de rotura
están probados uno a uno contra su mutante, y el caso sin mutar es verde:

```
  registro nuevo que no se re-deriva    → DIVERGENCIA_NO_DECLARADA
  hash almacenado reescrito             → HISTORIA_REESCRITA
  contrato cambiado tras la declaración → RECONSTRUCCION_MOVIDA
  forma de divergencia distinta         → FORMA_DE_DIVERGENCIA_CAMBIADA
  registro del acta desaparecido        → REGISTRO_AUSENTE
  el acta declara algo ya sano          → ACTA_OBSOLETA
  fila borrada del acta a mano          → DIVERGENCIA_NO_DECLARADA
```

Comprobado además con un mutante real sobre el árbol: añadir un campo a
`MetricCommitment` mueve la superficie de contratos y levanta
`RECONSTRUCCION_MOVIDA` en las 285 filas de preregistro del acta. Revertirlo
devuelve el verde.

---

## 6 · Lo que deliberadamente no se hizo

**`service.verify()` sigue sin re-derivar.** Añadirle la reconstrucción pondría
los 141 preregistros bloqueados en `INVALID`, y sería engañoso: su integridad
almacenada es correcta y la API de gobernanza no es el sitio donde se descubre
que un contrato creció. La detección vive en el guardián, que es donde el
cambio se hace.

**`POLICY_VERSION` no se movió.** Moverlo cambiaría el hash de
`policy_snapshot()` y con él el de todo bundle futuro; es una decisión sobre la
identidad de los sellados, no sobre este defecto. Lo que se añadió es el clavo
que impide que el conjunto vuelva a cambiar en silencio.

**No se migró ni se reescribió nada.** La provenance histórica se conserva tal y
como ocurrió, que era la condición.

---

## 7 · Cómo se corre

```
python scripts/reconstruccion_check.py --root <ruta>/.terrario
python scripts/reconstruccion_check.py --root <ruta>/.terrario --detalle
TERRARIO_DATA_ROOT=<ruta>/.terrario pytest tests/test_reconstruccion_contrato.py
```

En un árbol sin raíz de datos las tres mitades sin base de datos corren igual y
la cuarta se salta diciendo qué ejecutar.

`--write` re-declara el acta con lo que se mide hoy. **No es «arreglar».** Se
corre cuando la diferencia se ha entendido y se quiere dejar declarada, y este
informe dice por qué. Regenerarlo para poner el gate en verde es exactamente el
fallo que existe para impedir.

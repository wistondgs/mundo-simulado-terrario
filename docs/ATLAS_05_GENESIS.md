# Atlas 05 · Genesis · `lab/genesis/`

**2026-09-21** · genesis-v2 `602516d` · depositado en
`RNE_v16-genesis-v2/docs/CARTOGRAFIA_GENESIS_01.md` **§VII**, que es donde su
gate puede vigilarlo · 10 citas verificadas.

**Reasignación de alcance.** Las seis secciones que ya existían mapean
`runtime/` —el organismo y su andamiaje, material del Atlas 06— y **no
mencionan `lab/genesis/` ni una vez**: cero ficheros vigilados de 19 861
líneas. Este volumen cubre ese hueco.

---

## 1 · Qué entra · el espacio de capacidades es aritmética univariada

Una capacidad **no es una entrada en un registro mutable: es un artefacto de
programa inmutable**, con identidad estructural de AST y sin una línea de Python
embebida ni ejecutada.

```
DSL      X · CONST · ADD · SUB · MUL_CONST · ABS · SQUARE      7 operadores
         una sola variable entera · evaluación total y acotada
tareas   affine-0/1 · abs_affine-0/1 · quadratic_simple-0/1    6 confirmatorias
```

El propio módulo lo declara antes que nadie pueda malinterpretarlo: «**no es
evidencia sobre búsqueda ilimitada o abierta**». Hay que decirlo primero, porque
«Genesis adquiere capacidades» significa exactamente esto.

## 2 · Qué transforma · las reglas tienen nombre y versión

```
DATASET_SPLITS              TRAIN · AUDIT · HIDDEN · TRANSFER
CANDIDATE_RANKING_RULE      training_error_then_mdl_then_canonical_program_hash-v1
PROMOTION_RULE              train_exact_audit_once_exact_no_leakage-v1
HUMAN_INTERVENTION_POLICY   no_interactive_corrective_selection-v1
```

Los cuatro invariantes son constantes declaradas, no conducta enterrada en una
función. La síntesis es enumerativa determinista **y sólo sobre TRAIN**.

Y algo que casi nadie escribe: el identificador de la semántica de búsqueda v1,
`FIRST_SEEN_BEHAVIOR_REPRESENTATIVE-v1`, existe «para documentar la semántica
histórica **en vez de afirmar que la regla del primer representante fuera
correcta para ordenar**». Se congeló una regla que se sabe imperfecta para poder
replicar la evidencia que produjo, y se escribió la ordenada al lado.

El ledger de evidencia es una cadena de hashes con `verify` sobre la cadena
entera.

## 3 · Qué produce · la cadena corrió entera una vez, y promovió

Cuatro campañas en `rnfe_artifacts/`. Tres son un `LAUNCH` y nada más. La cuarta
corrió de verdad — 5 560 ficheros, 24 MB —:

```
tareas completadas   1 de 6      abs_affine-0
evaluación           AUDIT · 5/5 · exact_pass: true
promoción            genesis-m7-v2-promotion-receipt-h2b1 · status: PROMOTED
sin empezar          5
```

Frontera auditada → campaña sellada → síntesis → compromiso de candidato →
ranura de auditoría de un solo uso → evaluación exacta → **promoción**.

Después el lanzador desapareció, y el registro de la interrupción es lo más
honesto del subsistema:

```
recovery_action  NONE
reason           el escritor de journals es create-only y el runner rechaza un
                 journal existente en vez de reconstruir una clausura en
                 memoria. Cambiarlo tras consumir una campaña canónica violaría
                 el congelado de H2B1.
```

**Un corte de proceso gastó una ranura canónica y las reglas prohibieron
rescatarla.** Nadie reparó el registro para salvar la corrida. Eso es
disciplina — y es el precio exacto de no poder reanudar.

## 4 · Quién lo consume · nadie

| Pregunta | Respuesta |
|---|---|
| ¿Importa `lab/genesis` algo fuera de `lab/` y `tests/`? | **0 ficheros** |
| ¿Menciona el runtime `ProgramSkillArtifact` o `PromotionReceipt`? | **0 ficheros** |
| ¿Lee alguien las campañas de `rnfe_artifacts/`? | nadie las lee |
| ¿Cuántos tests lo ejercitan? | **70** |

La frase «un G1 promovido es exactamente G0 más esa habilidad concreta» está en
el docstring de los contratos y **no existe como código**: no hay función que
componga un organismo con la habilidad promovida. El artefacto se promueve; no
se entrega a nadie.

> **El hecho arquitectónico:** Genesis adquiere, audita y promueve con una
> disciplina de evidencia mejor que casi todo lo demás del proyecto, y lo
> promovido **no llega al organismo**. La receta `PROMOTED` es el último eslabón
> que existe.

No invalida Genesis: lo sitúa. Hoy es un **laboratorio de adquisición cerrado
sobre sí mismo**, con su ledger, su congelado y sus ranuras de un solo uso. Lo
que falta no es rigor — es la arista de la receta de promoción a `runtime/`.

## 5 · Lo que no se sabe

1. **K2** · Si el aislamiento es deliberado. No hay ADR en `canon/normative` que
   diga «Genesis no se integra todavía», ni uno que prometa la arista. Sin eso,
   «aislamiento deliberado» e «integración incompleta» son indistinguibles desde
   el código.
2. **K2** · Qué haría falta para que una habilidad promovida entrase en el
   organismo. El DSL produce funciones `int → int`; ningún punto del runtime
   consume una función así.
3. **K2** · Por qué las tres campañas v3 se detuvieron en `LAUNCH`.
4. **K1** · Si alguna campaña corrió bajo la regla de ordenación corregida. No
   consta en `rnfe_artifacts/`.

---

**De paso:** el gate de Genesis no tenía el comprobador de citas `fichero:línea`
que el de Terrario ganó ayer. Portado — los dos árboles vigilan ahora las dos
cosas, el fichero y la cita.

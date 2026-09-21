# Fase A · ¿existe ya el contrato de construcción de capacidad?

**2026-09-21** · `662038c` · sin modificar código.

---

## Respuesta

**Sí, en un ~70 %, repartido en cuatro módulos — y le falta exactamente el
invariante que el encargo llama el más importante.**

No hay que crear un tipo nuevo. Hay que **extender `CapabilityPassport`**, que
ya es «la unidad de la campaña: ningún algoritmo entra sin uno».

---

## Lo que ya existe · cuatro piezas, no una

| módulo | líneas | qué es |
|---|---|---|
| [capability_passport.py](terrario/lab/capability_passport.py) | 561 | **el contrato** · 22 campos y un estado **derivado**, no declarado |
| [capability_operationalization.py](terrario/lab/capability_operationalization.py) | 478 | los puentes aprobados por un humano de capacidad → claim del corpus |
| [capability_intervention.py](terrario/lab/capability_intervention.py) | 103 | contratos de intervención del plano de ejecución |
| [capability_exam.py](terrario/lab/capability_exam.py) | 320 | el examen reservado de una capacidad **adquirida** |

Lo que hace fuerte al pasaporte no es la lista de campos: es que `status_of`
([:113](terrario/lab/capability_passport.py:113)) **calcula** el estado en orden
de precondición —contrato completo → procedencia → pureza → mundo que la exige →
endpoint calibrado— y devuelve un `PassportState`
([:42](terrario/lab/capability_passport.py:42)) que dice **por qué** todavía no
se certifica. Su propia cabecera lo formula mejor que yo: «un estado que se
escribe a mano es una opinión; uno que se calcula es un gate».

Y ya se defiende de la deriva: `__post_init__` rechaza un `composition_flag` que
no esté en `agent_composition.CONCEPTS`, «porque el pasaporte y el catálogo
derivaron».

---

## El schema pedido, contra lo que hay

| pedido | dónde vive hoy | veredicto |
|---|---|---|
| `identity` · capability_id, revision | `capability_id`, `algorithm_id`, `algorithm_version` | **existe** |
| `target` · qué capacidad | `concept_id`, `operational_definition` | **existe** |
| `target` · claim/nodo teórico | `corpus_provenance`, y `CorpusClaimReference` ([:40](terrario/lab/capability_operationalization.py:40)) | **existe**, sin unir |
| `formalization` · definición operacional | `operational_definition` | **existe** |
| `formalization` · formulación matemática | — | **falta** |
| `prerequisites` | `known_dependencies` | **existe** |
| **`supplied`** | — | **FALTA** |
| **`acquisition_target`** | — | **FALTA** |
| `forbidden_shortcuts` | `forbidden_information` | **parcial** · vigila información, no mecanismo |
| `implementation_contract` | `inputs`, `outputs`, `internal_state`, `allowed_information`, `forbidden_information` | **existe** |
| `experimental_contract` | `required_world_property`, `demanding_world`, `falsification_controls`, `intervention_purity` | **existe** |
| `falsifiers` | `negative_prediction`, `falsification_controls` | **existe** |
| `evidence_requirements` | `primary_endpoint`, `secondary_endpoints` | **existe** |
| **`non_claims`** | — | **FALTA** |
| `provenance` | `corpus_provenance`, `operationalization_id` | **existe** |

**Cuatro huecos, y tres de ellos son el mismo hueco.**

---

## El invariante que falta es justo el que importa

El encargo dice que la estructura debe impedir que `SUPPLIED` colapse con
`ACQUIRED`. **Hoy el pasaporte no puede ni nombrarlos.** Barrido sobre los
cuatro módulos: ni `supplied`, ni `acquired`, ni `acquisition` aparecen.

Lo notable es que la distinción **sí existe en el proyecto**, fuera del tipo:

* `capability_exam.py` se titula «examen reservado de una capacidad
  **adquirida**»;
* la fusión distingue en su informe `B·Q·H` aprendidos de `M` suministrado y de
  la composición suministrada «que sostiene todos los resultados»;
* 1.7 declara `hereda el MECANISMO … no una tabla forastera`.

Es decir: el proyecto **piensa** en suministrado-vs-adquirido en cada campaña y
lo escribe en prosa distinta cada vez. Eso es exactamente lo que el encargo
quiere volver objeto.

Y hay deuda ya declarada que apunta al mismo sitio, en el propio campo
`composition_flag`:

> «una capacidad no debería ser sinónimo de una bandera interna de un espécimen»

Colapsar la capacidad en su bandera **es** el colapso supplied/acquired, escrito
por adelantado por quien lo construyó.

---

## Resto del mapeo obligatorio

```
conceptos                 agent_composition.py:74     CONCEPTS
catálogo concepto↔agente  agent_composition.py:40     AGENT_CONFIGS
                          agent_composition.py:163    concepts_for
capability passports      capability_passport.py:60
hipergrafo teórico        hypergraph/theory_operational.py:185   validate_bindings
hipergrafo operacional    hypergraph/operational.py             sin consumidor de producción
claims / revisiones       capability_operationalization.py:40   CorpusClaimReference
preregistration/domain    preregistration/domain.py:430         PreregistrationDraft
GateCommitment            preregistration/gate_manifest.py      SealedGate · desde 712a2f7
GateResult                preregistration/gate_manifest.py      GateOutcome
instrumentos/endpoints    instrument_registry.py                InstrumentRef · 3 códigos
config de agente          agent/agents/__init__.py:48           create_agent
ejecución experimental    execution/runtime.py:28               ScientificTrialIdentity
evidence admission        evidence_admission.py                 admit_evidence
canonicalización/hash     persistence/canonical.py              plain · canonical_json · content_hash
```

---

## Extensión mínima que propongo

Tres campos en `CapabilityPassport`, más una regla que los cruza:

```
supplied              tuple[str, ...]   mecanismo/estructura que damos
acquisition_target    tuple[str, ...]   contenido u organización que debe surgir
non_claims            tuple[str, ...]   lo que no se podrá afirmar aunque salga positivo
```

Y en `__post_init__`, la negativa que el encargo pide: **`supplied` y
`acquisition_target` no pueden intersecarse**, y ningún elemento de
`forbidden_information` puede aparecer en `supplied`.

`PassportState` gana un estado previo a `NO_CORPUS_PROVENANCE`:

```
SUPPLIED_AND_ACQUIRED_NOT_SEPARATED
```

de modo que **el colapso no sea un error de validación sino un estado del
pasaporte** —igual que los otros cinco: calculado, no declarado—.

Eso reutiliza `status_of`, el hash canónico existente y los 22 campos, y no crea
ningún registro paralelo.

---

## La bifurcación que decide el encargo

Tu última línea dice: si ya existe el equivalente, no lo hacemos de nuevo y la
siguiente tarea es conectarlo con la ejecución.

El resultado no es ninguno de los dos extremos:

* **no** hay que construir un `CapabilityPackage` nuevo;
* **sí** falta el invariante central, y sin él el contrato no responde a «¿qué
  debe aprender el organismo?» ni a «¿qué no se le permite recibir ya resuelto?»
  —dos de tus nueve criterios de aceptación—.

Así que la recomendación es **extender, no crear ni saltar**: tres campos, una
regla y un estado. Después, conectar.

---

## Limitación de este mapeo

**`NO VERIFICADO`** · No he comprobado si los 10 pasaportes registrados pueden
rellenar `supplied` y `acquisition_target` sin falsear su historia. Con `1.6` y
`1.7` —los que el encargo prefiere para la Fase E— la distinción está escrita en
sus informes, pero **esos árboles no registran pasaportes**: los diez que existen
son de los módulos A4/A5, no del linaje 1.x. Eso hay que resolverlo antes de la
Fase E, y es una contradicción entre el encargo y el árbol que dejo señalada en
vez de forzar.

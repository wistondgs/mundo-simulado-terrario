# Qué se congela, cuándo y con qué identidad

**2026-09-21** · item 1 del backlog · medido antes de proponer nada.

---

## El hallazgo que cambia la forma del problema

**El contrato de archivo ya existe, está direccionado por contenido, se
verifica, y se ha ejercitado 141 veces.** No hay que construirlo.

Y sin embargo la condición `A` bloquea a las diez campañas, por una razón
distinta de la que suponíamos:

```
el carril científico     141 preregistros · 141 ejecuciones · 476 artefactos sellados
                         1.480 manifiestos de blob · 1.664 eventos de ejecución
                         scientific_results ......... 0
                         empirical_evidence ......... 0

las campañas reales      10 oráculos sellados · la única ciencia del proyecto
                         0 módulos tocan el repositorio de artefactos
                         0 blobs · 0 CAS · informes en markdown
```

**La ciencia está en el mundo sin archivo; el archivo está en el mundo sin
ciencia.** Son dos disciplinas de sellado reales, ninguna defectuosa, sin puente
entre ellas.

Verificado: de las siete campañas —1.2, 1.3, 1.4, fusión, 1.6, 1.7, 1.8—
**ninguna** importa `ArtifactRepository`, `register_blob`, `seal_metric_result`,
`admit_evidence` ni `content_hash`.

---

## 1 · Lo que ya está construido, exactamente

### Lado del protocolo · diez roles, congelados al sellar

[commitments.py](terrario/lab/preregistration/commitments.py) construye un
manifiesto determinista con **diez componentes**, cada uno escrito al CAS y
descrito por dos hashes —`cas_sha256` del blob y `content_sha256` del payload
canónico—:

```
scientific_question · causal_design · protocol · metrics_and_endpoints
observer · seeds_partitions_randomization_replication · analysis
policies · environment_and_software · validation_policy
```

`verify` ([:106](terrario/lab/preregistration/commitments.py:106)) recorre los
descriptores y falla con código por rol: `CAS_OBJECT_MISSING:<rol>`,
`COMPONENT_HASH_MISMATCH:<rol>`, `ROOT_CAS_OBJECT_MISSING`. Y la construcción
misma se autocomprueba: si el canónico y el digest del CAS divergen, levanta
`"canonical root and CAS digest diverged"`.

Contra las siete condiciones, ese manifiesto ya cubre la mayor parte de `Ω` y de
`I_M`.

### Lado del resultado · el sello existe y lleva la revisión del claim

`seal_metric_result` ([metric_result_sealing.py:58](terrario/lab/metric_result_sealing.py:58))
emite un descriptor con:

```
execution_plan_hash          preregistration_root_hash
hypothesis_revision          ← el claim CON revisión
trace_blob_hash              ← el dato crudo, en CAS
analysis_rule · scope        descriptor_hash
```

Y `evidence_publication` verifica al leer: `content_hash(envelope)` contra el
`result_hash` guardado **y** los dos blobs contra el CAS.

### La puerta · ya existe, y es la correcta

`admit_evidence` ([evidence_admission.py](terrario/lab/evidence_admission.py))
resuelve el instrumento, exige que sea reportable, y lo **compara contra el
preregistrado** con tres códigos distintos —`INSTRUMENT_MISMATCH`,
`INSTRUMENT_VERSION_DRIFT`, `INSTRUMENT_SPEC_DRIFT`—. Se niega a recomputar la
métrica, a modificar una lectura, a imputar ausencia y a reinterpretar
`INVALID`. Su propio encabezado dice por qué pregunta de nuevo lo que ya
preguntaron el preregistro y el runtime: *«a gate that trusts its callers is
documentation, not a gate»*.

**Tu condición `I_M` está implementada.** Y `numeric_claim` ya separa «admisible»
de «afirma una cantidad», que es la mitad de `R`.

---

## 2 · La obligación de congelado, dicha sobre lo que existe

No hace falta vocabulario nuevo salvo en un punto. La tabla es lo que una
ligadura `(E, C, rev_C, G, I, Ω, P, R)` necesita, mapeado a dónde vive hoy.

| qué se congela | cuándo | identidad | existe hoy |
|---|---|---|---|
| **el oráculo entero** · pregunta, diseño causal, protocolo, taxonomía de resultado, condiciones de parada | al sellar, **antes de que exista código** | `content_sha256` del payload canónico + blob CAS | **sí**, como 4 de los 10 roles |
| **métricas y endpoints**, con `instrument_ref` | al sellar | ya lleva `specification_hash`, `implementation_identity`, `calibration_report_hash` | **sí** |
| **semillas, particiones, aleatorización, réplica** | al sellar | rol propio del manifiesto | **sí** |
| **entorno y software** | al sellar | rol propio | **sí** |
| **manifiesto de gates** · por gate: id, **qué propiedad certifica**, criterio, fixtura negativa | al sellar, y **re-verificado al ejecutar** | ninguna | **NO EXISTE** |
| **traza cruda por vida/semilla** | al ejecutar | `trace_blob_hash` en CAS | **sí** en el carril · **no** en las campañas |
| **lectura por endpoint**, con estado | al ejecutar | `Reading` con sus cuatro estados | **sí** |
| **resultado sellado** | al cerrar | `result_hash` + `descriptor_hash`, atado a `hypothesis_revision` | **sí** |
| **veredicto de admisión**, con sus bloqueadores | al admitir | `AdmissionVerdict.as_record()` | **sí** |

### La única pieza que no existe en ninguna parte

**El manifiesto de gates.** Ni el carril ni las campañas lo tienen. El carril
sella métricas y endpoints; las campañas evalúan gates. Son cosas distintas: un
endpoint es *qué se mide*, un gate es *qué queda certificado si el número cae
del lado bueno*.

Es exactamente la condición `I_G`, y es la que habría hecho falsable `F-9`. Su
forma mínima ya está escrita en el linaje B —`GateResult(name, certifies,
passed, evidence)`—; lo que falta es que `certifies` se congele **con el
oráculo** y se vuelva a comprobar **al ejecutar**, en vez de escribirse en el
mismo sitio y momento que el resultado.

Porque ése es el punto: hoy el nombre del gate y lo que certifica se escriben
**juntos, al correr**. Aunque el linaje B los escriba los dos, nada compara esa
pareja contra el sello. Congelarla aparte es lo que convierte una etiqueta en
una afirmación falsable.

---

## 3 · Por qué las campañas no usan el carril, y qué decidir

No es descuido. Son dos disciplinas de sellado con **momentos y autoridades
distintas**:

| | el carril | las campañas |
|---|---|---|
| sella | un manifiesto de 10 roles al CAS | un documento markdown, con `git commit` |
| autoriza | `create → submit → review → decide → lock`, con **decisión humana** | el commit del oráculo, antes de existir el código |
| verifica el sello | `verify()` contra CAS | nada: los valores sellados se **transcriben** a constantes |
| produce | 476 artefactos y **0 resultados** | 10 resultados y **0 artefactos** |

Y la transcripción es literal: la fusión compara contra `SEALED = {("ON","ON"):
float(F(1,55)), …}` —fracciones exactas, buena práctica— pero **nada comprueba
que esas fracciones sean las que dice el documento sellado**. Editar el markdown
no rompe nada; editar la constante tampoco.

Ahí hay una decisión que no me corresponde tomar:

> **¿Cuál es el sello autoritativo de una campaña — el commit del oráculo, o un
> manifiesto en el carril? ¿Y debe una campaña entrar al carril antes de
> correr?**

El carril exige revisión humana para cerrar `lock`. Las campañas preregistran
escribiendo el oráculo y commiteándolo, que es una disciplina distinta y no
peor. Forzar el carril tal cual añadiría una puerta humana donde hoy hay una
convención que ha funcionado diez veces.

---

## 4 · 1.6 confirma tu distinción, y no se puede reparar hacia atrás

Las 16 huellas de trayectoria de 1.6 no existen y no van a existir. Volver a
correr la campaña produce **evidencia nueva**, no las reconstruye.

Así que 1.6 sólo puede entrar como lo que dijiste:

```
SCIENTIFICALLY_SUPPORTED  ∧  HISTORICAL_ARTIFACTS_UNAVAILABLE
```

Y hay un matiz que lo hace menos malo de lo que parece: su reconciliación
**replicó por determinismo contra la tabla committeada, celda por celda,
tolerancia 5e-5, cero diferencias**. Eso no es el artefacto original, pero
tampoco es nada: es una afirmación verificable de que la re-ejecución reproduce
lo publicado. Merece su propio valor, distinto de «artefacto congelado» y de
«no verificable».

Lo mismo vale, con menos fuerza, para las campañas cuyos valores sellados son
**cerrados** —1.2 con `8/55`, la fusión con `F(1,55)`—: un número derivable no
necesita archivo para verificarse, necesita que la derivación esté sellada. Las
diez campañas no están en la misma situación y el grafo no debería tratarlas
igual.

---

## 5 · Lo que sale de aquí, por coste

1. **Nada que construir para `P` y para la mitad de `Ω`.** El manifiesto de diez
   roles, el CAS, el perfil de canonicalización y `verify()` funcionan y llevan
   141 usos. La obligación es **usarlos desde una campaña**, que hoy es
   invocable desde Python —`PreregistrationService`, y un guion ya lo hace—.
2. **Una pieza nueva y pequeña: el manifiesto de gates.** Es la única condición
   sin ningún soporte, y es la que decide `F-9`.
3. **Una decisión tuya antes de tocar nada**: cuál de los dos sellos manda, y si
   una campaña entra al carril antes de correr.
4. **Tres estados distintos de archivo**, porque las diez campañas no están en el
   mismo sitio: artefacto congelado · derivación cerrada verificable · réplica
   determinista contra tabla publicada. Tratarlos como uno solo falsearía en las
   dos direcciones.

---

## 6 · Lo que no se sabe

1. **K2** · Por qué el carril se detuvo en `scientific_results = 0` tras 141
   ejecuciones. Hay 476 artefactos sellados esperando un paso que nadie dio; no
   está escrito si fue decisión o abandono.
2. **K2** · Si los 476 artefactos del carril corresponden a algo que valga la
   pena admitir, o son las mismas corridas de humo con `seed-42` que pueblan el
   grafo de evidencia.
3. **K1** · Qué exige Genesis que Terrario no: su campaña canónica sí produjo
   5.560 ficheros con CAS y journals. Si su contrato de congelado ya es
   suficiente, la obligación debería escribirse una vez para los dos árboles.

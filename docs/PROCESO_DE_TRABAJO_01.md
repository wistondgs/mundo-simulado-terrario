# PROCESO-DE-TRABAJO-01

**Estatus:** normativo para el trabajo conjunto a partir del 2026-09-16.
**Autoría:** las decisiones D1–D3, el backlog P0–P5 y el orden de diez pasos son del
investigador. Las notas marcadas **[instrumento]** son aportes verificados en código durante la
sesión y no modifican ninguna decisión.
**Motivo:** hasta ahora se trabajó por impulsos — encontrar algo, arreglarlo, encontrar otra
cosa. Eso sirvió para limpiar y no cierra nada. El diagnóstico de la revisión nocturna, «la
pieza está y el cable no», tiene causa de proceso: **se añadieron mecanismos más rápido de lo
que se cerraron ciclos.**

---

## 0. Los tres objetos, que no son el mismo

```
RNFE runtime   = el organismo
Genesis v2     = laboratorio de evidencia, adquisición y promoción
Terrario       = instrumento experimental causal
```

No existe todavía el ciclo cerrado entre los tres. **La prioridad inmediata no es construir el
puente: es demostrar que Terrario puede medir una modificación causal de principio a fin.**

---

## 1. Invariante central — D1 · medición antes de materialización

> Ninguna capacidad producida por Genesis se materializa en RNFE antes de existir un **contrato
> experimental preregistrado** que declare qué cambio constituirá ganancia, ausencia de efecto,
> regresión y resultado indeterminado.

Protege contra selección retrospectiva de métricas, reinterpretación del objetivo tras ver el
resultado, promoción de capacidades que solo *parecen* útiles, contaminación de la línea base, y
construir un puente que no sabemos evaluar.

La arquitectura objetivo **no** es `Genesis → candidato → promoción → RNFE' → medir`, sino:

```
RNFE_t → límite observable → contrato de medición preregistrado
       → Genesis(C) → Terrario(C, ¬C) → evidencia → promoción
       → RNFE_t+1 → retest con el MISMO contrato
```

**[instrumento]** La parte del retest ya tiene maquinaria: `evidence_publication.py` comprueba
`measured["analysis_rule"] != endpoint["decision_rule"]` antes de publicar, así que la regla de
análisis congelada se verifica sola.

## 2. D2 · `validated` precede a `promoted`

```
Candidate → OperationalDefinition → Intervention → Measurement
          → Evidence → Promotion → Materialization
```

Nunca `Candidate → Materialization → buscar después cómo evaluarlo`.

## 3. D3 · no llamar todavía «historia causal» a RNFE nominal

La hipótesis, no el teorema:

```
H0_nominal :  P(A_t | O_t, H_t) = P(A_t | O_t)
```

Antes de afirmarla hay que excluir formalmente autoevolución, estado del organismo,
certificación/promoción, historia de recompensa y cualquier mutación persistente consumida
aguas abajo.

**[instrumento] Una ruta secundaria ya está trazada, y cambia el sentido de N1.**
`RNFE_AUTOEVOLUTION` **viene encendido por defecto** (`os.environ.get("RNFE_AUTOEVOLUTION","1")`)
y muta `memory_retrieval_limit` y `memory_filter_mode`, que son precisamente los parámetros con
que `scenario_runner` llama a `MemoryRetrieval.retrieve()`. La cadena nominal existe entera:

```
degradación sostenida → autoevolución → knobs → retrieve() → memory_hits → [N1] → ✗
```

y **se corta en el último eslabón**, `scenario_runner.py:806`. Por tanto N1 no es código muerto:
es el único eslabón roto de la única ruta historia→acción activa por defecto. Repararlo no añade
un mecanismo; enciende un bucle ya cableado salvo una línea. `H0_nominal` se sostendría hoy **no
por ausencia de ruta sino por severación**, y eso es una afirmación más fuerte y más comprobable.

---

## 4. La vuelta — unidad de trabajo

```
1  LÍMITE        agente   UNA cosa concreta que el organismo no puede hacer, con evidencia
                          de código. No un deseo: un fallo medido.
2  INSTRUMENTO   agente   ¿existe métrica validada? Si no, primero el detector. INNEGOCIABLE.
3  DISEÑO        agente   el diseño pareado más pequeño que PUEDA fracasar, con las hipótesis
                          rivales nombradas desde el corpus.
4  FIRMAS        humano   las cuatro compuertas en UNA sesión, con la tarjeta mostrando el
                          diseño. En bloque, no a goteo.
5  EJECUCIÓN     máquina  correr y verificar.
6  INGESTA       máquina  contador +1.
7  LECTURA       ambos    qué autoriza a afirmar y qué no.
```

### Tres reglas que la hacen sostenible

1. **Una vuelta a la vez.** Nada nuevo se construye hasta que la actual cierre.
2. **Moratoria de mecanismos hasta que `scientific_results > 0`.** Hay 106 banderas y el
   organismo por defecto está apagado; el problema no es que falten mecanismos.
3. **El paso 2 es innegociable.** Si no hay forma de medir el fracaso, no hay vuelta.

### Reparto

| | |
|---|---|
| Terrario | donde se cierran las vueltas |
| RNFE | donde viven las capacidades |
| Genesis | de donde salen los candidatos |
| agente | instrumento, medición, refutación — **no firma compuertas** |
| humano | los límites, las firmas, el canon |

---

## 5. Principio de compatibilidad — P1

> **«Aditivo» es una afirmación experimental sobre compatibilidad, no una propiedad que el
> programador pueda asumir.**

Para cualquier cambio de superficie contractual: (1) suite dirigida, (2) guards de forma e
identidad, (3) suite completa, (4) **solo entonces** puede declararse «sin regresiones».

Y los guards deben fijar **identidad, no cardinalidad**:

```
len(registry) == 6                                   insuficiente
IDs(registry) == {D0,D1,D2,D3,D4,D4S}                correcto
```

**[instrumento]** Esta regla nació de un error del agente: se declaró que registrar `D4S` era
aditivo sin correr la suite completa, y rompió dos guards. Los guards funcionaron.

---

## 6. Antes de reparar un no-op, caracterizarlo — P3

Una suite de **1.879 tests en verde** convivió con N1 muerto. Eso no es un hallazgo sobre N1:
es un hallazgo sobre la estrategia de pruebas — **verifican ejecución, no semántica.**

Por tanto, antes de cualquier arreglo hace falta un reproductor causal que demuestre

```
MemoryHit → DecisionDifference
```

cuando el contenido recuperado es causalmente relevante. Hoy:

```
A_memory == A_control
```

Primero el reproductor. Después el arreglo. **No al revés.**

Los siete no-ops de la auditoría **no se arreglan juntos**: se ordenan según qué camino necesita
la hipótesis activa. Una campaña de «quitar todos los no-ops» produciría cambios simultáneos y
destruiría la atribución de ganancia.

---

## 7. Contrato de medición para la vuelta 1

```
R = (recovery_observed, time_to_recovery, viable_at_end, relapse, censored)
```

más η, `dwell_k`, banda de viabilidad, evento de entrada/salida, política para episodios
terminales, línea base, ablación, semillas, exclusiones, stop/retry e identidad de configuración.

**η y `dwell_k` no se eligen mirando el resultado deseado.** Se fijan en una fase de calibración
separada del confirmatorio.

**[instrumento]** Esa maquinaria ya existe y no hay que inventarla: la métrica de CL-7 declara
`calibration_seed_set` y `confirmatory_seed_set` con comprobación de no solapamiento. Y
`viability-recovery-profile` ya implementa las cinco magnitudes de `R`, incluidas `relapse` y
`censored` — esta última porque `recovery_steps = None` tiene dos causas, «nunca se recuperó» y
«el episodio terminó antes», y confundirlas sesga cualquier agregado.

---

## 8. Orden de trabajo

```
 1   cierre de medición en Terrario
 2a  cierre de D4S
 2b  gate del manifiesto de hashes            ← decisión humana, no se mezcla con 2a
 3   caracterización causal de N1
 4   RNFE scar:        estado → acción         (Gate H1)
 5   RNFE experiencia: historia → estado → acción  (Gate H2)
 6   persistencia y transferencia
 7   identidad canónica de activación de RNFE
 8   contrato de promoción de Genesis
 9   puente de materialización Genesis → RNFE
10   retest posterior bajo métrica congelada
```

### Los dos gates de RNFE, que no son el mismo experimento

```
H1   do(S=1) vs do(S=0)   mismo snapshot, misma observación, misma semilla
                          → demuestra que el mecanismo PUEDE modificar conducta
                          controles: scar relevante · sin scar · scar irrelevante

H2   H_experiencia vs H_control, sin inyectar el scar, ambos llevados a O*
                          → demuestra dependencia causal de la EXPERIENCIA
```

Separarlos evita confundir **inyectar memoria** con **aprender de la experiencia**.

---

## 9. Contrato de capacidad de Genesis — a futuro

Ningún `CapabilityManifest` debería existir solo por tener código. Debe llevar incorporada su
epistemología:

```
CapabilityManifest = (mechanism, predeclared_claim, intervention,
                      measurement_contract, evidence, failure_condition, promotion_status)
```

Así el puente no instala funcionalidad: instala **una capacidad con evidencia y criterio de
regresión asociado**.

---

## 10. El invariante, en una línea

```
medir → modificar → volver a medir
```

y nunca

```
modificar → buscar evidencia
```

El problema dejó de ser que Genesis estuviera conceptualmente perdido. Es convertir el sistema
en una máquina donde **ninguna afirmación de ganancia pueda adelantarse al instrumento capaz de
refutarla.**

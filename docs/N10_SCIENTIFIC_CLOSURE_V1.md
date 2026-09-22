# N1.0 · Cierre científico

**2026-09-21** · el estudio, cerrado. Ninguna semilla nueva, ningún mundo
regenerado, ningún reentrenamiento. Sólo reconstrucción desde lo preservado.

## 1 · Pregunta

¿Puede una experiencia pasada convertirse en una coordenada funcional de una
decisión presente, bajo un presente observable equivalente?

## 2 · Scope

Mundo `EPMEM-A1`, corredor cue→demora→elección, `num_channels=4`,
`expose_time_fraction=False`, economía informativa con normalización de aparato.
Dos historias, dos acciones, 32 réplicas.

## 3 · Suministrado y adquirido

```
SUMINISTRADO   tokenización opaca · ranura de memoria · regla de actualización
               repertorio motor · canal de consecuencia · exploración mínima
ADQUIRIDO      qué acción conviene bajo cada token. Nada más.
```

## 4 · Genealogía del preregistro

```
V1  4d18ffcc…  inicial                                  SUPERSEDED, preservado
V2  762d5e6a…  correcciones estadísticas y de protocolo  SUPERSEDED, preservado
V3  de93859a…  añade las intervenciones B/C ejecutables
               y el runner al conjunto sellado           AUTORITATIVO
```

Ninguno se borró ni se reescribió. Hay un contrato que comprueba sus hashes.

## 5–7 · Aparato, aprendiz y protocolo

Instrumento con catorce gates, U1 con la forma causal sellada **antes** de
existir, y una campaña de 32 réplicas contra V3, con verificación del sello
antes de la primera semilla.

## 8 · Gates de validez, recalculados desde el crudo

Diez gates, recomputados y no heredados de `CAMPAIGN_VALID`: paridad de
snapshot, congelación, paridad de `decision_id`, `SAME_PRESENT`, un solo
`obs_hash`, ambas historias en adquisición y en evaluación, marginales y fuerza
del barajado, cero sustituciones. **Todos PASS.**

## 9–10 · Reconstrucción independiente

Un agente en contexto separado, con prohibición de abrir el resumen y el
informe publicados, reconstruyó el análisis desde el crudo y V3. Y
[n10_reanalysis.py](scripts/n10_reanalysis.py) lo repite dentro del repo.

```
                    publicado            reconstruido
acquisition_gain    +0.5149756133        +0.5149756133    LCB +0.5014622161
lesion_loss         +0.5149756133        +0.5149756133    LCB +0.5014622161
shuffle_loss        +0.4962376739        +0.4962376739    LCB +0.4816495950
BA  N/A/B/C         0.4850 1.0000 0.4850 0.5038
veredicto           NEW_DF_DETECTED      NEW_DF_DETECTED
```

Coincide hasta el décimo decimal.

## 11 · Adquisición · `A` contra `N`

`BA(N) = 0.4850` con `signed_branch = −0.0300`: antes de la experiencia no hay
mapeo. `BA(A) = 1.0000`. `LCB95 = +0.5015 > 0`.

## 12 · Correspondencia histórica · `A` contra `C`

**La lesión conceptualmente más limpia del estudio.** `C` conserva la tabla
entrenada, la maquinaria de memoria, la capacidad de leer el token, el
repertorio motor, el mundo, el presente y la distribución marginal de
historias. Rompe **una** cosa: que el token corresponda a la historia real.

```
BA(A) 1.0000   BA(C) 0.5038   LCB95 +0.4816 ≥ 0.10
```

Responde exactamente a «¿necesita el organismo la historia **correcta**, o le
basta con tener algún estado interno?». Le hace falta la correcta.

## 13–14 · Lectura de memoria · `A` contra `B`, y `B ≡ N`

`BA(B) = BA(N)` en **32 de 32** réplicas, en las dos lecturas.

El audit de código lo explica y lo prueba: `Q[EMPTY,*]` **nunca se escribe**
—el agente sólo aprende tras una decisión de puerta, y en la puerta el token ya
fue escrito cinco pasos antes—, así que `B` toma siempre el desempate. El naive
tiene la tabla vacía y toma el mismo. Y el punto que lo decide: **ambos
consumen exactamente dos sorteos por decisión y devuelven `ACTIONS[segundo
sorteo]`** — son la misma función del mismo flujo.

```
ARM_EQUIVALENCE_B_N = BEHAVIORAL desde el crudo · STRUCTURAL desde el código
```

Desde el crudo no puede afirmarse `EXACT`: no guarda acciones por decisión.

## 15 · Claim permitido

> Bajo el scope preregistrado de N1.0, U1 adquirió mediante experiencia una
> correspondencia entre una huella histórica retenida y una acción. Con el
> aprendizaje congelado y el presente observable equivalente, la historia
> correcta permitió seleccionar diferencialmente la acción apropiada.
> Desacoplar la huella de la historia real eliminó la solución; impedir su
> lectura hizo colapsar la expresión al régimen naive.

**Dos contrastes independientes, no tres.** `A−N` demuestra adquisición; `A−C`
demuestra dependencia de la historia correcta; `A−B` es la misma cifra que
`A−N` en este diseño.

## 16 · No-claims

No establece: adquisición del mecanismo de memoria, formación autónoma de
representaciones, memoria episódica, espacial o semántica, comprensión causal,
planificación, generalización a historias arbitrarias, inteligencia general,
conciencia.

## 17 · Limitaciones

**`LIMIT-N10-01`** · la lesión de lectura colapsa al régimen naive, de forma
estructural. `lesion_loss` no es evidencia estadísticamente independiente.
Condicionada a `novelty = 0.0` y a la geometría cue-antes-de-puerta, **ninguna
de las dos verificada por una aserción**.

**`LIMIT-N10-02`** · **32.768 filas por decisión se produjeron y no se
escribieron.** `DecisionRow` lleva los doce campos primitivos; el runner los
redujo a ocho agregados y tiró las tuplas. El objeto más primitivo recuperable
es una tabla 2×2 por brazo, y por inferencia. El paquete reproduce sus números
a partir de sus propios números.

**`LIMIT-N10-03`** · **el gate de paridad de decisiones no puede fallar.**
`decision_id = len(filas)`, siempre `0..n−1`, así que compara tres copias del
mismo rango. Se declaraba «secuencias idénticas, no sólo recuentos iguales» y
comprueba exactamente los recuentos. Un criterio que no puede fallar no es un
criterio, y éste es mío.

Y una cuarta, sobre la lectura primaria: **las cotas por clase son
degeneradas**. `accuracy` por historia en `A` vale exactamente `1.0` en las 32
réplicas, así que toda remuestra da `1.0` y el `LCB = 1.0000` está trivialmente
satisfecho, no estrechamente estimado. La lectura informativa para esa pregunta
es la secundaria: `BA(A) = 0.8969`, clases entre `0.7544` y `0.9828`.

## 18 · Deudas

Una lesión más discriminativa tendría que preservar un contexto **dentro del
soporte aprendido** y quitar específicamente la información histórica. No se
diseña aquí: es otro estudio.

## 19 · Manifiesto de evidencia

[N10_EVIDENCE_BUNDLE_V1.json](docs/N10_EVIDENCE_BUNDLE_V1.json) ·
`cdfc83875ea2864a…` · 14 artefactos con hash.

**No admitido al EvidenceGraph.** Que la evidencia exista no es que esté
admitida, y la admisión es otra decisión que no se ha tomado.

Mapa de Composición v0.1 **sin tocar**: N1.0 es un estudio de adquisición, no
una composición entre dos protoórganos, y no se inventó ninguna arista.

## 20 · Estado final

```
N1.0  CONFIRMATORY_RESULT       = NEW_DF_DETECTED
      SCIENTIFIC_CLOSURE        = CLOSED
      EVIDENCE_BUNDLE_COMPLETE  = NO   (LIMIT-N10-02)
```

Los dos últimos difieren a propósito. El criterio de cierre era que el análisis
independiente reprodujera el resumen, el bootstrap y el veredicto, y que los
hashes coincidieran: lo hace. El criterio de completitud del paquete era que un
consumidor pudiera contestar **qué datos produjo**, y a eso el paquete responde
con agregados. Armonizar las dos cosas en un solo veredicto escondería la
segunda.

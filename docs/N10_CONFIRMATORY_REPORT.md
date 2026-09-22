# N1.0 · Informe confirmatorio

**2026-09-21** · campaña corrida contra el preregistro V3 sellado, sin tocar
nada después de abrirla. Crudo en
[N10_RAW_RESULTS.json](docs/N10_RAW_RESULTS.json), resumen por semilla en
[N10_SEED_SUMMARY.json](docs/N10_SEED_SUMMARY.json).

```
HEAD                871fc41ebbcf9130343a089b6e5a69b9ef353df1
raíz del código     f4231fb8a3adb0fb48b975659a0ee6298c8f5c98ff4c681848a560feacf3c410
manifiesto V3       de93859afe4486440752fc3a335d45e6aca496e12bec84d4160bce1f4dfc861c
árbol               limpio · ficheros distintos del sello: ninguno
réplicas            32 · sustituciones de semilla: 0
```

## Validez, antes que cualquier métrica

Los dieciocho gates pasan en las dos lecturas: paridad de snapshot, congelación
sostenida, paridad de `decision_id`, `SAME_PRESENT` en A/B/C, un solo `obs_hash`
por brazo, shuffle fuerte y marginales conservados. **`CAMPAIGN_VALID = True`.**

Coincidencia del barajado: `min 0.4062 · media 0.5059 · max 0.6250`, contra un
suelo de azar en torno a `0.50`. La permutación está en azar, que es donde debe
estar.

## Lectura primaria · ε = 0

```
BA(N)  0.4850      BA(A)  1.0000      BA(B)  0.4850      BA(C)  0.5038

bootstrap pareado · seed 20260921 · 10 000 remuestras · LCB unilateral 95 %

acquisition_gain   +0.5150   LCB +0.5015   IC95 [+0.4987, +0.5311]   > 0     PASS
lesion_loss        +0.5150   LCB +0.5015   IC95 [+0.4987, +0.5311]   ≥ 0.10  PASS
shuffle_loss       +0.4962   LCB +0.4816   IC95 [+0.4786, +0.5135]   ≥ 0.10  PASS
BA(A)               1.0000   LCB  1.0000                             ≥ 0.75  PASS
acc H=0.10          1.0000   LCB  1.0000                             > 0.5   PASS
acc H=0.90          1.0000   LCB  1.0000                             > 0.5   PASS
signed_branch(A)   +1.0000   descriptivo, no contraste
```

## Lectura secundaria · ε = 0.2 · descriptiva

```
BA(A) 0.8969 · acquisition_gain +0.4119 · lesion_loss +0.4119
shuffle_loss +0.3919 · signed_branch(A) +0.7939
```

No adjudica y no se promedia con la primaria.

## El hallazgo que estrecha la lectura · `B ≡ N` en 32 de 32

**Los brazos B y N dieron resultados idénticos en todas las réplicas**, hasta el
último decimal y con las mismas secuencias de decisión.

La razón es estructural. Con la lectura bloqueada la política ve `EMPTY`, y
`Q[EMPTY, up] == Q[EMPTY, down] == 0` porque `EMPTY` nunca se entrenó, así que el
brazo B toma **siempre** el camino del desempate. El organismo naive tiene la
tabla entera vacía y toma ese mismo camino. Misma semilla de evaluación, mismos
sorteos, mismas acciones.

**Consecuencia:** `acquisition_gain` y `lesion_loss` **son el mismo número**. La
prueba de intersección-unión tiene tres componentes nombrados y **dos
distintos**: `A` contra `N≡B`, y `A` contra `C`. Los dos pasan de forma
contundente, pero afirmar tres contrastes causales independientes sería decir
más de lo que se midió.

No es una desviación de protocolo: no se cambió nada. Es una propiedad del
diseño que el preregistro no anticipó, y el brazo C sí resulta ser un contraste
genuinamente independiente — difiere de N en las 32 réplicas.

## Veredicto

```
NEW_DF_DETECTED
```

Los doce requisitos preregistrados, simultáneamente: instrumento válido,
suficiencia informacional ya establecida, forma causal de producción PASS,
mapeo inicial ausente (`BA(N) = 0.4850`, `signed_branch(N) = −0.0300`),
`acquisition_gain` positivo, **ambas** historias resueltas, `SAME_PRESENT` PASS,
`lesion_loss` y `shuffle_loss` sobre su cota, evaluación congelada, paridad de
decisiones y ninguna fuga privilegiada.

## El claim, y nada más

> Bajo el scope preregistrado de N1.0, U1 adquirió mediante experiencia una
> asociación entre una huella histórica retenida y una acción posterior. Con
> observación presente equivalente y aprendizaje congelado, esa historia moduló
> funcionalmente la decisión; interrumpir su lectura o desacoplarla de la
> historia real redujo la conducta apropiada.

No dice memoria general, ni comprensión del pasado, ni causalidad aprendida, ni
experiencia general, ni inteligencia emergente, ni un grado de libertad
cognitivo general. N1.0 es una transición extremadamente estrecha, y su alcance
es el de un token opaco, dos historias, dos acciones y cuatro números.

## Deudas

La no-independencia de `lesion_loss` respecto de `acquisition_gain` bajo esta
arquitectura. Un brazo B que discriminara de verdad exigiría que la política
tuviera algo distinto de `EMPTY` que leer, y eso es diseño de otro estudio.

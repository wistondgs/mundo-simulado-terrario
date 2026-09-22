# N1.0 · Preregistro confirmatorio v1

**2026-09-21** · sellado antes de consumir una sola semilla confirmatoria.
Manifiesto legible por máquina en
[N10_CAMPAIGN_MANIFEST_V1.json](docs/N10_CAMPAIGN_MANIFEST_V1.json), generado
por [n10_preregistration.py](scripts/n10_preregistration.py) con **todos los
hashes leídos del disco**, no transcritos.

## El claim, y lo que no dice

> Bajo el scope preregistrado de N1.0, U1 adquirió mediante experiencia una
> asociación entre una huella histórica retenida y una acción posterior. Con
> observación presente equivalente y aprendizaje congelado, esa historia moduló
> funcionalmente la decisión; interrumpir su lectura o desacoplarla de la
> historia real redujo la conducta apropiada.

No afirma memoria general, comprensión del pasado, causalidad aprendida,
experiencia general, inteligencia emergente ni un grado de libertad cognitivo
general.

**Tres claims que no se mezclan**, y `NEW_DF_DETECTED` exige los tres:

```
A  ADQUISICIÓN        U1 aprende τ→acción por experiencia
B  EXPRESIÓN          congelado, usa τ para elegir bajo O idéntica
C  DEPENDENCIA CAUSAL lesión y barajado degradan esa relación
```

## Por qué la lectura primaria va sin exploración

Medido sobre el **mismo snapshot reproducido bit a bit** —`785eef13841936be`—
y sin reentrenar:

```
ε = 0.2   acc 0.9297   BA 0.9274   signed_branch +0.8548
ε = 0.0   acc 1.0000   BA 1.0000   signed_branch +1.0000
```

La predicción bajo la hipótesis de exploración es `(1−ε)·1 + ε·0.5 = 0.90`, y lo
observado cae dentro de 1,1 errores estándar con n=128.
**`EXPLORATION_EXPLAINS_RESIDUAL = ESTABLISHED`** — se midió antes de escribirlo,
no se dedujo.

```
PRIMARIO      learning=False · ε=0      adjudica N1.0
SECUNDARIO    learning=False · ε=0.2    descriptivo · NO se promedia con el primario
```

## Unidad de inferencia

**La semilla de entrenamiento, no la decisión.** Las decisiones de un mismo
aprendiz no son réplicas independientes; sirven para estimar el comportamiento
de esa semilla, y la inferencia se hace entre semillas. Bootstrap pareado sobre
deltas por semilla, 10.000 remuestras.

**Prueba conjuntiva** de tipo intersection-union: los tres contrastes tienen que
pasar su cota. No se selecciona a posteriori el favorable.

## Las tres intervenciones

```
A  COMPLETE             sin intervención
B  MEMORY_READ_LESION   el token SE SIGUE ESCRIBIENDO; la política no puede
                        consumir su valor retenido. NO se llama ablación
C  HISTORY_SHUFFLED     permutación determinista sellada sustituye el token que
                        lee la política; mundo, Q, observaciones y consecuencias
                        intactos
N  NAIVE                el snapshot anterior a la adquisición
```

Los tres nacen del **mismo** snapshot: `hash(θ_A) == hash(θ_B) == hash(θ_C)`,
exacto, antes de intervenir. Tres entrenamientos independientes están prohibidos.

## Métricas

**Balanced functional accuracy**, porque el reparto H0/H1 no es exactamente
mitad y mitad:

```
BA = [ P(acierto|H0) + P(acierto|H1) ] / 2        azar = 0.5
```

**Branch con signo**, porque el valor absoluto no distingue gobernar de
gobernar al revés:

```
B_s = P(UP|H_up) − P(UP|H_down)     +1 perfecto · 0 no gobierna · −1 invertido
```

Contrastes por semilla: `acquisition_gain = BA(A)−BA(N)`,
`lesion_loss = BA(A)−BA(B)`, `shuffle_loss = BA(A)−BA(C)`.

**No se exige que B y C valgan 0.5 exacto.** B fluctúa por desempates y C
conserva coincidencias accidentales entre token barajado e historia real. La
prueba causal es `A > B` y `A > C`, pareada y preregistrada.

## Umbrales, derivados y no inventados

| gate | umbral | derivación |
|---|---|---|
| paridad de snapshot | igualdad exacta de hash | estructural |
| paridad de decisiones | `set(decision_ids)` idéntico, no sólo el recuento | estructural |
| congelación | digest de θ idéntico antes y después | estructural |
| `SAME_PRESENT` | **un** `obs_hash` con las dos historias | estructural |
| no-fuga de verdad del mundo | PASS en el commit sellado | estructural |
| `BA(A)` cota inferior 95 % | **0.75** | punto medio entre el azar 0.5 y el techo 1.0: el mapeo tiene que estar más presente que ausente |
| `acquisition_gain` | **> 0** | estrictamente positivo |
| `lesion_loss` | **≥ 0.10** | sin historia utilizable se está en 0.5 y el piloto congelado a ε=0 dio 1.0, así que la pérdida esperada ronda 0.5; 0.10 es **un quinto** de eso, para que una diferencia de un pelo no se llame causal |
| `shuffle_loss` | **≥ 0.10** | igual que la lesión |
| por historia en A | cota inferior **> 0.5** | azar binario; **las dos** clases tienen que superarlo, así que una media alta resolviendo sólo una no basta |

## Semillas

```
32 réplicas    train 2600000+i · eval 2700000+i · shuffle 2800000+i
reserva        2900000..2900007
disjuntas de   piloto train 100-107 · piloto eval 0-3 · fixtures 0, 7, 8
```

Namespaces de RNG separados por propósito: exploración, desempate, barajado y
mundo no comparten flujo — una intervención cambia cuántos sorteos consume un
brazo, y un flujo mutable compartido desplazaría el mundo de los demás.

**Regla de reserva:** una semilla se sustituye **sólo** si el mundo generado la
hace inevaluable —su evaluación contiene una sola clase histórica y la balanced
accuracy no tiene segundo término—. Nunca por mal desempeño del agente, y toda
sustitución queda registrada.

## Presupuesto

```
adquisición   512 decisiones por semilla de entrenamiento (512 estaciones)
evaluación    128 decisiones por semilla de evaluación (128 estaciones)
coste medido  9,78 s por entrenamiento
```

Son los totales del propio piloto, leídos de su corrida: 8×64 y 4×32.

## Parámetros, congelados del piloto

```
alpha_train = 0.3 · epsilon_train = 0.2
epsilon_primary_eval = 0.0 · epsilon_secondary_eval = 0.2
regla  Q(τ,a) ← Q(τ,a) + α·[c − Q(τ,a)]
c      transition.consequence_t1.energy_delta
```

Sin grid search y sin selección de hiperparámetros sobre datos confirmatorios.

## Veredictos posibles

```
INVALID           el experimento dejó de medir el claim
INDETERMINATE     medición válida, conjunción causal no adjudicable
MEASURED_ZERO     campaña válida y exposición suficiente, sin contingencia nueva
                  bajo Ω y ESTE presupuesto — no «U1 jamás podrá»
NEW_DF_DETECTED   los doce requisitos a la vez
```

## Centinelas, corridos sobre el commit sellado

```
positive fixture            PASS · acc 1.0000
negative fixture            PASS · acc 0.4688
leaky fixture               FAIL · OBSERVATIONAL_ALIASING_VIOLATED
degenerate fixture          INVALID / SINGLE_HISTORY_CLASS
suficiencia informacional   INFORMATIONALLY_SUFFICIENT
D1-D9                       todos rechazados
D10/D11                     rechazados
PRODUCTION_U1_CAUSAL_FORM   PASS · 11 gates
```

## Qué invalida la campaña

Fuga observacional · cualquier gate del instrumento fallando en el commit
sellado · código distinto de los hashes sellados · desigualdad de snapshot ·
fallo de paridad de `decision_id` · cualquier actualización durante evaluación ·
`history_id` llegando al organismo · feedback tomado de algo que no sea
`consequence_t1.energy_delta` · una clase histórica ausente · traza corrupta ·
cualquier desviación de protocolo no registrada antes de correr.

Ninguna se corrige estadísticamente.

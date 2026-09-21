# Nivel 1.8 · Calibración RONDA A — cerrada sin presupuesto

> **CERRADA.** Este documento se llamó «final» durante unas horas y el nombre era
> falso: es la primera ronda de calibración, y no seleccionó presupuesto.
> Se conserva entera —los cinco `T`, los 16 pares, el fallo literal de (a) y la
> operacionalización defectuosa de (c)— porque el fallo es el dato.

```
C18 aprendido · SEÑAL                       POSITIVA
ventaja más allá de DEPTH-1                 PRESENTE EN MEDIA · 12/16 vidas
estabilidad entre vidas exigida por §10     NO
regla de cobertura (c)                      OPERACIONALIZACIÓN DEFECTUOSA
presupuesto seleccionado                    NINGUNO
confirmatorio 180000011…180000074           CERRADO · semillas vírgenes
```

**Adjudicado por el humano el 2026-09-20**, tras ver estos resultados y en su
contra: «sd» significa desviación estándar entre vidas, no error estándar ni
CI95. 4096 **no se rescata** reinterpretando el símbolo — pasaría por 0,0002, y
elegir la lectura favorable después de mirar es precisamente la libertad que este
protocolo existe para eliminar. La regla sellada resultó exigir un tamaño de
efecto pareado `d ≥ 2`; no se cumplió; la ronda se cierra.

La corrección de (a) y (c) es **prospectiva**: Enmienda 04, sobre vidas nuevas.

---

**Veredicto de la regla sellada: `T_18` NO SELECCIONADO.**
Ningún peldaño de la escalera, ni el peldaño de agotamiento, cumple las tres
condiciones de §10. Las semillas `180000011…180000074` siguen intactas.

---

## 1 · Linaje y commits

```
eaf9d26  ¿necesita el sucesor al predecesor? · retractación de un claim
32531ef  ORÁCULO SELLADO · antes de que existiera el learner · 16 gates
e7b4058  los 16 gates y sus falsificadores · ANTES del learner
6e0ce44  L18-6 afilado
acb6b14  primer learner · negativo, por defectos identificados después
e105cff  Enmienda 01 · C17-ONLY continuo · L18-16 BASELINE-PARITY · 17 gates
f0222f2  diagnóstico: el autómata era absorbente
1a35caa  reparación del routing, y sólo del routing
12294da  Enmienda 02 · semántica de merge sellada ANTES de implementarla
645b650  L18-17 REFINEMENT-REVERSIBILITY · antes de que merge existiera · 18 gates
17993ef  merge implementado como inverso causal de un split
0c127f7  reparación: puntuar exige SEGUIR el estado · y `organization` absorbente
fbfbdf0  atribución de merge, separada del instrumento
1c5f475  Enmienda 03 · escalera sellada · ruta única · auditoría de trayectoria
```

**16 gates fueron pre-código. 17 y 18 no.** `L18-16` nació con la Enmienda 01,
después del primer learner; `L18-17` nació con la Enmienda 02, antes de que
existiera una línea de merge pero después del learner. No se afirma otra cosa.

---

## 2 · Pregunta sellada

`ΔL = L_POST(C17-ONLY continuo) − L_POST(C18)`, criterio
`CI95_inferior(media ΔL) > 0` con `CI95_inferior = media − 1.96·sd(ddof=1)/√N`
(§7 línea 158, fijado en el oráculo).

Presupuesto por REGLA, no por número (§10): el MENOR `T` que cumpla
(a) margen ≥ 2 sd sobre FIXED-DEPTH-1 · (b) `ΔL/0.3427 < 0.90` · (c) cobertura
no es el cuello de botella.

---

## 3 · Enmiendas y cronología

| | qué selló | ¿antes de ver el dato? |
|---|---|---|
| 01 | `C17-ONLY` CONTINÚA aprendiendo; `L18-16` BASELINE-PARITY | sí, tras medir el confusor |
| 02 | merge = inverso causal de un split; prohibidas 7 constantes | sí, antes de una línea de merge |
| 03 | escalera `64·256·1024·4096` + agotamiento; aritmética pareada de (a); operacionalización de (c) | sí, antes de la calibración de 16 vidas |

---

## 4 · Arquitectura final del learner

Nace siendo 1.7 bit a bit: `C_18 = 0 ⇒ M_1 = M_0^W`. Estado recursivo
`Z_t = F(Z_{t-1}, A_{t-1}, O_t)`. Refina por firma de entrada con criterio
prequencial (MDL), sin una sola constante ajustada. Merge retira el split cuando
el favor acumulado —inicializado con el balance que lo justificó, jamás
reiniciado— llega a cero. Rutas desconocidas hacen *backoff* por la cadena de
padres: UNKNOWN ROUTE ≠ STAY. Conservación de masa `Σ_z C_0 = C_17`.

---

## 5 · Defectos hallados, y por qué invalidaban mediciones anteriores

| defecto | efecto medido | cómo se descubrió |
|---|---|---|
| autómata absorbente en `_next_state` | 0 % de cambios de estado | diagnóstico dirigido |
| **scoring que nunca avanzaba el estado** | learner puntuado siempre desde la raíz: 1 estado visitado en 2048 pasos, teniendo 30 | al instrumentar para el microscopio |
| **`organization` seguía absorbente** | `L18-6` comparaba particiones de un autómata que se quedaba quieto | lectura al reparar lo anterior |
| helper de test que informaba historia, no estado | `refinements>0` con 0 hijos vivos | fallo tras implementar merge |

El segundo invalidó **todo** número `LEARNER` previo:

| | reportado | reparado |
|---|---:|---:|
| ΔL · T=1024 | +0,0166 | +0,0757 |
| ΔL · T=4096 | −0,1148 | +0,0901 |

Ninguno de los 81 tests cogía los dos primeros. Ahora los cogen el falsificador
temporal A (seguir el estado debe COMPRAR verosimilitud) y `F7` con cláusula de
no-vacuidad, verificados contra sus mutantes.

---

## 6 · Demostración de scoring temporal correcto

Sobre `terrario/level18/life.py` —la ruta que recorrerá la campaña—, semilla
`150000011`, `T`=4096, 2048 pasos puntuados:

```
[PASA] 1 · puntuar usa el estado correcto    2048 pasos · desalineados 0
[PASA] 2 · la transición ocurre DESPUÉS      Z_t+1 == _next_state(Z_t,A_t,O_t+1)
[PASA] 3 · evaluar no aprende                updates [4096] · splits [16]
[PASA] 4 · entrenar sí actualiza             updates = 4096 = T_18
[PASA] 5 · sin fuga de O_t+1                 la distribución suma 1 antes de
                                              revelarlo · desviación máx 4,4e-16
transiciones de estado 1792/2048 (87,5 %) · estados distintos visitados 24
```

---

## 7–10 · Los cuatro brazos · 16 vidas `150000011…150000026`

| T | L(C17 continuo) | L(FIXED-DEPTH-1) | L(C18) | L(ORACLE) |
|---:|---:|---:|---:|---:|
| 64 | 0,9688 | 0,9634 | 0,9669 | 0,8482 |
| 256 | 0,9358 | 0,9183 | 0,9148 | 0,6149 |
| 1024 | 0,8348 | 0,7926 | 0,7558 | 0,2756 |
| 4096 | 0,6363 | 0,5845 | **0,5471** | 0,0874 |
| 16384 | 0,4592 | 0,4319 | 0,4075 | 0,0235 |

El orden `C17 < C18 < ORACLE` se sostiene desde `T`=256. **A `T`=64 el organismo
es PEOR que FIXED-DEPTH-1** (0,9669 contra 0,9634).

El techo del oráculo es diagnóstico. No se convierte en «C18 debe recuperar X %».

---

## 11 · Lesión formal de merge · 16 vidas, todo lo demás idéntico

| T | L(C18) | L(sin merge) | Δ log-loss | activos | sin merge | celdas | sin merge |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 | 0,9669 | 0,9603 | **−0,0065** | 3,6 | 14,1 | 17.728 | 57.280 |
| 256 | 0,9148 | 0,9041 | **−0,0107** | 7,1 | 36,8 | 35.200 | 160.128 |
| 1024 | 0,7558 | 0,7730 | +0,0172 | 8,8 | 75,6 | 48.128 | 362.496 |
| 4096 | 0,5471 | 0,5705 | +0,0234 | 10,9 | 116,3 | 59.328 | 609.088 |
| 16384 | 0,4075 | 0,4026 | **−0,0049** | 10,9 | 151,4 | 59.136 | 841.856 |

**Corrijo lo que dije sobre 8 semillas.** Entonces reporté que merge ayudaba a la
predicción y más cuanto mayor el presupuesto. Sobre las 16 y la escalera
completa, **el signo se invierte en tres de cinco peldaños**: merge sólo ayuda a
predecir en 1024 y 4096. Lo que sí es consistente y grande es la economía: reduce
el censo entre 3,9× y 13,9×, y la memoria retenida hasta 14,2×.

El resultado es el dual: **merge aporta poco —y no siempre positivo— a la
predicción, y mucho a la economía representacional.** Para un sistema de recursos
acotados eso sigue siendo causalmente relevante.

---

## 12 · Churn y recursos · brazo C18

| T | splits | merges | % revertidos | 1er split | superv. media | superv. máx | upd/episodio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 | 3,9 | 3,2 | 82,5 % | 8,5 | 0,4 | 23 | 16,3 |
| 256 | 8,1 | 6,5 | 85,4 % | 8,5 | 4,1 | 111 | 31,5 |
| 1024 | 10,2 | 8,2 | 86,0 % | 8,5 | 6,0 | 220 | 99,9 |
| 4096 | 11,4 | 9,2 | 86,8 % | 8,5 | 38,3 | 2350 | 360,1 |
| 16384 | 12,4 | 10,2 | 88,4 % | 8,5 | 101,0 | 11618 | 1324,0 |

**El split temprano, re-juzgado sólo como diagnóstico.** El primer split cae en
el paso **8,5 de media sobre 16 vidas, idéntico a los cinco presupuestos** —como
debe ser: depende de los primeros pasos, que no cambian con `T`. No es un
artefacto de una semilla. `t=10` sigue **sin adjudicar**; ahora está medido.

La distinción que pedías, por coste y no por estética: entre el 82 % y el 88 % de
los splits se revierten a todos los presupuestos, pero la supervivencia media
pasa de 0,4 pasos a 101. A presupuesto bajo es **churn** —nace y muere sin llegar
a usarse—; a presupuesto alto es **búsqueda estructural reversible**, con
estructuras que viven miles de pasos. El coste por episodio crece ×81.

---

## 13 · Cobertura

| T | celdas con soporte | totales | % | firmas | estados sin evidencia | masa que retienen | hambre C18 | hambre FD1 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 | 26,1 | 232,0 | 11,3 % | 8,7 | 0,56 | 0,0266 | 0,5721 | 0,5766 |
| 256 | 72,6 | 452,0 | 16,1 % | 17,9 | 1,00 | 0,0315 | 0,3012 | 0,1903 |
| 1024 | 146,2 | 564,0 | 25,9 % | 26,5 | 1,25 | 0,0324 | 0,0423 | 0,0089 |
| 4096 | 212,7 | 700,0 | 30,4 % | 33,1 | 1,38 | 0,0278 | 0,0058 | 0,0000 |
| 16384 | 237,6 | 700,0 | 33,9 % | 33,0 | 1,19 | 0,0269 | 0,0006 | 0,0000 |

El organismo nunca llega a sostener con evidencia más de un tercio de sus propias
celdas, y arrastra siempre ~1 estado con evidencia nula que retiene ~3 % de la
masa heredada.

---

## 14–15 · Tabla por presupuesto · deltas PAREADOS `m_i = L(FD1)_i − L(C18)_i`

| T | media(m) | sd(m) | tamaño de efecto | vidas que ganan | ΔL | ΔL/0,3427 | % del techo |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 | −0,0034 | 0,0083 | −0,41 | 3/16 | +0,0020 | 0,006 | 1,6 % |
| 256 | +0,0035 | 0,0345 | 0,10 | 5/16 | +0,0210 | 0,061 | 6,5 % |
| 1024 | +0,0368 | 0,0812 | 0,45 | 11/16 | +0,0789 | 0,230 | 14,1 % |
| 4096 | +0,0374 | 0,0744 | 0,50 | 12/16 | **+0,0892** | 0,260 | **16,2 %** |
| 16384 | +0,0244 | 0,0367 | 0,67 | 12/16 | +0,0518 | 0,151 | 11,9 % |

**`ΔL` no es monótono.** Cae de +0,0892 a +0,0518 entre 4096 y 16384, porque el
baseline continuo alcanza al organismo: `L(C17)` baja de 0,6363 a 0,4592. La
ventaja de 1.8 es un efecto de **eficiencia muestral**, y se lava con datos
suficientes — coherente con lo ya medido en §2 del oráculo (4,89× a `T`=64 →
1,13× a 4096).

---

## 16 · La regla, aplicada mecánicamente

```
T=   64   (a) NO   (b) sí   (c) sí    → descartado
T=  256   (a) NO   (b) sí   (c) NO    → descartado
T= 1024   (a) NO   (b) sí   (c) NO    → descartado
T= 4096   (a) NO   (b) sí   (c) NO    → descartado
          ── Enmienda 03 §3 · cláusula de agotamiento ──
T=16384   (a) NO   (b) sí   (c) NO    → descartado
```

**(a) falla en los cinco peldaños bajo la lectura literal.** «≥ 2 sd entre vidas»
exige tamaño de efecto ≥ 2,00; el máximo alcanzado es **0,67**. El efecto es
menor que su propia dispersión entre vidas.

**La lectura de error estándar** (`media ≥ 2·sd/√N`) sí se cumple desde `T`=4096
—y por un pelo: 0,0374 contra 0,0372. Enmienda 03 §4 anticipó exactamente este
desacuerdo y pre-declaró que se aplica lo literal, se reportan ambas, y **decide
el humano sin elegir la favorable**. El desacuerdo se ha producido.

**Sobre (c), y esto es una crítica a mi propio sello.** Lo operacionalicé como
`hambre(C18) ≤ hambre(FD1)`. Los datos muestran que FIXED-DEPTH-1 llega a hambre
exactamente 0,0000 desde `T`=4096, porque sólo tiene 256 celdas: a partir de ahí
(c) exige hambre cero a un modelo con 700 celdas, lo cual es **casi
estructuralmente inalcanzable**. Es el reflejo especular de un gate vacío: un
criterio cuyo único comportamiento posible es FALLAR tampoco es un criterio.

Lo declaro en vez de enmendarlo después de verlo fallar. **Y no cambia el
veredicto:** aun eliminando (c) por completo, (a) literal falla en los cinco
peldaños y `T_18` seguiría sin seleccionarse.

---

## 17 · Valor seleccionado

**Ninguno.** Enmienda 03 §3: agotada la escalera y su peldaño adicional,
`1.8 queda NO DEMOSTRADO al presupuesto sellado`.

---

## 18 · Qué claims permite este dato

Como descripción de **calibración**, no de confirmatorio:

> El mecanismo adquiere un refinamiento predictivo dependiente de historia
> sensoriomotora que mejora sobre `C17` continuo, y que en 12 de 16 vidas supera
> a una retención de profundidad 1 suministrada.

Y sobre merge:

> Merge reduce el censo de estados entre 3,9× y 13,9× con efecto inconsistente en
> signo sobre la predicción.

---

## 19 · Qué claims prohíbe

- «el organismo adquirió el estado latente» · «descubrió la posición» · «construyó
  un mapa» · «descubrió objetos» · «modeló el mundo» · «adquirió representación
  espacial» — `I(C;Z|O)` corregida por nula es el **1,0–1,6 %** de `H(C|O)`.
- «bate a profundidad 1» **sin** el margen y el conteo de vidas: son 12/16 con
  tamaño de efecto 0,50.
- «más presupuesto es mejor»: `ΔL` cae después de 4096.
- «merge mejora la predicción»: sólo en 2 de 5 peldaños.
- Cualquier claim confirmatorio. **No se ha abierto ninguna semilla `180…`.**

---

## 20 · Checklist para abrir el confirmatorio

**BLOQUEADO.** La regla sellada no seleccionó presupuesto. Antes de que exista
checklist que ejecutar hace falta una adjudicación humana sobre:

1. Si «≥ 2 sd entre vidas» se lee literal (y entonces 1.8 no se demuestra a estos
   presupuestos) o como error estándar (y entonces `T_18 = 4096`).
2. Si (c) queda como está —sabiendo que es casi inalcanzable— se retira, o se
   reemplaza por una operacionalización que pueda cumplirse y fallar.
3. Qué significa un efecto que **no es monótono en el presupuesto** para un nivel
   cuyo endpoint se define contra un baseline que también aprende.

Sólo después: enmienda pre-confirmatoria de presupuesto, congelación de learner,
gates, runner, ledger, fixtures, métricas y comparadores, ensayo general con
semillas basura verificando que el runner ejecuta **cada** gate —no repetir
D-4— y sólo entonces `180000011…`.

---

## Apéndice · lo que no se tocó

Learner, criterio de split, semántica de merge, prior, reparto de masa, routing,
scoring, endpoint, baseline, controles y gates: intactos desde el sello. 1.7
sigue congelado y verde en su propio árbol (47 tests, `level18` ausente); `L17-0`
falla **dentro** de este árbol y debe fallar. Semillas `180000011…180000074`:
vírgenes.

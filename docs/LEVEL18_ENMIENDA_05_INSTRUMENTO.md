# Nivel 1.8 · Enmienda 05 — reparación instrumental preconfirmatoria

**Sólo instrumento.** No cambia ninguna propiedad científica de 1.8, ningún
umbral de rendimiento, ningún brazo, ningún presupuesto y ningún endpoint.
Se sella antes de abrir una sola semilla `180…`.

La regla que la gobierna: **reparar el termómetro, no cambiar la temperatura.**

---

## 1 · `L18-5` · el gate certificaba lo contrario de lo que §6 sella

El oráculo §6 sella, sin ambigüedad:

```
C_18 = 0  ⇒  P_18(O'|O,A,z_0) = P_17(O'|O,A)   EXACTAMENTE, bit a bit
          ⇒  el organismo vuelve a 1.7 + S0, NO a la ignorancia
```

y `P_17` **depende de `A`**: ésa es la adquisición entera de 1.7.

La implementación anterior recibía `predict_17(observation)` —un solo argumento—
y comparaba contra ella todas las predicciones del recién nacido. Es decir,
exigía

```
P_18(·|o,a₁,z_0) = P_18(·|o,a₂,z_0)     para todo par de comandos
```

que es la **independencia de la acción**: el invariante de 1.6→1.7, no el de
1.8. Su falsificador lo dejaba explícito —
`test_l18_5_falla_si_la_prediccion_depende_del_comando_al_nacer` — y por tanto
el defecto estaba en el gate desde `e7b4058`, no en ningún learner.

Medido sobre la mesa heredada real:

```
peor diferencia entre comandos al nacer   0.257431   (y DEBE ser ≠ 0)
P_18(·|o,·) contra P_17(·|o,·)            0.000e+00  (y DEBE ser = 0)
```

**Esto no es «un learner que falla un gate». Es un gate mal especificado**, y
habría producido `CAMPAÑA INVÁLIDA` con independencia del organismo.

### Reemplazo de la operacionalización

```
ANTES   ∀o ∀a:  P_18(·|o,a,z_0) = predict_17(o)          ← independencia de A
AHORA   ∀o ∀a ∀o': P_18(o'|o,a,z_0) = P_17(o'|o,a)       ← §6 literal
```

Ambas funciones reciben ahora `(observación, comando)`, de modo que el gate deja
de tener dos interpretaciones posibles. La igualdad sigue siendo **exacta**,
dentro de la semántica numérica ya admitida en `MASS_RTOL`/`MASS_ATOL`.

Se añaden dos observaciones que §6 también implica y que el gate no miraba: que
el recién nacido tenga **un solo estado funcional** y que su prior sea
**literalmente el `C_17` heredado**, comparado por huella.

---

## 2 · `L18-17` · evidencia y acción llegaban por el mismo cable

El gate comprueba que una distinción refutada se deshaga y que una justificada
sobreviva. Pero el runner derivaba ambas de la misma variable:

```
refuted := favour ≤ 0
merged  := favour ≤ 0        ← el mismo suceso lógico
```

y entonces `refuted ⇒ merged` no falsifica nada. La propiedad no era incorrecta;
**el instrumento observaba la decisión y su justificación por el mismo cable.**

### Separación de fuentes

```
refuted   del marcador prequencial      último `favour` observado ≤ 0
merged    del cambio REAL de organización  los hijos ya no están en states()
```

Dos observaciones independientes: una mira la evidencia acumulada, la otra mira
la estructura. Con eso los mutantes existen:

```
M1  refutado pero merge desactivado   → refuted True · merged False  → FALLA
M2  fusionar con favour > 0           → refuted False · merged True  → FALLA
M3  merge correcto                                                   → PASA
M4  ruta colgante tras fusionar                                      → FALLA
M5  masa alterada al fusionar                                        → FALLA
```

**M1 es el que prueba que el gate dejó de ser tautológico.** Si no pudiese
construirse, el gate seguiría midiendo su propia definición.

No cambia nada de la semántica sellada en la Enmienda 02: ni `favour ≤ 0`, ni
cuándo se evalúa, ni la penalización, ni el scoring, ni la regla de fusión. Sólo
de dónde lee el gate.

---

## 3 · `L18-11` · NO SE TOCA

En calibración, el margen sobre FIXED-DEPTH-1 es positivo en **10 de 16 vidas**,
y el gate exige unanimidad. Queda escrito así:

```
L18-11 FALLA EN CALIBRACIÓN
```

No se quita la unanimidad, no se convierte en mayoría, no se convierte en `LCB`,
no se armoniza con la regla de presupuesto y no se cambia porque 16384 ya fuese
seleccionado. La Enmienda 04 preguntaba **qué presupuesto tiene ventaja media
reproducible**; `L18-11` pregunta **si esa ventaja aparece en todas las vidas**.
Son preguntas distintas, y la segunda es mucho más exigente. Estaba sellada.

**Corrección de lenguaje, que importa:** no se afirma que «el confirmatorio
devolverá NO DEMOSTRADA». Lo que se sabe es que *esta versión no satisface
`L18-11` sobre las 16 vidas de calibración*. Las semillas confirmatorias todavía
no existen experimentalmente, y una observación de calibración no es un
resultado de confirmación. Lo que sí viaja con el protocolo es que `L18-11` es
severo y que el learner no mostró unanimidad al calibrar.

---

## 4 · El ensayo general no exige PASS científico

```
DEBE demostrar    los 20 gates fueron EJECUTADOS: presentes, invocados, con
                  input y alcance correctos, vida correcta, resultado registrado,
                  procedencia válida, ledger completo
NO debe exigir    que los gates científicos pasen sobre semillas basura
```

Un `FAIL` científico en el ensayo puede ser perfectamente correcto. Un gate
**nunca ejecutado** sí invalida la campaña. Esta separación existe para que las
semillas de ensayo no se usen para «prepasar» la ciencia.

---

## 5 · Defensa en tiempo de ejecución contra las semillas reservadas

`grep` no vuelve a ser la defensa. Todo camino marcado como calibración,
diagnóstico, nulo, permutación, fixture o ensayo **se niega a consumir** una
semilla de `180000011…180000074`. La trampa de `180000000+k` fue potencial y no
consumada; la próxima no dependerá de que alguien la vea.

---

## 6 · Cronología · no se reescribe

```
32531ef   oráculo PRE-CÓDIGO                                    16 gates
e105cff   Enmienda 01 · + L18-16 BASELINE-PARITY                17
645b650   Enmienda 02 · + L18-17 REFINEMENT-REVERSIBILITY       18
a311c35   instrumentación preconfirmatoria · + L18-18, L18-19   20
ESTA      reparación semántica de L18-5 · reparación observacional de L18-17
```

Nunca se afirma que los 20 fueran pre-código. Lo fueron 16.

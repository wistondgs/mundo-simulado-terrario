# 1.8 · diagnóstico del descubrimiento · causa localizada

```
┌────────────────────────────────────────────────────────┐
│   DIAGNÓSTICO PASIVO · CALIBRACIÓN · NO CONFIRMATORIO  │
│   `_refine` NO se ha tocado · learner congelado        │
└────────────────────────────────────────────────────────┘
```

**Fecha:** 2026-09-20 · learner `acb6b14` · semillas `150000011…150000018`

---

# 0 · Precisión cronológica, para no describirlo mal después

```
32531ef   oráculo PRE-CÓDIGO · 16 gates · antes de la primera línea del learner
acb6b14   primer learner · falla
e105cff   Enmienda 01 · define C17-ONLY continuo Y AÑADE L18-16 · 17 gates
```

**Los diecisiete gates no existían antes del learner.** `L18-16 BASELINE-PARITY`
nació **después** del primer mecanismo y **antes** de cualquier semilla
confirmatoria. Es corrección prospectiva legítima, pero la cronología se conserva
tal cual y no debe contarse como si los diecisiete hubieran sido pre-código.

---

# 1 · ¿Está condenada la profundidad 1?

Cuatro organizaciones, misma evidencia, misma conservación de masa.

```
  T_18  NO-SPLIT   DEPTH-1   LEARNER    ORACLE      ΔL d1    ΔL lrn   ΔL orac
  1024    0.8499    0.8064    1.0048    0.2696    +0.0435   -0.1549   +0.5803
  4096    0.6456    0.5928    1.0001    0.0859    +0.0529   -0.3545   +0.5598

  masa: DEPTH-1 0.00e+00 · ORACLE 1.14e-13        estados 14.2 · splits 3.2
```

**`DEPTH-1` gana.** Condicionar por `a_{t-1}` —exactamente lo que el primer split
debería producir— es positivo y consistente. El objetivo no está condenado.

Pero el learner cae a `−0.35` con **14 estados donde `DEPTH-1` necesita 4**.

---

# 2 · La causa · **el autómata es absorbente**

```
splits ocurridos en los pasos     [10, 118]
entradas de routing               128
estados creados                   10

tramo                     pasos   estados visitados   cambios de estado
antes del 1er split          10           1                0  (0.0 %)
tras el 1er split           108           1                0  (0.0 %)
último cuarto              1024           1                0  (0.0 %)
```

Una partición de profundidad 1 exige cambiar de estado en **~75 %** de los pasos
—el estado *es* la acción anterior, y la acción cambia casi siempre—. El learner
cambia en **0 %**.

## 2.1 · Por qué

Al separar `ROOT` por firma `(ROOT, a_prev)` se escriben entradas de routing para
`(ROOT, a, o)`. Una vez dentro de `hijo_2`, la clave de la transición siguiente es
`(hijo_2, a', o')`, **que no existe en la tabla**, y

```python
self._routing.get((self._here, command, after), self._here)
```

devuelve el estado actual. El organismo aterriza en un hijo y **no sale nunca**.

## 2.2 · Y eso explica el `ΔL` entero

Tras el primer split el modelo efectivo es **un solo hijo** con
`prior = C_17 · share` —un quinto de la masa heredada— y sólo su fragmento de
evidencia. Es estrictamente peor que el baseline, y **peor cuanto más corre**:
coincide con que `ΔL` pase de `−0.15` a `−0.35` al cuadruplicar el presupuesto.

---

# 3 · Los siete modos, adjudicados

| modo | veredicto |
|---|---|
| 1 · split no propuesto | **NO** · se proponen y se ejecutan |
| 2 · split correcto rechazado | **NO** |
| 3 · split incorrecto aceptado | **SECUNDARIO** · dispara en el paso 10, con diez observaciones |
| 4 · **routing incorrecto tras el split** | **SÍ · CAUSA PRIMARIA** · 0 % de cambios de estado |
| 5 · sobrefragmentación | aparente (14 estados) pero **consecuencia de 4**, no independiente |
| 6 · fusión destructiva | **no aplica** · el mecanismo **no implementa merge**, y el oráculo lo menciona |
| 7 · representación buena que se degrada | **NO** · nunca llegó a ser buena |

---

# 4 · Estado

```
C18 EXPRESABLE            SÍ · ORACLE-PARTITION +0.58
PROFUNDIDAD 1 VIABLE      SÍ · +0.04 / +0.05
LEARNER ACTUAL            NEGATIVO
CAUSA                     LOCALIZADA · routing absorbente tras el split
                          secundaria: split prematuro (t = 10)
                          hueco: merge no implementado
```

**No se ha ajustado ninguna constante ni cambiado el algoritmo.** La causa ya se
puede señalar; qué hacer con ella es adjudicación.

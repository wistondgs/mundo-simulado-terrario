# LEVEL1-SENSORIMOTOR-REVERSAL-01 · preregistro sellado

**Sellado antes de escribir una línea del experimento.**
Rama `experiment/level1-reversal-plasticity-01`, base científica `83a96d8`,
auditoría PRE `EXIT 0`.

---

## 1 · Parámetros congelados

```
n_A = 2048          adquisición bajo C_A
n_B = 16384         experiencia bajo C_B          n_B / n_A = 8
τ_recovery = 0.05
```

`m_A = identidad` · `m_B = {UP↔DOWN, LEFT↔RIGHT}` · el ser registra el **comando**
`a_t`, nunca `m(a_t)`.

Control positivo: **tabla EMA sobre `(o,a)`**, `q ← q + 0.2(y − q)`. Tabular a
propósito, para que el contraste con CASES aísle la regla de actualización y no
la representación.

## 2 · Cuarentena de semillas

El desarme mecanístico **leyó** dirección del efecto, suelos y mecanismo sobre
`20260919`, que es `BASE_SEED + 0` del Experimento 1. Esa realización queda
inhabilitada como evidencia confirmatoria.

```
desarme              20260919
Experimento 1        20260919 … 20260950
quemada              31415926          ← ver la enmienda de abajo
verificación         99999937          ← dedicada a comprobar implementación
REV confirmatorio    31415927 … 31415958        ← congeladas aquí
```

Disjunción verificada **incluidas las imágenes** de `+20 000 003` (banco) y
`+10 000 003` (permutación): intersección vacía entre los cinco conjuntos.

### Enmienda 1 · semilla `31415926` quemada durante la verificación

Al comprobar que las referencias independientes coinciden con `predict()` usé
`31415926`, que era la primera confirmatoria, y **vi la dirección del efecto**:
RASGOS `0.00438833` frente a CASOS `0.00774028` — precisamente lo que §14-nueva
predice. La comprobación era de implementación, pero la mirada fue a la
hipótesis.

Reparación: `31415926` queda fuera del conjunto confirmatorio y la ventana se
desplaza a `31415927 … 31415958`, manteniendo 32. Toda comprobación de
implementación futura usa `99999937`, dedicada y disjunta.

Se registra como desviación del preregistro en vez de corregirse en silencio,
porque el conjunto confirmatorio se congeló *antes* y esto lo cambia *después*.

## 3 · §14-original · `REFUTED_PRE_RUN_BY_MECHANISTIC_AUDIT`

Hipótesis retirada, conservada en el registro:

> FEATURES concentra ~10× más evidencia por estadístico, luego debería mostrar
> mayor inercia frente al reversal: `τ_FEATURES > τ_CASES`.

Refutada **antes** de correr, por auditoría de su propio mecanismo. Suelos
derivados de los suficientes estadísticos, no aproximados:

```
BS_floor CASES     0.007069
BS_floor FEATURES  0.003771          ambos ≤ τ = 0.05
```

El argumento que la sostenía —contar conteos por celda— es exactamente la
aproximación que §13 prohibía. La cometí.

## 4 · §14-nueva · activa

$$BS^{final}_{B,\text{FEATURES}} < BS^{final}_{B,\text{CASES}}$$

y, si ambos alcanzan `τ`:

$$recovery_{n,\text{FEATURES}} < recovery_{n,\text{CASES}}$$

### Diagnósticos mecanísticos preregistrados

**M1 · reasignación estructural sin inversión.** Medido sobre el desarme, para el
comando `ARRIBA`:

```
rasgo          tras fase A   tras fase B
bit 0 v=0           +5.342        +0.142    portaba la estructura → NEUTRALIZADO
bit 0 v=1           -5.743        -0.200
bit 1 v=0           -0.182        +2.551    era neutro → PASA A PORTARLA
bit 1 v=1           +0.278        -2.944
bit 2, bit 3         ~0.2          ~0.05    mudos, siguen mudos
```

Ningún estadístico de FEATURES cruza cero desde saturación. El viejo recibe
evidencia **mezclada** y su cociente vuelve hacia 1; el nuevo parte de un pool
**equilibrado** y se construye con evidencia consistente. CASES, en cambio, debe
desplazar la media de cada celda contradictoria de un extremo al otro:

```
tras fase A   P = 0.0238
+  2048       P = 0.5000        ← el valor del ignorante, exacto, con n_B = n_A
+ 16384       P = 0.9010
```

**M2 · densidad de actualización, por TIPO de estadístico.** No es «8× para todo
FEATURES»; esa simplificación es falsa:

```
CASES   celda (o,d)     64 celdas, 1 act/transición →   256 en fase B    1×
FEATURES  base_d         4 celdas, 1 act/transición →  4096 en fase B   16×
FEATURES  rasgo (d,j,v) 32 celdas, 4 act/transición →  2048 en fase B    8×
```

`base_d` y `feature_{d,j,v}` se registran **por separado** en cada checkpoint.

### Límite de atribución, declarado antes

M1 y M2 vienen **acoplados a la representación**. Este experimento puede
comprobar que ambos ocurren y que las predicciones siguen de los suficientes
estadísticos. **No puede separar cuánto aporta cada uno.** Si REV confirma la
predicción, lo permitido es:

> La ventaja observada queda mecanísticamente explicada por la reorganización de
> qué rasgos portan la contingencia junto con una mayor densidad de actualización
> de los estadísticos de rasgo.

Y **no**: «M1 aporta X %, M2 aporta Y %». Eso es otro experimento.

## 5 · Conocimiento presente pero mal indexado

$$P_B(y\mid o,d)=P_A(y\mid o,m_B(d))$$

La contingencia nueva **ya está** dentro del ser, bajo otras etiquetas motoras.
Ninguno de los dos mecanismos tiene operador de reetiquetado; los dos deben
reconstruir contando. REV mide por tanto:

> reaprendizaje bajo reetiquetado causal, sin mecanismo explícito de reetiquetado.

Un organismo que detectara `m_B ∈ S_4` y reutilizara `K_B(d) ← K_A(m_B(d))` es
otro mecanismo y otro experimento. **Parking lot.**

## 6 · Recuperación

```
recovery_n        = mín{ n ∈ 𝒦 : BS_B(n) ≤ 0.05 }
floor_recovery_n  = mín{ n ∈ 𝒦 : BS_floor(n) ≤ 0.05 }
recovery_lag      = recovery_n − floor_recovery_n
```

`recovery_n` **nunca** se interpreta solo. Si el suelo no cruza `τ`:
`REVERSAL_DOSE_INSUFFICIENT`, y `recovery_n` no es fallo del organismo.

`τ = 0.05` no exige volver a la competencia pre-switch, que es
**aritméticamente imposible**: `BS_pre,CASES = 0.004884` frente a
`BS_floor,final = 0.007069`.

### Suelo de CASES · definición canónica

$$BS_{\text{floor}}=\frac{1}{|\mathcal C|}\left[\sum_{c\,\text{voltean}}\left(\frac{1+n_A^{(c)}}{2+n_A^{(c)}+n_B^{(c)}}\right)^{2}+\sum_{c\,\text{firmes}}\left(\frac{1}{2+n_A^{(c)}+n_B^{(c)}}\right)^{2}\right]$$

Las dos formas valen para cualquier verdad de celda: la aportación al Brier es
idéntica por simetría. El suelo de FEATURES **no** se deriva de aquí, sino de sus
propios suficientes estadísticos y de la misma ecuación log-momio de `predict`.

## 7 · Cuatro regiones, no tres

```
BS_obs ≈ BS_floor                → mecanismo consistente
BS_obs > BS_floor                → peor de lo que explican sus estadísticos
BS_floor > τ                     → REVERSAL_DOSE_INSUFFICIENT
BS_obs < BS_floor − ε            → FLOOR_VIOLATED · imposible · STOP
```

`ε` declarado por precisión numérica, no igualdad bit a bit.

## 8 · Exclusión por semilla, nunca por brazo

Si una semilla incumple una precondición de un contraste primario, se excluye de
**todos** los brazos de ese contraste. Nunca `n_CASES ≠ n_FEATURES`. Se reportan
total, excluidas, motivo exacto y descriptivos de las excluidas.

## 9 · Aislamiento del azar

$$RNG_{\text{policy}}=f(\text{semilla},\ \text{brazo},\ \text{checkpoint})$$

Nunca se comparte con el generador de adquisición; una sonda nunca avanza el
iterador experimental.

## 10 · Métricas por checkpoint

`𝒦 = {0,1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384}`

```
BS_total · BS_chosen · BS_unchosen · R_move
log-momio del rasgo antiguo · del nuevo · de los mudos · del acumulador base
dosis por suficiente estadístico · floor · floor_gap · estado del control positivo
```

`BS_total` gobierna `τ`. `BS_chosen` y `BS_unchosen` se reportan porque en el
Experimento 1 el 75 % de la medida es conocimiento que la conducta nunca usa, y
bajo reversal las celdas que voltean y las direcciones tomadas no tienen por qué
coincidir.

## 11 · «Conducta» significa exactamente esto

> capacidad de seleccionar un comando cuyo acto físico resultante no choque.

No navegación. Medido: hay `2.41` de 4 direcciones libres por situación, y la
política no prefiere ninguna libre sobre otra.

## 12 · Cierre

```
REV_STATUS = PASS | FAIL | INCONCLUSIVE | INSTRUMENT_FAILURE
```

y STOP. El objetivo siguiente se decide revisando la evidencia, no durante la
implementación.

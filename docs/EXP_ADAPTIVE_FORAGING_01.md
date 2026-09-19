# EXP-ADAPTIVE-FORAGING-01 · resultado

**2026-09-18.** Primer experimento conductual de la escalera. Base `25fd0d0`, worktree
`/home/wis/exp-foraging-01`, rama `exp/adaptive-foraging-01`.
`scripts/exp_adaptive_foraging_01.py`.

```
E2-A  APRENDIBILIDAD          INSUFFICIENT_INFORMATION
E2-B  ADQUISICIÓN AUTÓNOMA    INSUFFICIENT_INFORMATION
```

Ninguno es `FALSIFIED`: la dirección puntual es mayoritariamente positiva. Ninguno es
`DEMONSTRATED`: los intervalos cruzan el cero y el efecto lo carga una semilla.

---

## Lo que SÍ queda establecido

**La adquisición interna es consistente.** La ventaja que el world model asigna a CONSUME frente a
MOVE —`E[energía prevista | CONSUME] − E[energía prevista | MOVE]`— cruza a positivo en **7 de 7**
semillas, **sólo en NORMAL**:

```
semilla        0        1        2        3        4        5        7
NORMAL   +0.0124  +0.0155  +0.0035  +0.0092  +0.0058  +0.0088  +0.0052
PARAM    -0.0051  +0.0157  -0.0042  +0.0061  -0.0099  -0.0001  -0.0018
FULL     -0.0053  +0.0146  -0.0039  +0.0061  -0.0081  -0.0001  -0.0019
```

El organismo **aprende**, y se ve en el órgano. Lo que no está establecido es que lo **use**.

**La adaptación no paramétrica no aporta nada detectable.** `M`, buffer episódico y línea base se
mueven en PARAMETRIC exactamente igual que en NORMAL —medido por componente con la huella canónica—
y `Δ(PARAM − FULL) = +1.86, IC95% [−0.43, +5.43]`. Todo el efecto conductual, cuando lo hay, viene
de los parámetros. **Esta separación sólo es visible porque OCF-G3 construyó los tres brazos**, y es
la primera vez que dice algo.

**El probe congelado es limpio.** `learning_enabled=False` salta `agent.learn()` entero, y la huella
adaptativa quedó **intacta en los tres brazos en las siete semillas**. Nada de aprendizaje se coló
en la medición de persistencia.

---

## E2-A · aprendibilidad · n = 7 semillas pareadas

Adquisición: 300 pasos del mismo stream forzado, 152–187 experiencias informativas por semilla.
Probe: `learning_enabled=False` para todos, comida a distancia 3.

```
                          media     IC95% bootstrap pareado   NORMAL gana
consumos  NORMAL−FULL     −3.86        [−37.29, +18.29]           5/7
consumos  NORMAL−A0       +9.29        [ +0.71, +18.71]           5/7
consumos  PARAM−FULL      +1.86        [ −0.43,  +5.43]           3/7

supervivencia   NORMAL 5/7 · PARAM 3/7 · FULL 2/7 · A0 2/7
Δ N−FULL        +0.43        [−0.14, +0.86]
```

**NORMAL bate al azar** (el intervalo excluye el cero). **NORMAL no bate a FULL** de forma
establecida.

## E2-B · adquisición autónoma · n = 6 semillas pareadas

Sin acciones forzadas. Familia de disponibilidad de recurso.

```
distancia      NORMAL    PARAM     FULL       A0    supervivencia N/P/F/A0
    2           19.17     1.50     2.17     5.33    3/6 · 1/6 · 3/6 · 4/6
    3           19.00     9.33    10.67     2.50    4/6 · 3/6 · 3/6 · 2/6

Δ(NORMAL−FULL) distancia 2    +17.00   [−2.00, +48.33]   3/6
   sin el máximo (94)          +1.60   [−3.20,  +7.20]   2/5
Δ(NORMAL−FULL) distancia 3     +8.33   [−6.33, +27.33]   3/6
   sin el máximo (51)          −0.20   [−9.60,  +8.80]   2/5
```

**El efecto entero lo carga una semilla en cada condición.**

**La no monotonía se confirma**: a distancia 2 el azar (5.33) bate a FULL (2.17) y a PARAMETRIC
(1.50); a distancia 3 el azar se hunde (2.50) y los brazos de A4 suben. Con el recurso demasiado
cerca el encuentro domina sobre la política, como el piloto sugería.

---

## El diagnóstico · esto es un problema de varianza, no de efecto

```
consumos de FULL por semilla:  [1, 97, 2, 7, 2, 0, 0]      varianza = 1110
```

FULL está **congelado desde la inicialización**: no aprende nada. Esa varianza es **pura suerte de
inicialización**. En la semilla 1 un organismo congelado consiguió 97 consumos y sobrevivió mientras
NORMAL consiguió 0 y murió — es decir, en una semilla de siete **aprender fue activamente
perjudicial**.

Con ese ruido de fondo, n=7 no puede resolver un efecto de la magnitud que buscamos. El experimento
está limitado por varianza, no por tamaño del efecto.

**La reparación tiene nombre y ya existe a medias.** Los tres brazos comparten semilla, así que
comparten inicialización *nominal* — pero las políticas divergen desde el primer paso y con ellas la
trayectoria. `InitialStateFingerprint` ([experiment_composer.py:114](terrario/lab/experiment_composer.py:114))
existe exactamente para declarar el estado inicial compartido de un par, con nueve hashes
requeridos... y **sólo valida configuraciones de planner**
(`{"use_planner": …, "use_world_model": True}`). Extender su vocabulario de brazos es lo que
convierte esta campaña en decidible.

---

## Contratos del montaje

- **El planner va ENCENDIDO en los tres brazos de A4.** Medido: con `use_planner=False` A4 no emite
  un solo CONSUME en 201 pasos y se muere. Ese brazo no es «A4 sin una pieza», es otro organismo, y
  queda declarado como control mecanístico, nunca como A4 completo.
- **`view_size` del agente y `view_radius` del mundo se declaran juntos** y el script falla
  ruidosamente si no coinciden: el encoder fija `64·⌈view_size/2⌉²` al construirse y no se negocia.
- **`action_availability` no se usa como supuesto**: el runtime no la aplica.
- Nada de A4, Planner, WorldModel ni Physics fue modificado.

## Condiciones de parada · ninguna disparó

El stream contenía 152–187 eventos informativos por semilla; la huella bajo FULL no se movió en
ninguna; el probe congelado corrió sin reaprendizaje en las 21 corridas; y la diferencia conductual
**no** desapareció por completo en el probe —existe en 5 de 7 semillas, simplemente no es
separable del ruido.

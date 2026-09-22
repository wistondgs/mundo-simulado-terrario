# N1.0 · Preregistro confirmatorio v2

**2026-09-21** · **V1 queda intacto y marcado `SUPERSEDED`**; no se editó ni se
regeneró. Todas las correcciones se hicieron **sin haber consumido una sola
semilla confirmatoria**, que es lo que las hace baratas y legítimas.

```
V1  docs/N10_CAMPAIGN_MANIFEST_V1.json
    sha256 4d18ffcc29322f916901fe7c7b4738e5f016b7cc7d81bdd978aec5d7e143703f
V2  docs/N10_CAMPAIGN_MANIFEST_V2.json
    sha256 762d5e6a7c7a1eaa680a2852569e2861078dd1dc86ea0a041c246bb3c645297f
```

## Lo que NO cambia

U1, el instrumento, los presupuestos, los mundos, α, ε y las tres
intervenciones A/B/C. Las 32 réplicas se mantienen: con la unidad inferencial
por learner y los efectos del piloto no hay motivo para inflar a 64.

## Las seis correcciones

### 1 · El umbral conserva su valor y pierde su justificación

`0.10` se quedaba, pero «un quinto de la pérdida esperada» deriva la vara de lo
que esperamos que pase, que es la dirección equivocada.

> **Mínimo efecto causal relevante, preregistrado: 10 puntos de balanced
> accuracy, un quinto del rango funcional disponible entre azar (0.5) y
> solución (1.0).**

Es una vara que declaramos estar dispuestos a llamar causal, no una derivada
del tamaño que anticipamos. Y se aplica a la **cota inferior unilateral**, no
al estimador puntual:

```
LCB95(Δ_lesion)   ≥ 0.10
LCB95(Δ_shuffle)  ≥ 0.10
LCB95(Δ_acquisition) > 0
LCB95(BA_A)       ≥ 0.75
```

### 2 · La evidencia por clase se acota, no se estima

`accuracy_H0` y `accuracy_H1` se calculan **por semilla** y se bootstrapean
**entre semillas**; las dos cotas inferiores deben superar `0.5`. Dos
estimadores puntuales por encima del azar dejarían pasar una clase por ruido.

### 3 · `signed_branch` se reporta y no es un cuarto contraste

En una tarea binaria reexpresa la misma separación que ya lleva la balanced
accuracy. Sirve para la **dirección** —distinguir gobernar de gobernar al
revés— y no entra en la conjunción confirmatoria.

### 4 · La evaluabilidad se decide desde el mundo, antes de correr nada

Se lee de `GeneratedWorld.stations` **antes** de que ningún agente exista. Una
semilla se sustituye sólo si su mundo no contiene las dos clases históricas.

> Si las dos historias estuvieron disponibles y U1 termina con una fila
> empatada o sin aprender, **eso es resultado científico y no se reemplaza**.

Precomprobado sobre las 72 semillas:

```
train    32 semillas · 512 estaciones    NO evaluables: ninguna
eval     32 semillas · 128 estaciones    NO evaluables: ninguna
reserva   8 semillas · 128 estaciones    NO evaluables: ninguna
```

El caso «token nunca visto» queda cerrado por construcción, no por sorteo ni
por un `INDETERMINATE` decidido después de mirar el desempeño.

### 5 · El shuffle tiene que ser fuerte, no sólo conservar marginales

Una permutación que deje el 85 % de los tokens en su sitio convertiría el brazo
C en el brazo A con ruido: la intervención existiría en el código y no en los
datos. Se registra y se acota:

```
P(policy_token == actual_history) ≤ 0.75
```

contra el suelo de azar `(n0² + n1²)/n²`. Medido en la semilla de evaluación
`2700000`: coincidencia `0.4844`, azar `0.5044`.

### 6 · Sellado criptográfico completo, y la semilla del bootstrap

```
código sellado      11 ficheros
raíz del código     811205cd835d69663a4bbb64429de7ca90dee61b2a76f9ad6019be0883e31720
manifiesto semillas 3d92c56533bff2fad770f4aa95555acd3cb6a4358277242b4069455c8313450d
bootstrap seed      20260921
remuestras          10 000
método              LCB unilateral 95 % (percentil 5) DECIDE
                    IC bilateral 95 % (2,5–97,5) descriptivo
```

**El sello es la raíz del código, no el commit.** Un commit puede diferir en
documentación sin que cambie una línea de lo que corre; la campaña tiene que
verificar que los once hashes coinciden en el momento de ejecutar.

## El diagnóstico del piloto, con el alcance estrechado

```
EXPLORATION_EXPLAINS_RESIDUAL_WITHIN_PILOT = ESTABLISHED
```

Es un hecho sobre los snapshots del piloto, **no una propiedad general de U1**.
El mismo snapshot reproducido bit a bit, `785eef13841936be`: `BA 0.9274` con
`ε=0.2` y `BA 1.0000` con `ε=0`.

## Lo demás sigue como en V1

Claim, los tres claims separados, brazos A/B/C, unidad de inferencia por
semilla, intersection-union, presupuestos, semillas, regla de reserva,
invalidación y veredictos posibles: sin cambios. Ver
[N10_PREREGISTRATION_V1.md](docs/N10_PREREGISTRATION_V1.md).

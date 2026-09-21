# `LEVEL1.6` · crítica al nivel que acabo de certificar, y backlog

**Fecha:** 2026-09-20 · **Emitido después de** `4592576` (mapa causal)
**Nada de esto está implementado.** No se toca campaña, clasificación ni umbrales.

---

## 0 · Un error de auditoría, mío

En `3bfc4cf` §9 escribí:

> «Que sólo se haya dado una categoría no significa que las demás no existan. […]
> las cinco restantes simplemente no ocurrieron en esta campaña.»

**Es falso para una de ellas.** `N-EXPERIENCIA` no es que no ocurriera: **no podía
ocurrir.**

```
regla         N-EXPERIENCIA  si  gained < 0.25 * available
medido        gained = 0.9796 * available     mínimo de las 16 vidas: 0.9539
```

Para dispararse haría falta una captura por debajo de 0.25 y la peor vida está en
0.95. Certifiqué como «no observada» una categoría **estructuralmente
inalcanzable**. Queda como **AN-11, severidad alta**, y es un fallo del auditor,
no del experimento.

## 1 · Por qué era inalcanzable · el dato que lo explica todo

```
T        captura A1   cobertura S0        sd cobertura
  32        0.3048        0.4795             0.2774
  64        0.4375        0.6077             0.2046
 128        0.5856        0.7972             0.1493
 256        0.7216        0.9037             0.1176
1024        0.9164        0.9984             0.0063
4096        0.9796        1.0000             0.0000
16384       0.9955        1.0000             0.0000

correlación cobertura(S0) -> captura(A1), 112 corridas:  r = +0.9274
```

`cobertura` = fracción de las transiciones **alcanzables** del mundo que la
trayectoria de S0 efectivamente visitó.

**A `T = 4096` la cobertura es 1.0000 con desviación cero: S0 visitó todas las
transiciones posibles de las 16 vidas.** El problema de exposición estaba resuelto
antes de que A1 hiciera nada, y lo único que quedaba era que un contador
convergiera sobre una cadena estacionaria de dieciséis estados.

## 2 · Qué significa esto para el claim

**El claim de `b9c0b4d` §11 sigue siendo cierto, palabra por palabra.** Todos los
gates pasan, la intervención causal se sostiene y la campaña reproduce bit a bit.
Lo que cambia no es la verdad de la frase sino **su alcance**:

```
DEMOSTRADO      A1 adquiere y converge   ·  la competencia reside en el estado
NO PUESTO A PRUEBA   A1 bajo escasez de experiencia
```

Y hay una consecuencia incómoda que conviene decir sin adornos: **el presupuesto
se eligió en el punto donde la variable interesante ya había saturado.** El
oráculo justificó `T = 4096` porque «la curva ya está saturada — de 4k a 16k sólo
gana 0.027 nats». Traté la saturación como comodidad. Para la medición es lo
contrario: en saturación, el experimento ya no puede distinguir un organismo de un
contador, porque la cobertura es 1 y sólo queda aritmética.

## 3 · El régimen informativo existe y funciona

Medido con **la misma maquinaria, sin cambiar nada**:

```
T       ΔL vs SHUFFLED   sd      mín      IC95 inf   clases que aparecen
  64        0.3053     0.1365   0.0573     0.2384    N-EXPERIENCIA 1 · POSITIVO 15
 128        0.4853     0.1833   0.1046     0.3954    POSITIVO 16
 256        0.6434     0.2573   0.0851     0.5173    POSITIVO 16
1024        0.7808     0.2828   0.1199     0.6422    POSITIVO 16
4096        0.8452     0.3259   0.1162     0.6856    POSITIVO 16
```

A `T = 64` el contraste **sigue siendo positivo** (IC95 inferior +0.2384) **y la
taxonomía se enciende**: una vida cae en `N-EXPERIENCIA`. Es decir: existe un
presupuesto donde el nivel es a la vez válido e informativo, y no es el que se
corrió.

---

# Backlog · nada implementado

## B-1 · `SHUFFLE_NOT_DESTRUCTIVE` debe tener gate (cierra AN-1)

`audit_shuffle` ya calcula la destrucción y `LifeOutcome.shuffle_destructive` la
guarda. Falta un gate que lo lea y su fixture negativa —que ya existe como test.
Es media hora y cierra el único agujero procedimental del nivel.

## B-2 · La cobertura como instrumento de primera clase

Hoy `N-EXPERIENCIA` se decide por un proxy del lado del resultado
(`gained < 0.25 * available`). La **cobertura** es la medida directa de lo que S0
entregó, es computable sin el organismo, y correlaciona 0.93 con la captura.

```
propuesto   instrumentar cobertura por vida
            usarla como discriminante de N-EXPERIENCIA
            reportarla siempre, que es lo que hace visible el eje S0
```

Esto convierte `N-EXPERIENCIA` en evidencia **medida** sobre S0 en vez de inferida.

## B-3 · El presupuesto en la pendiente, no en la meseta

Preregistrar `T` donde la curva todavía discrimina —o mejor, **la curva de
adquisición completa como endpoint** en lugar de un punto. Un barrido
`T ∈ {64, 256, 1024, 4096}` con el mismo banco POST convierte «¿aprendió?» en
«¿con qué eficiencia por experiencia aprendió?», que es una pregunta sobre el
mecanismo y no sobre la aritmética.

## B-4 · Tamaños de efecto analíticos por mundo, sellados antes del código

Medido en esta auditoría: `ΔL vs SHUFFLED` aproxima `I(o_t;o_{t+1})` del mundo con
`r = 0.9935`, y `ΔL vs FROZEN` aproxima `log 16 − H(o'|o)` con `r = 0.9964`, ambos
calculables de la topología.

**Consecuencia procedimental:** un oráculo futuro puede sellar el tamaño de efecto
**por semilla**, antes de existir código, en lugar de un valor poblacional salido
de un piloto. Eso **elimina estructuralmente AN-6** —no se puede sellar un número
medido sobre una población filtrada sin declararlo si el número se calcula de cada
mundo.

Es la misma doctrina de oráculos analíticos del linaje, aplicada al tamaño de
efecto y no sólo al techo.

## B-5 · Lo que NO propongo

No propongo repetir 1.6, ni cambiar su veredicto, ni tocar el oráculo. La campaña
corrida es válida. B-2, B-3 y B-4 son para el **siguiente** preregistro, sea cual
sea la capacidad que se decida medir.

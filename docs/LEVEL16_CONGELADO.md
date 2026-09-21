# AGENTE NIVEL 1.6 · CONGELADO

```
┌──────────────────────────────────────────────────────────────┐
│   A1  =  D E M O S T R A D A                                 │
│   RÉGIMEN  =  E X P O S I C I Ó N   S A T U R A D A          │
└──────────────────────────────────────────────────────────────┘
```

**Fecha de congelación:** 2026-09-20 · **No se repite.** Las dos etiquetas van
juntas y ninguna se cita sin la otra.

Oráculo `9b0d39b` intacto · enmiendas `d0ce9f8` `8f8c85d` `5c54848` ·
informe `0503874` · auditoría `3bfc4cf` · cierre formal `b9c0b4d` ·
mapa `4592576` · crítica `0c9e3d1` · deuda del verificador `ffe97e8`

---

## 1 · Lo que queda demostrado

> A1 está demostrada como adquisición de un modelo temporal a partir de
> experiencia propia; **no** está demostrada todavía como adquisición bajo
> escasez, selección de experiencia ni aprendizaje eficiente.

```
DEMOSTRADO       adquisición y convergencia bajo exposición prácticamente exhaustiva
NO DEMOSTRADO    adquisición eficiente bajo experiencia escasa
```

Un óptimo predecible analíticamente **no elimina el aprendizaje**: el estado
inicial no contiene `P(o'|o)`, la experiencia modifica el estado, y la sustitución
`M_T → M_0 → M_T` demuestra que la competencia está en lo adquirido.

## 2 · El régimen, con su número

```
T = 4096   cobertura de S0 sobre las transiciones alcanzables:  1.0000   sd 0.0000
```

S0 visitó **todas** las transiciones posibles de las 16 vidas. El problema de
exposición estaba resuelto antes de que A1 hiciera nada.

**Corrección de lenguaje, adoptada.** Escribí que en saturación «el experimento ya
no distingue al organismo de la aritmética». Es demasiado fuerte y es falso:
FROZEN, TEMPORAL-SHUFFLED y la intervención causal **sí** distinguen aprender de
no aprender. Lo que el experimento no distingue es al organismo de **un estimador
tabular elemental suficientemente alimentado**. Ésa es la limitación real y es más
pequeña que la que yo enuncié.

**El 98.13 % deja de usarse como indicador de sofisticación.** Con cobertura
1.0000 y una tabla de conteos, ese número mide principalmente **convergencia del
estimador**. Se conserva como dato, no como mérito.

## 3 · `AN-11`, en su redacción definitiva

> `N-EXPERIENCIA`: rama implementada pero **no ejercitable** en el régimen
> confirmatorio de 1.6.

Con `T = 4096` y captura mínima 0.9539 frente a un umbral de 0.25, la categoría
era prácticamente inaccesible bajo la regla clasificatoria. **El veredicto
`POSITIVO` no se modifica.** El clasificador está probado sobre entradas
sintéticas que alcanzan las seis ramas.

## 4 · Artefactos confirmatorios · registro congelado

Lo que faltaba: la campaña era reproducible por determinismo y **no estaba
archivada**. Queda archivada aquí.

```
       semilla   huella de trayectoria (sha256)                                      clase
     140000011   434c05dc9ad062cc4f77a8a3f32f559b75def25c0e5c16a690b158d877a196a5   POSITIVO
     140000012   57493afe9383ce5f3d998d840797b7d41f82b185f27e96eafccb9ea094c10762   POSITIVO
     140000013   47155c46833e247165d42427d5c73a26f6cd7fd803aec9a71bce18e740c5912e   POSITIVO
     140000014   9939d8d023e9d112b6bbcb42caeddb29b8bc9a28e2810c75810902a446bd421b   POSITIVO
     140000015   cce5fc58e5203618b16431ca9fd702041a440d5034c945b8cffe4e6f18c48a3c   POSITIVO
     140000016   4fd0793c3944b3a0f78bad485d66e0ac207333136d6a26554a5d698c1a05ba22   POSITIVO
     140000017   579f9b1ab0ebc7a772b70f4c020eba31658adba633c53d1a8ea716aa6dcf8b85   POSITIVO
     140000018   aa31d0aa2ccf863493e50a949378b5fcab152dfda142a8042236110cc0c9a2cf   POSITIVO
     140000019   5fd23236915d9add512446cb4c37f99841c9f37204516971f987053f9da5ecf8   POSITIVO
     140000020   ab564c33eed19886ecbc71f86f78ea79e6f760209c07f91ba46652588e998c51   POSITIVO
     140000021   441debe020d76cf3e9cfab6bd0b32fc550b41776ac2c4efd4d08b864df6a89d6   POSITIVO
     140000022   a94820ea10bc7ef84effa515bf11592db4f5fcf8f30819746465f12512c51b09   POSITIVO
     140000023   3e26972c0bce5b4487332560e64341b7f0d75b793e611555ef5c75f7195fe253   POSITIVO
     140000024   dbcf0552dc879f1d413a1ffaf7d08c226adf2f6a533dfe7ab75062b4b81c683f   POSITIVO
     140000025   a26b8a277febc6ef13fc8e5adbc7bf9d6baf340d4a50814861eafb6ed2b5c34a   POSITIVO
     140000026   c9d3a85a2c8c36a6db089dc26410007440e2404c3964128f44c2a334078add86   POSITIVO

digest de las 16 salidas   cca758237cc43131d08cae70aa9f39d6fe78fa09e26f891dc2f5dcabec04e86e
IC95 inferior  +0.680501   ·   veredicto POSITIVO   ·   gates 12/12
```

La primera huella coincide con la única que el informe `0503874` había registrado.

## 5 · La identidad analítica · lección metodológica del linaje

En el límite poblacional, con `P(o'|o)` estacionaria:

```
L(FULL)      →  H(O_{t+1} | O_t)
L(SHUFFLED)  →  H(O_{t+1})                    el control converge a la marginal
L(FROZEN)    =  log 16                        exacto, no asintótico

⇒   ΔL(FULL vs SHUFFLED)  →  I(O_t ; O_{t+1})
⇒   ΔL(FULL vs FROZEN)    →  log 16 − H(O_{t+1} | O_t)
```

Medido: `r = 0.9935` y `r = 0.9964`, con sesgo negativo constante —el que
corresponde a un contador finito frente a la conditional verdadera.

**Consecuencia para el método, no para 1.6:** donde el mundo admita solución
cerrada, el tamaño de efecto esperado debe calcularse **por semilla antes de
ejecutar al aprendiz**. Eso separa la dificultad del mundo del rendimiento del
organismo, y hace difícil repetir `AN-6` —no se puede sellar un valor medido sobre
una población filtrada sin declararlo si el valor se calcula de cada mundo.

**Y no sustituye al endpoint preregistrado.** Es corroboración post hoc
independiente.

## 6 · Tres instrumentos para el próximo preregistro

No son mejoras de A1. Son instrumentos del método:

```
1 · cobertura directa de experiencia como variable causal del lado de S0
    --no inferirla después a partir del rendimiento del aprendiz

2 · curva competencia-vs-presupuesto, cuando importe la adquisición como proceso
    --un presupuesto en saturación es magnífico para demostrar convergencia
      y pésimo para estudiar cómo aprende el ser

3 · oráculo analítico por mundo/semilla, siempre que sea matemáticamente posible
```

## 7 · Lo que 1.6 NO es

**No es evidencia de un ser que aprende con pocos datos.** Es evidencia de algo
anterior y necesario:

> cuando su propia vida le proporciona la estructura suficiente, el ser puede
> convertir esa experiencia en una expectativa temporal interna correcta.

Y sigue sin demostrarse, ninguna de ellas por omisión sino por diseño:
contingencia acción→consecuencia, causalidad sobre el mundo, exploración dirigida,
curiosidad, motivación, valor, búsqueda, memoria selectiva, descubrimiento
autónomo, generalización entre mundos y agencia fuerte.

---

**Congelado.** No se repite, no se embellece, no se cita una etiqueta sin la otra.

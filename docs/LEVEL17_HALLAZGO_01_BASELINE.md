# 1.7 · hallazgo previo al preregistro · `D_C` contra `M_0` congelado está confundido

**Fecha:** 2026-09-20 · trabajo de diseño cuantitativo, **antes** del oráculo
**Semillas:** calibración `150000011…150000026`. Las confirmatorias
`160000011…160000074` siguen **ciegas y sin medir**.

---

## 1 · Lo que se midió y por qué obliga a parar

Con el baseline que la adjudicación proponía —`M_0^W` congelado al terminar la
fase P— el control del mundo gemelo **falla**:

```
                D_C vs M_0 congelado    ¿positivas?
mundo B, T_17=256        +0.0254           16/16
mundo B, T_17=1024       +0.0752           16/16
mundo B, T_17=4096       +0.1053           16/16
```

En B, `I_B(A;O'|O) = 0` **exactamente** —verificado al nivel del kernel de
estados. Ahí `D_C` no puede ser positivo por información de acción, porque no la
hay. Y sin embargo lo es, y **crece con el presupuesto**.

## 2 · La causa

`M_0^W` se congela al acabar la fase P. `M_1` recibe, además, **todas las
transiciones de la fase A**. Así que

```
D_C(vs M_0 congelado)  =  información de la acción  +  simplemente más datos
```

En el mundo A el segundo término se esconde detrás del primero. En B queda solo, y
por eso el control lo destapa. Es exactamente la clase de defecto que produciría
«otro 1.6»: resultado positivo con interpretación demasiado ancha.

## 3 · La corrección · `NO-ACTION` no es `M_0` y no es un brazo duplicado

La adjudicación decía:

> «NO-ACTION es prácticamente M0. Si no aporta una falsificación distinta, no
> necesitamos otro brazo duplicado.»

**La medición lo contradice.** `NO-ACTION` parte de `M_0^W` y **sigue aprendiendo
`P(o'|o)`** durante la fase A, sobre las mismas transiciones que ve `M_1` pero sin
el comando. Con él como baseline:

```
T_17   mundo |  D_C vs M_0 congelado |  D_C vs NO-ACTION      sd      >0
 256       A |              +0.2778  |            +0.2497  0.0415   16/16
 256       B |              +0.0254  |            -0.0108  0.0052    0/16
1024       A |              +0.6124  |            +0.5436  0.0686   16/16
1024       B |              +0.0752  |            -0.0109  0.0077    0/16
4096       A |              +0.8893  |            +0.7703  0.0768   16/16
4096       B |              +0.1053  |            -0.0067  0.0057    1/16
```

En B la ventaja pasa a ser **negativa**, que es lo correcto: cuatro veces más
parámetros cuestan un poco sobre datos no vistos cuando no compran nada.

En A el resultado **sobrevive**: 0.889 → 0.770. No era un artefacto, estaba medido
contra el baseline equivocado.

```
D_C  ≡  L_POST(NO-ACTION)  −  L_POST(M_1)
```

`M_0^W` sigue siendo necesario —es lo que define la herencia y el punto al que
vuelve la lesión— pero **no es el comparador del endpoint**.

---

## 4 · Las curvas de presupuesto

### `T_P ↦ calidad de M_0^W` (pérdida en POST, `T_17 = 1024`)

```
T_P       L(M_0^W)     sd
 128        1.9601   0.2563
 256        1.7157   0.2361
1024        1.3609   0.2046
4096        1.2694   0.1594
```

Satura entre 1024 y 4096. Un `M_0^W` bien aprendido **no es ilegítimo**: hace más
difícil atribuir ventaja espuria a 1.7.

### `T_17 ↦ (D_E, D_K, D_C)` (`T_P = 1024`)

```
T_17      D_W      D_E      D_K   D_K/D_W      D_C
  64   0.8817   0.8638  -0.0626   -0.0709   0.0980
 256   0.8817   0.8716   0.1161    0.1326   0.2778
1024   0.8817   0.8786   0.4662    0.5290   0.6124
4096   0.8817   0.8726   0.7327    0.8310   0.8893
```

*(`D_C` de esta tabla está contra `M_0` congelado; con `NO-ACTION` baja a 0.250 /
0.544 / 0.770.)*

Tres lecturas:

- **`D_W` es constante** porque es una propiedad del mundo, no de la vida. Es el
  oráculo analítico por semilla que 1.6 pedía tener.
- **`D_E ≈ D_W` ya a `T_17 = 64`.** S0 visita casi toda la dependencia disponible
  casi de inmediato. La exposición **no** es el cuello de botella en 1.7 —al
  contrario que en 1.6, donde la cobertura era la variable dominante.
- **`D_K` sí tiene pendiente.** Negativo a 64 —con 1024 celdas y 64 muestras las
  desviaciones añaden ruido— y todavía en 0.83 de lo disponible a 4096. **1.7 no
  satura donde 1.6 saturaba.** El régimen informativo existe y es ancho.

`D_K` negativo **no se trunca**: dice algo real sobre el mecanismo con poca
experiencia.

---

## 5 · Estado

```
hecho      invariante de nacimiento     C_17 = 0 ⇒ M_1(o,a) = M_0^W(o)   bit a bit
hecho      invariante de lesión         C_17 → 0 devuelve EXACTAMENTE a M_0^W
hecho      lo heredado nunca se toca    huella verificada tras la fase A
hecho      canal opaco                  un campo, comando, antes de la transición
hecho      cableado φ                   24 biyecciones alcanzables · flujo disjunto
hecho      K-SOMBRA de acción           P(o'|o,a) exacta desde la topología
hecho      D_W, D_E, D_K, D_C           ejecutables
hecho      mundo B físico               control, y el que destapó el confundido
hecho      NO-ACTION                    baseline correcto del endpoint

abierto    SHUFFLED-ACTION calibrado por su nula, no por umbral heredado
abierto    permutación opaca de actuadores, medida
abierto    los dos presupuestos T_P y T_17
abierto    el oráculo preregistrado
```

**Nada de esto ha tocado las semillas confirmatorias.**

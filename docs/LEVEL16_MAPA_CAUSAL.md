# Mapa causal · estado tras el cierre de 1.6

**Fecha:** 2026-09-20 · **Fuente:** `b9c0b4d` (cierre formal) y `3bfc4cf` (auditoría)

Este documento sólo mueve los estados que la evidencia de 1.6 permite mover.
**Ninguna flecha posterior se promociona.**

---

## 1 · Estados

```
┌─────────────────────────────────────────────────────────────────────┐
│  S0   variación motora endógena            SUSTRATO SUMINISTRADO    │
│       ─────────────────────────────────────────────────────────     │
│       No es adquisición. Nace con el cuerpo, no cambia en toda la   │
│       vida, y su papel aquí es producir la experiencia, no tenerla. │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │  genera la trayectoria
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  A1   estructura temporal sensorial              D E M O S T R A D A │
│       ─────────────────────────────────────────────────────────     │
│       P(o_{t+1} | o_t) adquirida de la propia vida.                 │
│       16/16 vidas · IC95 inferior +0.6805 · 98.13 % del óptimo      │
│       causal en 16/16 por ablación y restauración                   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ╎  HIPÓTESIS DEVELOPMENTAL
                                   ╎  (línea discontinua: no hay experimento)
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  dependencia siguiente · contingencia propia   NO DEMOSTRADA        │
│       ─────────────────────────────────────────────────────────     │
│       Que un ser que predice su flujo esté en mejores condiciones   │
│       de atribuirse cambios es una conjetura razonable y NADA MÁS.  │
│       Permanece HIPÓTESIS hasta que exista experimento causal.      │
└─────────────────────────────────────────────────────────────────────┘
```

## 2 · Lo que la campaña dice de `S0`, y lo que no

**[M]** Ninguna vida cayó en `N-EXPERIENCIA`. **[I]** Por tanto la política motora
uniforme **no fue el cuello de botella** a `T = 4096` en esta clase de mundos.

Eso **no** es una afirmación sobre la calidad de `S0`. Dice únicamente que no
estorbó. La asimetría preregistrada sigue en pie y es importante conservarla: si en
una campaña futura A1 cayera en `N-EXPERIENCIA`, eso sería **evidencia negativa
sobre S0** —la trayectoria endógena no llevó al ser por donde había algo que
aprender— y no una refutación de A1.

## 3 · Lo que explícitamente NO se mueve

```
contingencia acción→consecuencia     NO DEMOSTRADA · sin experimento
causalidad sobre el mundo            NO DEMOSTRADA · sólo se intervino el estado
exploración dirigida                 NO DEMOSTRADA · política uniforme, inmóvil
curiosidad · motivación · valor      NO DEMOSTRADA · ninguna señal existe
memoria selectiva                    NO DEMOSTRADA · la tabla no retiene ni olvida
generalización entre mundos          MEDIDA COMO CASI NULA · 2.7241 vs FROZEN 2.7726
agencia fuerte                       NO DEMOSTRADA
```

## 4 · Deuda que el mapa arrastra

**[C]** `AN-1`: `SHUFFLE_NOT_DESTRUCTIVE` es condición de parada declarada, se
calcula por vida y **ningún gate la lee**. Se cumple en 16/16, así que el estado
`DEMOSTRADA` de A1 no depende de ello —pero el procedimiento entra en la siguiente
campaña con ese agujero abierto. Queda anotado, no corregido.

## 5 · Regla de promoción

Un estado pasa a `DEMOSTRADA` cuando, y sólo cuando, existen a la vez:

```
1.  oráculo sellado antes del código, con la población declarada
2.  control que pueda salir negativo
3.  intervención causal sobre el estado, no sólo correlación
4.  gate con fixture negativa por la vía real del verificador
5.  campaña reproducible bit a bit
```

1.6 cumple las cinco. Ninguna flecha posterior cumple ninguna.

---

## 6 · Enmienda del 2026-09-20 · etiqueta de régimen

Este mapa se emitió con `A1 = DEMOSTRADA` y sin cualificar el régimen. La crítica
posterior (`0c9e3d1`) midió que a `T = 4096` la cobertura de S0 sobre las
transiciones alcanzables es `1.0000` con desviación cero. El estado de A1 **no
cambia**, pero no debe citarse solo:

```
A1  =  DEMOSTRADA
RÉGIMEN  =  EXPOSICIÓN SATURADA
```

Demostrado: adquisición y convergencia bajo exposición prácticamente exhaustiva.
No demostrado: adquisición eficiente bajo experiencia escasa.

El texto original de §1 a §5 se conserva sin editar. Congelación definitiva en
`docs/LEVEL16_CONGELADO.md`.

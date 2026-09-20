# `ORGANISM-FUSION-REMEMBERED-BINDING-01` · preregistro

**Sellado antes de existir el código.** Base `68d852d`, el cierre documental del
Nivel 1.4, en árbol propio.

---

## 0 · Qué es · y qué no

**No es un decimal.** No se adquiere nada nuevo: se reúnen `B` (1.0), `Q` (1.1),
`H` (1.2), `M` (1.3) y `ψ` (1.4) en una sola instancia. Es la pieza que falta
antes del 1.5, porque hoy existe `B+Q+H+M` y existe `1.4` con `ψ`, pero **ningún
organismo tiene memoria y binding a la vez**.

## 1 · La tarea · y por qué es la única que hace trabajar a las dos

```
PRESENT   se presenta un cue g*        ·  M lo escribe   ·  sin acción
TICK
QUERY     escena de DOS referencias    ·  el cue ya no está fuera
          direcciones  {(x₁,g₁),(x₂,g₂)}   con g* ∈ {g₁,g₂}
          proximidades {(y₁,s₁),(y₂,s₂)}   con yᵢ = ψ(xᵢ)
RESET
```

La pregunta: **¿cuál es la proximidad de la referencia cuyo cue recordé?**

```
sin M   → no se sabe QUÉ referencia es la diana
sin ψ   → se sabe cuál es, pero no qué evidencia le pertenece
```

Ninguna de las dos basta sola. `M` sigue guardando **un solo `CueToken`**, sin
portador y sin ampliar su horizonte: su contrato de `09c1d80` queda intacto.

## 2 · Una operación de lectura que declaramos, porque es nueva

Para usar el cue recordado hay que **localizar el elemento direccional cuyo cue
coincide con el recordado**. Es una comparación de identidad sobre tokens
opacos --la misma operación que hace `Q` al indexar su fila por token-- pero
**ningún nivel anterior la tenía en su readout**.

Se declara aquí como **suministrada por diseño**, igual que la regla de
composición. Y se añade a la lista de lo no autorizado: esto **no** es atención,
ni búsqueda, ni memoria relacional.

## 3 · El factorial · valores sellados

Con cuerpo y orientación ideales, en aritmética exacta. Sin `M` el factor
direccional cae a su prior ignorante `1/4` y la creencia de proximidad se mezcla;
sin `ψ` se mezcla igual.

```
    M     ψ            BS_joint      exacto
   ON    ON            0.036364      2/55
   ON   OFF            0.049432      87/1760
  OFF    ON            0.096662      1361/14080
  OFF   OFF            0.096662      1361/14080
```

```
mejora sólo M        0.047230
mejora sólo ψ        0.000000        ← EXACTAMENTE CERO
mejora conjunta      0.060298
INTERACCIÓN          0.013068        toda ella superaditiva
```

> **`ψ` sin `M` no aporta nada.** Su contribución marginal es cero exacto: sin
> saber cuál es la referencia diana, saber qué proximidad pertenece a cuál no
> sirve de nada.

Es más fuerte que la fusión `H+M`, donde las dos capacidades aportaban por
separado. Aquí la dependencia es total.

**Y hay que decir qué clase de hecho es:** es una propiedad de **la tarea que
diseñamos**, no un descubrimiento sobre el organismo. Elegimos una consulta donde
el binding es inútil sin la diana. Sigue siendo la tarea correcta, porque es la
única en la que las dos capacidades son portantes.

**Empate preregistrado:** las dos filas con `M OFF` valen lo mismo,
`1361/14080`. No es un hallazgo: es que `ψ` no tiene dónde aplicarse.

## 4 · Se reúnen procedimientos, no artefactos

```
una semilla σ  →  B, Q reconstruidos con el código sellado de 1.1
               →  H readquirida con el código de 1.2 sobre el flujo de σ
               →  ψ readquirida con el banco de 64 de 1.4, que es determinista
               →  M, mecanismo sin parámetros, copia literal del blob de 705239c
```

**Un solo núcleo, comprobado por identidad de objeto.** Cinco huellas idénticas
antes y después: `B`, `Q`, `H`, `ψ` y la ausencia de parámetros de `M`.

## 5 · Gates

| gate | criterio |
|---|---|
| **RB-0** un solo núcleo | identidad de objeto en todos los caminos |
| **RB-1** linaje intacto | huellas `B`, `Q`, `H`, `ψ` idénticas pre/post |
| **RB-2** `M` sin deriva | `memory.py` byte-idéntico al blob de `705239c` |
| **RB-3** semántica de `M` | leer antes del tick da nada · leer no consume · dos ticks expiran |
| **RB-4** `ψ` intacta | `C(ψ(x)\|x) = 17/20` tras la fusión |
| **RB-5** coexistencia | las cinco capacidades responden en la misma instancia |
| **RB-6** uso conjunto | los cuatro `BS_joint` reproducen la tabla sellada |
| **RB-7** dependencia total | la mejora marginal de `ψ` es **cero exacto** |
| **RB-8** el tick hace falta | omitirlo hunde el brazo completo al suelo de `M OFF` |
| **RB-9** pasividad | medir no mueve ninguna huella; cero RNG nuevo |

**Fixtures negativas:** dos núcleos distintos · `memory.py` alterado · binder sin
entrenar · omitir el tick · una métrica que escribe.

## 6 · Semillas

```
120000011 … 120000018      disjuntas de todo lo usado (verificado, con los +7)
```

Cero RNG nuevo: el banco de `ψ` y el factorial se enumeran; el azar heredado sólo
reconstruye `B`, `Q` y el flujo de `H`.

## 7 · Afirmación máxima autorizada

> Un mismo organismo conservó intactas cinco capacidades adquiridas en ramas
> distintas y las hizo participar en una misma predicción: recordó durante un tick
> qué referencia se le había señalado y usó una correspondencia aprendida entre
> portadores para recuperar la evidencia de proximidad que le pertenecía.

**Obligatorio:** la regla de composición y la operación de localización por token
fueron **suministradas por diseño**. Esto es verificación del conjunto, no
descubrimiento de integración. Y cada capacidad se adquirió **en aislamiento de
las demás**.

**No autorizado:** atención, búsqueda, memoria relacional, identidad de objeto,
selección de recuerdos, ni organismo unificado en sentido fuerte.

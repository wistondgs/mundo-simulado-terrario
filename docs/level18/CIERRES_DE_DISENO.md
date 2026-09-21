# 1.8 · los cuatro cierres previos a la implementación

```
┌────────────────────────────────────────────────────────┐
│   EXPLORATORIO / CALIBRACIÓN  ·  NO CONFIRMATORIO      │
│   OBJETIVO DEVELOPMENTAL ADJUDICADO                    │
│   C_18 = NO DEMOSTRADA / NO IMPLEMENTADA               │
└────────────────────────────────────────────────────────┘
```

**Nombre de trabajo:** desambiguación predictiva adquirida
**Fecha:** 2026-09-20 · base `6cf55a4` · no toca ningún archivo de 1.7

---

# Cierre 2 · la distribución de evaluación · **RETIRO MI DECLARACIÓN DE DISCREPANCIA**

Declaré que `0.3427` y `0.3156` estaban ponderados sobre poblaciones distintas.
**Es falso, y lo compruebo:**

```
H(O'|O,A) bajo p_ref, analítica, 16 semillas          0.3427
media sobre trayectoria, 16 semillas,  8 000 pasos    0.3436
media sobre trayectoria, 16 semillas, 30 000 pasos    0.3435
```

Las dos ponderaciones **coinciden**. El `0.3156` era simplemente el subconjunto de
**10** semillas que usé en aquella corrida. No había dos distribuciones: había una,
y yo estaba mirando menos mundos.

```
NÚMERO ÚNICO DE EVALUACIÓN          H(O'|O,A) = 0.3427 nats
estimador de trayectoria            consistente con p_ref · validado
```

Y los porcentajes de `§11` quedan tal como estaban escritos, contra `0.3427`. No
hay dos series.

---

# Cierre 1 · ¿es perceptiva o sensoriomotora?

```
   L   H | sólo O   H | O y A    gap O   gap O+A   aporte de A
   1      0.3060      0.1689    0.0097    0.1468      0.1371
   2      0.1856      0.0721    0.1301    0.2436      0.1134
   4      0.1144      0.0189    0.2013    0.2968      0.0956
   8      0.0753      0.0030    0.2404    0.3127      0.0722
```

*(ruido Monte Carlo estimado ±0.004, medido como la diferencia a `L = 0`, que debe
ser cero y sale −0.0037.)*

```
┌──────────────────────────────────────────────────────────────────┐
│  A L = 1, EL COMANDO PROPIO APORTA 0.1371 DE 0.1468              │
│  el 93 % de la desambiguación de un paso viene de saber QUÉ HICE │
└──────────────────────────────────────────────────────────────────┘
```

La historia de observaciones sola recupera `0.0097` nats a `L = 1` — dos veces y
media el ruido, es decir **prácticamente nada**.

**Por qué, y es intuitivo:** haber intentado ir a la izquierda **y no haberse
movido** dice que hay pared a la izquierda. Eso separa celdas que se ven igual. La
historia de observaciones no puede hacerlo porque la observación no dice qué acción
la produjo.

Incluso a `L = 8`, sólo con observaciones quedan `0.2404` de `0.3127`: **23 % corto**.

```
VEREDICTO   1.8 es GENUINAMENTE SENSORIOMOTORA
            y enlaza directamente con 1.7, no con 1.6
```

---

# Cierre 3 · qué se suministra sin suministrar la partición

```
SUMINISTRADO
    un mecanismo genérico de estado secuencial   Z_{t+1} = F(Z_t, A_t, O_{t+1})
    capaz de crear, separar y fusionar estados internos según evidencia predictiva
    el prior de composición sobre C_17
    la regla de actualización

NO SUMINISTRADO
    cuántos estados hay
    la partición
    ningún mapa a celdas, coordenadas ni etiquetas físicas
```

**`24` y `17` no se congelan.** Son evidencia de tratabilidad, no parámetros. Una
constante del tipo `NUM_LATENT_STATES` volvería a meter conocimiento humano de la
solución, y un gate AST puede prohibirla con el idioma que 1.6 y 1.7 ya usan.

**La prueba de que la partición no está suministrada**, y es medible: el **mismo
código**, en mundos con multiplicidad latente distinta, debe terminar con
organizaciones internas distintas. Mismo mecanismo, mundos diferentes,
representación diferente. Si no varía, se la dimos.

---

# Cierre 4 · la lesión incremental

El patrón de 1.7 se traslada literalmente. Allí:

```
C_0(o,a,o') = N_16(o,o') / 4          ⇒   C_17 = 0  ⇒  M_1 = M_0^W   bit a bit
```

Aquí, con `k` estados internos, cada uno hereda la tabla de 1.7 dividida entre `k`:

```
C_0(o,a,o' | z) = C_17(o,a,o') / k

⇒  si Z colapsa a UN solo estado, el k se cancela arriba y abajo
⇒  P_18(o'|o,a,z) = P_17(o'|o,a)    EXACTAMENTE
```

```
LESIÓN   colapsar Z a un estado único   ⇒   1.7 EXACTAMENTE + S0
```

No devuelve a la ignorancia ni a 1.6: devuelve al peldaño inmediatamente anterior,
igual que la lesión de 1.7 devolvía a 1.6. Es la propiedad que hace incremental
toda la arquitectura del linaje, y hay que conservarla.

---

# Ventaja metodológica que conviene no perder

**S0 permanece intacto.** El bucle política→experiencia no se cierra todavía, así
que:

```
la paridad de trayectoria del linaje SOBREVIVE un decimal más
todos los brazos pueden vivir literalmente la misma vida
CONTROL_CAUSAL_POLITICA_ENDOGENA.md queda en reserva, sin gastarse
```

```
1.7          P(O'|O,A)
1.8          P(O'|O,A,Z)   con Z adquirido · misma vida para todos los brazos
posterior    usar Z para controlar dónde voy y qué experiencia obtengo
```

# El control principal, normalizado

```
FIXED-DEPTH-1 (retención de un tick, SUMINISTRADA)    0.1468 / 0.3427 = 42.8 %
techo con historia suficiente                          0.3154 / 0.3427 = 92.0 %
margen de la adquisición                               ~49 puntos
```

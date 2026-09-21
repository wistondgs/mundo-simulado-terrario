# Agente Nivel 1.7 · cierre formal

```
┌───────────────────────────────────────────────────────────┐
│  PREDECESOR = SATURADO        ADQUISICIÓN 1.7 = PENDIENTE │
└───────────────────────────────────────────────────────────┘
```

**Fecha:** 2026-09-20 · **Veredicto:** `POSITIVO` · 16/16 pares · 13/13 gates
Oráculo `ac12cc3` intacto · protocolo V2 `1ca4b38` · campaña `4b6b325`

---

## 1 · La pregunta

> ¿Qué información adicional sobre la consecuencia aporta saber qué comando emití,
> por encima de todo lo que el ser ya sabía por temporalidad sola?

## 2 · Sustrato suministrado

```
cuerpo · física del Nivel 1.0 sin modificar
S0 · fuente motora endógena con su PRNG propio, serializable
el cableado φ · biyección comando→actuador por semilla, invisible al aprendiz
la copia eferente opaca · un campo, el comando, anterior a la transición
la factorización (O,A) → O' como HIPÓTESIS ESTRUCTURAL
el prior C_0 = N_16/4 · la regla de actualización
el par de mundos A/B · toda la instrumentación
```

## 3 · Lo heredado, y lo adquirido

```
HEREDADO    el MECANISMO de 1.6, instanciado en W como M_0^W y congelado
            NO una tabla de otro mundo: H(O'|O) varía 0.5623–1.5464 entre mundos,
            luego una tabla forastera es un baseline arbitrariamente sesgado

ADQUIRIDO   C_17(O, A, O') · las desviaciones específicas por acción respecto de
            la expectativa temporal previa

NO ADQUIRIDO   la relevancia causal o general del concepto «acción»
```

## 4 · El mundo · y su gemelo exacto

```
A    física del 1.0 · grid 7 · wall_probability 0.25 · D_W^A > 0
B    T_B(s'|s,a) = ¼ Σ_b T_A(s'|s,b)              · D_W^B = 0 EXACTAMENTE
```

Verificado al nivel del kernel de **estados**: misma topología, misma dinámica
marginal, misma estacionaria, `I(O;O')` idéntica a `0.00e+00`, y `I_B(A;O'|O) = 0`.
El azar del efecto de B es propio, serializable, y jamás compartido con S0.

## 5 · Controles

```
NO-ACTION          parte de M_0^W y SIGUE aprendiendo P(O'|O) en la fase A,
                   sobre las mismas transiciones, sin el comando
SHUFFLED-ACTION    (O_t, A_{π_o(t)}, O_{t+1}) · π dentro de cada estrato de O_t
FALSE-ACTION       K_T intacto, token falso en POST
MUNDO B            el gemelo action-null
```

`NO-ACTION` **no es `M_0^W`**, y ésa fue la corrección que salvó el diseño: contra
`M_0^W` congelado aparece una ventaja falsa que crece con el presupuesto, porque
`M_1` recibe datos que el predecesor congelado no vio.

## 6 · Métricas

```
D_W          I(A;O'|O) del mundo, desde la topología · oráculo analítico por semilla
D_E          rate · total · cobertura ponderada C_OA · recuentos N(o,a)
D_K^action   ε_NA − ε_A · conocimiento interno atribuible al comando
D_C          L_POST(NO-ACTION) − L_POST(M_1)
Γ            D_C^A − D_C^B                       ENDPOINT PRIMARIO

CI95_inferior = media(Γ) − 1.96 · sd(Γ, ddof=1) / √16      unidad: el par A/B
```

## 7 · Resultados

Semillas `170000011…170000026`, consecutivas, **cero saltadas**, 48 sin consumir.

```
Γ            media +0.280587   sd 0.036078   mín +0.221686   máx +0.342515
             CI95 inferior  +0.262909                CRITERIO PRIMARIO CUMPLIDO
             positivas 16/16
D_C^A        +0.278808   16/16 positivas
D_C^B        −0.001779    0/16 positivas
D_K^action A +0.281128   16/16 positivas
D_K^action B −0.001863
D_W^A        +0.927337

Γ/D_W        0.3024 ± 0.0165        r(D_W, Γ) = +0.9107
```

Las vidas **no aprenden una cantidad arbitraria**: adquieren una fracción estable
de lo que cada mundo ofrece.

Concordancia interna/externa: `D_K^action` +0.281128 contra `D_C^A` +0.278808 —
0.0023 nats de diferencia entre dos instrumentos distintos.

## 8 · Intervención causal

```
lesionar C_17 → la pérdida sube a 1.2261 en media
restaurar     → vuelve EXACTAMENTE al valor con estado        16/16
M_0^W intacto tras la lesión                                  16/16
```

Y el invariante que hace incremental la arquitectura:

```
C_17 = 0     ⇒  M_1(o,a) = M_0^W(o)   para toda acción, bit a bit
C_17 → 0     ⇒  vuelve a M_0^W, no a la ignorancia uniforme
```

**Lesionar 1.7 devuelve al ser exactamente a su competencia de 1.6.**

## 9 · Nulos y exclusiones

```
saltadas por condición física anterior a la vida     0
excluidas por resultado incómodo                     0 · está prohibido
pares en el denominador                             16 de 16
```

`170000024` y `170000026` tienen cobertura incompleta —`C_OA` 0.938 y 0.976, con al
menos un contexto informativo nunca visitado— y **no fueron excluidas ni tratadas
aparte**. `L17-6` no falló por ellas, que es para lo que se construyó así.

Lectura precisa: **no** «la exposición estaba completa», sino *la adquisición
sobrevivió con huecos locales de exposición*.

## 10 · Desviaciones

**La campaña V1 sobre `160000011…160000026` fue declarada INVÁLIDA por `D-4`.**

```
D-1  8 permutaciones por vida donde el protocolo exigía 32
D-2  agrupadas entre vidas
D-3  sólo 6 de 16 vidas contribuyeron
D-4  campaign.py ejecutaba CERO de los trece gates; el «13/13» se construyó
     íntegramente en un script escrito DESPUÉS de abrir las semillas
```

No se rescató. Sus datos quedan archivados como **piloto/diagnóstico fallido** y
**no se suman** al tamaño de muestra ni al argumento confirmatorio. La reparación
V2 fue mínima: `L17-8` dentro del runner, por vida, con 32 propias; ledger de los
trece; meta-verificador de integridad. Ninguna otra pieza cambió.

El método del intervalo estaba **infra-especificado** en `ac12cc3` —fijaba la
unidad, no la fórmula— y V2 congeló literalmente la que se había ejecutado, para no
cambiar el criterio después de ver resultados.

## 11 · Qué demuestra

> El Agente Nivel 1.7 adquirió, a partir de su propia experiencia, una
> representación predictiva de cómo las consecuencias sensoriales dependen de la
> acción que acaba de ejecutar, aportando información por encima de la estructura
> temporal heredada de Nivel 1.6. Esa ventaja desaparece cuando se elimina o
> destruye la correspondencia con la acción, no aparece en el mundo gemelo donde la
> acción es informativamente irrelevante, y depende causalmente del estado
> incremental adquirido; al lesionar ese estado, el organismo vuelve exactamente a
> su competencia de Nivel 1.6.

Cláusula por cláusula, contra los datos archivados:

| cláusula | evidencia |
|---|---|
| adquirió de su propia experiencia | `D_K^action` +0.2811 · 16/16 |
| por encima de la estructura heredada | `D_C^A` vs NO-ACTION +0.2788 · 16/16 |
| desaparece si se destruye la correspondencia | baraja +0.0048 · destructiva 16/16 |
| desaparece si se falsifica el canal | falso −0.0308 · negativa 16/16 |
| no aparece en el gemelo | `D_C^B` −0.0018 · positivas 0/16 |
| depende causalmente del estado | lesión → 1.2261 · restaura exacta 16/16 |
| vuelve exactamente a 1.6 | `M_0^W` intacto 16/16 |

Acompañada **siempre** de las dos etiquetas de régimen.

## 12 · Qué NO demuestra

```
que el organismo descubriera que la acción importa
     la factorización (O,A)→O' es SUMINISTRADA
razonamiento causal · intención · elección deliberada
control orientado a objetivos · asignación de crédito
curiosidad · autorregulación · distinción de correlación espuria
exploración dirigida · memoria selectiva · agencia fuerte
adquisición eficiente bajo experiencia escasa
```

Sobre lo último: `T_17 = 1024` está **en pendiente** (`D_K^action/D_W` ≈ 0.62 en
calibración) y no en saturación, así que lo medido es adquisición **en curso** —
pero eso no es lo mismo que haber demostrado eficiencia con pocos datos.

## 13 · El hallazgo metodológico, separado del confirmatorio

Demostrado en calibración, `T_17 = 1024` fijo:

```
T_P = 256    Γ ≈ +0.7736      T_P = 1024   Γ ≈ +0.5467      T_P = 4096   Γ ≈ +0.2755
D_W = 0.8817 idéntico en los tres · ΔD_W = 0.00e+00
ΔΓ(4096−1024) = −0.2712 en 16/16 · ΔD_K^action = −0.2709
```

> Un predecesor temporal más consolidado reduce cuánto puede desviarse el modelo
> condicionado por acción durante un presupuesto fijo de 1.7.

**No es un fracaso de 1.7.** La calibración a `T_P = 4096` predijo el confirmatorio
con 0.004 nats.

# `LEVEL1.8-PREDICTIVE-STATE-01` · oráculo preregistrado

```
┌──────────────────────────────────────────────────────────────┐
│   SELLADO ANTES DE ESCRIBIR EL LEARNER                       │
│   no existe terrario/level18/ · ni una línea del organismo   │
└──────────────────────────────────────────────────────────────┘
```

**Fecha:** 2026-09-20 · base `eaf9d26` (adjudicación de 1.8, sobre el cierre
congelado de 1.7) · campaña confirmatoria **no corrida**
Ventana confirmatoria `180000011…180000074` **virgen y sin abrir**.

**Esto es lo que 1.7 no pudo hacer:** allí el oráculo precedió a los gates pero no
a la arquitectura. Aquí precede a todo. Si la implementación obliga a cambiar algo,
se emite enmienda fechada — nunca se reescribe este documento.

---

# 1 · La pregunta

> ¿Puede el organismo adquirir, de su propia historia sensoriomotora, una
> representación interna que desambigüe situaciones perceptualmente idénticas
> cuyas consecuencias ante la misma acción son distintas?

# 2 · Genealogía y estado de la adjudicación

```
1.6/A1     estructura temporal            DEMOSTRADA · exposición saturada
1.7/C_17   contingencia acción→efecto     DEMOSTRADA · predecesor saturado
1.8/C_18   estado predictivo sensoriomotor   ← lo que este oráculo pone a prueba
```

Relación con el predecesor, **ya medida** (`docs/level18/CIERRES_DE_DISENO.md` §5):

```
C_17 aumenta causalmente la EFICIENCIA MUESTRAL de C_18
    T_18=64  4.89×   ·  256  3.64×  ·  1024  2.03×  ·  4096  1.13×
NO es condición necesaria: sin C_17 converge igual, más despacio
```

**El canal «C_17 ayuda a decidir cuándo separar» NO está testeado y NO entra en
ningún claim de este oráculo.**

# 3 · El recurso informativo existe · medido antes de sellar

```
H(O'|O,A)   bajo p_ref, 16 mundos                   0.3427 nats   ← el hueco
H(O'|C,A)   si se supiera la celda                  0.0000 nats   ← techo absoluto

G_hist(L)   L=1  42.8 %   L=2  70.6 %   L=8  91.3 %   L=16  92.0 % del hueco
            calculado EXACTO sobre creencias, sin sesgo de estimador

la desambiguación es SENSORIOMOTORA: a L=1 el comando propio aporta
0.1371 de 0.1468 nats, el 93 %. Sólo observaciones recupera 0.0097.

tratabilidad   contextos crudos a L=8   4.5·10¹⁵   tabla imposible
               creencias que ocurren      ~24       celdas del mundo ~17
```

# 4 · La vida · tres fases · S0 INTACTO

```
mundo W
  ├── P0 · 4096 pasos · el mecanismo de 1.6 adquiere M_16^W   FREEZE
  ├── P1 · 1024 pasos · el mecanismo de 1.7 adquiere C_17^W   FREEZE
  ├── A  · T_18 pasos · el mecanismo de 1.8 adquiere C_18
  └── POST · 2048 transiciones generadas por S0 · idéntico para TODOS los brazos
```

`P0` y `P1` **heredan los presupuestos que 1.7 selló**; no se vuelven a decidir.

> **S0 no se toca.** `C_18` **no puede** modificar la política. Por tanto la
> **paridad de trayectoria del linaje sobrevive**: todos los brazos viven
> literalmente la misma vida y el hash lo demuestra. `CONTROL_CAUSAL_POLITICA_
> ENDOGENA.md` queda en reserva, sin gastarse.

# 5 · Sustrato suministrado · y la frontera

```
SUMINISTRADO
    cuerpo · física del 1.0 · S0 con su PRNG · cableado φ · copia eferente opaca
    M_16^W y C_17^W congelados
    un mecanismo genérico de estado secuencial   Z_{t+1} = F(Z_t, A_t, O_{t+1})
    capaz de crear, separar y fusionar estados por evidencia predictiva
    el prior de composición y la regla de actualización

ADQUIRIDO
    la organización concreta que agrupa historias sensoriomotoras en los
    contextos predictivamente distintos DE ESTE MUNDO, y su contenido predictivo

NO ADQUIRIDO
    coordenadas · identidad de celda · mapa · la noción de «lugar»
```

## 5.1 · Prohibiciones estructurales

```
PROHIBIDO  coordenadas (x,y) · cell id · cualquier etiqueta física
PROHIBIDO  NUM_LATENT_STATES = 17 · 24 · o el número verdadero de cualquier mundo
PROHIBIDO  MAX_STATES, SPLIT_THRESHOLD, MERGE_THRESHOLD ajustados mirando el
           resultado — es conocimiento humano mejor escondido que una constante
PROHIBIDO  que el learner importe, llame o lea nada de `oracle/`
PERMITIDO  un criterio general (MDL, bayesiano, test estadístico) como MECANISMO,
           con sus constantes DECLARADAS EN ESTE DOCUMENTO o en enmienda fechada
           anterior a la calibración, jamás elegidas para reconstruir esta rejilla
```

**Prueba de que la partición no fue suministrada**, y es medible: el **mismo
código**, en mundos con multiplicidad latente distinta, debe terminar con
organizaciones internas distintas. Si no varía, se la dimos.

# 6 · Los invariantes de incrementalidad

```
CONSERVACIÓN DE MASA        Σ_z C_0(o,a,o' | z)  =  C_17(o,a,o')
```

Separar, fusionar o crear estado **nunca puede fabricar ni destruir evidencia
heredada**. El reparto `C_17/k` es *una* forma de conseguirlo; lo que se congela es
la conservación, no el `/k`.

```
LESIÓN        C_18 → 0 · Z colapsa a {z_0}
              ⇒  P_18(O'|O,A,z_0) = P_17(O'|O,A)   EXACTAMENTE, bit a bit
              ⇒  el organismo vuelve a 1.7 + S0, NO a la ignorancia
```

# 7 · Brazos y controles

```
FULL             C_17 congelado + C_18 adquirido
C17-ONLY         el modelo de 1.7 sin estado                     ← baseline del endpoint
FIXED-DEPTH-1    retención de un tick SUMINISTRADA, sin aprender partición
O-HISTORY-ONLY   estado construido sólo de observaciones, sin comandos
C17-LESION       C_18 con la MISMA historia O+A pero prior plano en vez de C_17
ORACLE-CELL      la celda verdadera · TECHO · jamás accesible al learner
```

Los seis comparten **la misma vida** y el mismo banco POST.

## 7.1 · El null que este nivel trae de nacimiento

No hace falta un mundo gemelo: el nulo vive **dentro** de cada mundo.

```
contextos donde k_o = 1  (la observación no es ambigua)
    ahí NO hay nada que desambiguar
    si C_18 «mejora» ahí, está inventando distinciones
```

# 8 · Métricas y endpoint

```
ENDPOINT PRIMARIO     ΔL = L_POST(C17-ONLY) − L_POST(FULL)
                      mismo banco POST · misma trayectoria · unidad = la vida/mundo
                      criterio:  CI95_inferior( media de ΔL )  >  0
                      CI95_inferior = media − 1.96·sd(ddof=1)/√N      ← fijado aquí
```

Acompañado, como caracterización y **no** como criterio:

```
fracción del hueco de aliasing recuperada     ΔL / 0.3427
margen sobre FIXED-DEPTH-1                    L_POST(FD1) − L_POST(FULL)
margen sobre O-HISTORY-ONLY                   L_POST(OHO) − L_POST(FULL)
distancia al techo                            L_POST(FULL) − L_POST(ORACLE-CELL)
eficiencia debida al predecesor               L_POST(C17-LESION) − L_POST(FULL)
```

# 9 · Los dieciséis gates

| gate | certifica |
|---|---|
| **L18-0** `LINEAGE` | `level1`, `level16`, `level17` presentes y congelados; nada posterior en el disco |
| **L18-1** `INHERITED-FROZEN` | huellas de `M_16^W` y `C_17^W` intactas tras la fase A |
| **L18-2** `ACTION-PROVENANCE` | todo acto salió de S0; `C_18` no toca la política |
| **L18-3** `EFFERENCE-PURITY` | comando opaco anterior a la consecuencia, y nada más |
| **L18-4** `MASS-CONSERVATION` | `Σ_z C_0(·\|z) = C_17` tras cada creación, separación y fusión |
| **L18-5** `INCREMENTAL-INVARIANT` | `C_18 = 0 ⇒ P_18 = P_17` bit a bit; la lesión devuelve a 1.7 |
| **L18-6** `NO-SUPPLIED-PARTITION` | ninguna constante de conteo de estados; misma código → organización distinta entre mundos |
| **L18-7** `NO-ORACLE-LEAKAGE` | el learner no importa ni nombra celda, coordenada ni `oracle/` |
| **L18-8** `TRAJECTORY-PARITY` | los seis brazos comparten la vida, por hash |
| **L18-9** `EXPOSURE` | instrumentos medidos y consistentes · **cobertura baja NO falla** |
| **L18-10** `PREDICTIVE-DISAMBIGUATION` | el endpoint cumple el criterio primario |
| **L18-11** `NOT-EXPLAINED-BY-DEPTH-1` | `FULL` supera a `FIXED-DEPTH-1` |
| **L18-12** `NOT-EXPLAINED-BY-OBSERVATIONS` | `FULL` supera a `O-HISTORY-ONLY` |
| **L18-13** `NULL-CONTEXT` | `C_18` no inventa distinciones donde `k_o = 1` |
| **L18-14** `INTERNAL-LOCALIZATION` | lesionar `C_18` cuesta competencia y restaurarlo la recupera exactamente |
| **L18-15** `PASSIVITY-REPLAY` | evaluar no modifica al ser; la vida y su replay son deterministas |

**Cada gate nace con su falsificador real**, que debe fallar por la causa que el
gate afirma controlar — nunca por `AttributeError`, aserción tautológica, o un mock
que rompe también el control.

## 9.1 · La lección `D-4` se hereda entera

```
el runner confirmatorio ejecuta LOS DIECISÉIS y los registra en un ledger
verify_ledger es obligatorio ANTES de emitir veredicto, y fatal ante:
    cualquier gate ausente
    cualquier gate evaluado fuera de la ruta congelada
```

En 1.7 el runner ejecutó **cero** de sus trece y el «13/13» se construyó en un
script posterior a abrir las semillas. No vuelve a ocurrir por construcción.

# 10 · Presupuesto `T_18` · regla, no número

**No se fija aquí, y no se elegirá mirando dónde el efecto sale mayor.**

```
REGLA    calibrar sobre 150000011…150000026 y elegir el MENOR T tal que
         (a) FIXED-DEPTH-1 queda batido con margen ≥ 2 sd entre vidas
         (b) la adquisición NO ha saturado:  ΔL / 0.3427  <  0.90
         (c) la cobertura de contextos informativos no es el cuello de botella
         empate  →  el menor T
```

El `T_18` resultante se sella en **enmienda fechada antes de tocar ninguna semilla
confirmatoria**. La regla está fijada ahora; su salida la decide el dato.

`P0 = 4096` y `P1 = 1024` se heredan sellados de 1.7 y no se recalibran.

# 11 · Semillas

```
calibración        150000011 … 150000026    ya consumidas en la adjudicación
confirmatorias     180000011 … 180000074    64 · VÍRGENES · verificadas en 260 commits
```

Consumo ascendente, sin saltos, hasta 16 vidas físicamente válidas. **Sólo una
condición estructural anterior a la vida provoca reemplazo.** Jamás se sustituye
una vida porque `ΔL` sea pequeño, porque un control incomode, porque la exposición
sea baja o porque el resultado salga negativo: esa vida pertenece al denominador.

# 12 · Taxonomía del resultado

```
INVÁLIDO             gate roto, fuga, o gate evaluado fuera de la ruta · anula la campaña
N-MUNDO              sin aliasing alcanzable: k_o = 1 en todo el componente
                     ⇒ no había nada que desambiguar
N-EXPERIENCIA        había aliasing, la vida no dio bastante para separarlo
                     ← evidencia sobre S0, NO sobre C_18
N-PLASTICIDAD        experiencia suficiente, el mecanismo no creó estado alguno
NEGATIVO VERDADERO   creó estado, la información estaba, y aun así no mejora
POSITIVO             desambigua, supera a los cuatro controles, y la lesión devuelve a 1.7
```

# 13 · Condiciones de invalidez

```
ADVANCED_CAPABILITY_DEPENDENCY      INHERITED_NOT_FROZEN
POLICY_MODIFIED_BY_C18              TRAJECTORY_PARITY_FAILED
EFFERENCE_CARRIES_CONSEQUENCE       MASS_NOT_CONSERVED
INCREMENTAL_INVARIANT_BROKEN        LESION_TOUCHES_INHERITED
SUPPLIED_PARTITION                  STATE_COUNT_CONSTANT_PRESENT
ORACLE_LEAKAGE                      THRESHOLD_TUNED_ON_RESULT
GATE_EVALUATED_OUTSIDE_RUNNER       LEDGER_INCOMPLETE
EVALUATION_NOT_PASSIVE              TRAJECTORY_NOT_REPRODUCIBLE
```

# 14 · Afirmación máxima autorizada, si pasa

> El Agente Nivel 1.8 adquirió, únicamente de su propia historia de observaciones y
> comandos, una organización interna que distingue situaciones perceptualmente
> idénticas cuyas consecuencias ante la misma acción difieren, y que predice esas
> consecuencias mejor que el modelo de Nivel 1.7 sobre el mismo futuro no visto. La
> ventaja no se explica por retener un solo paso, ni por la historia de
> observaciones sin los comandos propios, y desaparece al lesionar el estado
> adquirido, que devuelve al organismo exactamente a su competencia de Nivel 1.7.

**No se afirma:** localización física, mapa, coordenadas, noción de lugar, memoria
general, navegación, retorno, inferencia causal, intención, valor, búsqueda,
curiosidad ni política endógena. `C_18` **no puede** modificar S0 en este nivel.

**Y sobre el predecesor**, sólo lo medido: `C_17` aumenta la **eficiencia muestral**
de `C_18`, no su posibilidad.

# 15 · El libro de suministro

```
SUMINISTRADO   cuerpo · S0 · φ · copia eferente · M_16^W y C_17^W congelados
               mecanismo genérico de estado · regla de actualización
               prior de composición con conservación de masa
               instrumentación · oráculos · los cinco controles

ADQUIRIDO      la partición de historias sensoriomotoras en contextos
               predictivamente distintos, y su contenido

NO ADQUIRIDO   dónde está · qué lugar es · adónde ir · qué conviene
```

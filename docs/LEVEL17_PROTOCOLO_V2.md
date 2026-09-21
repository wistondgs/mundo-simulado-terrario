# `LEVEL1.7` · protocolo confirmatorio **V2**

```
┌───────────────────────────────────────────────────────────┐
│  PREDECESOR = SATURADO        ADQUISICIÓN 1.7 = PENDIENTE │
└───────────────────────────────────────────────────────────┘
```

**Fecha:** 2026-09-20 · **V1 = INVÁLIDA POR D-4** · campaña V2 **no corrida**
**El oráculo `ac12cc3` no se reescribe.** Este documento es aditivo y separado.

---

# 1 · Qué falló · con el código a la vista

`ac12cc3` §7 selló:

```
línea 177   32 permutaciones estratificadas de la vida de B → distribución nula de D_C^B
```

«de **la** vida de B», singular: **32 por vida**.

Lo que la ruta confirmatoria ejecutó en realidad:

```
gate_null_world(report, observed, null_samples)   RECIBE la nula; no la genera
campaign.py  ->  gates ejecutados: NINGUNO        ← leído del AST del runner V1
campaign.py  ->  NULL_REPLICAS = 32 usado sólo en shuffled.audit, que es L17-9
```

Los trece gates se calcularon en un script ad-hoc escrito **después** de abrir las
semillas, y la nula de `L17-8` en ese script fue `for p in P[:6]` × `for k in
range(1,9)` = 48 muestras agrupadas.

```
D-1   8 permutaciones por vida donde el protocolo exigía 32
D-2   agrupadas entre vidas en vez de una nula por vida
D-3   sólo 6 de las 16 vidas contribuyeron
D-4   campaign.py ejecutaba CERO de los trece gates
```

**Corrección a mi propio informe anterior:** dije que el runner «no evaluaba
`L17-8`», lo que daba a entender que sí evaluaba los otros doce. **Ejecutaba
cero.** El «13/13» de V1 se construyó íntegramente fuera de la ruta congelada.

# 2 · Por qué V1 es inválida

No es negativa ni demostrativa. La validez prospectiva exige que el criterio se
aplique por una ruta fijada **antes** de ver los datos, y en V1 ninguna parte del
criterio vivía en esa ruta.

```
campaña 160000011…160000026   PILOTO / DIAGNÓSTICO POST-CONFIRMATORIO FALLIDO
                              no se reutiliza como confirmatoria
                              NO se «rescata» recalculando ahora las 32 correctas
```

Sus números quedan archivados en `resultados/confirmatorio_16_pares.json` y en
`docs/LEVEL17_AUDITORIA_PRE_CIERRE.md`, etiquetados como piloto.

# 3 · La única reparación metodológica

**La hipótesis científica no cambia.** Permanecen idénticos, sin una línea de
diferencia: el aprendiz, `T_P = 4096`, `T_17 = 1024`, el mundo A, el mundo B,
`NO-ACTION`, `SHUFFLED-ACTION`, `FALSE-ACTION`, el endpoint `Γ`, `N = 16`, las
definiciones de `D_W, D_E, D_K, D_C`, la lesión, la regla de consumo y el
significado de los trece gates.

Lo que cambia, y nada más:

```
1 · L17-8 se ejecuta DENTRO de campaign.py, una vez POR VIDA, con 32
    permutaciones estratificadas de esa misma vida B

2 · el runner ejecuta y registra los TRECE en un ledger explícito

3 · un meta-verificador de infraestructura hace fatal cualquier hueco
```

## 3.1 · Nota de diseño declarada, no asumida

La adjudicación pedía pasar los 32 al `gate_null_world()` **existente**, y también
detectar agrupamiento entre vidas y ausencia de nulas. Eso no cabe dentro de ese
gate sin cambiarle la firma. Resuelto como la propia adjudicación lo clasifica
—*reparación de infraestructura, no gate científico nuevo*—: el gate queda
**intacto** y decide; `verify_ledger` comprueba procedencia, conteo y completitud.

```python
REQUIRED_GATES = ("L17-0", …, "L17-12")

verify_ledger(ledger, seeds)  ->  LedgerIncomplete si
    falta cualquiera de los trece
    L17-8 no aparece exactamente una vez por vida
    alguna nula no tiene exactamente 32 muestras
    alguna nula mezcla semillas
```

## 3.2 · Los dos nulos de B siguen separados

```
L17-1   ¿construimos bien el mundo B?      I_B(A;O'|O) = 0 desde el kernel
        Un B roto levanta WORLD_PAIR_CONSTRUCTION_FAIL **antes de vivir**,
        y por tanto no llega a L17-8 a disfrazarse de problema del aprendiz.

L17-8   dado un B correcto, ¿el aprendiz inventa ventaja?
        Contra su propia nula de 32, por vida.
```

# 4 · El intervalo, ahora explícito

`ac12cc3` fijó la **unidad** (`intervalo pareado por mundo`) y no el **método**.
V2 congela literalmente el que se ejecutó, para no cambiar el criterio después de
haber visto resultados:

```
CI95_inferior  =  media(Γ)  −  1.96 · sd(Γ, ddof=1) / sqrt(16)
unidad         =  el par A/B por mundo · NUNCA la transición
```

Student y bootstrap podrán reportarse **como sensibilidad**, jamás como el gate.

# 5 · Ventana confirmatoria V2

```
170000011 … 170000074      64 reservadas · VÍRGENES
```

Verificado antes de reservarla, y **sin ejecutar ningún descriptor sobre ella**:

```
código, tests, scripts, docs, datos     0 apariciones
historial completo (244 commits)        0 semillas del rango
   las coincidencias de "170000" son dígitos dentro de literales flotantes
   del otro linaje del repositorio, p. ej. 0.0967170000076294
```

Las `160…` quedan contaminadas y no se reutilizan.

# 6 · Regla de consumo · sin cambios

Ascendente, sin saltos, hasta 16 pares físicamente válidos. **Sólo** una condición
estructural anterior a la vida reemplaza. Nunca se sustituye una vida porque `Γ`
sea pequeño, `D_K^action` sea pequeño, B resulte incómodo, `SHUFFLED` falle, la
exposición sea baja o el resultado salga negativo. Un defecto de construcción A/B
**anula la campaña**; no reemplaza la semilla.

# 7 · Fixtures de la reparación · las nueve exigidas

| exigida | fixture | falla por |
|---|---|---|
| runner sin `L17-8` | `test_un_runner_sin_L17_8_es_fatal` | `LedgerIncomplete` |
| 31 permutaciones | `test_una_nula_que_no_sea_de_32_es_fatal[31]` | conteo |
| 33 permutaciones | `…[33]` | conteo |
| 32 agrupadas entre vidas | `test_una_nula_de_32_pero_mezclada_entre_vidas_es_fatal` | procedencia |
| sólo algunas vidas | `test_si_solo_algunas_vidas_tienen_nula_es_fatal` | cobertura |
| permutación que rompe `Counter((O,A))` | `test_una_permutacion_que_no_conserva_Counter_OA…` | la global lo rompe, la estratificada no |
| B roto → `L17-1`, no `L17-8` | `test_un_B_estructuralmente_roto_muere_en_L17_1_antes_de_vivir` | `WORLD_PAIR_CONSTRUCTION_FAIL` |
| B correcto, aprendiz positivo → `L17-8` | `test_un_aprendiz_que_mira_la_consecuencia_lo_captura_L17_8` | `WORLD_B_OR_MODEL_NULL_FAIL` |
| baraja identidad | `test_la_baraja_identidad_falla_por_SHUFFLE_NOT_DESTRUCTIVE` | `destructiva False` |

Más `test_un_runner_al_que_le_falte_cualquier_gate_es_fatal`, que recorre los trece
uno a uno, y `test_el_runner_ejecuta_los_trece_dentro_de_la_ruta`.

**Una fixture se escribió mal y se corrigió:** la del aprendiz que filtra. La
primera versión filtraba sólo en **entrenamiento**, así que al puntuar con el
comando real las filas no correspondían y el modelo salía **peor** (`−0.3036`). Una
fuga que no está en consulta no infla nada. La versión válida fuga donde importa.

# 8 · El hallazgo sobre `T_P` · resultado metodológico, separado del confirmatorio

Demostrado sobre calibración, `T_17 = 1024` fijo:

```
T_P = 256    Γ ≈ +0.7736     Γ/D_W 0.878
T_P = 1024   Γ ≈ +0.5467     Γ/D_W 0.620
T_P = 4096   Γ ≈ +0.2755     Γ/D_W 0.313

D_W = 0.8817 idéntico en los tres          ΔD_W = 0.00e+00
ΔΓ(4096−1024) = −0.2712  en 16/16          ΔD_K^action = −0.2709
```

Conclusión permitida, y sólo ésta:

> Un predecesor temporal más consolidado reduce cuánto puede desviarse el modelo
> condicionado por acción durante un presupuesto fijo de 1.7.

**No es un fracaso de 1.7.** La calibración a `T_P = 4096` predijo el efecto del
piloto con 0.004 nats: `+0.2755` contra `+0.2794`.

# 9 · Engineering freeze al abrir la primera semilla V2

Después de `170000011`: nada de gates nuevos, métricas nuevas, réplicas distintas,
tolerancias corregidas, aprendiz modificado, presupuestos, endpoint, fixtures ni
selección de semillas. Un defecto de infraestructura declara **V2 INVÁLIDA**, se
detiene y se reporta. No se repara sobre la marcha.

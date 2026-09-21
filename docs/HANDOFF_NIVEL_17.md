# Handoff · Agente de Nivel 1.7

Desviaciones específicas por acción, sobre la estructura temporal de 1.6.
Para quien vaya a construir el decimal siguiente.

```
árbol   /home/wis/level17-action-contingency-01
rama    experiment/level17-action-contingency-01
base    c2b808b   cierre de 1.6
estado  CONGELADO · C_17 = DEMOSTRADA
        PREDECESOR = SATURADO · ADQUISICIÓN 1.7 = PENDIENTE
```

---

# 0 · Lee esto antes de escribir una sola línea

**Un decimal, una adquisición.** 1.7 añade exactamente `C_17(O,A,O')`: las
desviaciones por acción respecto de lo que el ser **ya sabía de ese mismo mundo**.

**Se hereda el mecanismo, no una tabla.** `H(O'|O)` varía entre 0.5623 y 1.5464
según el mundo: llevar una tabla de `W₁` a `W₂` no da un baseline neutro sino uno
arbitrariamente sesgado. El ser entra en `W` con la capacidad de 1.6 como
arquitectura y estado neutro, vive la fase P, adquiere `M_0^W`, y **se congela**.

**El aislamiento es estructural.** El árbol arranca del cierre de 1.6: `level1` y
`level16` están en el disco; `level11…14`, `organism` y `remembered` **no**.

**El oráculo se sella antes del confirmatorio y no se edita.** Y si algo falla, se
emite protocolo nuevo fechado — nunca se reescribe el anterior.

**Nunca `git add -A`. Un commit por trabajo. No push, no merge.**

---

# 1 · La lección más cara de este nivel

**La primera campaña confirmatoria fue INVÁLIDA**, y no por ciencia sino por
infraestructura:

```
campaign.py de V1  →  ejecutaba CERO de los trece gates
el «13/13» se construyó en un script escrito DESPUÉS de abrir las semillas
la nula de L17-8 en ese script: 6 vidas × 8 permutaciones, agrupadas
```

El oráculo pedía 32 **por vida**. Nada de eso vivía en la ruta congelada.

**Qué hay que llevarse de aquí, y vale más que el resultado:**

> Un criterio que no se ejecuta **dentro** de la ruta fijada antes de ver los
> datos no es un criterio preregistrado, aunque su número sea correcto.

V1 dio `Γ = +0.2794` y V2 dio `+0.2806`. La coincidencia **no** rescata V1: lo
único que dice es que la invalidación no costó señal, sólo validez prospectiva —
que era exactamente lo que había que reconstruir.

La defensa que quedó, y que conviene heredar:

```python
REQUIRED_GATES = ("L17-0", …, "L17-12")

verify_ledger(ledger, seeds)  ->  LedgerIncomplete si
    falta cualquiera de los trece
    L17-8 no aparece exactamente una vez por vida
    alguna nula no tiene exactamente 32 muestras
    alguna nula mezcla semillas
```

Obligatoria **antes** de emitir veredicto, fatal ante cualquier hueco, e
independiente del signo del resultado.

---

# 2 · La arquitectura incremental · lo que más merece copiarse

```
C_0(o,a,o')  =  N_16(o,o') / 4                 prior simétrico entre comandos

P_17(o'|o,a) =  [ N_16(o,o')/4 + C_17(o,a,o') ]
                ─────────────────────────────────
                Σ_v [ N_16(o,v)/4 + C_17(o,a,v) ]
```

Con `C_17 = 0` el cuarto se cancela arriba y abajo y queda exactamente
`P_16(o'|o)`. De ahí los dos invariantes, verificados **bit a bit**:

```
nacimiento   C_17 = 0   ⇒  M_1(o,a) = M_0^W(o)  para toda a    dif 0.000e+00
lesión       C_17 → 0   ⇒  vuelve a M_0^W, NO a uniforme
```

> **Lesionar 1.7 devuelve al ser a 1.6, no a la ignorancia.** Ésa es la clase de
> arquitectura incremental que conviene mantener en los decimales siguientes:
> quitar la capacidad nueva no destruye al organismo, lo retrocede un peldaño.

`M_0^W` se guarda como copia con huella y `inherited_is_intact()` lo comprueba: el
componente nuevo no puede tocarlo ni por accidente.

---

# 3 · `NO-ACTION` · el baseline que casi eliminamos

La adjudicación inicial decía que `NO-ACTION` era «prácticamente `M_0`» y candidato
a eliminarse. **La medición lo contradijo y ése fue el hallazgo que salvó el
diseño.**

```
                      D_C vs M_0^W congelado   D_C vs NO-ACTION
mundo B, T_17=256            +0.0254               −0.0108
mundo B, T_17=1024           +0.0752               −0.0109
mundo B, T_17=4096           +0.1053               −0.0067
```

En B no hay información de acción y aun así `D_C` contra el predecesor **congelado**
sale positivo y **crece con el presupuesto**: `M_0^W` se congela al acabar la fase
P y `M_1` recibe además todas las transiciones de la fase A.

```
D_C(vs M_0 congelado)  =  información de la acción  +  simplemente más datos
```

**`NO-ACTION` parte de `M_0^W` y sigue aprendiendo `P(O'|O)` durante la fase A**,
sobre las mismas transiciones, sin el comando. Es el único comparador que aísla la
acción.

El mismo confundido estaba en la métrica hermana y **no lo busqué**: `D_K` contra
el kernel verdadero mezclaba lo mismo. Corregido como `D_K^action = ε_NA − ε_A`.

---

# 4 · El par de mundos · gemelos físicos exactos

```
T_B(s'|s,a) = ¼ · Σ_b T_A(s'|s,b)      para toda a
```

Verificado al nivel del kernel de **estados**, no de una muestra:

```
[tautológico] T_B(·|s,a_i) == T_B(·|s,a_j)
[tautológico] Σ_a T_A/4 == Σ_a T_B/4
[prueba algo] I(O;O') conservada EXACTA        0.9356 → 0.9356
[prueba algo] I(A;O'|O) anulada                1.0678 → 0.000e+00
estacionaria idéntica · máx dif 0.00e+00
```

Las dos últimas no son obvias: el aliasing podía haber interactuado con la
marginalización. No lo hace. **B es idéntico a A en todo lo que 1.6 mide y no
lleva información de acción alguna.**

**El azar del efecto de B es propio (`[s,65]`), serializable, y jamás compartido
con S0** — si saliera del mismo azar que el comando podría fabricarse dependencia
comando–efecto justo en el mundo cuyo contrato es `D_W = 0`.

Y su detección funciona por grados:

```
B correcto            I_B(A;O'|O) = 0.0000
B con A0 intacta                    0.1617
B con A0+A2 intactas                0.3707
A completo                          0.8724
```

---

# 5 · La copia eferente · comando, y sólo comando, antes de la consecuencia

```python
@dataclass(frozen=True)
class EfferenceCopy:
    command: CommandToken        # UN campo. No hay dónde escribir `moved`.
```

Tres exigencias, las tres sobre lo que **no** lleva:

- es el **comando emitido**, no la acción ejecutada: `A_0` contra una pared sigue
  diciendo `A_0`, nunca «`A_0` que falló»;
- se genera **antes** de conocer `O_{t+1}`;
- el token es **opaco**: `A_0…A_3`, y la biyección `φ` a `UP/DOWN/LEFT/RIGHT` es
  por semilla y el aprendiz no la ve.

`CommandToken` es `Enum` y no `IntEnum`: tipos disjuntos, sin comparación
accidental con un índice de dirección.

**Las 24 permutaciones, medidas:** el mismo código adquiere las veinticuatro
correspondencias con sd **0.0134 nats** entre cableados, 24/24 positivas, y el
contenido aprendido difiere entre ellos. El contenido no vive en el token.

---

# 6 · Las cuatro magnitudes

```
D_W        I(A;O'|O) del mundo, desde la topología · oráculo analítico por semilla
D_E        rate · total · cobertura C_OA · recuentos N(o,a)
D_K^action ε_NA − ε_A · conocimiento interno atribuible al comando
D_C        L_POST(NO-ACTION) − L_POST(M_1)
Γ          D_C^A − D_C^B                              ENDPOINT PRIMARIO
```

**`D_E` partido en cuatro, y por qué.** `E_rate ≈ D_W` a 64 pasos **no** significa
que la exposición esté resuelta: es una tasa, mide densidad informativa de lo
visitado, no acumulación.

```
T_17   E_rate   C_OA    N mín
  64   0.8638   0.638     0.0     ← el contexto informativo mínimo: cero visitas
1024   0.8786   0.999     7.6
```

*Encuentra información* ≠ *ha acumulado muestras suficientes para aprenderla*.

**`Γ` explota el gemelo:** `A` mide lo que compra el comando cuando importa, `B`
mide el coste de tener cuatro veces más parámetros, y la resta lo cancela.

```
CI95_inferior = media(Γ) − 1.96 · sd(Γ, ddof=1) / √16    unidad: el par A/B
```

**El método del intervalo estaba infra-especificado en el oráculo** —fijaba la
unidad, no la fórmula— y el protocolo V2 congeló literalmente la ejecutada, para
no cambiar el criterio después de ver resultados. Student y bootstrap se reportan
como sensibilidad, nunca como gate.

---

# 7 · `SHUFFLED-ACTION` estratificado

```
(O_t, A_t, O_{t+1})  →  (O_t, A_{π_o(t)}, O_{t+1})     π DENTRO de cada estrato de O_t
```

Una permutación global destruiría también `P_L(O,A)`. Ésta conserva exactamente la
secuencia de `O_t`, la de `O_{t+1}`, las cuentas de acción por observación y el
tamaño de muestra — verificado por `Counter((O,A))` idéntico antes y después.

```
nula        32 permutaciones estratificadas independientes
tolerancia  null_mean + 4·sd          derivada, jamás un umbral fijo
```

**`32` está medido.** Con 8 réplicas la `sd` carga 26.7 % de error relativo y una
vida de dieciséis falla por 0.0002; con 16, 32 y 64 la tolerancia converge a
~0.0400 y pasan 16/16. El criterio estaba bien; lo que oscilaba era su estimador.

---

# 8 · Los trece gates

```
L17-0   LINEAGE                1.6 presente y congelado; nada posterior en el disco
L17-1   WORLD-PAIR             D_W^A > 0 y D_W^B = 0, desde el KERNEL FÍSICO
L17-2   ACTION-PROVENANCE      cada comando reconstruible desde S0
L17-3   EFFERENCE-PURITY       comando opaco, previo a la consecuencia, y nada más
L17-4   INCREMENTAL-INVARIANT  nacimiento y lesión, bit a bit
L17-5   BASELINE-PARITY        NO-ACTION y M_1 sólo difieren en el acceso al comando
L17-6   EXPOSURE               los instrumentos medidos y consistentes
L17-7   ACTION-ACQUISITION     Γ cumple el criterio primario
L17-8   NULL-WORLD             B no inventa ventaja · POR VIDA · 32 propias
L17-9   ACTION-NECESSITY       SHUFFLED y FALSE-ACTION matan la ventaja
L17-10  OPAQUE-MAPPING         el contenido no vive en la semántica del token
L17-11  INTERNAL-LOCALIZATION  la lesión aísla 1.7 y deja M_0^W intacto
L17-12  PASSIVITY-REPLAY       evaluar no mueve nada; el replay es determinista
```

**Doce son de alcance campaña y sólo `L17-8` es por vida**, porque su nula es la de
esa vida B y de ninguna otra. El ledger tiene 28 entradas, no 16 × 13.

**Ninguno escanea texto.** Se camina el AST. Mantener los gates afilados costó
renombres e imports en mi propio código —el aprendiz ya no importa ni el alias de
tipo de `level1.world`— y ésa es la dirección correcta: **renombrar lo inocente,
nunca ensanchar la lista blanca.**

Ejemplos de gates que se afilaron en vez de aflojarse:

```
L17-2   el criterio no es «quién consume azar» --la baraja, el gemelo y el runner
        sortean y ninguno mueve al ser-- sino quién puede llevar una dirección
        derivada del comando hasta el cuerpo. El gemelo la recibe y debe
        DESCARTARLA, y eso se lee del AST: caza al tramposo y al sutil que guarda
        la dirección antes del `del`.

L17-6   una cobertura baja NO hace fallar el gate. Eso sería un resultado
        experimental, no un defecto de instrumentación.
```

**31 filas de falsificación**, generadas ejecutando cada fixture, 0 sin confirmar.

---

# 9 · Resultados confirmatorios · V2

Semillas `170000011…170000026`, consecutivas, cero saltadas, 48 sin consumir.

```
Γ             +0.280587   sd 0.036078   mín +0.221686   máx +0.342515
CI95 inferior +0.262909                      CRITERIO PRIMARIO CUMPLIDO
positivas     16/16                          gates 13/13

D_C^A         +0.278808   16/16 positivas
D_C^B         −0.001779    0/16 positivas
D_K^action A  +0.281128   16/16 positivas
D_K^action B  −0.001863
D_W^A         +0.927337

Γ/D_W         0.3024 ± 0.0165      r(D_W, Γ) = +0.9107
```

**Las vidas no aprenden una cantidad arbitraria:** adquieren una fracción estable
de lo que cada mundo ofrece. Eso convence más que una media positiva sola.

`D_K^action` +0.281128 contra `D_C^A` +0.278808 — dos instrumentos distintos a
0.0023 nats.

**Dos vidas de exposición incompleta**, `170000024` y `170000026`, con `C_OA` 0.938
y 0.976 y algún contexto informativo nunca visitado. No fueron excluidas ni
tratadas aparte, y `L17-6` no falló. La lectura precisa no es «la exposición estaba
completa» sino **la adquisición sobrevivió con huecos locales de exposición**.

---

# 10 · El hallazgo metodológico sobre `T_P`

Demostrado en calibración, `T_17 = 1024` fijo, sólo variando el presupuesto del
predecesor:

```
T_P = 256    Γ ≈ +0.7736   Γ/D_W 0.878
T_P = 1024   Γ ≈ +0.5467   Γ/D_W 0.620
T_P = 4096   Γ ≈ +0.2755   Γ/D_W 0.313

D_W = 0.8817 IDÉNTICO en los tres · ΔD_W = 0.00e+00
ΔΓ(4096−1024) = −0.2712 en 16/16 · ΔD_K^action = −0.2709  ← caen juntos
```

> Un predecesor temporal más consolidado reduce cuánto puede desviarse el modelo
> condicionado por acción durante un presupuesto fijo de 1.7.

**No es un fracaso de 1.7.** La calibración a `T_P = 4096` predijo el confirmatorio
con 0.004 nats (`+0.2755` contra `+0.2806`), lo que descarta que los mundos
confirmatorios fueran distintos.

Regla developmental que queda: **saturación para el predecesor, pendiente para la
adquisición nueva.**

---

# 11 · Los defectos que se encontraron construyendo

Vale más que los resultados. Son las formas concretas en que este método falla.

| defecto | cómo apareció | lección |
|---|---|---|
| **El criterio fuera de la ruta** | el runner ejecutaba 0/13 gates | un criterio que no vive en la ruta congelada no está preregistrado |
| **Baseline confundido** | el gemelo destapó ventaja falsa creciente contra `M_0` congelado | el comparador debe recibir los mismos datos y diferir sólo en lo que se estudia |
| **El mismo confundido en la métrica hermana** | lo arreglé en `D_C` y no lo busqué en `D_K` | al reparar un confundido, auditar sus hermanas |
| **Sombra del gemelo desde la rejilla equivocada** | `MarginalisedBody._grid` es la de A: `D_W^B` salía 0.75 | un envoltorio que marginaliza en ejecución no cambia lo que envuelve |
| **Aserción vacua** | `twin.mean(axis=1)` comparado consigo mismo | marcar qué comprobaciones son tautológicas **dentro** del propio código |
| **Auditor que reconstruye lo que audita** | `audit` hacía `del learned` | un verificador debe consumir el objeto que se le pasa, o su fixture tiene que romper también el control |
| **Fixture que filtra sólo en entrenamiento** | el modelo salía peor, no mejor | una fuga ausente en consulta no infla nada |
| **Umbral fijo dependiente de la muestra** | 8 réplicas, falla por 0.0002 | derivar de la nula de los propios datos |
| **Generalizar desde una muestra sesgada** | las 16 de 1.6 estaban a z = −2.77 | un valor preregistrado debe declarar sobre qué población se midió |
| **Verificación que se contamina a sí misma** | la ventana «usada» porque el protocolo la nombra | excluir el commit que reserva antes de comprobar virginidad |

---

# 12 · Superficie de código

```
terrario/level17/
    efference.py    CommandToken · EfferenceCopy · ALL_COMMANDS · Observation
    wiring.py       ActuatorWiring · wiring_stream          [s,64]
    contingency.py  ActionContingencyModel · ContingencyContractError
    life.py         TwoPhaseLife · live_two_phase
    twin.py         MarginalisedBody · twin_stream [s,65] · state_kernels
    shadow.py       AnalyticActionShadow · .marginalised() · available/experienced
                    learner_error · marginal_learner_error · divergence_matrix
    exposure.py     Exposure · measure
    shuffled.py     stratified_permutation · build · audit · row_spread  [s,128+k]
    gates.py        los trece · identifiers/attributes/imported_modules
    campaign.py     PairOutcome · GateEntry · verify_ledger · run_campaign
                    REQUIRED_GATES · T_P 4096 · T_17 1024 · POST 2048 · N 16

tests/   test_level17_architecture.py · _gates.py · _v2_reparacion.py   84 contratos
scripts/ matriz_falsificacion.py                                        31 filas
resultados/ v2_confirmatorio_16_pares.json · v2_ledger_gates.json

flujos   mundo [s,0] · motor [s,1] · baraja 1.6 [s,2] · nulas 1.6 [s,3+k]
         cableado [s,64] · efecto de B [s,65] · SHUFFLED-ACTION [s,128+k]
```

---

# 13 · Lo que el decimal siguiente puede reusar

| pieza | por qué sirve |
|---|---|
| `verify_ledger` + `REQUIRED_GATES` | **lo primero que hay que copiar.** Es la defensa contra D-4 |
| `efference.py` · `wiring.py` | el canal opaco y `φ` no dependen de la capacidad |
| `twin.py` | la construcción de gemelos action-null y `state_kernels` |
| `shadow.py` | el oráculo analítico; extenderlo al condicionamiento nuevo |
| `exposure.py` | los cuatro instrumentos del lado del sustrato |
| `shuffled.py` | la baraja estratificada y la nula autocalibrada |
| `gates.py` · el escáner AST | `identifiers`, `attributes`, `imported_modules` |
| el patrón `C_0 = herencia/k` | hace que la lesión devuelva al peldaño anterior |

**Lo que NO se reusa:** `contingency.py` es la capacidad de 1.7 y queda congelada.

---

# 14 · Lo que NO está decidido

1. **Si la fase P debe seguir en saturación.** `T_P = 4096` se eligió para que 1.6
   estuviera sólidamente presente, y encoge el efecto a un tercio de lo disponible.
   Es deliberado, pero no es la única opción defendible.
2. **Si `Γ/D_W ≈ 0.30` es una propiedad del mecanismo o del presupuesto.** La curva
   de calibración sugiere lo segundo; no está demostrado.
3. **Cómo se hereda cuando haya más de una capacidad previa.** El patrón
   `C_0 = N_16/4` funciona con un predecesor. Con dos, la composición está sin
   resolver.
4. **Qué capacidades pertenecen al Nivel 2.**

---

# 15 · Reproducción

```bash
python -m pytest tests/test_level17_architecture.py tests/test_level17_gates.py \
                 tests/test_level17_v2_reparacion.py -q          # 84 contratos

python scripts/matriz_falsificacion.py                            # 31 filas

python -c "from terrario.level17.campaign import run_campaign; \
r = run_campaign(tuple(range(170000011,170000075))); \
print(r.interval_lower, len(r.gates_executed))"
```

```
base       c2b808b · cierre de 1.6
mundo      grid 7 · wall_probability 0.25          heredados del 1.0
prior      α₀ = 1.0 · C_0 = N_16/4
vida       T_P 4096 · T_17 1024 · POST 2048 · 16 pares A/B
oráculo    ac12cc3 · blob 4b6cdd1d5cbe45f20daa6de546ddba2581919bbc
protocolo  1ca4b38 · campaña 4b6b325 · pares sha256 0956e104fbfd8577
```

---

# 16 · El claim, y su frontera

**Permitido:**

> El Agente Nivel 1.7 adquirió, a partir de su propia experiencia, una
> representación predictiva de cómo las consecuencias sensoriales dependen de la
> acción que acaba de ejecutar, aportando información por encima de la estructura
> temporal heredada de Nivel 1.6. Esa ventaja desaparece cuando se elimina o
> destruye la correspondencia con la acción, no aparece en el mundo gemelo donde la
> acción es informativamente irrelevante, y depende causalmente del estado
> incremental adquirido; al lesionar ese estado, el organismo vuelve exactamente a
> su competencia de Nivel 1.6.

**Siempre con:** `PREDECESOR = SATURADO` · `ADQUISICIÓN 1.7 = PENDIENTE`.

**Prohibido:** que el organismo descubriera que la acción importa —la factorización
`(O,A)→O'` es **suministrada**—, razonamiento causal, intención, elección
deliberada, control orientado a objetivos, asignación de crédito, curiosidad,
autorregulación, distinción de correlación espuria, exploración dirigida, memoria
selectiva, agencia fuerte, y adquisición eficiente con pocos datos.

**Y sobre todo:** el ser no decide, no quiere y no busca. Su fuente motora sigue
siendo exactamente la que traía al nacer y no cambió un bit en todo el nivel. Lo
que 1.7 demuestra es anterior:

> distingue «esto suele pasar» de «esto cambia según lo que yo hago»,
> y lo segundo lo aprendió de su propia vida.

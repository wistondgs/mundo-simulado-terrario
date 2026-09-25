# ETP-AUTOPSY-01 · Autopsia causal del mecanismo de restauración

Estado: **CAUSAL_MECHANISM_IDENTIFIED**.

- **H-CORE:** se confirma, con cuatro precisiones (§4).
- **Alcance:** el espécimen A congelado bajo su dinámica síncrona, sobre dos poblaciones:
  - las 8 lesiones DATA autorizadas (P-DATA);
  - las 42 perturbaciones de un bit del estado completo (P-FULL).
- **Límite del alcance:** fuera de él el mecanismo tiene fronteras medidas (§16), y no se afirma nada más allá.

## 1. Base de repositorio

- **Rama:** `experiment/primitivo-causal-autopsy-01`, en worktree propio.
  - Sale de `f0fdf00c6661b466ffbf1806ab13afb4be616d13`, dentro del linaje científico:
    `41fccbf` (DISCOVERY-02/03) → PRE-01 → EXP-01 → EXP-02 → EXP-03 → preregistro EXP-04A.
  - No contiene `experiments/primitivo_n2/` (pista Gate A) ni
    `docs/LEVEL18_ANALISIS_CAUSA_RAIZ.md`. Ninguna de las dos pistas se tocó.
- **Instrumentos:**
  - [autopsy01_core.py](autopsy01_core.py): red booleana genérica, intervenciones explícitas y batería de evaluación.
  - [run_autopsy01_mechanism.py](run_autopsy01_mechanism.py): §0–§11.
  - [run_autopsy01_scaling_variants.py](run_autopsy01_scaling_variants.py): §12–§13, que sólo se corrió tras cerrar el núcleo.
  - [run_autopsy01_errata_check.py](run_autopsy01_errata_check.py): se añadió tras el cierre, al corregir siete frases que afirmaban más que su evidencia (§6, §8, §11, §16). Recalcula en sólo lectura las cifras de esas correcciones y no regenera ningún artefacto.
- **Artefactos:** `artifacts/autopsy01_*`. El índice de veredictos está en
  [autopsy01_verdicts.json](artifacts/autopsy01_verdicts.json).
- **Cómo se trataron las predicciones.**
  - Quedaron escritas en los instrumentos antes de su primera ejecución, y cada corrida registra si se cumplió.
  - No se sellaron en un commit previo: esto es una serie de análisis, no un preregistro.
  - Ninguna predicción se modificó tras ver resultados.
  - Una verificación se añadió después: la ley del triángulo para n=3..8 (§14), evaluada sobre corridas ya producidas. Se declara como tal.
- **EXP-04A** sigue preregistrado y sin ejecutar. Dos brazos de aquí, el localizador erróneo y el pulso erróneo, anticipan parte de su seguimiento secundario, y se declara así.

## 2. Ecuaciones reales

La red reconstruida desde las reglas declaradas es **idéntica** a
`build_baseline_atlas.step` en los **2,097,152** estados de 21 bits: 0 discrepancias
([auditoría](artifacts/autopsy01_equation_audit.json)).

| familia | nombre descriptivo | regla |
| --- | --- | --- |
| X | datos | `x_i' = x_i XOR p_i` |
| D | comparadores de desacuerdo | `d12'=x1^x2, d13'=x1^x3, d23'=x2^x3, d14'=x1^x4, d24'=x2^x4` (no hay `d34`) |
| E | localizadores de error | `e1'=d12&d13, e2'=d12&d23, e3'=d13&d23, e4'=d14&d24` |
| L | registro de un paso | `l_i' = e_i` |
| P | pulso de un disparo | `p_i' = e_i & ~l_i` |

Cada localizador usa dos testigos fijos: `x1←{x2,x3}`, `x2←{x1,x3}`, `x3←{x1,x2}`, `x4←{x1,x2}`.

Lo siguiente se observó sobre la tabla completa, no se infirió del código:

- **Entradas esenciales.** Las de cada coordenada son exactamente sus padres declarados, con fan-in máximo 2.
- **Complemento.** Complementar x conmuta con G en todos los estados.
- **Automorfismo.** `(x1 x2)`, con su reetiquetado inducido, es un automorfismo global.
- **Puntos fijos.** Hay **16**: los 2 blancos y 14 «alarmas enclavadas», con x errónea, D/E/L altos y P=0.

## 3. Ledger causal heredado

Se leyeron los artefactos comiteados, sin regenerarlos
([ledger](artifacts/autopsy01_causal_ledger.csv)):

- las 8 trazas P-DATA comiteadas se reproducen bit a bit;
- el punto fijo de EXP-01 se reproduce 8/8 con el runner de esta autopsia;
- las filas registradas de EXP-02 y EXP-03 coinciden con sus informes, y las 64
  comparaciones de fase son exactas;
- los dos bloqueos de EXP-03, el persistente y el transitorio, se reproducen 8/8 con la
  maquinaria de esta autopsia.

| fase | intervención | observación | prueba | no prueba |
| --- | --- | --- | --- | --- |
| ONSET | EXP-03: bloqueo del padre DATA en las D incidentes | bloqueo persistente: x perturbada con q=q* fijo (8/8); bloqueo transitorio: la misma secuencia desplazada un paso (64/64 comparaciones exactas) | x→D es necesaria; el onset se regenera desde la perturbación presente | qué calculan D/E ni de dónde sale la dirección |
| ACTION | EXP-01: corte de p_i(t3)→x_i(t4) | punto fijo no objetivo (8/8); los shams, idénticos al natural | la arista P→X es necesaria | qué elige la coordenada ni por qué el pulso es único |
| TERMINATION | EXP-02: escribir sólo x=blanco sobre el estado cortado | reingreso al estado natural t4 y q* en t7 (8/8) | la restauración de x media el apagado de D/E/L; P termina por L | la lógica del circuito |
| PROJECTED APD | ninguna; enumeración (§11) | Φ existe en R_X; ninguna función de aridad ≤2 lo extiende | no es una regla directa de fan-in 2 | cómo lo compila la red |

**DISCOVERY-03 = NO_LOCAL_SOLUTION** quedó verificado ahora, corriendo el instrumento: 0
candidatos para C4 y para C3, tanto con d_max≤1 como con d_max≤2. DISCOVERY-02 (n=3) da
también 0. Hasta ahora ese claim tenía procedencia `RESEARCHER_SUPPLIED`; su salida queda
registrada en [compilation.json](artifacts/autopsy01_compilation.json).

## 4. R_X y Φ como teoría de códigos; veredicto H-CORE

`C = {0000, 1111}` es el código de repetición lineal [4,1,4]
([tabla completa](artifacts/autopsy01_code_theory.csv)).

- **A.** `R_X = B_H(0000,1) ∪ B_H(1111,1)` exactamente: 10 estados.
- **B.** Todo estado de R_X que no es blanco tiene un código más cercano único (distancias 1 y 3).
- **C.** Los estados de peso 2 son exactamente el conjunto de empates: distancia 2 a ambos códigos, 6 estados.
- **D.** En R_X, Φ es decodificación por palabra más cercana.
- **E.** `d_min = 4`, así que el radio de corrección es `t = ⌊(4−1)/2⌋ = 1` y la capacidad de detección es 3.
  - Las bolas cubren 10 de 16 estados.
  - Como d_min es par, quedan 6 empates.
- **Síndrome.** D evalúa 5 controles de paridad de rango 3 sobre GF(2). Hay 8 cosets:
  - 5 tienen líder único (error de peso 0 o 1);
  - 3 son cosets de peso 2 con dos líderes, los empates.

**Veredicto: H-CORE CONFIRMADA.** A implementa **decodificación por síndrome de un
error** del código de repetición, con localizadores AND de fan-in 2 y un actuador de
conmutación disparado por flanco.

Precisiones sobre la formulación original:

1. **No lee «los tres bits restantes» como bloque.** Cada coordenada se compara con
   dos testigos fijos, y el bit dañado es el único que discrepa de ambos. De los tres
   bits sanos, cada localizador usa sólo dos.
2. **La dirección no se extrae de los bits sanos.** El circuito auxiliar es ciego al
   blanco (§7). La dirección es la ubicación que da E, aplicada como conmutación del
   valor actual.
3. **«Se apaga» son dos terminaciones distintas.** La del pulso ocurre en t4, por L;
   la del soporte en t5–t7, porque la x corregida elimina los desacuerdos.
4. **El núcleo decisor es el triángulo {x1,x2,x3}; x4 es seguidor.** En R_X esto no
   cambia nada, pero es lo que decide los empates (§9).

## 5. Roles causales exactos

| componente | calcula | evidencia causal (§8) |
| --- | --- | --- |
| X, datos | estado físico e identidad del blanco (redundancia 4×) | P-DATA; es la única variable que difiere entre blancos |
| D, comparadores de desacuerdo | síndrome `x_i XOR x_j`; invariante al complemento | quitar un comparador usado por E_k deja la lesión k detectada pero no localizada; quitar uno no usado no cambia nada |
| E, localizadores de error | `1` sii x_i discrepa de sus dos testigos; en R_X es el indicador exacto del bit dañado | ablación: no hay reparación aunque haya desacuerdo; rescate: un solo evento E basta |
| L, registro de un paso | `E(t−1)` (256/256 comprobaciones) | quitarlo convierte el pulso en nivel y produce oscilación |
| P, pulso de un disparo | `E(t) ∧ ¬E(t−1)`, flanco de subida (224/224) | ablación: alarma enclavada; rescate: un pulso basta, pero sin dirección propia |
| X ⊕ P, actuador de conmutación | invierte el bit señalado | dirección = ubicación × conmutación (§7) |

## 6. Tabla de las 8 lesiones

Fuente: [lesion_table.csv](artifacts/autopsy01_lesion_table.csv). D sigue el orden
`d12 d13 d23 d14 d24`.

| lesión | x | D en t1 | E en t2 | coordenada elegida | P en t3 | X en t4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0000:x1 | 1000 | 11010 | 1000 | x1 | 1000 | 0000 |
| 0000:x2 | 0100 | 10101 | 0100 | x2 | 0100 | 0000 |
| 0000:x3 | 0010 | 01100 | 0010 | x3 | 0010 | 0000 |
| 0000:x4 | 0001 | 00011 | 0001 | x4 | 0001 | 0000 |
| 1111:x1 | 0111 | 11010 | 1000 | x1 | 1000 | 1111 |
| 1111:x2 | 1011 | 10101 | 0100 | x2 | 0100 | 1111 |
| 1111:x3 | 1101 | 01100 | 0010 | x3 | 0010 | 1111 |
| 1111:x4 | 1110 | 00011 | 0001 | x4 | 0001 | 1111 |

**¿Se activa exactamente un E_i, y es siempre el bit dañado?** **Sí, cuando E se
activa.** En las 8 lesiones hay a lo sumo un E alto en cada paso, y es siempre e_k:

- **Cuándo:** e_k está alto de t2 a t5, 4 pasos (patrón en t0–t8: `001111000`).
- **Sin E:** en t0, t1, t6 y t7 no hay ninguno.
- **Ningún otro:** ningún E_i con i ≠ k se activa en ningún paso.

*Demostración.*

- Sea `k` la única coordenada minoritaria. `e_i = [x_i ≠ x_a ∧ x_i ≠ x_b]`, donde
  a y b son sus testigos, distintos entre sí y de i.
- **`e_k = 1`**: los dos testigos de k son sanos.
- **`e_i = 0` para i ≠ k**: x_i tiene el valor mayoritario, y a lo sumo uno de sus
  testigos es k.
- **Duración:** x está lesionada de t0 a t3, así que D lleva el síndrome del error en
  t1–t4 y E_k está alto en t2–t5. La x corregida en t4 anula D en t5 y E en t6.
- **Generalidad:** el argumento vale para cualquier asignación de testigos, y la
  comprobación exhaustiva da 81 de 81 exactas en R_X.

## 7. Dirección de la reparación: de dónde sale

**Búsqueda de objetivo u oráculo, por observación y no por grep:**

- **Variable de blanco:** no hay ninguna. En ambos blancos `q = 0^17`, así que sólo `x1..x4` difieren entre ellos.
- **Recompensa, token de meta o entrada externa:** no hay ninguna. Cada coordenada lee exactamente sus ≤2 padres, y G es una tabla sobre los 21 bits.
- **Interruptor de dirección codificado:** no hay ninguno. G conmuta con complementar x en los 2²¹ estados, así que toda reparación hacia 0000 tiene su espejo hacia 1111.
- **Reloj:** no hay ninguno. La tabla es homogénea en el tiempo.

**El circuito auxiliar es ciego al blanco.**

- **Complemento:** las lesiones complementarias comparten la trayectoria completa de q.
- **Información mutua sobre el blanco** ([direction_information.csv](artifacts/autopsy01_direction_information.csv)):
  `I(q_t; blanco) = 0` bits para todo t, e `I(x_t; blanco) = 1` bit.
- **Información mutua sobre la posición:** `I(q_t; posición) = 2` bits en t1–t6.
- **Mismo pulso, efecto opuesto:** el mismo pulso `p_k` produce 1→0 desde una lesión
  de 0000 y 0→1 desde una de 1111 ([direction_toggle.csv](artifacts/autopsy01_direction_toggle.csv)).

**Formalización.**

- **Quién porta el blanco:** la identidad de la cuenca la portan los bits
  concordantes, que son la mayoría m.
- **El bit dañado** es la única minoría, así que `x_k = ¬m`.
- **Qué extrae el circuito:** los comparadores extraen la **ubicación** k, nunca el
  valor m.
- **Cómo se vuelve dirección:** la conmutación convierte la ubicación en dirección
  porque el alfabeto es binario: `x_k ⊕ 1 = ¬x_k = m`.
- **Clasificación:** el decodificador es SUPPLIED. Su función es IMPLICIT_IN_RULES.
  El patrón D/E/L/P realizado es DYNAMICALLY_GENERATED y TRAJECTORY_CONTINGENT, porque
  depende de la posición.
- **Rótulo:** corresponde **corrección causal intrínseca de errores** o **regla de
  restauración endógena**. No corresponde intención ni deliberación.

## 8. Intervenciones causales

- **Volumen y resultado:** 320 corridas, **320/320 predicciones cumplidas**, **84/84 shams no-op idénticos** a la trayectoria natural.
- **Semántica de las intervenciones:**
  - clamp persistente, o sustitución de regla por constante;
  - escritura puntual en un tiempo dado;
  - G sin cambios fuera de lo intervenido.
- **Fuentes:** [resumen](artifacts/autopsy01_interventions_summary.csv) y
  [trazas](artifacts/autopsy01_interventions_traces.csv).

| familia | brazo | n | resultado |
| --- | --- | ---: | --- |
| A1 ablación de comparador | `d≡0`, usado por E_k | 16 | la lesión persiste con D parcialmente alto y sin pulso: **detectada, no localizada** |
| | `d14≡0` o `d24≡0` con lesión en x1 o x2 | 4 | reparación normal: la información está disponible pero **no se usa causalmente** |
| | shams, d naturalmente 0 | 20 | idénticos al natural |
| A2 localizador con un solo testigo | e_i = un solo d | 64 | 48 normales; en 16, la lesión del otro extremo también dispara e_i: el bit sano se conmuta y queda enclavado (dos pulsos, sin retorno) |
| B ablación de localizador | `e_k≡0` | 8 | desacuerdo presente, sin reparación |
| | shams | 24 | idénticos |
| C rescate de localizador (D amputada) | sin inyección | 8 | lesión fija con q=q* |
| | un evento `e_k=1` en t2 | 8 | x reparada en t4 y estado completo en t4; **E basta para toda la cadena posterior** |
| | `e_k` sostenido desde t2 | 8 | exactamente 1 conmutación y x restaurada al blanco en t4; E_k y L_k quedan en 1 mientras dura la sujeción (D amputada, P=0). No es una alarma enclavada: x es correcta |
| | sham | 8 | idéntico |
| D localizador erróneo | intacto, `e_j` en t2 | 24 | error transitorio de x_j en t4, detectado y deshecho en t8; estado completo en t11 (3 pulsos) |
| | D amputada, `e_j` en t2 | 24 | doble error permanente: **el tramo posterior ejecuta la ubicación que reciba** |
| | blanco sano, `e_j` en t0 | 8 | 2 conmutaciones; estado completo en t9 (clase E de P-FULL) |
| E ablación de actuador | `p_k≡0` | 8 | D, E_k y L_k altos, x lesionada: detección y localización intactas, sin acción |
| | shams | 24 | idénticos |
| F rescate de actuador (E amputada) | sin inyección | 8 | lesión fija, D alto |
| | `p_k` en t3 | 8 | x en t4, estado completo en t5: basta físicamente, pero la elección vino de fuera |
| | `p_j` erróneo en t3 | 24 | doble error permanente: **P no tiene dirección propia** |
| | sham | 8 | idéntico |
| G sin compuerta temporal | `P = E` | 8 | ciclo de 15 con x en movimiento |
| | X lee E directo | 8 | ciclo de 7 con x en movimiento |

Qué separa cada familia:

- **Detección:** D.
- **Localización:** E. D sin E no repara.
- **Compuerta temporal:** L/P, que convierten el nivel en un evento único.
- **Actuación:** P→X, que ejecuta sin dirección propia.
- **Terminación:** la de pulso ocurre por L, y la de soporte por la x corregida.

## 9. Frontera: los seis estados de peso 2

Fuente: [weight2_boundary.csv](artifacts/autopsy01_weight2_boundary.csv).

| x | partición | D en t1 | E en t2 | pulsos | final | t |
| --- | --- | --- | --- | --- | --- | ---: |
| 1100 | 12\|34 | 01111 | e3,e4 | p3,p4 en t3 | 1111 | 7 |
| 0011 | 12\|34 | 01111 | e3,e4 | p3,p4 en t3 | 0000 | 7 |
| 1010 | 13\|24 | 10110 | e2 | p2 en t3; p4 en t7 | 1111 | 11 |
| 0101 | 13\|24 | 10110 | e2 | p2 en t3; p4 en t7 | 0000 | 11 |
| 0110 | 14\|23 | 11001 | e1 | p1 en t3; p4 en t7 | 1111 | 11 |
| 1001 | 14\|23 | 11001 | e1 | p1 en t3; p4 en t7 | 0000 | 11 |

- **Sin ciclos ni atascos.** Ningún estado cicla ni se estanca: los 6 llegan a un
  código con q*.
- **Cuándo dispara E_i en peso 2:** sólo si sus dos testigos están en la clase
  opuesta a la suya. Por eso no hay un único bit minoritario:
  - en la partición 12|34 disparan e3 y e4 a la vez;
  - en las otras dos, un solo localizador dispara primero y el estado pasa a
    peso 1 o 3, que se corrige en una segunda ronda.
- **Desempate arquitectónico.** El empate se decide por el grafo de testigos: desde
  q*, **el código final es `maj(x1,x2,x3)⁴` para los 16 estados de x**.
- **Simetrías:**
  - se conserva la del complemento;
  - se conserva la de `(x1 x2)`;
  - no hay simetría S4.
- **Por qué es una frontera causal y no un caso excluido.** El peso 2 es exactamente
  donde la prueba «mis dos testigos discrepan de mí» deja de identificar una minoría
  única. La dinámica sigue siendo determinista, pero pasa de decodificar a desempatar
  por arquitectura.

## 10. ¿Volvió igual por dentro, o sólo funcionalmente?

Fuente: [exact_vs_functional.csv](artifacts/autopsy01_exact_vs_functional.csv).

- **Funcional:** x se restaura en t4 en 8/8.
- **Exacta:** el estado completo de 21 bits es **idéntico al previo a la lesión** en
  t7, en 8/8.
- **Ventana sólo funcional:** t4–t6. En ella x está sana y q todavía no es basal.
- **Degeneración de trayectorias:** hay 4 trayectorias internas distintas, una por
  posición, que las lesiones complementarias comparten. Esto es convergencia
  muchos-a-uno: degeneración de caminos, no del estado final.
- **Sin memoria residual ni histéresis:** el estado final es el mismo que el de un
  sistema nunca lesionado, y G es markoviana en los 21 bits.
- **P-FULL:** 42/42 exactas.

Clasificación: **restauración de estado exacta**, precedida por **restauración
funcional** durante 3 pasos, con **degeneración** de trayectorias. **No hay histéresis
ni memoria residual.**

## 11. Compilación causal del Φ no extensible

Fuente: [compilation.json](artifacts/autopsy01_compilation.json).

- **El mapa a cuatro pasos.** Sea `F4(x) = π_x G⁴(x, q*)`. Entonces
  `F4 = (maj(x1,x2,x3), maj(x2,x1,x3), maj(x3,x1,x2), maj(x4,x1,x2))` en los 16 estados
  de x: es de aridad 3 por coordenada, y es igual a Φ en R_X desde t4.
- **Aridad mínima.** Ninguna función de aridad esencial ≤2 extiende Φ_i: hay 0. La
  aridad mínima es 3.
  - Φ_i fija 10 de los 16 estados de x y deja libres los 6 empates, así que admite
    2⁶ = 64 extensiones por coordenada.
  - De ellas, 4 tienen aridad 3, que son la mayoría de cada una de las 4 ternas, y
    las otras 60 tienen aridad 4.
- **Reglas sólo-X.** Si cada coordenada lee a lo sumo 2 variables de X y ambos códigos
  son fijos, quedan sólo 16 reglas por coordenada (`x_a`, `x_a∧x_b`, `x_a∨x_b`), todas
  monótonas y ninguna XOR. Eso no explica por sí solo que DISCOVERY-03 no encuentre
  solución:
  - maj3, que A realiza en t4, también es monótona; lo que impide una regla directa es
    la aridad (punto anterior), no la monotonía;
  - con los centros 0000/1110 (clave `C3`) sí hay reglas sólo-X no monótonas: 6 de 18
    en x1, x2 y x3, y 12 de 17 en x4. DISCOVERY-03 da igualmente 0 candidatos.

  Lo que descarta las redes sólo-X iteradas de fan-in ≤2 es la enumeración exhaustiva
  de DISCOVERY-03 (§3), no un argumento de monotonía.
- **Qué compran los auxiliares:**
  1. **Registros de resultados intermedios.** Guardan el XOR y luego el AND, lo que da
     aridad 3 en 2 capas. Es la profundidad mínima posible con fan-in 2
     (`⌈log2 3⌉ = 2`).
  2. **Un sistema de coordenadas nulo en ambos códigos, el síndrome.** Permite usar
     operaciones no monótonas (XOR) sin romper los puntos fijos, algo imposible para
     reglas sólo-X de fan-in 2 con los códigos de A (0000/1111). No es imposible en
     general: con 0000/1110, `x_j' = x_j ⊕ x4` (j ∈ {1,2,3}) deja fijos ambos centros.
  3. **Compuerta temporal.** E queda alto 4 pasos por la latencia de la tubería, y el
     actuador es una conmutación, así que hace falta convertir ese nivel en un evento
     único.
- **Recursos:**
  - 17 auxiliares: 5 D, 4 E, 4 L, 4 P;
  - 38 aristas estáticas;
  - 1,584 aristas efectivas en las 8 trayectorias naturales, igual que PRE-01;
  - profundidad causal de 4 pasos x→x.
- **Fases:**
  - detección en t1;
  - localización en t2;
  - compuerta en t3;
  - actuación en t3→t4;
  - drenaje en t5 (D), t6 (E) y t7 (L).

```text
x(t) ─XOR─▶ D(t+1) ─AND─▶ E(t+2) ─┬───────────────▶ P(t+3) = E(t+2) ∧ ¬L(t+2) ─XOR─▶ x(t+4)
                                  └─▶ L(t+3) = E(t+2)
```

## 12. Minimalidad

Fuentes: [ablaciones](artifacts/autopsy01_ablations.csv) y
[familia de testigos](artifacts/autopsy01_witness_family.csv).

Se evaluaron 366 variantes de A con una batería fija:

- blancos fijos;
- 8/8 P-DATA exactas;
- P-FULL;
- sin falsas reparaciones;
- sin ciclos;
- con autoapagado.

- **Auxiliares:** los **17 son individualmente necesarios**; cada clamp a 0 rompe la batería.
- **Aristas:** **0 de 76** sustituciones de una arista por constante pasan.
- **Compuertas:** **0 de 267** reemplazos pasan. Cada compuerta es la única, entre las
  funciones de sus mismos padres, que funciona.
- **Sin compuerta de un disparo:**
  - `P = E` da un ciclo de 15;
  - X que lee E da un ciclo de 7;
  - `P = E ∧ ¬P` cicla.
- **Fusiones:** fusionar D en E o P en X sólo funciona con fan-in 3. Cada capa existe
  para respetar fan-in 2.
- **Familia de testigos:** las 81 asignaciones posibles, con el mismo E/L/P/X; pasan 75.

| comparadores D | asignaciones que pasan | resuelven los 6 estados de peso 2 |
| ---: | ---: | --- |
| 4 (ciclos de 4, 16 aux) | 3 | 0: los empates se enclavan |
| 5 | 48 | sólo 12, exactamente las «triángulo + colgante»; **A es una** |
| 6 | 24 de 30 | 24; las 6 restantes ciclan |

**Conclusión:**

- **Aux-mínimo:** A no lo es para R_X solo: con 16 auxiliares basta.
- **Pareto-mínimo:** sí lo es en (comparadores, resolución de empates) dentro de la
  familia.
- **Componentes:** ninguno de A puede quitarse ni simplificarse.

## 13. Ley matemática

**Nivel de ecuación.**

```text
s(t+1) = H x(t)                            síndrome, 5 controles de paridad
ε_i(t+1) = s_{i,a(i)}(t) ∧ s_{i,b(i)}(t)   localizador
ℓ(t+1) = ε(t)                              registro
π(t+1) = ε(t) ∧ ¬ℓ(t) = ε(t) ∧ ¬ε(t−1)     flanco de subida
x(t+1) = x(t) ⊕ π(t)                       conmutación
```

**Consecuencias desde `(x0, q*)`:**

- `x(4) = x0 ⊕ ε(H x0)`, y por coordenada `x_i(4) = maj(x_i, x_{a(i)}, x_{b(i)})`;
- en R_X, `Φ(x) = x ⊕ e_k = argmin_{c∈C} d_H(x, c)`;
- en todo el cubo, el código final es `maj(x1,x2,x3)⁴`.

Verificado en las 8 lesiones (`law_verified`).

**Ley temporal.** Sea w(t) el indicador de que la coordenada dañada está errónea.

- **Sin compuerta** el lazo es lineal sobre GF(2):
  - con `P = E`: `w(t+1) = w(t) ⊕ w(t−3)`, de polinomio `z⁴+z³+1`, primitivo, con periodo 15;
  - con X leyendo E: `w(t+1) = w(t) ⊕ w(t−2)`, de polinomio `z³+z²+1`, con periodo 7.

  Ambos periodos se observaron exactos.
- **Con compuerta** el lazo es `w(t+1) = w(t) ⊕ (w(t−3) ∧ ¬w(t−4))`: una sola
  inversión, y luego se detiene.

**Nombre:** corrección causal intrínseca de errores. Es decodificación por síndrome
del código de repetición, con actuador de conmutación disparado por flanco.

## 14. Escala

Fuentes: [matemática](artifacts/autopsy01_scaling_math.csv) y
[arquitectura](artifacts/autopsy01_scaling_architecture.csv).

**Matemática.** Para el código {0ⁿ,1ⁿ}:

- el radio de corrección es `t = ⌊(n−1)/2⌋`;
- hay empates sólo si n es par, en el peso n/2 (6, 20, 70, … estados);
- para n impar el código es perfecto.

**Teorema: aridad mínima 2t+1.** Toda decisión de un disparo que restaure todo error de
peso ≤t tiene aridad esencial **≥ 2t+1**.

- *Prueba.* Si depende de un conjunto S con |S| ≤ 2t, se parte S en A y S∖A, ambos de
  tamaño ≤t. Entonces 0ⁿ con errores en A y 1ⁿ con errores en S∖A coinciden en S, pero
  exigen salidas distintas.
- **Verificación por fuerza bruta:** n=4 (t=1), n=5 (t=2) y n=6 (t=2). La mayoría de
  2t+1 coordenadas basta.
- **Consecuencia con fan-in 2:** profundidad `≥ ⌈log2(2t+1)⌉` y al menos 2t compuertas
  por localizador.

**Arquitectural.** La arquitectura de A (localizadores de radio 1) se probó para n=3..8:

- **Errores simples:** todos se corrigen, a todo n, con DATA en t4 y estado completo
  en t7. La profundidad es constante, con 3n + |D| auxiliares.
- **Triángulo + colgantes** (|D| = 2n−3):
  - restaura todos los errores dobles salvo los 6 internos al triángulo, que van al
    código opuesto;
  - **la ley del triángulo se cumple para n=3..8**: el triángulo sigue siendo el núcleo
    decisor a cualquier n, así que la red no calcula la mayoría global.
- **Ciclo** (|D| = n): los errores dobles casi siempre se atascan.
- **El radio arquitectónico sigue siendo 1** aunque el matemático crezca.

**No demostrado:**

- **Radio ≥2:** no se construyó ninguna arquitectura que lo alcance. Sólo se derivaron
  sus requisitos: aridad 2t+1, profundidad logarítmica y tuberías balanceadas.
- **Autoarranque y autoapagado:** se mostraron para errores simples hasta n=8, y no
  para corrección de varios errores.
- **Viabilidad computacional:** sólo se conocen las cotas inferiores anteriores.

## 15. Variantes cercanas

Esta sección se corrió después de cerrar el núcleo. Fuente:
[variants.csv](artifacts/autopsy01_variants.csv).

| variante | resultado |
| --- | --- |
| códigos 0000/1110 (distancia 3; control de peso 1 sobre x4) | 8/8; q idéntico por posición |
| par {0101,1010} (distancia 4, con XNOR donde los bits del código difieren) | 8/8: es un reetiquetado |
| distancias 2 y 1 | las bolas se solapan: ningún decodificador puede restaurar todo error simple |
| Rep3 ⊕ Rep3 (4 atractores) | 24/24 errores simples; 36/36 dobles con uno por bloque; los dobles dentro de un bloque van a otra palabra (24/24) |
| código [5,2,3] | los controles de peso ≤2 generan 2 de las 3 dimensiones del dual: hace falta un control de peso 3 (fan-in 3 o una etapa XOR extra) |
| dos errores DATA simultáneos en A | 6 vuelven al código original y 6 van al opuesto: los pares internos al triángulo |
| retardo extra D→E | 8/8; estado completo en t9 |
| retardo extra P→X | 8/8; estado completo en t8 |
| memoria del disparo con dos pasos de antigüedad | 8/8 tras 3 conmutaciones; estado completo en t14 |
| asincronía: barrido aleatorio | 529/2000 restauran; 1471 quedan en alarma enclavada |
| asincronía: una coordenada al azar | 481/2000 restauran; el resto, alarma enclavada |
| pérdida estocástica del pulso (0.1 / 0.25 / 0.5) | restauración 0.909 / 0.755 / 0.497 ≈ 1 − pérdida: **no hay reintento** |
| fallo permanente de x_k | un pulso, la conmutación anulada y la alarma enclavada (8/8) |
| lesión que se revierte sola en t1 | el pulso rancio rompe el bit sano en t4, y el detector repara su propio error: estado completo en t11 (8/8) |
| segunda lesión durante la reparación | τ=1–3: 12/32 caen al ciclo de 12; τ=4: 8/32 se enclavan; τ≥5: todas restauran |

**Pertenece a una familia amplia:**

- el mecanismo vale para códigos cuyos controles de paridad son pares: sumas directas
  de códigos de repetición, más coordenadas constantes;
- es invariante al reetiquetado;
- es modular, como muestran los 4 atractores de Rep3 ⊕ Rep3.

**Es específico de A:**

- el desempate por el triángulo;
- el disparo único sin reintento;
- la dependencia de la sincronía;
- la ventana de una sola corrección en vuelo.

## 16. Frontera global

Fuente: [censo](artifacts/autopsy01_state_space_census.json).

**Espacio completo de 21 bits:**

- **38.57 %** fluye a los blancos (808,816 estados);
- **60.50 %** cae en seis **ciclos de longitud 12** (1,268,736 estados);
- **0.93 %** cae en 14 alarmas enclavadas (19,600 estados);
- el transitorio máximo es de 22 pasos.

**Perturbaciones del blanco:**

- las de un bit vuelven todas (42/42);
- las de dos bits vuelven 366/420, 183 de 210 en cada blanco. De las 54 que no:
  - 18 van al código opuesto (9 por blanco): dos errores dentro del triángulo en una
    misma familia, `x_i+x_j`, `e_i+e_j` o `p_i+p_j`;
  - 36 caen en un ciclo de 12 (18 por blanco): mezclas de dos familias (x+e, x+p o
    e+p) sobre dos coordenadas distintas del triángulo, como `x1+e2`.
- de las 96 mezclas x+e, x+p o e+p sólo ciclan esas 36. Vuelven al blanco las 24 que
  caen en la misma coordenada y las 36 que tocan la coordenada 4. Los dobles volteos
  que involucran d o l vuelven todos.

**Los ciclos de 12** son correcciones rancias que se persiguen, porque la tubería de 3
pasos actúa sobre copias viejas de x.

- **En los seis ciclos, por periodo:** x cambia 6 veces (2 de esos cambios mueven dos
  bits a la vez), cada coordenada se conmuta exactamente 2 veces y hay 8 pulsos P.
- **El ritmo no es el mismo en todos:**
  - en 2 ciclos (cuenca de 235,008 estados cada uno), x cambia exactamente cada dos
    pasos;
  - en los otros 4 (199,680 estados cada uno), los cambios de x se separan alternando
    1 y 3 pasos.
- **Estado del análisis:** aquí sólo se describen; no se diseccionaron.

Las cifras de este apartado, del §6, de la rama C del §8 y del §11 las recalcula
[run_autopsy01_errata_check.py](run_autopsy01_errata_check.py), en sólo lectura
([resultado](artifacts/autopsy01_errata_check.json)).

**Condiciones necesarias medidas:**

- actualización síncrona;
- q basal o casi basal cuando llega la lesión;
- **a lo sumo una corrección en vuelo** (t1–t3);
- que el único pulso actúe.

## 17. Registro causal candidato

Está en [ETP_AUTOPSY_01_CAUSAL_RECORD_CANDIDATE.json](ETP_AUTOPSY_01_CAUSAL_RECORD_CANDIDATE.json).
No se modificó la base de datos del proyecto.

## 18. Lo que sigue sin saberse

- **Minimalidad global:** no está probada. ¿Hay una red de fan-in 2 con menos de 16
  auxiliares que cumpla la batería? Sólo se exploró la familia de testigos y las
  ablaciones simples.
- **El ciclo de 12:** su causa, «correcciones rancias», es por ahora descriptiva. Falta
  intervención.
- **El fallo asíncrono:** no se diseccionó por qué ocurre.
- **Radio ≥2 con fan-in 2:** no hay construcción; sólo cotas inferiores.
- **Claims heredados sin reverificar:** RAAC, RDDA, STARTUP y HEADROOM APD no se
  reverificaron aquí; sí PROJECTED APD y DISCOVERY-02/03.
- **H0–H3:** siguen abiertas. La autopsia explica la función de un circuito suministrado;
  no adjudica entityhood. El núcleo decisor del triángulo es un dato pertinente para
  H1 frente a H2.

## 19. Siguiente experimento único (propuesto, no ejecutado)

**ETP-EXP-05 · Refresco del síndrome rancio.**

- **Qué es:** en las corridas de segunda lesión en t1–t3 que caen al ciclo de 12, se
  sustituye en el instante de la segunda lesión el estado auxiliar por el que tendría
  una lesión fresca con la x actual. Se compara contra un sham.
- **Qué prueba:** si el ciclo desaparece, la condición «una sola corrección en vuelo»
  queda probada causalmente y no sólo observada. Eso cierra la última pieza de la
  terminación.
- **Relación con EXP-04A:** sigue preregistrado. Su criterio principal queda predicho
  por la ecuación `x' = x ⊕ p`; el valor que conserva está en su seguimiento secundario.

## 20. Criterios de aceptación

| # | pregunta | respuesta | evidencia |
| --- | --- | --- | --- |
| 1 | ¿Por qué ocurre la restauración? | decodificación por síndrome: el bit que discrepa de sus dos testigos se conmuta una vez | §4, §6, §13 |
| 2 | ¿De dónde sale la información del blanco? | de la mayoría en x. El circuito sólo da la ubicación, y la conmutación binaria da el sentido | §7 |
| 3 | ¿Qué reglas detectan el bit dañado? | los comparadores D detectan; los localizadores E, un AND de dos testigos, localizan | §5, §8 A1/A2/B |
| 4 | ¿Qué convierte la detección en una sola acción? | L más P: detector de flanco de subida | §6, §8 C/G |
| 5 | ¿Por qué termina? | pulso: por L; soporte: la x corregida anula el síndrome | §6; EXP-02 |
| 6 | ¿Qué es necesario y qué suficiente? | necesarios: los 17 auxiliares y cada compuerta. Suficientes: un solo evento E, o un solo P elegido desde fuera | §8, §12 |
| 7 | ¿Por qué el peso 2 queda fuera? | es el conjunto de empates del código; allí el localizador pierde la minoría única y decide el triángulo | §9 |
| 8 | ¿Exacta o funcional? | exacta en 21 bits (t7), precedida de restauración funcional (t4–t6) | §10 |
| 9 | ¿Cómo compila Φ con fan-in 2? | registros intermedios (aridad 3 en 2 capas), síndrome nulo en ambos códigos y compuerta temporal | §11 |
| 10 | ¿Qué ley lo describe? | `x(4) = x ⊕ ε(Hx)`, con `x_i(4) = maj3`; lazo con compuerta frente a lazo lineal | §13 |
| 11 | ¿Qué escala? | el decodificador matemático sí, con aridad 2t+1. La arquitectura de A sólo a radio 1, y siempre con el triángulo como núcleo | §14 |

## Claims permitidos

- **A_IMPLEMENTS_SINGLE_ERROR_SYNDROME_DECODING_OF_THE_REPETITION_CODE:** EXHAUSTIVE,
  sobre A × R_X × q*.
- **A_AUXILIARY_STATE_IS_TARGET_BLIND:** EXHAUSTIVE (complemento en 2²¹ estados;
  `I(q;blanco) = 0`).
- **A_DIRECTION_EQUALS_LOCATION_TIMES_TOGGLE:** INSTANCE_CAUSAL (familias C, D, F).
- **A_P_IS_A_RISING_EDGE_DETECTOR_OF_E:** EXHAUSTIVE en las trayectorias P-DATA;
  INSTANCE_CAUSAL (familia G).
- **A_EXACT_21_BIT_RESTORATION_WITHOUT_RESIDUAL_MEMORY:** sobre P-DATA y P-FULL.
- **A_TIE_BREAK_IS_TRIANGLE_MAJORITY:** EXHAUSTIVE sobre los 16 estados de x desde q*.

No se afirma entidad, proto-orgánulo, intención, finalidad ni generalización fuera del
alcance declarado.

# PRIMITIVO · Informe detallado de hallazgos de la autopsia causal

**Mecanismo de restauración, localización del error, pulso único, terminación y límites de escala**

*Versión corregida.* Sustituye a `Informe_PRIMITIVO_Autopsia_Causal_Hallazgos.docx`.

- **Cómo se verificó.** Se contrastaron sus 252 afirmaciones de dos formas:
  - lo que atañe a la autopsia, contra el código y los artefactos comiteados;
  - lo que atañe a los experimentos previos, contra sus informes y las comprobaciones del ledger (Apéndice E).
- **Resultado.** No se encontró ningún error grave.
- **Correcciones.** Se aplican **26 correcciones**, registradas en el
  [Apéndice C](#apéndice-c-fe-de-erratas-respecto-del-docx):
  - 3 incorrectas;
  - 9 imprecisas;
  - 9 incompletas;
  - 1 sin soporte;
  - 4 de terminología.
- **Otros cambios.** Hay además cambios de redacción que no eran errores, también listados en el Apéndice C.
- **Contenido añadido.** Se incorpora lo que el .docx dejaba fuera de la autopsia
  ([Apéndice D](#apéndice-d-contenido-de-la-autopsia-que-el-docx-omitía)).

| campo | valor |
| --- | --- |
| Estado científico | `CAUSAL_MECHANISM_IDENTIFIED` |
| Hipótesis central | H-CORE **confirmada**, con cuatro precisiones (§1) |
| Rama | `experiment/primitivo-causal-autopsy-01` |
| Worktree | `/home/wis/worktrees/primitivo-causal-autopsy-01` |
| Commits | `e4a72f4` (autopsia) + `b5bb8a7` (verificación de los registros de EXP-02/03) + `09153fa` (corrección de siete erratas del informe técnico) |
| Base | `f0fdf00`, del linaje científico que contiene `41fccbf` (DISCOVERY-02/03) |
| Alcance | espécimen A congelado × dinámica síncrona × lesiones DATA autorizadas (P-DATA, 8) y perturbaciones de un bit del estado completo (P-FULL, 42) |

**Objeto del informe.** Consolidar los hallazgos experimentales y matemáticos que
explican:

- por qué PRIMITIVO restaura una lesión de un solo bit;
- cómo identifica la coordenada afectada;
- por qué actúa una sola vez;
- por qué su organización auxiliar vuelve al reposo después de reparar;
- bajo qué condiciones deja de funcionar.

**Base de evidencia:**

- **Instrumentos:** EXP-01, EXP-02, EXP-03, DISCOVERY-02, DISCOVERY-03 y ETP-AUTOPSY-01.
- **Auditoría:** exhaustiva de la red reconstruida sobre los 2²¹ = 2.097.152 estados.
- **Intervenciones:** 320/320 predicciones cumplidas y 84/84 controles sham idénticos a la trayectoria natural.
- **Minimalidad:** 366 variantes de A y 81 grafos de testigos.
- **Escala:** a n = 3..8.
- **Variantes:** 18 variantes cercanas.
  - 17 tenían predicción escrita antes de correr, y se cumplieron 17/17.
  - La 18.ª, la segunda lesión durante la reparación, es exploratoria y no tiene predicción.

---

## 1. Resumen ejecutivo

> **Resultado principal.** PRIMITIVO implementa un decodificador dinámico de un solo
> error sobre las palabras de código {0000, 1111}. La dirección de la reparación no
> viene de un objetivo externo:
>
> - la identidad del blanco está en la redundancia de X, es decir, en la mayoría;
> - la cadena D → E → L/P sólo extrae la **ubicación** del bit dañado;
> - el actuador `X ⊕ P` convierte esa ubicación en **dirección** al conmutar el valor
>   actual del bit.

**El mecanismo completo de restauración:**

- Un bit lesionado queda en minoría frente a sus testigos sanos.
- Los comparadores D convierten los desacuerdos entre bits de X en un síndrome.
- El localizador E marca la única coordenada que discrepa de sus dos testigos.
- El registro L conserva E durante un paso.
- El pulso P es un detector de flanco de subida de E y produce un único pulso.
- La regla `x_i' = x_i ⊕ p_i` conmuta solamente el bit localizado.
- Una vez corregido X, el síndrome deja de sostenerse y el estado auxiliar vuelve a
  reposo (`q* = 0¹⁷`).
- La reparación de X es funcional en **t4**, y la restauración del estado global de 21
  bits es exacta en **t7**.

**H-CORE queda confirmada con cuatro precisiones:**

1. **Testigos fijos.** Cada bit se compara con dos testigos fijos, no con una lectura
   conjunta de los tres bits sanos: de los tres, cada localizador usa sólo dos.
2. **La dirección no se extrae de los bits sanos.** El estado auxiliar es ciego al
   blanco, por tres pruebas:
   - `I(q_t; blanco) = 0` en todo t de las trayectorias P-DATA;
   - G conmuta con el complemento de x en los 2²¹ estados;
   - las lesiones complementarias comparten toda la trayectoria de q.

   La dirección es la ubicación que marca E, aplicada como conmutación del valor
   actual.
3. **Dos terminaciones distintas.**
   - La del pulso ocurre en t4 y la produce L.
   - La del soporte auxiliar ocurre entre t5 y t7, porque la x corregida anula el
     síndrome.
4. **Núcleo decisor.** El triángulo {x1, x2, x3} es el núcleo decisor y x4 es seguidor.
   Desde q*, el código final es siempre `maj(x1,x2,x3)⁴`. En R_X esto coincide con el
   código más cercano, y sólo se nota en los empates de peso 2.

**El hallazgo más general.** Una conducta global que no puede expresarse con reglas de
salida de aridad esencial ≤ 2 puede **compilarse** mediante una secuencia temporal de
operaciones locales de fan-in 2. En PRIMITIVO, la composición causal realiza una
decisión efectiva de aridad 3. Por eso la restauración no contradice la no
extensibilidad del mapa proyectado Φ. La sortea con tres recursos (§11):

- **profundidad**: los intermediarios D y E, la memoria de un paso L y el actuador de un
  disparo P;
- **un estado auxiliar cuyo reposo es el mismo en los dos códigos**: esto permite usar
  operaciones no monótonas (XOR) sin romper los puntos fijos;
- **una política temporal de actuación**, que convierte un nivel en un único evento.

| pregunta | respuesta experimental |
| --- | --- |
| ¿Por qué aparece la respuesta? | La lesión en X genera desacuerdos que entran por X→D y construyen el síndrome. |
| ¿Por qué se repara el bit correcto? | E identifica la única coordenada que discrepa de sus dos testigos. P no aporta dirección propia, y la conmutación binaria da el sentido. |
| ¿Por qué actúa una sola vez? | L retrasa E un paso, y `P = E ∧ ¬L` convierte el inicio de E en un único pulso. |
| ¿Por qué termina? | El pulso termina porque L alcanza a E. El soporte termina porque, al corregirse X, desaparece la fuente del síndrome: D, E y luego L vuelven a cero. |
| ¿Dónde falla? | Ver la lista inmediatamente debajo. |

Dónde falla:

- **Errores dobles.**
  - En DATA, desde q*, son empates de peso 2 y la mitad va al código opuesto.
  - En el estado completo hay 420 perturbaciones de dos bits de los dos blancos (210 en
    cada uno), y 54 no vuelven: 18 van al código opuesto y 36 caen en el ciclo de 12, la
    mitad en cada blanco (9 y 18) (§13).
- **Segunda lesión con una corrección en vuelo (τ = 1–3):** 12 de 32 corridas en cada τ
  entran en un ciclo de 12; todas son segundas lesiones sobre otro bit del triángulo.
- **Relesión del mismo bit en τ = 4:** el pulso ya se gastó. E sigue alto, no hay flanco
  nuevo ni reintento, y la alarma queda enclavada (8 de 32).
- **Pulso perdido:** no hay reintento; P(restauración) = 1 − pérdida.
- **Fallo permanente de un bit:** el pulso se gasta y la alarma queda enclavada.
- **Actualización asíncrona:** restaura ~25 %.
- **Fuera de la región autorizada del espacio completo:**
  - predominan los ciclos de 12 (60,50 %);
  - el 0,93 % cae en 14 alarmas enclavadas.

## 2. Alcance y preguntas científicas

Este informe no trata de certificaciones, Gate A, A1b ni réplicas de gobernanza. Su
alcance es estrictamente causal: explicar el fenómeno ya observado y delimitar su
dominio de validez.

La separación de pistas es estructural, no declarativa:

- la rama no contiene `experiments/primitivo_n2/` (pista Gate A) ni
  `docs/LEVEL18_ANALISIS_CAUSA_RAIZ.md`;
- ninguna de las dos pistas se tocó (D-17 del registro de decisiones).

Las preguntas rectoras son éstas:

1. ¿Qué condición inicia el episodio transitorio?
2. ¿Qué mecanismo contiene la información necesaria para seleccionar la dirección
   correcta de reparación?
3. ¿Qué reglas localizan el bit lesionado y cuáles solamente ejecutan la corrección?
4. ¿Por qué la acción correctiva ocurre una sola vez?
5. ¿Por qué la organización auxiliar vuelve a q* después de la corrección? Hay dos
   terminaciones: la de pulso, por L, y la de soporte, porque la x corregida anula el
   síndrome.
6. ¿La restauración final es funcional o exacta en todo el estado interno?
7. ¿Por qué el mapa global de restauración no puede implementarse directamente con
   aridad ≤ 2 y, sin embargo, la red sí puede realizarlo?
8. ¿Cuáles son la frontera de fallo, la minimalidad conocida y el potencial de
   escalamiento?

> **Criterio de cierre causal.** El mecanismo se considera identificado sólo si se
> cumplen dos condiciones:
>
> - la lectura de ecuaciones, las intervenciones, los controles sham y los resultados de
>   frontera convergen sobre la misma explicación;
> - la detección, la localización, la actuación y la terminación pueden disociarse.

## 3. Linaje experimental y cierre de los tres eslabones

La autopsia no empieza desde cero: tres experimentos previos ya habían aislado onset,
acción y terminación.

**Cómo se construyó el ledger.** Se leyeron los artefactos comiteados, sin
regenerarlos (`autopsy01_causal_ledger.csv`).

- Las 8 trazas P-DATA comiteadas de PRE-01 se reproducen bit a bit.
- El punto fijo del corte de EXP-01 se reproduce 8/8 con el runner de la autopsia.
- El seguimiento `b5bb8a7` cerró un hueco metodológico: EXP-02 y EXP-03 dejaron de
  aceptarse por su prosa y se contrastaron contra sus CSV.
  - Sus filas registradas coinciden con los informes.
  - Las 64 comparaciones de fase de EXP-03 son exactas.
  - Los dos bloqueos de EXP-03, el persistente y el transitorio, se reprodujeron 8/8 con
    la maquinaria de la autopsia.

El veredicto no cambió.

| eslabón | intervención / evidencia | resultado | qué prueba | qué no prueba |
| --- | --- | --- | --- | --- |
| BASELINE (PRE-01) | Ninguna: atlas basal, más P-FULL (volteo de cada coordenada en cada blanco) | Onset en t1; D, E, L y P en t1, t2, t3 y t3; x corregida en t4; estado completo en t7. P-FULL 42/42, con latencia máxima 9 | Las trayectorias exactas y las clases de respuesta | La necesidad causal de cada parte |
| ONSET | EXP-03: sustitución del padre DATA lesionado en las D incidentes, transitoria (sólo t0→t1) y persistente, ambas reproducidas 8/8. Sham no-op espacial (sustitución sobre un padre DATA que ya vale su blanco): 8/8 idéntico al natural | **Transitoria:** la cadena se desplaza un paso (onset en t2, DATA en t5, completo en t8; 64/64 comparaciones de fase exactas). **Persistente:** **impide el onset**. x queda perturbada con q = q* (D = E = L = P = 0), una configuración fija que sostiene la intervención y no un punto fijo natural de A (8/8) | La transmisión X→D es necesaria para el onset P-DATA, y el onset se regenera desde la perturbación DATA que sigue presente. Que la x lesionada **sostiene** D/E/L lo muestran EXP-01 + EXP-02, no EXP-03 | Qué calculan D o E, ni de dónde sale la dirección |
| ACCIÓN | EXP-01: corte de la arista `p_i(t3) → x_i(t4)`, con shams temporal y espacial. El punto fijo del corte se reproduce 8/8 con el runner de la autopsia | La reparación desaparece. El sistema queda en un punto fijo no objetivo: x lesionada, D/E/L altos, P = 0 (8/8). Los 16 shams son idénticos al natural | P→X es el canal causal necesario de la actuación física, y está aguas arriba de la terminación normal | Qué selecciona la coordenada, ni por qué el pulso es único |
| TERMINACIÓN | EXP-02: desde el punto fijo del corte (t4), se escribe sólo x = blanco y se conserva q. Sham de escritura no-op | Se reingresa al estado natural de t4. D cae en t5, E en t6 y L en t7; P ya estaba en 0 en t4 (8/8). El sham conserva el punto fijo | La restauración de x media la terminación de D/E/L (terminación de soporte). P termina por L aunque x no se restaure (terminación de pulso) | La función lógica del circuito completo |
| MAPA PROYECTADO | DISCOVERY-02/03, ejecutados en la autopsia (antes su procedencia era `RESEARCHER_SUPPLIED`), y enumeración de extensiones directas | Φ existe en R_X. Como mapa, envía cada estado directamente a su código y no tiene ciclos fuera de los blancos. Ninguna función de aridad esencial ≤ 2 lo extiende (0 extensiones). DISCOVERY-03 (N = 4): ninguna red sólo-X de fan-in ≤ 2 con ambos centros fijos restaura todos los errores de radio 1 en ≤ 14 pasos; da 0 candidatos con aridad máxima por coordenada 1 o 2, tanto para los centros 0000/1111 (distancia 4, los de A) como para 0000/1110 (distancia 3). DISCOVERY-02 (n = 3, centros 000/111, hasta 6 pasos) también da 0 | El comportamiento global es realizable, pero requiere compilación causal | Cómo lo compila la red con auxiliares |

**La red auditada es la congelada.** La red reconstruida que usa la autopsia coincide con
el `step` congelado en los 2.097.152 estados del sistema de 21 bits. La maquinaria de
análisis no estudia una aproximación, sino una reconstrucción exhaustivamente
equivalente.

Sobre esa tabla completa se observó, sin inferirlo del código:

- **Entradas esenciales:** las de cada coordenada son exactamente sus padres declarados,
  con fan-in máximo 2.
- **Complemento:** complementar x conmuta con G en todos los estados.
- **Automorfismo:** la permutación (x1 x2), con su reetiquetado inducido, es un
  automorfismo global.
- **Puntos fijos:** hay exactamente 16, los 2 blancos y 14 «alarmas enclavadas».

## 4. El dominio restaurador como problema de decodificación

Los dos estados estables de interés forman el conjunto de palabras de código
C = {0000, 1111}, el código de repetición lineal [4,1,4]. El dominio autorizado R_X
contiene exactamente esos dos centros y los ocho estados a distancia de Hamming 1, así
que R_X es la unión de dos bolas de radio 1.

```text
C   = {0000, 1111}
R_X = B_H(0000, 1) ∪ B_H(1111, 1)
Φ(x) = argmin_{c ∈ C} d_H(x, c),   para x en R_X
```

**Distancias y cosets:**

- **Radio de corrección.** La distancia mínima entre las dos palabras es **4**, así que
  el radio de corrección unívoca es `t = ⌊(4−1)/2⌋ = 1`. La capacidad de detección es 3.
- **Unicidad en R_X.** Toda lesión autorizada tiene un único centro más cercano, a
  distancias 1 y 3.
- **Empates.** Los seis estados de peso 2 están a distancia 2 de ambos centros y forman
  la frontera de empate. Las bolas cubren 10 de 16 estados, y como d_min es par quedan
  esos 6 empates.
- **Síndrome.** Los 5 comparadores evalúan controles de paridad de rango 3 sobre GF(2).
- **Cosets.** Hay 8 cosets:
  - 5 tienen líder único, un error de peso 0 o 1;
  - 3 son cosets de peso 2 con dos líderes: son los empates.

| peso de x | cantidad | relación con C | estado causal |
| ---: | ---: | --- | --- |
| 0 | 1 | centro 0000 | blanco estable |
| 1 | 4 | una lesión de 0000 | restauración unívoca hacia 0000 |
| 2 | 6 | empate entre 0000 y 1111 | frontera: no existe centro único |
| 3 | 4 | una lesión de 1111 | restauración unívoca hacia 1111 |
| 4 | 1 | centro 1111 | blanco estable |

> **Interpretación.** La restauración autorizada equivale a decodificar una palabra del
> código de repetición de longitud 4 bajo una sola inversión. Por eso los tres bits no
> lesionados contienen información suficiente para inferir el centro sin un blanco
> externo: la información está *disponible*. La red *usa* sólo dos de esos tres bits
> por localizador.

## 5. Ecuaciones y descomposición del mecanismo

La arquitectura usa 4 bits de datos X y 17 auxiliares: 5 D, 4 E, 4 L y 4 P. En la
implementación congelada las ecuaciones síncronas son éstas; cada lado derecho lee sólo
el estado en t.

```text
d12' = x1 ⊕ x2    d13' = x1 ⊕ x3    d23' = x2 ⊕ x3
d14' = x1 ⊕ x4    d24' = x2 ⊕ x4                    (no existe d34)
e1' = d12 ∧ d13   e2' = d12 ∧ d23   e3' = d13 ∧ d23   e4' = d14 ∧ d24
l_i' = e_i
p_i' = e_i ∧ ¬l_i
x_i' = x_i ⊕ p_i
```

Testigos de cada localizador: `x1←{x2,x3}`, `x2←{x1,x3}`, `x3←{x1,x2}` y `x4←{x1,x2}`.

| familia | función causal | lo que no hace |
| --- | --- | --- |
| X, datos | Contiene el patrón redundante, que es la identidad del blanco con redundancia 4×, y recibe la corrección física. | No contiene una variable separada de objetivo. |
| D, comparadores de desacuerdo | Convierte los desacuerdos entre pares de X en un síndrome distribuido, invariante al complemento y ciego al blanco. | No decide por sí solo qué coordenada debe cambiar. |
| E, localizadores de error | Marca la coordenada que discrepa simultáneamente de sus dos testigos. En R_X es el indicador exacto del bit dañado. | No ejecuta la reparación física ni lleva dirección. |
| L, registro de un paso | Conserva E un paso (`L(t) = E(t−1)`): es la memoria temporal mínima. | No almacena el blanco. |
| P, pulso de un disparo | Extrae el flanco de subida de E (`P(t+1) = E(t) ∧ ¬E(t−1)`) y genera un único pulso. | No tiene dirección propia: ejecuta la ubicación que marca E. |
| X ⊕ P, actuador de conmutación | Invierte el bit señalado. Aquí nace la dirección: ubicación × conmutación del valor actual. | No lee el valor de la mayoría. |

**Ubicación y dirección se separan así:**

- **El blanco lo fija X.** Lo fija la mayoría contenida en X, y ningún auxiliar lee ese
  valor: `I(q_t; blanco) = 0` en todo t.
- **Los auxiliares sólo llevan la ubicación.** Extraen y temporizan la ubicación del bit
  discordante: `I(q_t; posición) = 2` bits en t1–t6.
- **El sentido lo da la conmutación.** Resulta de conmutar ese bit: `x_k ⊕ 1 = ¬x_k = m`,
  donde m es el valor de la mayoría.
- **Mismo pulso, efecto opuesto.** El mismo pulso `p_k` produce 1→0 desde una lesión de
  0000 y 0→1 desde una de 1111.

**Búsqueda de objetivo u oráculo, por observación de la tabla completa y no por grep:**

- **Variable de blanco:** no hay ninguna. En ambos blancos `q = 0¹⁷`, así que sólo x1..x4
  difieren entre ellos.
- **Recompensa, token de meta o entrada externa:** no hay ninguna. Cada coordenada lee
  exactamente sus ≤ 2 padres, y G es una tabla sobre los 21 bits.
- **Interruptor de dirección codificado:** no hay ninguno. G conmuta con el complemento
  en los 2²¹ estados, así que toda reparación hacia 0000 tiene su espejo hacia 1111.
- **Reloj:** no hay ninguno. La tabla es homogénea en el tiempo.

**Clasificación supplied/generated.**

- El decodificador está **suministrado por diseño** (SUPPLIED).
- Su función es consecuencia lógica de las reglas (IMPLICIT_IN_RULES).
- Lo generado dinámicamente es sólo el patrón D/E/L/P de cada trayectoria, que es
  DYNAMICALLY_GENERATED y TRAJECTORY_CONTINGENT porque depende de la posición lesionada.

## 6. Las ocho lesiones autorizadas y su síndrome

En las ocho lesiones de un solo bit sólo llega a activarse un localizador, e_k, el de la
coordenada lesionada.

- **Cuándo está alto:** de t2 a t5, 4 pasos (patrón de e_k por paso: `001111000`).
- **Ningún otro:** en ningún paso de la trayectoria se activa otro E_i.
- **Sin E:** en t0, t1, t6 y t7 no hay ningún E activo.
- **Qué mide la comprobación registrada:** en cada paso, el conjunto de E activos es ∅
  o {e_k}.

La tabla da el patrón de D en t1, en el orden (d12, d13, d23, d14, d24), obtenido de la
dinámica real.

| lesión (x) | blanco | bit dañado | D en t1 | comparadores activos | E en t2 | P en t3 | X en t4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 0000 | x1 | 11010 | d12, d13, d14 | e1 | p1 | 0000 |
| 0100 | 0000 | x2 | 10101 | d12, d23, d24 | e2 | p2 | 0000 |
| 0010 | 0000 | x3 | 01100 | d13, d23 | e3 | p3 | 0000 |
| 0001 | 0000 | x4 | 00011 | d14, d24 | e4 | p4 | 0000 |
| 0111 | 1111 | x1 | 11010 | d12, d13, d14 | e1 | p1 | 1111 |
| 1011 | 1111 | x2 | 10101 | d12, d23, d24 | e2 | p2 | 1111 |
| 1101 | 1111 | x3 | 01100 | d13, d23 | e3 | p3 | 1111 |
| 1110 | 1111 | x4 | 00011 | d14, d24 | e4 | p4 | 1111 |

**Por qué se activa exactamente un E.**

- Sea k la única coordenada minoritaria. Entonces `e_i = [x_i ≠ x_a ∧ x_i ≠ x_b]`,
  donde a y b son los testigos de i.
- **`e_k = 1`**, porque los dos testigos de k son sanos.
- **`e_i = 0` para i ≠ k**, porque x_i tiene el valor mayoritario y a lo sumo uno de sus
  testigos es k.
- **Generalidad:** el argumento vale para cualquier asignación de testigos. La
  comprobación exhaustiva da **81 de 81** asignaciones exactas en R_X.

**Información disponible pero no usada.** En las lesiones de x1 y x2 hay un tercer
comparador activo, d14 o d24. Ninguno de los dos entra en e1 ni en e2: registran el
daño, pero no se usan para localizarlo (§8, A1).

**La coordenada correctiva no la selecciona P: P hereda la selección de E.** Lo confirma
el control de localizador erróneo (§8, D):

- con D amputada, P conmuta el bit que marque E, aunque sea el equivocado;
- con la red intacta, el bit sano conmutado por error se detecta y se deshace.

## 7. Trayectoria temporal: detectar, localizar, pulsar y terminar

Partiendo de auxiliares en reposo y una lesión autorizada en X, la secuencia síncrona
tiene dos terminaciones:

- primero termina el pulso correctivo;
- después se vacía el soporte que todavía refleja el estado lesionado previo.

Estado completo de la lesión `0000:x1`:

| t | x | D (d12 d13 d23 d14 d24) | E | L | P | auxiliares activos | lectura |
| ---: | --- | --- | --- | --- | --- | ---: | --- |
| 0 | 1000 | 00000 | 0000 | 0000 | 0000 | 0 | Existe la perturbación, pero todavía no el síndrome. |
| 1 | 1000 | 11010 | 0000 | 0000 | 0000 | 3 | Los desacuerdos de X se convierten en síndrome. |
| 2 | 1000 | 11010 | 1000 | 0000 | 0000 | 4 | Se localiza la coordenada que discrepa de sus testigos. |
| 3 | 1000 | 11010 | 1000 | 1000 | 1000 | 6 | El flanco de subida produce el único pulso correctivo; L ya registra E. |
| 4 | **0000** | 11010 | 1000 | 1000 | 0000 | 5 | X ya está corregida y P = 0. Es la restauración funcional; D todavía lee el x de t3. |
| 5 | 0000 | **00000** | 1000 | 1000 | 0000 | 2 | D = 0. E y L siguen activos. |
| 6 | 0000 | 00000 | **0000** | 1000 | 0000 | 1 | E = 0. L sigue activo. |
| 7 | 0000 | 00000 | 0000 | **0000** | 0000 | 0 | L = 0. Estado global en reposo: restauración exacta de los 21 bits, sin memoria residual. |

Las ocho lesiones tienen la misma cronología: onset en t1, E en t2, L y P en t3, x en t4
y estado completo en t7.

**Lo que se comprueba sobre las trayectorias:**

- **`L(t) = E(t−1)`:** 256 de 256 comprobaciones.
- **`P(t+1) = E(t) ∧ ¬E(t−1)`**, es decir, P es el flanco de subida de E: 224 de 224.
- **El bloque de E del bit dañado es contiguo y dura 4 pasos (t2–t5)**, así que tiene un
  solo flanco de subida y produce un solo pulso.
- **Por qué E dura 4 pasos:** D lee x con un paso de retraso y E lee D con otro, de modo
  que la corrección de t4 llega a D en t5 y a E en t6. Basta una memoria de un paso,
  porque el bloque de E es contiguo.

> **Dos terminaciones distintas.** El pulso termina antes que el episodio auxiliar
> completo: P termina en t4 porque L ya alcanzó a E. El vaciado de D, E y L necesita
> otra cosa: que la x corregida recorra **hacia adelante** la misma tubería X→D→E→L,
> con D cayendo en t5, E en t6 y L en t7. Confundir ambos tiempos ocultaba parte del
> mecanismo.

## 8. Evidencia intervencional

La explicación no descansa sólo en la inspección de ecuaciones. Las intervenciones
permiten asignar roles causales, y no sólo correlaciones temporales.

**Resultados:**

- 320 corridas;
- **320/320 predicciones cumplidas**;
- **84/84 shams no-op idénticos** a la trayectoria natural.

**Cómo se trataron las predicciones:**

- quedaron escritas en los instrumentos antes de su primera ejecución, y cada corrida
  registra si se cumplió;
- ninguna se modificó tras ver resultados;
- **no se sellaron en un commit previo**: ETP-AUTOPSY-01 es una serie de análisis, no un
  preregistro (D-18), así que el 320/320 no es un resultado preregistrado;
- en este linaje sólo está preregistrado EXP-04A, que no se ejecutó;
- una verificación se añadió después: la ley del triángulo para n = 3..8 (§14), evaluada
  sobre corridas ya producidas.

**Semántica de las intervenciones:**

- clamp persistente o sustitución de una regla (ablación);
- escritura puntual en un instante;
- G sin cambios fuera de lo intervenido.

| familia | brazo | n | observación | inferencia |
| --- | --- | ---: | --- | --- |
| A1 · ablación de un comparador (`d ≡ 0`) | el comparador es uno de los dos que lee E_k | 16 | La lesión queda **detectada pero no localizada**: D parcialmente alto, ningún E, ningún pulso, punto fijo no-código | No hace falta «un número suficiente de comparadores», sino **los dos testigos concretos** de cada E_k |
| | `d14 ≡ 0` o `d24 ≡ 0` con lesión en x1 o x2 | 4 | Reparación normal | La información está disponible pero **no se usa causalmente** |
| | shams: el comparador vale 0 en esa trayectoria | 20 | Idénticos al natural | — |
| A2 · localizador con un solo testigo | `e_i` lee un único comparador | 64 | 48 reparaciones normales. En 16, la lesión del otro extremo también dispara e_i: el bit sano se conmuta y queda enclavado (dos pulsos, sin retorno) | El AND de **dos** testigos es necesario para la especificidad |
| B · ablación del localizador (`e_k ≡ 0`) | localizador del bit dañado | 8 | La reparación falla aunque persista el desacuerdo | Localizar es causalmente necesario antes de actuar |
| | shams | 24 | Idénticos | — |
| C · rescate del localizador (D amputada) | sin inyección | 8 | Lesión fija con q = q* | — |
| | un único evento `e_k = 1` en t2 | 8 | x reparada en t4 y estado completo en t4 (1 pulso) | **Un solo evento E basta** para toda la secuencia posterior |
| | `e_k` sostenido desde t2 | 8 | Exactamente 1 conmutación (x_k en t4) y x restaurada al blanco. Pero q no vuelve a q*: E_k y L_k quedan en 1 mientras dura la sujeción de E (D amputada = 0; P = 0). No es una alarma enclavada en el sentido del glosario (allí x es errónea); es un estado que sostiene la intervención | El flanco convierte incluso un E atascado en una sola acción |
| | sham | 8 | Idéntico | — |
| D · localizador erróneo | red intacta, `e_j` (j ≠ k) en t2 | 24 | En t4 se repara x_k y además **se conmuta por error x_j**. La propia red lo detecta y lo deshace en t8, y el estado completo vuelve en t11 (3 pulsos) | El circuito corrige su propio error en una segunda pasada |
| | D amputada, `e_j` en t2 | 24 | Doble error permanente | El tramo posterior **ejecuta la ubicación que reciba** |
| | blanco sano, `e_j` en t0 | 8 | 2 conmutaciones y estado completo en t9 (la clase E de P-FULL) | — |
| E · ablación del actuador (`p_k ≡ 0`) | pulso del bit dañado | 8 | D, E_k y L_k altos, x lesionada: alarma enclavada | La detección y la localización están intactas; falta la acción. P→X es necesario (confirma EXP-01, que cortó sólo la arista en t3) |
| | shams | 24 | Idénticos | — |
| F · rescate del actuador (E amputada) | sin inyección | 8 | Lesión fija con D alto | — |
| | `p_k` correcto en t3 | 8 | x en t4 y estado completo en t5 | Basta físicamente, pero la elección vino de fuera |
| | `p_j` erróneo en t3 | 24 | Doble error permanente | **P no tiene dirección propia**: basta para actuar, no para decidir |
| | sham | 8 | Idéntico | — |
| G · sin compuerta de un disparo | `P = E` | 8 | Ciclo de periodo 15 con x en movimiento | La compuerta temporal convierte un lazo oscilatorio en una acción discreta que se detiene |
| | X lee E directamente (sin L ni P) | 8 | Ciclo de periodo 7 | — |

**Lo que las intervenciones disocian:**

- **Detección:** D.
- **Localización:** E. D sin E no repara.
- **Compuerta temporal:** L/P, que convierten el nivel en un evento.
- **Actuación:** P→X, que ejecuta sin dirección propia.
- **Terminación:** la de pulso por L; la de soporte por la x corregida.

**Solapamiento declarado con EXP-04A.** Los brazos «localizador erróneo» (D) y «pulso
erróneo» (F) anticipan parte del seguimiento secundario de EXP-04A, que sigue
preregistrado y sin ejecutar (§19).

## 9. Frontera de peso 2 y ruptura de la unicidad

Los seis estados de peso 2 no pertenecen al dominio autorizado porque son equidistantes
de 0000 y 1111. En la arquitectura concreta estos empates no producen ciclo ni atasco:
los resuelve la estructura de testigos.

| x | partición | D en t1 | E en t2 | pulsos | final | t de reposo |
| --- | --- | --- | --- | --- | --- | ---: |
| 1100 | 12\|34 | 01111 | e3, e4 | p3 y p4 en t3 | 1111 | 7 |
| 0011 | 12\|34 | 01111 | e3, e4 | p3 y p4 en t3 | 0000 | 7 |
| 1010 | 13\|24 | 10110 | e2 | p2 en t3; p4 en t7 | 1111 | 11 |
| 0101 | 13\|24 | 10110 | e2 | p2 en t3; p4 en t7 | 0000 | 11 |
| 0110 | 14\|23 | 11001 | e1 | p1 en t3; p4 en t7 | 1111 | 11 |
| 1001 | 14\|23 | 11001 | e1 | p1 en t3; p4 en t7 | 0000 | 11 |

**Cómo se resuelven:**

- **Cuándo dispara E_i:** sólo si sus dos testigos están en la clase opuesta a la suya.
  Por eso no hay un bit minoritario único.
  - En la partición 12|34 disparan dos localizadores a la vez, en una ronda.
  - En las otras dos dispara uno solo; el estado pasa a peso 1 o 3 y se corrige en una
    segunda ronda.
- **Ley del desempate:** desde q*, el código final es **`maj(x1, x2, x3)⁴` para los 16
  estados de x**.
- **Simetría:** se conservan la del complemento y la de (x1 x2); no hay simetría S4.
- **Dos errores DATA simultáneos sobre un blanco:** son 12 casos. 6 vuelven al código
  original y 6 van al opuesto, que son los pares internos al triángulo.

Este hecho importa por dos razones:

- **La geometría de Hamming no basta.** El comportamiento fuera de R_X no lo determina
  sólo la geometría de Hamming: interviene la asimetría del grafo de testigos.
- **Es una frontera causal, no un caso excluido arbitrariamente.** Es exactamente donde
  la prueba «mis dos testigos discrepan de mí» deja de identificar una minoría única, y
  ahí «reparación» deja de ser intrínseca: no existe un centro correcto unívoco sin una
  convención estructural adicional.

> **No sobreinterpretar.** En peso 2, llegar a uno de los centros no equivale a haber
> corregido un error frente a una verdad de referencia. La red resuelve un empate según
> su topología; no recupera información que ya no es unívocamente reconstruible.

## 10. Restauración funcional frente a restauración exacta

La restauración ocurre en dos niveles.

- **Funcional (t4).** X recupera el blanco en t4, en las 8 lesiones: la función externa
  ya está recuperada.
- **Ventana t4–t6.** El estado interno todavía contiene residuos temporales del
  episodio, que desaparecen de forma determinista.
- **Exacta (t7).** En t7 el estado de 21 bits es idéntico, bit a bit, al previo a la
  lesión (8/8).

**Trayectorias.** Hay cuatro trayectorias internas distintas de q, una por posición
lesionada, y las lesiones complementarias las comparten. Cada una converge al estado
restaurado de su blanco. Es degeneración de caminos, no del estado final.

- **Sin histéresis ni memoria residual:** el estado final es el de un sistema nunca
  lesionado, y G es markoviana en los 21 bits.
- **Clasificación:** restauración exacta del estado, precedida por restauración
  funcional durante 3 pasos, con diversidad de trayectorias. No es simple equivalencia
  funcional.
- **P-FULL:** 42 de 42 perturbaciones de un bit del estado completo vuelven de forma
  exacta.
- **Perturbaciones de dos bits:** vuelven 366 de 420 (§13).

## 11. Cómo fan-in 2 compila una decisión global

**Lo que quedó descartado.**

- **Extensión directa.** Ninguna función de aridad esencial ≤ 2 extiende Φ en R_X: la
  enumeración da 0 extensiones.
  - Φ_i fija 10 de los 16 estados de x y deja libres los otros 6, así que admite
    2⁶ = 64 extensiones por coordenada.
  - De ellas, 4 tienen aridad 3 (la mayoría de cada una de las 4 ternas) y 60 tienen
    aridad 4.
  - La aridad mínima es, por tanto, 3.
- **Redes sólo-X iteradas (DISCOVERY-03).** Recorrió todas las redes sólo-X en que cada
  coordenada tiene aridad esencial ≤ d_max, con d_max = 1 y d_max = 2 (fan-in ≤ 2).
  - Cada red deja fijos sus dos centros y se itera hasta 14 pasos.
  - Se probaron dos pares de centros: {0000, 1111}, a distancia 4 (clave `C4`, el par de
    A), y {0000, 1110}, a distancia 3 (clave `C3`).
  - Ninguna red lleva cada error de radio 1 a su propio centro: 0 candidatos en los
    cuatro casos.
  - Esto incluye como caso particular cualquier extensión directa, que restauraría en un
    paso.
- **DISCOVERY-02 (n = 3):** también da 0 candidatos.
- **Cambio de procedencia.** Hasta la autopsia, DISCOVERY-03 = `NO_LOCAL_SOLUTION` era
  un claim de procedencia `RESEARCHER_SUPPLIED`. Ahora está verificado ejecutando los
  instrumentos en sólo lectura, con la salida registrada en
  `artifacts/autopsy01_compilation.json`.

**Qué deja disponible iterar.** Con los códigos de A (0000 y 1111), una regla sólo-X de
fan-in ≤ 2 que deja fijos los dos sólo puede ser `x_a`, `x_a ∧ x_b` o `x_a ∨ x_b`. Son
16 reglas por coordenada, todas monótonas, y ninguna es una XOR. La monotonía no explica
por sí sola el fracaso, por dos razones:

- maj3, que A realiza en t4, también es monótona y extiende Φ en un paso;
- con los centros 0000/1110 (`C3`), el espacio sólo-X sí contiene reglas no monótonas
  (con d_max = 2, 6 de 18, 6 de 18, 6 de 18 y 12 de 17 por coordenada), y DISCOVERY-03 da
  igualmente 0 candidatos.

Lo que descarta las redes sólo-X de fan-in ≤ 2 es la búsqueda exhaustiva de
DISCOVERY-03, no un argumento de monotonía.

**Cómo lo evita la red.** Distribuye el cálculo en capas y tiempos sin violar la
restricción local: dos comparaciones XOR de fan-in 2 alimentan un AND de fan-in 2, y el
resultado efectivo evalúa una condición sobre tres bits.

```text
fan-in local ≤ 2  +  composición en profundidad y tiempo  →  aridad efectiva 3
x(4) = x(0) ⊕ ε(H x(0))            desde (x0, q*)
x_i(4) = maj(x_i, x_a(i), x_b(i))  en los 16 estados de x
```

- **H** es el operador de síndrome que forman los comparadores D.
- **ε** es el localizador: `ε_i = s_{i,a(i)} ∧ s_{i,b(i)}`, que vale 1 si y sólo si x_i
  discrepa de sus dos testigos. No siempre marca un solo bit:
  - en los 8 estados de peso 1 y 3 marca sólo el bit dañado;
  - en 0000 y 1111 vale 0000;
  - en 0101, 0110, 1001 y 1010 marca un solo bit;
  - en 0011 y 1100 vale 0011, porque disparan e3 y e4 a la vez (§9).

  En total hay 12 estados con un bit, 2 con ninguno y 2 con dos, y la ley `x(4) = x ⊕ ε(Hx)`
  se cumple en los 16.

La ecuación resume el episodio desde el reposo: el estado de datos se corrige con esa
máscara, sea de uno, cero o dos bits.

**La parte temporal no es decorativa.** Aquí `w(t)` es el indicador de que el bit dañado
está erróneo. Sin la compuerta de un disparo el lazo es lineal sobre GF(2):

- con `P = E`, `w(t+1) = w(t) ⊕ w(t−3)`: polinomio `z⁴+z³+1`, primitivo, periodo 15;
- con X leyendo E, `w(t+1) = w(t) ⊕ w(t−2)`: polinomio `z³+z²+1`, periodo 7.

Ambos periodos se observaron exactos. Con la compuerta,
`w(t+1) = w(t) ⊕ (w(t−3) ∧ ¬w(t−4))`: una sola inversión, y luego se detiene.

**Qué recursos aportan los auxiliares.** No hay una regla global escondida. Hay tres
recursos:

1. **Registros de resultados intermedios.** Guardan el XOR y luego el AND, lo que da
   aridad 3 en 2 capas. Es la profundidad mínima posible con fan-in 2 (`⌈log2 3⌉ = 2`).
2. **Un sistema de coordenadas que vale 0 en ambos códigos, el síndrome.** Permite
   operaciones no monótonas (XOR) sin romper los puntos fijos, algo imposible para reglas
   sólo-X con los códigos de A (0000/1111). Con otros centros, como 0000/1110, sí hay
   reglas XOR sólo-X que dejan fijos ambos centros (`x_j ⊕ x4`), y aun así no hay
   solución.
3. **Una política temporal de actuación.** E queda alto 4 pasos por la latencia de la
   tubería, y el actuador es una conmutación, así que L/P convierten ese nivel en un
   evento único.

**Recursos medidos:**

- 17 auxiliares (5 D, 4 E, 4 L, 4 P);
- 38 aristas estáticas, todas necesarias (§12);
- 1.584 aristas efectivas en las 8 trayectorias naturales, igual que PRE-01;
- profundidad causal de 4 pasos x→x.

**Fases:**

- detección en t1;
- localización en t2;
- compuerta en t3;
- actuación en t3→t4;
- drenaje en t5 (D), t6 (E) y t7 (L).

```text
x(t) ─XOR─▶ D(t+1) ─AND─▶ E(t+2) ─┬────────────────▶ P(t+3) = E(t+2) ∧ ¬L(t+2) ─XOR─▶ x(t+4)
                                  └─▶ L(t+3) = E(t+2)
```

## 12. Minimalidad y recursos necesarios

**Se evaluaron 366 variantes de A:**

- 1 línea base;
- 17 clamps de auxiliar a 0;
- 76 sustituciones de una arista por una constante (38 aristas × {0, 1});
- 267 reemplazos de compuerta;
- 3 variantes estructurales sin la memoria del disparo;
- 2 fusiones de fan-in 3.

**La batería fija** (`battery_passes`) exige:

- blancos fijos;
- 8/8 P-DATA restauradas exactamente;
- ninguna falsa reparación en P-DATA ni en P-FULL;
- ningún ciclo en P-DATA, en P-FULL ni en los 16 arranques de x desde q*;
- autoapagado: ninguna x restaurada con los auxiliares fuera de q*.

La restauración exacta de P-FULL no es criterio de paso: entra sólo por las falsas
reparaciones y los ciclos. Aun así, todas las variantes que pasan la cumplen, con 42/42,
40/40 o 44/44.

**Familia de testigos.** También se evaluaron los 81 grafos de testigos posibles, con el
mismo E/L/P/X. Pasan la batería 75:

- 3 de 3 con 4 comparadores;
- 48 de 48 con 5;
- 24 de 30 con 6.

| hallazgo | significado |
| --- | --- |
| Los 17 auxiliares son individualmente necesarios en A | Cada clamp a 0 rompe la batería. |
| 0 de 76 sustituciones de una arista por constante pasan | Las 38 aristas son necesarias. |
| 0 de 267 reemplazos de compuerta pasan | Cada compuerta es la única, entre las funciones de sus mismos padres, que funciona. |
| Sin la memoria del disparo hay oscilación | Las tres variantes dan 0/8 P-DATA. `P = E` cicla en 46 de 66 corridas de la batería, X que lee E en 38 de 50, y `P = E ∧ ¬P` en 46 de 66. |
| Fusionar capas sólo funciona con fan-in 3 | D dentro de E, o P dentro de X, pasan la batería completa (8/8 P-DATA, 42/42 P-FULL), pero con aridad 3: cada capa existe para respetar fan-in 2. |
| Con **4 comparadores** (16 auxiliares) basta para todo R_X | Las 3 asignaciones de 4 comparadores pasan la batería completa: 8/8 P-DATA exactas en t7 con un pulso por lesión, P-FULL 40/40, sin falsas reparaciones, sin ciclos y con autoapagado. |
| Con 4 comparadores los 6 empates de peso 2 se enclavan | El quinto comparador de A sólo aporta la resolución de los empates. |
| A es Pareto-mínima en (comparadores, resolución de empates) | A es una de las 12 asignaciones de 5 comparadores que resuelven los 6 empates, exactamente las «triángulo + colgante». No puede mejorarse una de esas dimensiones sin empeorar la otra. |
| A no es mínima en número de auxiliares | La minimalidad global sigue abierta; no debe afirmarse optimalidad absoluta. |

| comparadores | asignaciones que pasan la batería | resuelven los 6 empates |
| ---: | ---: | --- |
| 4: grafos en ciclo de 4, 16 auxiliares | 3 de 3 | 0: los 6 empates se enclavan |
| 5 | 48 de 48 | 12, las «triángulo + colgante» (A entre ellas). Las otras 36 resuelven 2 de 6 y enclavan los otros 4 |
| 6 | 24 de 30 | 24. Las 6 restantes fallan la batería: en cada una, 4 de los 6 arranques de peso 2 caen en ciclos de 16 y 2 se enclavan, aunque P-DATA (8/8) y P-FULL (44/44) siguen exactos |

**Los ciclos de 4.** Las 3 asignaciones de 4 comparadores son los tres ciclos de 4 sobre
{x1..x4}:

- D = {d12, d13, d24, d34};
- D = {d12, d14, d23, d34};
- D = {d13, d14, d23, d24}.

La fila n = 4 «ciclo» de la tabla de escalamiento (§14) es una de ellas, D = {d12, d14,
d23, d34}.

## 13. Dominio autorizado frente a espacio completo

La propiedad de restauración no debe extrapolarse al espacio completo. Está establecida
para dos casos:

- x en R_X **con los auxiliares en reposo** (q = q*);
- P-FULL.

**Censo exhaustivo de los 2²¹ estados:**

| destino | estados | fracción |
| --- | ---: | ---: |
| los dos blancos | 808.816 | 38,57 % |
| seis ciclos de longitud 12 | 1.268.736 | 60,50 % |
| 14 alarmas enclavadas (puntos fijos con x errónea, D/E/L altos y P = 0) | 19.600 | 0,93 % |

El transitorio máximo es de 22 pasos.

**Perturbaciones de dos bits de los dos blancos** (210 por blanco). Vuelven 366 de 420,
183 de 210 en cada blanco. De las 54 que no:

- **18 van al código opuesto** (9 por blanco). Son dos errores dentro del triángulo en
  una misma familia: x_i + x_j, e_i + e_j o p_i + p_j.
- **36 caen en el ciclo de 12** (18 por blanco). Son mezclas de dos familias distintas
  (x+e, x+p o e+p) sobre dos coordenadas distintas del triángulo {1, 2, 3}, por ejemplo
  x1+e2 o e3+p1.
  - De las 96 mezclas x+e, x+p o e+p (48 por blanco), sólo ciclan esas 36.
  - Las otras 60 vuelven al blanco: las que caen en la misma coordenada (x1+e1, e2+p2…)
    y las que tocan la coordenada 4.
  - Los dobles volteos que involucran d o l vuelven todos.

**Los ciclos de 12** son correcciones rancias que se persiguen, porque la tubería de 3
pasos actúa sobre copias viejas de x.

- **En los seis ciclos, por periodo:** x cambia 6 veces (dos de esos cambios mueven dos
  bits a la vez), cada coordenada se conmuta exactamente dos veces y hay 8 pulsos P.
- **El ritmo no es el mismo en todos:**
  - en 2 ciclos (235.008 estados de cuenca cada uno), x cambia exactamente cada dos
    pasos;
  - en los otros 4 (199.680 estados cada uno), los cambios de x se separan alternando 1
    y 3 pasos, así que sólo en promedio es cada dos pasos.
- **Estado del análisis:** hoy esto es sólo una descripción; no se diseccionó.

**Lo que muestra el contraste.**

- El mecanismo está bien entendido en su región autorizada, pero no es un restaurador
  universal.
- La gran cuenca cíclica muestra que las mismas reglas que implementan corrección bajo
  condiciones estructuradas generan dinámicas cualitativamente distintas fuera de ellas.
- La causa de los ciclos de 12 sigue abierta; es el objeto de EXP-05 (§19).

## 14. Ley matemática y escalamiento

**Ley.**

```text
s(t+1) = H x(t)                                síndrome, 5 controles de paridad
ε_i(t+1) = s_{i,a(i)}(t) ∧ s_{i,b(i)}(t)       localizador
ℓ(t+1) = ε(t)                                  registro
π(t+1) = ε(t) ∧ ¬ℓ(t) = ε(t) ∧ ¬ε(t−1)         flanco de subida
x(t+1) = x(t) ⊕ π(t)                           conmutación
```

**Consecuencias desde `(x0, q*)`:**

- `x(4) = x0 ⊕ ε(H x0)`;
- en R_X, `Φ(x) = x ⊕ e_k = argmin_{c∈C} d_H(x, c)`;
- en todo el cubo, el código final es `maj(x1,x2,x3)⁴`.

Verificado en las 8 lesiones. Nombre: **corrección causal intrínseca de errores**, es
decir, decodificación por síndrome del código de repetición con un actuador de
conmutación disparado por flanco.

**Teorema de aridad.** Toda decisión de un disparo que restaure todo error de peso ≤ t
—no sólo la mayoría— tiene aridad esencial **≥ 2t + 1**.

- *Prueba.* Si depende de un conjunto S con |S| ≤ 2t, se parte S en A y S∖A, ambos de
  tamaño ≤ t. Entonces 0ⁿ con errores en A y 1ⁿ con errores en S∖A coinciden en S, pero
  exigen salidas distintas.
- **Verificación por fuerza bruta:** n = 4 (t = 1), n = 5 (t = 2) y n = 6 (t = 2). La
  mayoría de 2t+1 coordenadas basta.
- **Consecuencia con fan-in 2:** profundidad `≥ ⌈log2(2t+1)⌉` y al menos 2t compuertas
  por localizador.

```text
corrección de t errores  ⇒  aridad efectiva mínima ≥ 2t + 1
radio probado de A = 1
```

**Escala matemática del código {0ⁿ, 1ⁿ}** (fuente: `autopsy01_scaling_math.csv`):

- **Empates:** sólo hay empates si n es par, todos en el peso **n/2**: son C(n, n/2)
  estados (2, 6, 20, 70, 252 y 924).
- **n impar:** el código es perfecto y los 2ⁿ estados se decodifican unívocamente.

| n | radio t | detección n−1 | empates | peso del empate | decodificables / total | ¿perfecto? | aridad mínima | profundidad mínima (fan-in 2) | compuertas mínimas por localizador (2t) |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 2 | 0 | 1 | 2 | 1 | 2/4 | no | 1 | 0 | 0 |
| 3 | 1 | 2 | 0 | — | 8/8 | sí | 3 | 2 | 2 |
| 4 | 1 | 3 | 6 | 2 | 10/16 | no | 3 | 2 | 2 |
| 5 | 2 | 4 | 0 | — | 32/32 | sí | 5 | 3 | 4 |
| 6 | 2 | 5 | 20 | 3 | 44/64 | no | 5 | 3 | 4 |
| 7 | 3 | 6 | 0 | — | 128/128 | sí | 7 | 3 | 6 |
| 8 | 3 | 7 | 70 | 4 | 186/256 | no | 7 | 3 | 6 |
| 9 | 4 | 8 | 0 | — | 512/512 | sí | 9 | 4 | 8 |
| 10 | 4 | 9 | 252 | 5 | 772/1024 | no | 9 | 4 | 8 |
| 11 | 5 | 10 | 0 | — | 2048/2048 | sí | 11 | 4 | 10 |
| 12 | 5 | 11 | 924 | 6 | 3172/4096 | no | 11 | 4 | 10 |

**Escala arquitectónica.** La arquitectura de A, con localizadores de radio 1, se probó
para n = 3..8. La escala y las variantes (`run_autopsy01_scaling_variants.py`) se
corrieron sólo tras cerrar el mecanismo N = 4, con predicciones escritas antes de correr:

- las variantes con predicción, 17 de 18, la cumplieron 17/17 (portada, Apéndice D);
- la escala matemática no llevaba predicción;
- la escala arquitectónica llevaba estas dos, y se cumplieron ambas
  (`autopsy01_scaling_variants.json`: `P1_all_met` y `P2_all_met`):
  - **P1:** todo error simple se restaura exactamente, con DATA en t4 y estado completo
    en t7, a todo n.
  - **P2:** para n ≥ 5 (radio matemático ≥ 2), algún error doble no se restaura, porque
    el radio arquitectónico sigue en 1.

| n | testigos | comparadores | auxiliares | errores simples | dobles restaurados | dobles al opuesto | dobles atascados | ley del triángulo (a posteriori) |
| ---: | --- | ---: | ---: | --- | --- | ---: | ---: | --- |
| 3 | triángulo | 3 | 12 | 6/6 | 0/6 (*) | 6 | 0 | sí |
| 4 | triángulo + colgantes | 5 | 17 | 8/8 | 6/12 | 6 | 0 | sí |
| 4 | ciclo | 4 | 16 | 8/8 | 0/12 | 0 | 12 | — |
| 5 | triángulo + colgantes | 7 | 22 | 10/10 | 14/20 | 6 | 0 | sí |
| 5 | ciclo | 5 | 20 | 10/10 | 0/20 | 0 | 20 | — |
| 6 | triángulo + colgantes | 9 | 27 | 12/12 | 24/30 | 6 | 0 | sí |
| 6 | ciclo | 6 | 24 | 12/12 | 6/30 | 0 | 24 | — |
| 7 | triángulo + colgantes | 11 | 32 | 14/14 | 36/42 | 6 | 0 | sí |
| 7 | ciclo | 7 | 28 | 14/14 | 14/42 | 0 | 28 | — |
| 8 | triángulo + colgantes | 13 | 37 | 16/16 | 50/56 | 6 | 0 | sí |
| 8 | ciclo | 8 | 32 | 16/16 | 24/56 | 0 | 32 | — |

(*) Con n = 3, un error doble está a distancia 1 del código opuesto: ir al opuesto es la
decodificación correcta.

**Lectura de la tabla:**

- **Latencia constante:** los errores simples se corrigen a todo n con DATA en t4 y
  estado completo en t7, usando 3n + |D| auxiliares.
- **P-FULL:** es exacto en todos los casos.
- **Triángulo + colgantes:** restaura todos los dobles salvo los 6 internos al triángulo.
- **Ley del triángulo:** se cumple en todos los n probados. El triángulo sigue siendo el
  núcleo decisor, así que la red no calcula la mayoría global. Esta verificación se
  añadió después de las predicciones P1/P2 y se evaluó sobre corridas ya producidas.

**Hay que distinguir tres niveles:**

- **Escalabilidad matemática:** la del decodificador por mayoría es clara (tablas de
  arriba).
- **Escalabilidad arquitectónica:** la de esta implementación no está demostrada más
  allá del radio 1. Su radio sigue en 1 aunque el matemático crezca. Una construcción de
  radio ≥ 2 con fan-in 2 sigue siendo un problema abierto: no se ha hecho ninguna.
- **Factibilidad computacional:** depende del crecimiento de auxiliares, de la
  profundidad temporal y de la exploración de estados.
  - Los auxiliares crecen como 3n + |D| en la familia de A: 12 con n = 3 y 37 con n = 8.
  - Explorar el espacio de estados es el coste de verificar: el censo de A recorrió los
    2²¹ estados, y la cota de aridad sólo se comprobó por fuerza bruta hasta n = 6.
  - Por ahora sólo se conocen cotas inferiores: aridad esencial ≥ 2t + 1; con fan-in 2,
    profundidad `≥ ⌈log2(2t+1)⌉`; y al menos 2t compuertas por localizador.
  - Para radio ≥ 2 sólo se derivaron requisitos de diseño: aridad 2t + 1, profundidad
    logarítmica y **tuberías balanceadas**, es decir, todos los caminos x→D→E de la misma
    longitud, como en A, donde miden 2. Esto último es un requisito de diseño, no una
    cota.
  - El autoarranque y el autoapagado están mostrados para errores simples hasta n = 8;
    para varios errores, no.

## 15. Dependencia de la sincronización

La arquitectura depende fuertemente del orden temporal.

- **Resultados asíncronos** (8 lesiones × 250 semillas por modo):
  - con barrido aleatorio restauran **529 de 2.000**;
  - con una coordenada al azar, **481 de 2.000**, alrededor del 25 %.
- **Desenlace de los fallos.** Las 4.000 corridas se absorbieron en un punto fijo de G
  antes del horizonte de 5.000 pasos: ninguna quedó sin absorber y ninguna llegó al
  código opuesto. Todos los fallos acabaron en alarma enclavada: 1.471 con el barrido
  aleatorio y 1.519 con una coordenada al azar.
  - Que los únicos estados absorbentes sean los 16 puntos fijos de G es cierto por
    definición, pero eso solo no excluye atractores cíclicos bajo asincronía.
  - La ausencia de ciclos terminales es un resultado medido, no una consecuencia lógica.
- **Tolerancia a retardos síncronos:**
  - un retardo extra entre D y E, o entre P y X, mantiene 8/8 con 1 conmutación por
    lesión, con el estado completo en t9 y t8;
  - con la memoria del disparo dos pasos vieja, la primera ráfaga tiene dos pulsos (uno
    repara y otro vuelve a romper); aun así se restaura 8/8, tras 3 conmutaciones y con
    el estado completo en t14.

**Interpretación, todavía no demostrada.** Esto es coherente con el papel de L y P: el
mecanismo necesita que el síndrome, su localización y el flanco temporal permanezcan
coordinados durante varios pasos. Si los componentes se actualizan en momentos
incompatibles, una parte puede actuar sobre información obsoleta. **No se diseccionó**,
y hoy es una hipótesis.

**EXP-05 no trata la asincronía.** EXP-05 (§19) estudia, bajo actualización síncrona,
el ciclo de 12 que aparece con una segunda lesión durante una corrección en vuelo. Por
qué falla la actualización asíncrona sigue siendo una pregunta abierta, sin experimento
asignado.

## 16. Qué significa científicamente el hallazgo

**Qué significa «endógena».** El mecanismo puede describirse como corrección causal
endógena de errores: la dirección de la acción se deriva del propio estado redundante
del sistema, no de una orden externa. «Endógena» o «intrínseca» significa aquí que las
reglas locales y el estado presente contienen todo lo necesario para producir la
corrección. No implica intención, deliberación, recompensa, representación consciente
ni objetivo aprendido.

**La capacidad no surgió de la dinámica.** El decodificador está suministrado por diseño
(SUPPLIED) y su función es consecuencia lógica de las reglas (IMPLICIT_IN_RULES). Lo que
se genera dinámicamente es el patrón D/E/L/P de cada trayectoria.

**Separación funcional.** El hallazgo muestra también una forma elemental de separación
funcional: detectar, localizar, actuar y terminar son operaciones causalmente distintas.
Esto es valioso para el proyecto, porque permite construir y comparar motivos causales
reutilizables en vez de tratar la restauración como una propiedad indivisible del
programa completo.

| dimensión | hallazgo | utilidad conceptual |
| --- | --- | --- |
| Redundancia | Tres bits sanos determinan el centro bajo una sola lesión. | La información de reparación puede estar distribuida. |
| Localidad | Cada puerta usa fan-in ≤ 2. | Una función global puede compilarse por composición de operaciones locales en profundidad y tiempo. |
| Temporalidad | L/P convierte la activación sostenida del localizador E (4 pasos) en un pulso único. | Una memoria mínima puede cambiar cualitativamente la dinámica. |
| Terminación | Corregir X elimina la causa que mantenía activo el soporte; el pulso termina por L. | La terminación puede ser consecuencia del éxito, no de un reloj externo. |
| Frontera | El peso 2 pierde la unicidad; la asincronía, la segunda lesión en vuelo y la pérdida del pulso degradan el mecanismo. | La capacidad tiene condiciones de validez medibles. |

## 17. Lo que el experimento NO demuestra

- **Inteligencia, intención o deliberación.** No las demuestra: el comportamiento se
  explica por reglas booleanas y dinámica temporal.
- **Que la capacidad correctora surgiera de la dinámica.** El decodificador está
  suministrado por diseño; sólo el patrón de cada trayectoria se genera dinámicamente.
- **Autorreparación universal.** No la demuestra: la restauración está establecida en una
  región autorizada (x en R_X con q = q*, más P-FULL) y bajo actualización síncrona.
- **Minimalidad global de la arquitectura.** Sólo establece dos cosas: que A es
  Pareto-mínima dentro de la familia explorada y que cada componente de A es necesario.
- **Radio de corrección mayor que 1.** No lo demuestra.
- **Robustez a la actualización asíncrona.** No la demuestra; es una debilidad conocida.
- **Reintento tras un pulso perdido.** No lo hay: P(restauración) = 1 − pérdida.
- **Robustez ante una segunda lesión con una corrección en vuelo (τ = 1–3).** No la
  demuestra.
- **La causa de los ciclos de periodo 12.** Todavía no la explica.
- **La validez de los claims heredados sin reverificar.** Cuatro veredictos cerrados en
  ramas anteriores siguen con su procedencia heredada (`RESEARCHER_SUPPLIED_CONTEXT`, sin
  traza localizada en la rama):
  - RAAC, el control auxiliar alcanzable (`REACHABLE_AUXILIARY_CONTROL_PROVED`). PRE-01
    derivó un atlas RAAC nuevo y EXP-01 probó que la arista p_i→x_i es necesaria, pero el
    veredicto heredado no se volvió a comprobar.
  - RDDA, no necesario estructuralmente (`RDDA_NOT_STRUCTURALLY_NECESSARY`).
  - APD viable al arranque (`STARTUP_COMPATIBLE_APD_FEASIBLE`).
  - APD con margen por coordenada (`COORDINATEWISE_HEADROOM_APD_FEASIBLE`).

  La autopsia sólo reverificó el APD proyectado, por enumeración, y DISCOVERY-02/03,
  ejecutando los instrumentos.
- **Las hipótesis H0–H3** (ETP_PRE_00 §11):
  - H0, sin entidad;
  - H1, un módulo causal transitorio;
  - H2, un proceso transitorio distribuido;
  - H3, un proto-orgánulo.

  No las cierra, y no por falta de datos: explicar la función de un circuito suministrado
  por diseño no adjudica si hay entidad (D-21 del registro de decisiones). El núcleo
  decisor del triángulo es sólo un dato pertinente para H1 frente a H2.

## 18. Motivo causal candidato para la base de conocimiento

La autopsia generó el artefacto `ETP_AUTOPSY_01_CAUSAL_RECORD_CANDIDATE.json`, con estado
«CANDIDATE — not written to the project database» y commit base `f0fdf00`. No modificó la
base de datos. Resumen del motivo candidato:

| campo | contenido candidato |
| --- | --- |
| Fenómeno | Restauración exacta tras una lesión de un solo bit: detección, localización, una sola conmutación y retorno del estado auxiliar a q*. |
| Dominio | Espécimen A con actualización síncrona estricta y fan-in ≤ 2. Hay dos poblaciones: x en B_H(0000,1) ∪ B_H(1111,1) con los auxiliares en q* = 0¹⁷ (P-DATA, 8), o un estado blanco completo con una coordenada invertida (P-FULL, 42). |
| Condiciones iniciales | x en R_X con q = q*, o un estado blanco completo con una coordenada invertida. |
| Reglas locales | XOR de desacuerdo, AND de localización, retardo de un paso, flanco de subida y XOR de actuación. |
| Mecanismo | Síndrome → localización → pulso único → conmutación → terminación del pulso y del soporte. Dirección = ubicación × conmutación binaria. |
| Condiciones necesarias | Cada uno de los 17 auxiliares y de las 21 compuertas; la transmisión x→D (EXP-03); la arista P→X (EXP-01); la memoria de un paso para el flanco; la actualización síncrona; auxiliares en q* o cerca cuando llega la lesión; a lo sumo una corrección en vuelo; y que el único pulso actúe. |
| Condiciones suficientes | Las reglas congeladas desde (x ∈ R_X, q*), 8/8. Aguas abajo de la detección, un solo evento E correcto, 8/8. Físicamente, un solo P correcto, 8/8, aunque entonces la ubicación viene de fuera. |
| Facilitadores | Bolas disjuntas de radio 1 (d_min = 4); linealidad del código (el síndrome depende sólo del error, no de la palabra de código); tubería balanceada (todo camino x→D→E mide 2); grafo de testigos triángulo + colgante, que resuelve los 6 empates (lo hacen 12 de las 48 asignaciones de 5 comparadores). |
| Inhibidores | Asincronía; pérdida o ablación del actuador; fallo permanente de x; mezclas dobles x+e, x+p o e+p sobre dos coordenadas distintas del triángulo (36 de 420 dobles, al ciclo de 12); segunda lesión durante una corrección en vuelo. |
| Frontera | En DATA, los empates de peso 2 se resuelven por la mayoría del triángulo. En el estado completo, 38,57 % a blancos, 60,50 % a ciclos de 12 y 0,93 % a alarmas enclavadas. En perturbaciones, 42/42 de un bit y 366/420 de dos bits. |
| Invariantes | Equivariancia al complemento; automorfismo (x1 x2); q idéntico en lesiones complementarias, con `I(q; blanco) = 0`; `l(t) = e(t−1)` y `p(t+1) = e(t) ∧ ¬e(t−1)`. En P-DATA hay exactamente un evento E y un pulso P por trayectoria. En P-FULL no se cumple: invertir una x da 1 pulso, una e o una p dan 2 pulsos y 2 conmutaciones, y una d o una l dan 0; aun así las 42 terminan en el blanco original. |
| Contraejemplos | `P = E` (ciclo de 15); X que lee E (ciclo de 7); localizador con un solo testigo; grafos de 4 comparadores (enclavan los empates); 6 de 30 asignaciones de 6 comparadores ciclan. |
| Escala verificada | N = 4 de forma exhaustiva. La arquitectura de A para n = 3..8: errores simples, que era la predicción P1. La ley del triángulo es una verificación añadida después, sobre corridas ya producidas. |
| Escala predicha | Radio matemático `⌊(n−1)/2⌋`; aridad ≥ 2t+1 (demostrado); la arquitectura de A se queda en radio 1; el radio ≥ 2 necesita localizadores nuevos, no construidos. |
| Ley formal | `x(4) = x0 ⊕ ε(H x0)` y `x_i(4) = maj(x_i, x_a, x_b)`; flanco `π(t+1) = ε(t) ∧ ¬ε(t−1)`. |
| Evidencia | Ver la lista bajo la tabla. |
| Preguntas abiertas | La causa del ciclo de 12; el fallo asíncrono; la minimalidad global; el radio ≥ 2; los claims heredados sin reverificar; H0–H3. |

**El campo INHIBITORS ya está corregido.** En su primera versión el registro candidato
decía «mixed x+e, x+p, e+p double perturbations (12-cycle)», sin restringirlo a
coordenadas distintas del triángulo, pero 60 de esas 96 mezclas se restauran (§13,
Apéndice C). Desde el commit `09153fa` ese campo dice lo mismo que la fila de arriba.

**Evidencia, por tema** (todos los archivos bajo `artifacts/`):

- **Ecuaciones:** `autopsy01_equation_audit.json`.
- **Lesiones:** `autopsy01_lesion_table.csv`.
- **Dirección:** `autopsy01_direction_information.csv`.
- **Intervenciones:** `autopsy01_interventions_summary.csv`.
- **Peso 2:** `autopsy01_weight2_boundary.csv`.
- **Compilación:** `autopsy01_compilation.json`.
- **Minimalidad:** `autopsy01_ablations.csv` y `autopsy01_witness_family.csv`.
- **Espacio de estados:** `autopsy01_state_space_census.json`.
- **Escala y variantes:** `autopsy01_scaling_architecture.csv` y `autopsy01_variants.csv`.
- **Veredictos:** `autopsy01_verdicts.json`.

## 19. Siguiente experimento: EXP-05 · refresco del síndrome rancio

Propuesto y no ejecutado. No tiene preregistro ni commit sellado, a diferencia de EXP-04A.

**Objeto.** Las corridas síncronas en que una segunda lesión, sobre otro bit del
triángulo, llega en τ = 1–3 mientras la primera corrección está en vuelo, y que caen en el
ciclo de 12: son 12 de 32 en cada τ = 1, 2, 3.

**Qué ya está medido** (8 lesiones × 4 bits para la segunda lesión, es decir, 32 corridas
en cada τ):

| instante τ de la segunda lesión | restauran | ciclo de 12 | enclavadas |
| ---: | ---: | ---: | ---: |
| 1 | 20 | 12 (todas pares internos al triángulo) | 0 |
| 2 | 20 | 12 (ídem) | 0 |
| 3 | 20 | 12 (ídem) | 0 |
| 4 | 24 | 0 | 8 (todas relesión del mismo bit) |
| 5–8 (32 en cada τ) | 32 | 0 | 0 |

**Las dos condiciones de la versión anterior ya están medidas:**

- **Antes de terminar la primera corrección** (τ = 1–3; x se corrige en t4): restauran
  20/32 y 12/32 caen en el ciclo de 12.
- **Después del pulso P (t3) y antes del vaciado completo de D/E/L** (L = 0 en t7), es
  decir, en τ = 4–6:
  - en τ = 4 se enclavan 8/32, todas relesiones del mismo bit, y restauran las 24 con
    otro bit;
  - en τ = 5–6 restauran 32/32.
- **En total** fallan 44 de 256 corridas (8 instantes × 32), todas con τ ≤ 4.

EXP-05 no tiene que volver a introducir estas lesiones: interviene sobre las que ya se
midieron.

**Diseño propuesto en la autopsia** (§19 de `ETP_AUTOPSY_01_CAUSAL_MECHANISM.md`). En el
instante de la segunda lesión se sustituye el estado auxiliar por el que tendría una
lesión fresca con la x actual (q := q*, x se conserva), frente a un sham no-op.

- **Criterio:** si el ciclo de 12 desaparece frente al sham, la condición «una sola
  corrección en vuelo» queda probada causalmente, no sólo observada. Con ello se cierra la
  última pieza de la terminación.

**Añadido en esta revisión** (no forma parte del diseño de la autopsia, que registró la
variante de segunda lesión sin predicción fija):

- **Criterio reforzado:** exigir además que no aparezca otro ciclo ni un punto fijo fuera
  de las palabras de código. Un refresco parcial podría introducir oscilaciones nuevas,
  que es lo que pedía el ítem 6 del informe anterior («si aparecen nuevas oscilaciones»).
- **Qué medir:** en cada corrida, si desaparece el ciclo de 12, a qué palabra de código
  se llega (original u opuesta), la latencia y si el refresco introduce oscilaciones
  nuevas, distintas del ciclo de 12.
- **Predicción:** los pares del triángulo irán al código **opuesto**. Dos errores superan
  el radio 1 y el empate lo resuelve la mayoría del triángulo. Se sigue de la ley
  exhaustiva de desempate desde q*.
- **Por qué no sirve medir «exacta o funcional».** Ese eje sólo pregunta si, además de x,
  el estado auxiliar volvió a q*, y da por hecho que x vuelve a su propio código. En los
  12 pares del triángulo el desenlace esperado es un punto fijo completo (21 bits,
  q = q*), pero en el código opuesto. Eso no es una restauración, ni exacta ni funcional,
  porque el estado no vuelve al previo a la lesión. Lo que discrimina es a qué palabra de
  código se llega.
- **Comprobación informal por simulación.** Al reponer q := q* con la x actual en
  τ = 1, 2 y 3, las 36 corridas que ciclaban (12 por τ, todas pares internos al
  triángulo) terminan en el código opuesto, y las 60 restantes (20 por τ) siguen en el
  original. No aparece ninguna oscilación nueva: las 96 terminan en un punto fijo de
  código. No sustituye a EXP-05, porque no tiene sham, no está sellada y no es un
  artefacto comiteado.

**Límites que ya se conocen:**

- **El enclavamiento en τ = 4 ya está explicado.** Es la relesión del mismo bit: E sigue
  alto, no hay flanco nuevo y el disparo no se reintenta. Es otro fenómeno, que no
  requiere EXP-05.
- **La arquitectura no se limita a «un solo episodio».** Admite a lo sumo una corrección
  en vuelo (τ = 1–3).
  - Una segunda lesión que llega cuando la primera corrección ya actuó (x corregida en
    t4) se restaura 24/32 en τ = 4, todas salvo las 8 relesiones del mismo bit.
  - En cada τ = 5–8 se restaura 32/32. En τ = 5 siguen activos E y L del primer episodio,
    en τ = 6 sólo L, y desde t7 (τ = 7–8) el soporte ya está vacío.
  - Lo decisivo no es el vaciado, sino que el localizador de la nueva lesión tenga un
    flanco de subida. En τ = 5, por ejemplo, E cae en t6 y vuelve a subir en t7.
  - La red intacta repara incluso su propio error de conmutación (§8, D).

**Relación con EXP-04A** (remapeo de la salida del efector). Sigue preregistrado y sin
ejecutar.

- **Su criterio principal ya está predicho por la ecuación `x' = x ⊕ p`.** Ese criterio es
  el destino DATA que cambia en t4:
  - dH = 0 en los brazos natural e identidad;
  - dH = 1 en el nulo;
  - dH = 2 en los 24 remapeos erróneos, con q4 idéntica a la natural.
- **El valor que conserva está en su seguimiento secundario:** la dinámica posterior a
  t4.
- **Dos brazos de esta autopsia lo anticipan en parte:** el localizador erróneo (§8, D) y
  el pulso erróneo (§8, F).

**Ampliaciones opcionales**, propuestas por el informe anterior y que no forman parte del
diseño propuesto en la autopsia:

- comparar el síndrome calculado una sola vez frente al síndrome refrescado después de
  cada cambio de X;
- comparar refresco inmediato, refresco retardado y ausencia de refresco;
- añadir controles sin segunda lesión, para comprobar que el refresco no introduce falsos
  positivos.

Un refresco parcial podría introducir oscilaciones nuevas, y por eso las ampliaciones
deben medirlas.

> **Pregunta causal de EXP-05.** ¿El ciclo de 12 que aparece cuando una segunda lesión
> sobre otro bit del triángulo llega en τ = 1–3 se debe al estado auxiliar rancio? Aunque
> el refresco lo elimine, dos errores en vuelo superan el radio 1: el desenlace será un
> desempate del triángulo, no una corrección.

## 20. Preguntas abiertas

| prioridad | pregunta | por qué importa |
| --- | --- | --- |
| Alta | ¿Cuál es la causa exacta de los ciclos de periodo 12? ¿La elimina el refresco del estado auxiliar? (EXP-05) | Delimita la dinámica global y puede revelar otro motivo causal. |
| Alta | ¿Por qué la asincronía reduce la restauración a ~25 %? (sin experimento asignado) | Probaría qué componentes de fase son realmente necesarios. |
| Media | ¿Existe una arquitectura de radio ≥ 2 con restricciones locales comparables? | Evalúa el escalamiento de la capacidad, no sólo del código matemático. |
| Media | ¿Cuál es la minimalidad global? ¿Hay redes de fan-in 2 con menos de 16 auxiliares que pasen la batería? | Separa la necesidad estructural de las contingencias de la arquitectura A. |
| Media | ¿Se sostienen RAAC, RDDA, STARTUP APD y HEADROOM APD al reverificarlos contra el código y los artefactos, como ya se hizo con PROJECTED APD y DISCOVERY-02/03? | Hoy descansan en procedencia heredada, sin traza localizada. |
| Pendiente | ¿Qué establecen H0–H3? El núcleo decisor del triángulo es un dato pertinente para H1 frente a H2. | Mantiene abierto el programa causal más amplio. Explicar el circuito no las decide (D-21). |

## 21. Conclusión

**La autopsia convierte el fenómeno de PRIMITIVO en un mecanismo explicable.** La
restauración aparece por una cadena de pasos:

1. la lesión genera un síndrome de desacuerdo;
2. la coordenada dañada se localiza mediante comparaciones locales con dos testigos;
3. una memoria de un paso convierte esa localización en un único pulso;
4. el pulso conmuta el bit correcto;
5. el éxito de la corrección elimina la causa que mantenía activo el soporte auxiliar.

Dentro del dominio autorizado el sistema no necesita una orientación externa para
escoger 0000 o 1111. La redundancia de X ya contiene esa información, y la conmutación
del bit minoritario la convierte en dirección sin que ningún auxiliar la lea.

**La lección arquitectónica más general.** Una función global que no puede implementarse
directamente bajo una restricción local puede **compilarse** mediante composición causal
en profundidad y tiempo.

- En PRIMITIVO, fan-in 2 no basta como regla de salida directa, pero sí como lenguaje
  para construir una decisión efectiva de aridad 3.
- La red lo consigue con tres recursos (§11):
  - registros intermedios, que dan aridad 3 en 2 capas;
  - un estado auxiliar cuyo reposo es el mismo en ambos códigos, el síndrome, que permite
    usar XOR sin romper los puntos fijos;
  - una compuerta temporal, L/P.
- No está demostrado que estos recursos basten fuera de A, por ejemplo para radio ≥ 2
  (§14).
- La capacidad no reside en una puerta aislada, sino en la organización temporal del
  circuito.

**Siguiente paso.** El estado científico apropiado es `CAUSAL_MECHANISM_IDENTIFIED`. El
siguiente avance no consiste en volver a demostrar la restauración, sino en estudiar sus
límites dinámicos:

- el síndrome rancio y el ciclo de 12;
- las perturbaciones sucesivas;
- la asincronía;
- las construcciones de radio mayor.

Esas preguntas permiten pasar de un mecanismo particular a una teoría de familias de
mecanismos restauradores.

---

## Apéndice A. Registro técnico de reproducibilidad

| elemento | identificador / estado |
| --- | --- |
| Rama científica | `experiment/primitivo-causal-autopsy-01` |
| Worktree | `/home/wis/worktrees/primitivo-causal-autopsy-01` |
| Base | `f0fdf00` (`f0fdf00c6661b466ffbf1806ab13afb4be616d13`, commit del preregistro de EXP-04A) |
| Linaje | `41fccbf` (DISCOVERY-02/03) → `68119ce` PRE-01 → `c19a0a2` EXP-01 → `9ba600d` EXP-02 → `e559326` EXP-03 → `f0fdf00` preregistro EXP-04A → `e4a72f4` autopsia → `b5bb8a7` verificación de los registros de EXP-02/03 → `09153fa` corrección de erratas del informe técnico |
| Aislamiento | Rama y worktree propios desde `f0fdf00`, sin material de Gate A (D-17). La rama no contiene `experiments/primitivo_n2/` ni `docs/LEVEL18_ANALISIS_CAUSA_RAIZ.md`, y ninguna de las dos pistas se tocó |
| Commit principal de la autopsia | `e4a72f4` |
| Seguimiento de verificación del ledger | `b5bb8a7` |
| Corrección de erratas del informe técnico | `09153fa` |
| Informe técnico | `research/primitivo/entidad_transitoria/ETP_AUTOPSY_01_CAUSAL_MECHANISM.md` |
| Registro causal candidato | `research/primitivo/entidad_transitoria/ETP_AUTOPSY_01_CAUSAL_RECORD_CANDIDATE.json` |
| Este informe | `research/primitivo/entidad_transitoria/Informe_PRIMITIVO_Autopsia_Causal_Hallazgos_CORREGIDO.md` |
| Instrumentos | Ver la lista bajo la tabla |
| Artefactos | `artifacts/autopsy01_*`, 24 archivos: 23 de `e4a72f4` y `autopsy01_errata_check.json` de `09153fa`. El índice de veredictos está en `autopsy01_verdicts.json` |
| EXP-04A | Preregistrado, no ejecutado. Su criterio principal lo predice `x' = x ⊕ p`, y los brazos D y F de §8 anticipan parte de su seguimiento secundario (§19) |
| Veredicto | `CAUSAL_MECHANISM_IDENTIFIED` |
| H-CORE | Confirmada, con cuatro precisiones |

**Instrumentos.** La numeración § de esta lista es la interna de cada instrumento, no la
de este informe.

- **`autopsy01_core.py`:** red booleana genérica, intervenciones explícitas (clamp
  persistente, escritura puntual, edición de regla) y batería de evaluación.
- **`run_autopsy01_mechanism.py`, §0–§11:**
  - auditoría exhaustiva;
  - ledger heredado;
  - teoría de códigos;
  - tabla de las 8 lesiones;
  - dirección;
  - mecanismo temporal;
  - intervenciones;
  - peso 2;
  - exacta frente a funcional;
  - compilación;
  - minimalidad;
  - ley.

  En este informe corresponde a §3–§13 y a la ley del §14.
- **`run_autopsy01_scaling_variants.py`, §12–§13:**
  - escala matemática;
  - cota de aridad por fuerza bruta;
  - arquitectura de A para otros n;
  - variantes cercanas.

  En este informe corresponde a la escala del §14, al §15, a la segunda lesión del §19 y
  al Apéndice D. Se corrió sólo después de cerrar el núcleo.
- **`run_autopsy01_errata_check.py`:** se añadió en `09153fa`, tras el cierre. Recalcula
  en sólo lectura las cifras de las siete erratas corregidas del informe técnico, afirma
  cada una y escribe `autopsy01_errata_check.json`. No regenera ningún otro artefacto.

  En este informe corresponde a §6, §8, §11, §13 y §18, y a las erratas heredadas del
  Apéndice C.

**Qué contiene cada commit:**

- `e4a72f4`: los instrumentos, los resultados y el informe de la autopsia, más 5 líneas
  en `DECISION_LOG.md` (D-17 a D-21).
- `b5bb8a7`: verifica contra los registros los resultados heredados de EXP-02 y EXP-03, y
  reproduce los dos bloqueos de EXP-03.
- `09153fa`: corrige siete frases del informe técnico que afirmaban más que su evidencia,
  además del campo INHIBITORS del registro candidato y de un comentario de
  `run_autopsy01_mechanism.py`. Añade `run_autopsy01_errata_check.py` con su resultado. El
  veredicto no cambia.
- El commit siguiente a `09153fa` añade este informe a la rama.

**Reproducibilidad.** Al repetir el instrumento principal, los demás artefactos se
regeneraron byte a byte idénticos: la ejecución es determinista. Esta revisión lo
confirmó por su cuenta con una nueva corrida (Apéndice E).

## Apéndice B. Glosario operacional

| término | definición en este informe |
| --- | --- |
| Síndrome | Patrón de desacuerdos D derivado de X, invariante al complemento. |
| Comparador de desacuerdo (D) | `d_ij = x_i ⊕ x_j`: control de paridad de un par de bits. |
| Localizador (E) | `E_i`: marca la coordenada que discrepa de sus dos testigos. |
| Testigos | Las dos coordenadas fijas con las que se compara cada bit. |
| Ubicación y dirección | La ubicación es qué bit está dañado; la llevan D y E. La dirección es 0→1 o 1→0; la produce la conmutación del valor actual, y ningún auxiliar la lleva. |
| Disparo único (one-shot) | Mecanismo L/P que convierte la activación sostenida de E en un único pulso: el flanco de subida. |
| Terminación de pulso | P vuelve a 0 porque L ya alcanzó a E (t4), aunque x no se haya restaurado. |
| Terminación de soporte | D, E y L vuelven a 0 porque la x corregida anula el síndrome (t5, t6 y t7). |
| Restauración funcional | X ya coincide con el blanco aunque queden auxiliares activos (t4–t6). |
| Restauración exacta | Todo el estado global vuelve al estado previo a la lesión, bit a bit (t7). |
| q* | Estado de reposo de los 17 auxiliares, `0¹⁷`. Es el mismo para ambos blancos. |
| P-DATA / P-FULL | P-DATA: lesiones de un bit de x con q = q* (8). P-FULL: un bit invertido del estado completo de un blanco (42). |
| R_X | Dominio autorizado: estados x de peso 0, 1, 3 o 4. |
| Φ | Mapa proyectado que lleva cada estado autorizado a su palabra de código más cercana. |
| Fan-in | Número máximo de entradas esenciales de una operación local. |
| d_max | Cota de aridad esencial por coordenada en la búsqueda de DISCOVERY-03. Se probaron 1 y 2. |
| C4 / C3 (DISCOVERY-03) | Los dos pares de centros que prueba DISCOVERY-03: C4 = {0000, 1111}, a distancia 4 (el par de A); C3 = {0000, 1110}, a distancia 3. En el código se llaman `DISTANCE_4` y `DISTANCE_3`. No confundir con DISCOVERY-02 (n = 3, centros 000/111). |
| Compilación causal | Realización temporal de una función global mediante operaciones locales y estados auxiliares. |
| Peso 2 | Frontera de empate entre 0000 y 1111. |
| Alarma enclavada | Punto fijo no objetivo: x errónea, D/E/L altos y P = 0. Se llega a él si el pulso no actúa o si E no tiene un flanco nuevo. No confundir con el estado de la rama C con E sostenido, donde x es correcta y E/L quedan altos por la sujeción. |
| Ciclo de 12 | Atractor periódico del espacio completo en que las correcciones rancias se persiguen. |
| Síndrome rancio | Información de error calculada sobre un x anterior y usada después de que x ya cambió. |
| SUPPLIED / IMPLICIT_IN_RULES | El circuito lo pone el diseño; su función se sigue lógicamente de las reglas (taxonomía de PRE-00). |

## Apéndice C. Fe de erratas respecto del .docx

Los números de línea son los del texto extraído del .docx original.

| # | líneas | decía (resumen) | corrección aplicada | tipo |
| ---: | --- | --- | --- | --- |
| 1 | 22 | Precisión (2): «el blanco no está almacenado en los auxiliares… información mutua 0 en el análisis reportado» | La dirección no se extrae de los bits sanos. La ceguera al blanco se apoya en `I = 0` en P-DATA, en la equivariancia exhaustiva al complemento y en que las lesiones complementarias comparten q. La dirección es ubicación × conmutación (§1) | incompleto |
| 2 | 58 | «el bloqueo persistente mantiene el episodio atrapado» | El bloqueo persistente **impide** el onset: x perturbada con q = q*. El estado atrapado con D/E/L altos es el de EXP-01 (§3) | incorrecto |
| 3 | 59 | «X→D es necesario para iniciar y sostener la lectura del daño» | EXP-03 prueba X→D para el onset. El sostén lo muestran EXP-01 + EXP-02 (§3) | impreciso |
| 4 | 138 | «Los auxiliares extraen y temporizan esa información» (la del blanco) | Los auxiliares sólo llevan la ubicación: `I(q; blanco) = 0` e `I(q; posición) = 2` bits. La dirección nace de la conmutación (§5) | incorrecto |
| 5 | 217–222 | «t5–t6: D/E/L se vacían en cascada» | D cae en t5, E en t6 y L en t7 (§7) | impreciso |
| 6 | 225 | La corrección «se propaga hacia atrás por la cadena causal» | Recorre **hacia adelante** la tubería X→D→E→L (§7) | impreciso |
| 7 | 232–234 | Lesión de D: se pierde la localización; «el síndrome necesita suficientes comparadores» | Es una ablación. Importa si el comparador es uno de los dos testigos de E_k: si lo es, no hay pulso y la lesión queda fija (16/16); si no, la reparación es normal (4/4). A2 lo confirma (§8) | impreciso |
| 8 | 241–242 | E erróneo: «el sistema corrige la coordenada equivocada» | Con la red intacta, x_j se conmuta por error y se deshace, y el estado completo vuelve en t11 (24/24). Sólo con D amputada queda un doble error permanente (§8) | incompleto |
| 9 | 243 | «P… obedece la dirección codificada por E» | E codifica la ubicación, no la dirección. P ejecuta esa ubicación y la dirección sale de la conmutación (§8) | impreciso |
| 10 | 276–277 | «4 comparadores pueden cubrir R_X; la detección no exige toda la redundancia» | Con 4 comparadores pasa la batería completa (R_X y P-FULL). El quinto sólo aporta el desempate (§12) | impreciso |
| 11 | 286 | «el resumen no desglosa el pequeño resto» | El resto es 0,93 %: 19.600 estados en 14 alarmas enclavadas (§13) | incompleto |
| 12 | 296 | EXP-05 conectado con la asincronía | EXP-05 trata el ciclo de 12 con una segunda lesión en vuelo, bajo sincronía. La asincronía queda abierta sin experimento (§15, §19) | incorrecto |
| 13 | 298, 308, 320 | No decía que el decodificador está suministrado | Se añade la clasificación SUPPLIED / IMPLICIT_IN_RULES (§5, §16, §17) | incompleto |
| 14 | 334 | Dominio del motivo: «bolas de radio 1» | Se añaden q = q*, la sincronía, fan-in ≤ 2, el espécimen A y P-FULL (§18) | incompleto |
| 15 | 351 | «corrector de un solo episodio» | Admite a lo sumo una corrección en vuelo (τ = 1–3). Una segunda lesión posterior a la corrección se restaura 24/32 en τ = 4 (salvo la relesión del mismo bit) y 32/32 en cada τ = 5–8. Esto incluye τ = 5, con E y L del primer episodio todavía activos, y τ = 6, con sólo L; el soporte está vacío desde t7. Lo decisivo es el flanco de subida del nuevo E (§19) | impreciso |
| 16 | 351, 358–359 | El objeto de EXP-05 era una dicotomía abstracta | El objeto de EXP-05 es el ciclo de 12 en las 12/32 corridas en τ = 1–3, con el criterio de que el ciclo desaparezca frente al sham (§19) | incompleto |
| 17 | 353–354 | La segunda lesión antes o después del pulso, como pasos pendientes | Ya está medido para τ = 1..8. Antes de terminar la corrección (τ = 1–3), 12/32 ciclan. Tras el pulso y antes del vaciado (τ = 4–6), en τ = 4 se enclavan 8/32 y en τ = 5–6 restauran 32/32 (§19) | incompleto |
| 18 | 357 | Medir «exacta o funcional» | No discrimina: hay que medir a qué código se llega. Se predice el opuesto, un punto fijo con q = q* que no es restauración (§19). Esto lo añade esta revisión, no el diseño de la autopsia, y la simulación informal da 36/36 al opuesto. Se conserva «si aparecen nuevas oscilaciones», en «Qué medir» y como criterio reforzado, ambos añadidos por esta revisión | incompleto |
| 19 | 359 | «¿falla ante perturbaciones sucesivas por capacidad o por síndrome rancio?» | Sólo falla en 44 de 256 corridas, con τ ≤ 4. El enclavamiento en τ = 4 se explica por la falta de reintento, y el radio 1 limita el desenlace (§19) | impreciso |
| 20 | 369–370 | «¿Puede un síndrome refrescado sostener múltiples correcciones en vuelo?» | Reformulada: ¿el refresco elimina el ciclo de 12? Aun así, dos errores superan el radio 1 (§19, §20) | incompleto |
| 21 | 3, 21 | «autoextinción», «se extingue» | «terminación (de pulso y de soporte)», «vuelve a q*». PRE-01 rechaza *self-extinction* | terminología |
| 22 | 43 | «¿Por qué la dinámica se autoextingue…?» | «¿Por qué la organización auxiliar vuelve a q*…?», con las dos terminaciones (§2) | terminología |
| 23 | 308 | «Una capacidad global puede emerger…» | «puede compilarse…». PRE-00 excluye «emergente» (§16) | terminología |
| 24 | 310 | «L/P transforma detección sostenida…» | L/P lee E (P = E ∧ ¬L), no D: convierte la activación sostenida del localizador E (4 pasos) en un pulso único. Detección (D) y localización (E) son operaciones distintas (§16) | impreciso |
| 25 | 355–356 | Brazos de refresco inmediato o retardado presentados como el diseño de EXP-05 | Se marcan como ampliación opcional, no como el diseño propuesto en la autopsia (§19) | sin soporte |
| 26 | 386 | «puede emerger mediante composición causal» | «puede compilarse mediante composición causal», con los recursos acotados a PRIMITIVO (§21) | terminología |

**Otros cambios respecto del .docx que no eran errores.** El paso adversarial consideró
defendible la redacción original, y ninguno de estos cambios cuenta entre las 26
correcciones. Se hicieron por precisión o por coherencia con las correcciones de la
tabla. Los números de línea son los del .docx.

*Consecuencia de una corrección de la tabla:*

- **l.19 (§1).** «Extraída por la cadena D→E→L/P→X» pasa a «la cadena D→E→L/P sólo
  extrae la ubicación, y `X ⊕ P` la convierte en dirección» (por las n.º 1 y 4). Por lo
  mismo, en l.385 (§21) se añade «sin que ningún auxiliar la lea».
- **l.33 (§1, tabla) y l.66-67 (§3, fila TERMINACIÓN).** Se separan la terminación de
  pulso, que produce L, y la de soporte, que produce la x corregida (n.º 21 y 22).
- **l.13 (portada), l.32 (§1, tabla) y l.197 (§7, título).** Por la n.º 21 cambian tres
  expresiones:
  - «por qué se apaga después de reparar» pasa a «por qué su organización auxiliar vuelve
    al reposo después de reparar»;
  - «¿Por qué se apaga?» pasa a «¿Por qué termina?»;
  - «…pulsar y extinguir» pasa a «…pulsar y terminar».
- **l.225 (§7).** «P se autoextingue por E/L» pasa a «P termina en t4 porque L ya alcanzó
  a E» (n.º 6 y 21).
- **l.312-316 (§16, tabla).** La fila «Autoextinción» pasa a «Terminación», y la fila
  Frontera añade la segunda lesión en vuelo y la pérdida del pulso (n.º 21 y §1).
- **l.338 (§18).** «Extinción» pasa a «terminación del pulso y del soporte; dirección =
  ubicación × conmutación» (n.º 1 y 21).
- **l.196 (§6).** «Hace reparar el bit equivocado» pasa a dos variantes: con D amputada, P
  conmuta el bit que marque E; con la red intacta, el error se detecta y se deshace
  (n.º 8).
- **l.232, 235, 244-246 (§8).** «Lesión» o «bloqueo» pasan a «ablación» en las familias
  A1, B y E. En E, `p_k ≡ 0` deja la detección y la localización intactas, y el corte de
  arista es el de EXP-01 (criterio de la n.º 7).

*Precisiones independientes:*

- **l.13 (portada) y l.19 (§1).** Se añade la fila «Alcance» en la tabla de cabecera
  (l.4-11 del .docx): espécimen A × dinámica síncrona × P-DATA (8) y P-FULL (42).
- **l.31 (§1).** «Onset de E» pasa a «inicio de E», porque «onset» queda reservado para la
  fase ONSET.
- **l.35 (§1).** «Fuera del dominio autorizado» pasa a «fuera de la región autorizada del
  espacio completo», y la fila «¿Dónde falla?» enumera todos los modos de fallo medidos.
- **l.65 (§3).** EXP-02 «desde el estado lesionado» pasa a «desde el punto fijo del corte
  (t4)», escribiendo sólo x = blanco y conservando q.
- **l.69-70 (§3).** La fila se atribuye a DISCOVERY-02/03, ejecutados en la autopsia, y a
  la enumeración de extensiones directas. Se añaden las redes sólo-X iteradas (0
  candidatos) y se conserva, con su precisión, «no tiene ciclos no-target».
- **l.107 (§4).** La información de los tres bits sanos está disponible, pero cada
  localizador usa sólo dos.
- **l.140-194 (§6).** «Patrón basal de D» pasa a «patrón de D en t1».
- **l.228 (§8).** Se añaden el estatus de las predicciones (no selladas, D-18) y el
  solapamiento con EXP-04A. Se conserva «asignar roles causales y no sólo correlaciones
  temporales».
- **l.255 (§9) y l.286 (§13).** La ley del desempate se acota a «desde q*» (l.255). La
  restauración se acota a dos casos (l.286): x en R_X «con los auxiliares en reposo»
  (q = q*) y P-FULL.
- **l.262 (§10).** Las cuatro trayectorias son de q, una por posición, compartidas por
  las lesiones complementarias, y cada una converge al estado restaurado de su blanco.
- **l.264 (§3, §11).** El resultado de DISCOVERY-03 cubre las redes sólo-X iteradas e
  incluye la extensión directa como caso particular.
- **l.269 y l.23 (§1, §11).** «El recurso que faltaba es profundidad» se completa con el
  estado auxiliar cuyo reposo es el mismo en ambos códigos y con la política temporal.
- **l.287 (§13).** Se añaden la descripción de los ciclos de 12 (correcciones rancias, sin
  diseccionar) y su asignación a EXP-05.
- **l.289 (§14).** La cota 2t+1 vale para toda decisión de un disparo, no sólo para la
  mayoría.
- **l.293 (§14).** Sobre la escala:
  - el radio de A sigue en 1 aunque el matemático crezca;
  - «sigue siendo problema abierto» se conserva, precisando que no se ha hecho ninguna
    construcción de radio ≥ 2;
  - la factibilidad conserva sus tres factores (auxiliares, profundidad temporal y
    exploración de estados) y añade las cotas inferiores y el requisito de tuberías
    balanceadas.
- **l.295 (§15).** La interpretación de la asincronía se marca como «todavía no
  demostrada» y se añaden los desenlaces medidos.
- **l.299 (§16).** «Modularidad» pasa a «separación funcional», porque el proyecto reserva
  «módulo» para H1.
- **l.319-326 (§17).** Se añaden «reintento tras un pulso perdido», «segunda lesión con
  una corrección en vuelo» y los claims heredados sin reverificar.
- **l.340 (§18).** «Condición necesaria» toma el campo NECESSARY_CONDITIONS del registro;
  redundancia y testigos pasan a Facilitadores.
- **l.342 (§18).** «Frontera» toma el campo del registro: 38,57 / 60,50 / 0,93 %, 42/42 y
  366/420.
- **l.344 (§18).** «Invariante» toma el campo INVARIANTS. Que el blanco se derive de X sin
  variable externa sigue en §1, §5 y §21.
- **l.346 (§18).** «n pequeño según el informe» pasa a «N = 4 exhaustivo y la
  arquitectura de A en n = 3..8».
- **§18, filas nuevas.** Se añaden las del registro que el .docx no resumía:
  - condiciones iniciales;
  - suficientes;
  - facilitadores;
  - inhibidores;
  - contraejemplos;
  - escala predicha;
  - ley formal;
  - evidencia.
- **l.352 (§19).** «Comparar síndrome calculado una sola vez frente a refrescado» se
  conserva como ampliación opcional.
- **l.372-373 (§20).** Se añade «sin experimento asignado», y «Prueba» pasa a «Probaría».
- **l.378 (§20).** Se añade la pregunta de las redes con menos de 16 auxiliares.
- **l.380-382 (§20).** Se añade el núcleo del triángulo como dato para H1 frente a H2.
- **l.387 (§21).** El síndrome rancio y el ciclo de 12 forman un solo frente, el de
  EXP-05.
- **l.408-409 (Apéndice A).** EXP-04A «No ejecutado» pasa a «Preregistrado, no
  ejecutado», con su relación con la autopsia.
- **l.415 (Apéndice A).** Se suprime «El informe reporta», porque la regeneración byte a
  byte consta en el mensaje del commit `b5bb8a7` y en la corrida de esta revisión, no en
  el informe técnico.
- **Apéndice B.** El glosario se amplía.
- **Se conserva el texto del .docx** en cinco objeciones que no se aplicaron:
  - el criterio de cierre (l.47-48);
  - la pregunta 2 (l.40);
  - «366 variantes» (l.15 y l.271);
  - la fila Redundancia (l.304-305);
  - «gran cuenca cíclica» (l.287).

**Erratas heredadas del informe técnico de la autopsia.** Esta revisión corrige además
siete frases que venían de `ETP_AUTOPSY_01_CAUSAL_MECHANISM.md`. Una de ellas aparecía
también en `ETP_AUTOPSY_01_CAUSAL_RECORD_CANDIDATE.json`.

- **Estado en el repositorio:** las siete están corregidas desde el commit `09153fa`. En
  el mismo commit se corrigieron el campo INHIBITORS del registro y un comentario de
  `run_autopsy01_mechanism.py` que repetía la errata del §6.
- **Comprobación:** `run_autopsy01_errata_check.py` recalcula y afirma cada cifra de las
  correcciones.

Las siete frases:

- «x cambia cada dos pasos» en los ciclos de 12 sólo vale para 2 de los 6 ciclos (§13);
- «exactamente un E en todos los pasos» debe leerse «a lo sumo un E en cada paso, y sólo
  e_k» (§6);
- «alarma enclavada» para el brazo C con E sostenido es impropio: allí x es correcta
  (§8);
- «existen 4 extensiones por coordenada» debe leerse «4 de aridad 3 entre 64; las otras
  60 tienen aridad 4» (`autopsy01_compilation.json`) (§11);
- «36 caen en el ciclo de 12: son las mezclas x+e, x+p y e+p». También estaba en el campo
  INHIBITORS del registro: «mixed x+e, x+p, e+p double perturbations (12-cycle)». Sólo
  vale para las 36 mezclas sobre dos coordenadas distintas del triángulo {1, 2, 3}. De
  las 96 mezclas, las otras 60 vuelven al blanco: 24 caen en la misma coordenada y 36
  tocan la coordenada 4 (§13, §18);
- «todas monótonas. Por eso DISCOVERY-03 no encuentra solución» no es una demostración
  (§11):
  - maj3 también es monótona;
  - con los centros 0000/1110 hay reglas no monótonas y aun así no hay candidatos;
  - lo que establece el resultado es la enumeración exhaustiva;
- «[XOR sin romper los puntos fijos,] algo imposible para reglas sólo-X» (§11) debe
  acotarse a los códigos de A (0000/1111). Con 0000/1110 hay reglas XOR sólo-X, como
  `x_j ⊕ x4`, que dejan fijos ambos centros (§11).

## Apéndice D. Contenido de la autopsia que el .docx omitía

- **Auditoría de la tabla completa:** entradas esenciales iguales a los padres
  declarados; automorfismo (x1 x2); 16 puntos fijos (§3).
- **Réplica del ledger heredado** (§3):
  - la fila BASELINE y la columna «qué no prueba»;
  - las 8 trazas P-DATA reproducidas bit a bit;
  - el punto fijo de EXP-01, 8/8;
  - el sham de EXP-03;
  - las 64 comparaciones de fase exactas.
- **Procedencia de DISCOVERY-03 = NO_LOCAL_SOLUTION:** pasa de `RESEARCHER_SUPPLIED` a
  verificado por ejecución del instrumento (§3, §11).
- **Aislamiento de la rama** respecto de Gate A y de LEVEL18 (§2, Apéndice A).
- **Teoría de códigos del dominio** (§4):
  - capacidad de detección 3;
  - las bolas cubren 10 de 16 estados;
  - controles de paridad de rango 3;
  - 8 cosets, 5 con líder único y 3 de empate.
- **Taxonomía supplied/generated** (§5).
- **Búsqueda de objetivo por observación**, con sus cuatro negativas (§5).
- **Información mutua de la posición** (2 bits en t1–t6) y el experimento «mismo pulso,
  efecto opuesto» (§5).
- **Comparadores activos pero no usados** (d14 y d24): información disponible, no usada
  (§6, §8).
- **Estado completo t0–t7**, con las identidades `L = E(t−1)` (256/256) y flanco de subida
  (224/224) (§7).
- **Tabla completa de las 8 familias de intervención** (§8):
  - A2, el localizador con un solo testigo;
  - E sostenido;
  - E inyectado en un blanco sano;
  - los tiempos de C, D y F.
- **Estatus de las predicciones** (§8, §14):
  - escritas antes de correr y no selladas: es una serie de análisis, no un preregistro;
  - la ley del triángulo para n = 3..8 es una verificación a posteriori.
- **Relación con EXP-04A:** su criterio principal lo predice `x' = x ⊕ p`, y los brazos D
  y F anticipan parte de su seguimiento secundario (§8, §19, Apéndice A).
- **Tabla de peso 2 detallada** (§9) y los 12 errores dobles DATA simultáneos sobre un
  blanco: 6 vuelven al código original y 6 van al opuesto, los pares internos al
  triángulo.
- **P-FULL 42/42 y los dobles 366/420**, con su desglose exacto por tipo de par (§10,
  §13).
- **Aridad de Φ y reglas sólo-X** (§11):
  - 0 extensiones de aridad ≤ 2;
  - 64 extensiones por coordenada, 4 de aridad 3 y 60 de aridad 4;
  - 16 reglas sólo-X monótonas;
  - profundidad mínima 2.
- **El localizador ε** no siempre marca un solo bit (12/2/2 en los 16 estados) (§11).
- **Leyes del lazo sin compuerta** (polinomios primitivos, periodos 15 y 7), y con
  compuerta (§11).
- **Número de aristas estáticas (38) y efectivas (1.584)**, y las fases (§11).
- **Detalle de la minimalidad** (§12):
  - composición de las 366 variantes y definición exacta de la batería;
  - 0/76 sustituciones de arista y 0/267 reemplazos de compuerta;
  - ciclos de las variantes sin memoria;
  - fusiones con fan-in 3;
  - familia de testigos: 75/81 pasan, con los tres ciclos de 4 y el fallo de 6 de las
    asignaciones de 6 comparadores.
- **Censo completo del espacio** (§13):
  - alarmas enclavadas;
  - transitorio máximo;
  - ritmo exacto de los 6 ciclos de 12;
  - desglose de las mezclas dobles que ciclan.
- **Demostración del teorema 2t+1** para cualquier decisión de un disparo, con su
  consecuencia con fan-in 2 (§14).
- **Tablas de escala matemática** (con detección, peso del empate y estados
  decodificables) **y arquitectónica**, con P1/P2 y la ley del triángulo a posteriori
  (§14).
- **Resultados de asincronía:** absorción medida, sin ciclos terminales (§15).
- **Claims heredados sin reverificar:** RAAC, RDDA, STARTUP APD y HEADROOM APD (§17,
  §20).
- **Motivo causal candidato:** pasa de 9 a 17 campos, con condiciones iniciales,
  suficientes, facilitadores, inhibidores, contraejemplos, escala predicha, ley formal y
  evidencia (§18).
- **Variantes cercanas** (§15, §19; resumen abajo):
  - retardos;
  - pérdida estocástica del pulso;
  - fallo permanente;
  - lesión que se revierte sola;
  - segunda lesión durante la reparación.
- **Variantes de código** (resumen abajo):
  - el par 0000/1110;
  - el par trasladado {0101, 1010};
  - las distancias 2 y 1;
  - Rep3 ⊕ Rep3;
  - el código [5,2,3].
- **Claims permitidos** de la autopsia (abajo), y **criterios de aceptación** del encargo
  (Apéndice F).

**Variantes cercanas, resumen completo.** Son 18 (`artifacts/autopsy01_variants.csv`):

- 17 tenían predicción escrita antes de correr, y las 17 se cumplieron
  (`autopsy01_scaling_variants.json`);
- la de segunda lesión durante la reparación no tiene predicción fija, porque su
  desenlace depende del instante τ.

| variante | resultado |
| --- | --- |
| Códigos 0000/1110 (distancia 3; control de peso 1 sobre x4) | 8/8; q idéntico por posición |
| Par {0101, 1010} (distancia 4, con XNOR donde los bits del código difieren) | 8/8, q idéntico por posición: es un reetiquetado |
| Distancias 2 y 1: pares {0000, 1100} y {0000, 1000} | Las bolas se solapan (estados compartidos 0100 y 1000, y 0000 y 1000): ningún decodificador puede restaurar todo error simple |
| Rep3 ⊕ Rep3 (4 atractores, dos decodificadores de triángulo independientes) | Simples 24/24; dobles con uno por bloque 36/36; dobles dentro de un bloque van a otra palabra (24/24) |
| Código [5,2,3] | Los controles de peso ≤ 2 (00011 y 11000) generan 2 de las 3 dimensiones del dual: hace falta un control de peso 3 (fan-in 3 o una etapa XOR extra) |
| Dos errores DATA simultáneos en A | 6 al código original y 6 al opuesto (los pares internos al triángulo) |
| Retardo extra D→E / P→X | 8/8, 1 conmutación por lesión, con el estado completo en t9 / t8 |
| Memoria del disparo dos pasos vieja | La primera ráfaga tiene dos pulsos (repara y vuelve a romper); 8/8 tras 3 conmutaciones, con el estado completo en t14 |
| Asincronía: barrido aleatorio / una coordenada al azar (8 lesiones × 250 semillas por modo) | 529/2000 y 481/2000 restauran; el resto queda en alarma enclavada |
| Pérdida del pulso con probabilidad 0,1 / 0,25 / 0,5 (8 lesiones × 500 semillas) | 3637/4000 = 0,909; 3019/4000 = 0,755; 1986/4000 = 0,497. Es ≈ 1 − pérdida: **no hay reintento** |
| Fallo permanente de x_k | Un pulso, la conmutación anulada y la alarma enclavada (8/8) |
| Lesión que se revierte sola en t1 | El pulso rancio rompe el bit sano en t4 y la red repara su propio error: estado completo en t11 (8/8) |
| Segunda lesión durante la reparación | Tabla de §19 |

**Qué pertenece a una familia amplia y qué es propio de A:**

- **Familia amplia:**
  - códigos cuyos controles de paridad son pares, es decir, sumas directas de códigos de
    repetición más coordenadas constantes;
  - invariancia al reetiquetado;
  - modularidad de los atractores.
- **Propio de A:**
  - el desempate por el triángulo;
  - el disparo único sin reintento;
  - la dependencia de la sincronía;
  - la ventana de una sola corrección en vuelo.

**Claims permitidos por la autopsia:**

- `A_IMPLEMENTS_SINGLE_ERROR_SYNDROME_DECODING_OF_THE_REPETITION_CODE`: EXHAUSTIVE sobre
  A × R_X × q*.
- `A_AUXILIARY_STATE_IS_TARGET_BLIND`: EXHAUSTIVE (complemento en 2²¹ estados;
  `I(q; blanco) = 0`).
- `A_DIRECTION_EQUALS_LOCATION_TIMES_TOGGLE`: INSTANCE_CAUSAL (familias C, D y F).
- `A_P_IS_A_RISING_EDGE_DETECTOR_OF_E`: EXHAUSTIVE sobre las trayectorias P-DATA;
  INSTANCE_CAUSAL (familia G).
- `A_EXACT_21_BIT_RESTORATION_WITHOUT_RESIDUAL_MEMORY`: sobre P-DATA y P-FULL.
- `A_TIE_BREAK_IS_TRIANGLE_MAJORITY`: EXHAUSTIVE sobre los 16 estados de x desde q*.

No se afirma entidad, proto-orgánulo, intención, finalidad ni generalización fuera del
alcance declarado.

## Apéndice E. Cobertura y límites de esta revisión

- **Qué se contrastó.** Las 252 afirmaciones verificables del .docx se contrastaron con
  dos fuentes:
  - para la autopsia, con sus artefactos comiteados en `e4a72f4` y `b5bb8a7` (CSV, JSON y
    código);
  - para los experimentos previos (EXP-01, EXP-02, EXP-03, DISCOVERY-02 y EXP-04A), con
    sus informes, el ledger y las comprobaciones de `autopsy01_verdicts.json`.

  Las 26 que sobrevivieron a una refutación adversarial independiente quedan corregidas en
  el Apéndice C. El borrador corregido se auditó después con siete enfoques más: cobertura
  del .docx, correcciones aplicadas, cobertura de la autopsia y exactitud por secciones.
  Los problemas confirmados quedaron incorporados.
- **Qué se comprobó aparte.** Con `autopsy01_core.py` sin modificar se recalcularon hechos
  que no estaban en ningún artefacto comiteado:
  - las 36 corridas que ciclan en τ = 1–3 (12 por τ) son pares internos al triángulo;
  - las 8 enclavadas en τ = 4 son relesiones del mismo bit;
  - con el refresco q := q* en τ = 1–3, las 36 corridas que ciclaban van al código
    opuesto, y las 60 restantes siguen en el original, sin oscilaciones nuevas;
  - el desglose de las mezclas dobles: 36 ciclan, 24 de la misma coordenada vuelven y 36
    que tocan la coordenada 4 vuelven;
  - el fallo de las asignaciones de 6 comparadores (ciclos de 16);
  - el desglose por blanco de las perturbaciones de dos bits: 183 de 210 vuelven, 9 van al
    opuesto y 18 ciclan;
  - las reglas sólo-X no monótonas con los centros 0000/1110: 6, 6, 6 y 12 por
    coordenada, con `discovery03.py`.

  El ritmo de los ciclos de 12 se leyó del censo comiteado.

  Desde `09153fa`, cuatro de estos resultados están comiteados en
  `artifacts/autopsy01_errata_check.json`:
  - el desglose de las mezclas dobles;
  - el desglose por blanco;
  - las reglas sólo-X con 0000/1110;
  - el ritmo de los ciclos.

  Los otros cuatro (τ = 1–3, τ = 4, el refresco y el fallo de las asignaciones de 6
  comparadores) siguen fuera de todo artefacto.
- **Reejecución.** Durante la revisión se volvió a correr `run_autopsy01_mechanism.py`
  sobre una copia del árbol.
  - Todos sus artefactos coinciden byte a byte con los comiteados, salvo las marcas de
    tiempo del campo `log` de `autopsy01_verdicts.json`.
  - `run_autopsy01_scaling_variants.py` no se reejecutó: sus 4 artefactos se usan tal
    como están comiteados.
- **Profundidad desigual.** Tres fuentes no se revisaron en detalle; las afirmaciones
  sobre ellas se contrastaron con sus informes y con las comprobaciones del ledger:
  - los CSV de EXP-01/02/03;
  - `discovery02.py`;
  - el preregistro de EXP-04A.
- **Objeciones rechazadas.** Las 44 objeciones que el paso adversarial refutó no se
  volvieron a litigar. Las que se aplicaron igualmente como mejoras de redacción figuran
  al final del Apéndice C.
- **Sobre qué texto se trabajó.** Sobre el texto extraído del .docx. Si en la extracción
  se perdió formato, notas o tablas, eso no se verificó.

## Apéndice F. Criterios de aceptación del encargo

| # | pregunta | respuesta | dónde |
| --- | --- | --- | --- |
| 1 | ¿Por qué ocurre la restauración? | Decodificación por síndrome: el bit que discrepa de sus dos testigos se conmuta una vez | §4, §6, §14 |
| 2 | ¿De dónde sale la información del blanco? | De la mayoría en x. El circuito sólo da la ubicación, y la conmutación binaria da el sentido | §5 |
| 3 | ¿Qué reglas detectan el bit dañado? | Los comparadores D detectan; los localizadores E, un AND de dos testigos, localizan | §5, §8 |
| 4 | ¿Qué convierte la detección en una sola acción? | L más P: un detector de flanco de subida | §7, §8 |
| 5 | ¿Por qué termina? | El pulso, por L; el soporte, porque la x corregida anula el síndrome | §7; EXP-02 |
| 6 | ¿Qué es necesario y qué suficiente? | Necesarios: los 17 auxiliares y cada compuerta. Suficientes: un solo evento E, o un solo P elegido desde fuera | §8, §12 |
| 7 | ¿Por qué el peso 2 queda fuera? | Es el conjunto de empates del código; allí el localizador pierde la minoría única y decide el triángulo | §9 |
| 8 | ¿Exacta o funcional? | Exacta en los 21 bits (t7), precedida de restauración funcional (t4–t6) | §10 |
| 9 | ¿Cómo compila Φ con fan-in 2? | Registros intermedios (aridad 3 en 2 capas), un síndrome nulo en ambos códigos y una compuerta temporal | §11 |
| 10 | ¿Qué ley lo describe? | `x(4) = x ⊕ ε(Hx)`, con `x_i(4) = maj3`; lazo con compuerta frente a lazo lineal | §14 |
| 11 | ¿Qué escala? | El decodificador matemático sí, con aridad 2t+1. La arquitectura de A sólo a radio 1, y siempre con el triángulo como núcleo | §14 |

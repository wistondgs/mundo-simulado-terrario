# Orientaciones · dos unidades: el alumno que se vuelve maestro

**Fecha:** 2026-10-28 · **Para:** Opus 5.5 · **De:** Fable · **Adjudicado por Wis:** la población empieza **de a dos**, no de a muchos; la multitud viene cuando la transmisión entre dos funcione. Esta celda **se añade** a la enmienda de la ficha de la Fase 2 (`APERTURA_FASE_2_ACUMULACION.md`) junto a T1/T2 (`ORIENTACIONES_FASE_2_MAESTRO.md`) y corre **en paralelo con C5**, porque no necesita heredar máquina: lo que pasa entre unidades son **palabras**.

**La pregunta.** ¿Una unidad que vivió un mundo puede enseñárselo a otra con lo único que tiene, su propia máquina, posiblemente imperfecta? Y en una cadena alumno → maestro → alumno, ¿lo transmitido se conserva, se degrada o mejora?

**Lo que ya se sabe y lo que es hipótesis** (nivel al lado, E-42):
- Dos agentes cooperando aprenden grafos que uno solo no puede sin maestro: Bender & Slonim 1994 (`LC`, por leer; A4 de `LITERATURA_PENDIENTE.md`). Que eso valga en nuestro banco es `H`.
- En cadenas de transmisión con aprendices deterministas, lo transmitido tiende a **exagerar lo previo** y a lavar los datos según el cuello de botella: Kirby, Dowman & Griffiths 2007 (`LC`), Kirby, Griffiths & Smith 2014 (`SV`). Que nuestra cadena degrade es la **predicción por defecto**; que no degrade sería el hallazgo.
- La instrucción canaliza la exploración, para bien y para mal: Derex et al. 2025 (`SV`, `X13`). Un maestro con máquina equivocada canaliza hacia el error: `H` en nuestro banco, y es el control principal.
- Ya medido aquí (`M`, exploratorio): elegir ayuda con esqueleto correcto y estorba con esqueleto falso (43 vs 22 / 63 vs 95 pareado). El maestro-unidad es un esqueleto **externo**: el signo debería repetirse.

---

## 1 · Las unidades y lo que pasa entre ellas

- **Maestra (U_m):** una unidad de 08 que vivió W con el itinerario fijo y terminó con su máquina H_m (identificada o no: **las dos clases entran**, porque la pregunta incluye al maestro imperfecto).
- **Alumna (U_a):** fresca, vive el mismo W desde el mismo estado inicial, con el mismo presupuesto de vida que F1.
- **Lo único que pasa de U_m a U_a: palabras.** En cada paso en que la hipótesis de U_a predice distinto de lo que H_m predice para la misma situación, U_m le da **la palabra más corta** (≤ 2·|Q|) en la que, según H_m, la predicción de U_a falla; U_a la vive. U_m **no** le entrega transiciones, estados ni salidas; **no** ve el mundo durante la enseñanza: enseña desde su máquina, aunque esté equivocada. Es T1 con una unidad en el lugar del maestro omnisciente.
- **Cómo sabe U_m qué predice U_a:** porque las dos declaran su predicción antes de actuar (ya lo hacen en `vivir`). Es la única señal que cruza, y es la mínima: un bit por paso.
- **Nada de azar.** Si varias palabras empatan, el orden shortlex decide.

## 2 · Las celdas

| celda | maestro | qué controla |
|---|---|---|
| **F1** | ninguno | la vara (ya existe) |
| **T1** | omnisciente (conoce W) | el techo de lo que un maestro puede (ya en la enmienda) |
| **U1** | **unidad maestra que identificó W** | ¿una unidad enseña tan bien como el omnisciente cuando tiene razón? |
| **U2** | unidad maestra que **no** identificó W (máquina incompleta o errónea) | ¿canaliza hacia el error? (Derex) |
| **U3** | unidad maestra de **otro** mundo W′ de la misma clase | mutante: enseñar lo ajeno; predicción: ≤ F1 |
| **U-sham** | unidad maestra que da palabras donde U_a **acierta** según H_m | mutante: ≈ F1 |
| **Cadena K5** | U_a se vuelve maestra de una tercera, y así hasta 5 generaciones; cada generación vive W con el mismo presupuesto | la transmisión a lo largo del linaje: Kirby |
| **Pareja coop.** | **dos frescas** que se enseñan mutuamente (cada una da a la otra el contraejemplo según su propia máquina) | Bender–Slonim: ¿dos sin maestro llegan donde una sola no? |

Mismo banco de la Fase 2 (los 174 W₁ y sus familias W₂; para esta celda W = W₂ de la clase componible y de la control, pareado por familia). Mismo presupuesto de vida en todas las celdas, contado **para la alumna**; el gasto de la maestra se registra aparte y no decide (norma de Wis).

## 3 · Medidas (desarrollo, no coste)

- **Alcance** de U_a en la curva (64, 128, 256), pareado por familia contra F1 y contra T1.
- **Coste empírico de enseñanza:** intervenciones de U_m hasta que U_a identifica, por estrato; comparado con T1.
- **Fidelidad en la cadena K5:** por generación k, (i) ¿U_k identifica W? (ii) distancia entre la máquina de U_k y la de U_{k−1} (isomorfismo canónico sí/no; si no, número de transiciones distintas); (iii) alcance de U_k. La curva de fidelidad por k es el dato de Kirby.
- **Canalización** (Derex): número de hipótesis canónicas distintas que U_a visita con y sin maestro; si la verdad quedó dentro.
- **Retención y transferencia** (como en la enmienda del maestro): U_a sigue 512 pasos sin maestra; luego una cascada W₃ sin maestra, contra fresca.
- **Cooperación:** en la pareja, fracción de familias donde **ambas** identifican frente a la fracción de F1; y familias donde identifica la pareja y no F1 (pareado).

## 4 · Predicciones, antes de correr

1. **U1 ≈ T1 > F1** en alcance temprano en las familias donde `contraejemplos_imposibles` = 0: una unidad que tiene razón enseña como el omnisciente, porque lo que enseña es dónde mirar, no la verdad.
2. **U2 ≤ F1** en alcance, con canalización: U_a visita **menos** hipótesis y la verdad queda fuera más veces que sin maestra. Es el precio del maestro equivocado, y debe aparecer para que el mecanismo sea lo que creemos.
3. **U3 ≤ F1**, **U-sham ≈ F1**.
4. **Cadena K5:** predicción por defecto (Kirby), la fidelidad **cae** con k: U_5 identifica menos que U_1 y su máquina se aleja de la de U_1. Si la fidelidad se **mantiene** (identificación constante, máquinas isomorfas), es el hallazgo: lo transmitido por contraejemplos **no se lava**, porque cada alumna lo verifica en el mundo antes de volverse maestra. Eso es «antes de maestro, alumno» como resultado y no como lema.
5. **Pareja cooperativa:** identifica familias que F1 no (pareado > 0), concentradas en la clase recurrente; cero efecto en los transitorios.

**Falsadores.** U1 ≈ F1 con intervenciones > 0: una unidad no puede enseñar a otra con palabras en este banco. Fidelidad que **mejora** con k sin que mejore la identificación: la cadena converge a algo estable y falso (el prior exagerado de Kirby) y hay que decirlo. Si U-sham ≠ F1, el instrumento filtra información por otro canal que no son las palabras: defecto.

## 5 · Mutantes obligatorios, antes de la corrida real

U3 y U-sham (arriba); además **M-canal:** una alumna que recibe las palabras de U_m pero **no las vive** (las registra sin ejecutarlas) debe dar exactamente F1, para probar que el único canal es vivir la palabra. Presupuestos igualados; sin azar; mismo tope de longitud.

## 6 · Lo que esta celda deja preparado

- Si U1 ≈ T1: el maestro **no necesita ser omnisciente**: Opus y Fable no tienen que enseñar paso a paso; basta una unidad que ya vivió. Es la condición para que el linaje se enseñe a sí mismo.
- Si la cadena K5 conserva: Genesis tiene un segundo contenido que guardar además de las relaciones certificadas: **quién enseñó a quién y con qué palabras**, que es la genealogía del linaje.
- Si la pareja cooperativa supera a F1: la población de muchos tiene sentido y se diseña entonces; si no, se multiplica después de C5, no antes.

## 7 · Orden y roles

1. C5 y sus seis mutantes siguen primero; esta celda se **construye en paralelo** porque reutiliza `vivir`, `letra_elegida` y las familias de 08, y sólo añade la maestra como segunda unidad y el canal de un bit.
2. Enmienda prospectiva de la ficha: celdas U1, U2, U3, U-sham, K5, pareja; mutante M-canal; medidas y predicciones de §3–§4.
3. Corrida pareada sobre el banco de la Fase 2; cierre junto con C5 y T1/T2, con **una pregunta para Wis**: la que veo venir es si la población de muchos se abre ya o tras heredar máquina.

**Opus** construye y corre; **Fable** revisa la enmienda antes de la corrida y el cierre después; **Wis** adjudica. Ningún paso enseña paso a paso desde Opus o Fable: el maestro es una unidad.

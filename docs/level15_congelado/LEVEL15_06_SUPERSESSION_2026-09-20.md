# NIVEL 1.5 — SUPERSESIÓN DEL PILOTO DE COAPRENDIZAJE

**Fecha:** 2026-09-20  
**Estado:** diseño/piloto; Nivel 1.5 sigue sin rama, carpeta ni código de implementación.  
**Función de este documento:** preservar el snapshot anterior sin reescribirlo y declarar de forma explícita qué afirmaciones dejan de ser canónicas a la luz de evidencia posterior.

## 0. Regla de archivo

El paquete anterior `LEVEL15_DISENO_2026-09-20.zip` se conserva como snapshot histórico íntegro.

SHA-256 del paquete histórico:

`135d07ea36d13d554a200c59f31d3e866e2ce768212821e8606c06c9cfab9d78`

SHA-256 de su manifiesto histórico:

`15444032a977f75b831b5ff12a365321e01374d9e02c34b81afecfcf07449c06`

Los cinco documentos 01–05 incluidos aquí permanecen byte-idénticos al snapshot anterior. **No deben leerse aisladamente como estado canónico actual:** este documento de supersesión tiene precedencia sobre las afirmaciones retiradas que se enumeran abajo.

---

## 1. Qué provocó la supersesión

El piloto anterior de coaprendizaje usaba una regla de actualización que generó tasas de llegada a clase de:

- `R_G = 31/40`
- `R_P = 28/40`
- `R_J = 31/40`

y llevó a descomponer 30 fallos en:

- 9 óptimos locales exactos;
- 21 fallos no-local-optimum interpretados como barreras de coordinación encoder↔decoder.

Una nueva campaña exploratoria cambió la **regla de actualización** a paso constante, manteniendo el mecanismo de dos tablas y los contratos de información. Bajo esa regla, las tasas de llegada aumentaron drásticamente.

Por tanto, los 21 fallos anteriores **no pueden canonizarse como propiedad del problema de Nivel 1.5**. Eran, al menos en gran medida, consecuencia de la dinámica de actualización anterior.

---

## 2. Evidencia nueva explícitamente disponible

Resultados suministrados para tres semillas, dos presupuestos visibles y 20 repeticiones por celda:

| semilla | presupuesto | R_G | R_P | R_J |
|---:|---:|---:|---:|---:|
| 20260920 | 10.000 | 20/20 | 19/20 | 20/20 |
| 20260920 | 100.000 | 20/20 | 20/20 | 20/20 |
| 777 | 10.000 | 20/20 | 17/20 | 20/20 |
| 777 | 100.000 | 20/20 | 19/20 | 20/20 |
| 31337 | 10.000 | 19/20 | 19/20 | 20/20 |
| 31337 | 100.000 | 20/20 | 20/20 | 20/20 |

Agregados exactos derivados de esa tabla:

### Presupuesto 10.000

- `R_G = 59/60 = 98.333... %`
- `R_P = 55/60 = 91.666... %`
- `R_J = 60/60 = 100 %`
- total `174/180 = 96.666... %`

### Presupuesto 100.000

- `R_G = 60/60 = 100 %`
- `R_P = 59/60 = 98.333... %`
- `R_J = 60/60 = 100 %`
- total `179/180 = 99.444... %`

---

## 3. Discrepancia pendiente de reconciliar

El reporte textual afirma:

> `540 corridas, tres semillas, tres presupuestos`

pero la tabla suministrada contiene:

`3 semillas × 2 presupuestos × 3 regímenes × 20 repeticiones = 360 corridas`.

No se suministró en el mensaje la fila del tercer presupuesto.

Por tanto:

- **no se canoniza todavía el total de 540 como evidencia tabulada**;
- **no se inventa ni reconstruye el tercer presupuesto**;
- la evidencia canónica de esta supersesión se limita a las 360 corridas explícitamente mostradas;
- el total de 540 queda marcado `PENDING_RECONCILIATION` hasta incorporar la tercera tabla.

Esta discrepancia no impide retirar las afirmaciones antiguas, porque los dos presupuestos visibles ya contradicen materialmente las tasas previas.

---

## 4. Afirmaciones que quedan RETIRADAS

### R1 — Tasas `31/40`, `28/40`, `31/40` como expectativa vigente

Quedan históricas, ligadas a la regla de actualización anterior.

No deben utilizarse como tasa esperada del mecanismo vigente.

### R2 — “30 fallos = 9 óptimos locales + 21 barreras de coordinación” como propiedad del problema

Queda retirada.

Ese desglose describe una ejecución bajo la regla anterior, no una propiedad estructural de Nivel 1.5.

La categoría “barrera de coordinación” sigue siendo conceptualmente posible, pero su frecuencia anterior no puede preregistrarse como fenómeno inherente sin reproducirla bajo la regla vigente.

### R3 — `R_P` como régimen estructuralmente más difícil

Queda retirada en su forma fuerte.

Con paso constante, a 10.000 ensayos aparece un transitorio:

- `R_P = 55/60`
- `R_G = 59/60`
- `R_J = 60/60`

pero a 100.000:

- `R_P = 59/60`
- `R_G = 60/60`
- `R_J = 60/60`.

La formulación canónica pasa a ser:

> **R_P muestra una desventaja transitoria pequeña a bajo presupuesto en el piloto visible; la diferencia prácticamente desaparece con más experiencia. No se ha demostrado una dificultad estructural del régimen.**

No se preregistra explicación causal.

### R4 — `100.000` ensayos como presupuesto seleccionado por saturación

Queda retirada.

La selección de 100.000 se apoyaba en la curva de la regla anterior. Con paso constante, 10.000 ensayos ya producen `174/180 = 96.67 %` de llegada a clase y 100.000 producen `179/180 = 99.44 %`.

Por tanto el presupuesto confirmatorio debe **derivarse de nuevo desde cero** bajo la regla vigente.

No se fija en esta supersesión un presupuesto nuevo.

### R5 — `15–21 %`, `20–35 %` o cualquier banda anterior como frecuencia canónica de fallo

No se conserva ninguna de esas bandas como expectativa del experimento vigente.

Las frecuencias dependen materialmente de la regla de actualización y del presupuesto.

---

## 5. Qué permanece VIGENTE

### V1 — Entregable 1

Permanece vigente la estructura matemática del constructo, incluyendo:

- cuello de botella `16 estados → 4 mensajes`;
- capacidad abstracta de 2 bits;
- tres familias diagnósticas H1/H2/H3;
- matriz discriminante;
- óptimos analíticos `1/8`, `1/8`, `1/10`;
- cota de representación fija `L >= 1/3`;
- selector ideal `7/60`;
- lema combinatorio y sus verificaciones posteriores;
- isomorfismo de las 9 variantes conjuntas;
- cierre del caso estocástico por convexidad.

Ninguno de estos resultados depende de la regla de aprendizaje piloto.

### V2 — Endpoint primario

Sigue vigente:

> **resultado primario = clase informacional aprendida**.

El óptimo exacto sigue siendo secundario.

La nueva evidencia refuerza que las tres clases aparecen con alta frecuencia bajo una regla de aprendizaje adecuada, pero no convierte las tasas piloto en resultado confirmatorio.

### V3 — Feedback mínimo

Sigue vigente:

`1 ensayo → 1 retención → 1 respuesta → 1 bit`.

Sin reevaluación contrafactual del mismo ensayo.

### V4 — Tres contratos anti-fuga

Siguen vigentes:

1. decoder recibe sólo `(z,q)`;
2. por ensayo existe exactamente una actualización del encoder y una del decoder;
3. encoder y decoder permanecen read-only entre retención y respuesta.

### V5 — Mecanismo de dos tablas

Sigue vigente como mecanismo mínimo candidato:

- una tabla aprende qué mensaje emitir;
- una tabla aprende cómo leer el mensaje para cada tipo de consulta.

La corrección actual es que la dinámica usa **paso constante**, no la regla anterior de media corrida.

**La magnitud exacta del paso constante no consta en la evidencia textual preservada aquí y debe especificarse antes del preregistro final.**

### V6 — H1/H2/H3 no son acciones

Siguen siendo regiones diagnósticas del espacio completo de `4^16` encoders, nunca opciones ofrecidas al organismo.

---

## 6. Consecuencia epistemológica

La nueva evidencia cambia una interpretación importante:

Antes parecía que el coaprendizaje encoder↔decoder introducía una barrera de coordinación que explicaba gran parte de los fallos persistentes.

Con una regla de actualización diferente, la llegada a clase se aproxima a techo incluso a 10.000 ensayos.

Por tanto, **no puede atribuirse al constructo una dificultad observada bajo una sola dinámica de aprendizaje**.

La distinción correcta pasa a ser:

- propiedades del constructo: demostradas analíticamente;
- propiedades del mecanismo: dos tablas + feedback local;
- propiedades de la dinámica de optimización: dependientes de regla de actualización, paso, exploración y presupuesto.

---

## 7. Próximas decisiones que quedan abiertas

Antes de preregistro/implementación faltan, como mínimo:

1. reconciliar el tercer presupuesto que falta en la tabla de 540 corridas;
2. especificar exactamente la regla de paso constante y su parámetro;
3. redeterminar el presupuesto confirmatorio con la regla vigente;
4. mantener o rediseñar el análisis de sensibilidad a exploración;
5. fijar semillas y número final de repeticiones sólo después del nuevo análisis presupuestario;
6. conservar los tres contratos anti-fuga como validity gates.

Hasta entonces:

`NO IMPLEMENTAR`.

---

## 8. Regla de lectura del paquete

Orden de autoridad documental:

1. `LEVEL15_06_SUPERSESSION_2026-09-20.md` para cualquier afirmación retirada o corregida;
2. documentos 01–05 para material no supersedido;
3. `MANIFEST_LEVEL15_V1_FROZEN.md` sólo como registro histórico del snapshot previo.

La integridad del snapshot anterior se conserva. La supersesión cambia su **autoridad**, no sus bytes.

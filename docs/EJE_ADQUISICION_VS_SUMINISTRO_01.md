# El eje del proyecto · qué adquiere y qué le damos

**2026-09-20.** No es un informe de experimento: es la doctrina metodológica que
Wis fijó como eje principal, con la evidencia del linaje que la sostiene.

---

## 1 · La pregunta

> ¿Cómo hago para que el cibernético **adquiera** una habilidad cognitiva sin que
> yo se la programe ya resuelta?

Si le programamos «memoria», «selección», «binding» o «predicción» con toda la
lógica correcta, el organismo **usa** una habilidad. No necesariamente la
adquirió.

El cambio de eje: dejar de preguntar *«¿cuál es la siguiente habilidad que le
ponemos?»* y preguntar *«¿cuál es la menor maquinaria que podemos darle para que
una capacidad que antes no existía aparezca por experiencia?»*.

## 2 · «Adquirido» no es propiedad de un experimento

Siempre se puede redescribir lo suministrado como «más general» y reclamar que se
dio menos. La frase no decide nada. Lo que decide es un hecho comprobable:

> Un mecanismo es general **exactamente en la medida en que el mismo código,
> congelado, produce capacidades distintas bajo experiencias distintas.**

Eso no lo puede establecer un experimento: lo establece una **familia**. Y da un
criterio de admisión operativo para cualquier mecanismo nuevo — no «¿es mínimo?»
sino **«¿de cuántas capacidades distintas es suficiente sin modificarse?»**.

## 3 · Tres capas, no dos

La frontera «programado / aprendido» es binaria y es insuficiente. Hay una capa
intermedia que se cuela sin declararse porque parece un hiperparámetro.

**La evidencia que la obliga**, medida en el diseño de 1.5 con el mismo mecanismo,
la misma información y el mismo mundo:

```
V₀ = 0.0   →   0/20   0/20   0/20        la capacidad NO aparece
V₀ = 0.5   →  20/20  20/20  20/20        aparece siempre
```

`V₀ = 0.5` dice *«trata lo no probado como si valiera una moneda al aire»*;
`V₀ = 0` dice *«lo no probado no vale nada»*. La primera hace posible la búsqueda;
la segunda la mata. Eso no es un mecanismo ni es una solución.

```
LA SOLUCIÓN      qué guardar · qué significa cada mensaje · qué dirección significa un cue
EL MECANISMO       tablas, regla de actualización, alfabeto, composición
LA DISPOSICIÓN   optimismo ante lo desconocido, desempates, prior
```

**Cada nivel debe declarar las tres.** Y el proyecto debe medir, a lo largo de los
decimales, si la segunda y la tercera se mantienen constantes mientras la primera
cambia.

## 4 · El libro mayor del linaje

| nivel | la solución (aprendida) | el mecanismo (dado) | la disposición (dada) |
|---|---|---|---|
| 1.1 | qué dirección significa cada cue | Beta-Bernoulli · composición `B·Q` | prior `Beta(1,1)` |
| 1.2 | `H(s) = P(CERCA\|s)` | Beta-Bernoulli · composición `B·Q·H` | prior `Beta(1,1)` |
| 1.3 | **nada** — `M` no tiene parámetros | registro de un tick, TTL 1 | — |
| 1.4 | la correspondencia `ψ` | conteo con prior · argmax sobre 2 asignaciones | prior uniforme `1` |
| 1.5 | el código **y su lectura** | dos tablas de valor · `ε`-greedy · `α` | `V₀ = 0.5` · desempate por índice |

**Hecho de código, y es más favorable de lo que parece:** 1.1, 1.2 y 1.4 usan **la
misma familia de mecanismo** — conteo bayesiano con prior uniforme, media
posterior. Tres decimales con una sola maquinaria.

**Y se rompió en el cuarto, con el punto de rotura medido.** La media corrida
--que es exactamente el conteo-- no puede desaprender, y en 1.5 el significado de
los mensajes cambia mientras el descodificador se forma. Resultado:

```
media corrida (= conteo)   30/40   26/40   31/40
paso constante             40/40   40/40   40/40
```

No es que cambiáramos de maquinaria por gusto: **la vieja falló y sabemos dónde**.

## 5 · Lo que más regalamos y nunca examinamos

Cuatro veces hemos escrito a mano la regla de composición: `B·Q`, `B·Q·H`,
`B·Q(M)·H`, `B·Q·ψ`. Los cuatro informes lo declaran honestamente --«la
factorización la suministramos nosotros»-- pero **nunca la convertimos en
objetivo, y nunca la hicimos falsable**.

El organismo jamás ha tenido que averiguar **cómo** se combinan sus conocimientos;
sólo **con qué** valores. Mientras esa regla la pongamos nosotros cada vez, lo que
hay es una colección bien atornillada, no un organismo.

## 6 · Dónde está 1.5 exactamente

Es lo más cerca que se ha estado, y conviene la precisión: el organismo rellena
una tabla de `16×4` y **no puede representar nada fuera de ese espacio**. Elige
qué conservar dentro de un conjunto de opciones que dibujamos nosotros.

Lo que sería más: que pudiera cambiar **la forma** del espacio.

> **Propuesta · convertir la capacidad en un coste, no en una restricción.**
>
> En vez de «tenés exactamente cuatro mensajes», que cada mensaje distinguible
> adicional pague algo. Entonces *cuántos bits gastar* pasa a ser parte de lo que
> aprende, no parte de lo que le damos.

Es estrictamente más grande que 1.5 y no requiere maquinaria nueva: cambia una
restricción dura por una blanda. Y contesta de paso la pregunta de si el organismo
puede detectar que sus capacidades no bastan — un organismo que paga por capacidad
y ve que pagar más mejora, lo ha detectado sin que nadie se lo diga.

## 7 · La pregunta abierta, y es la del proyecto entero

Si dentro de cinco decimales seguimos con la misma maquinaria y la misma
disposición, y han aparecido cinco capacidades distintas, tenemos un mecanismo
general y podemos decirlo con números.

Si cada decimal necesita la suya, lo que tenemos es una colección de
demostraciones --bien hechas, todas verificadas-- de que sabemos programar
habilidades una por una.

**Ahora mismo estamos en medio:** una familia de mecanismo cubrió tres decimales
y falló en el cuarto por una razón identificada. Eso es un dato, no un veredicto.

## 8 · Qué medir de aquí en adelante

```
1. cada nivel declara sus TRES capas, no dos
2. un mecanismo nuevo se admite por su ALCANCE, no por su minimalidad:
   ¿de cuántas capacidades distintas es suficiente sin modificarse?
3. la prueba de generalidad es coger el mecanismo CONGELADO y ponerlo en un
   mundo donde lo útil sea otra cosa. Si aparece otra capacidad, era general.
   Si hay que retocarlo, suministramos la capacidad.
4. la regla de composición deja de ser un regalo tácito y pasa a ser objetivo
```

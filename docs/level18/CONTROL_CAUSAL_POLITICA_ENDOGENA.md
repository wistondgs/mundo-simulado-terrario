# Control causal cuando la política deja de ser pasiva

```
┌────────────────────────────────────────────────────────┐
│   EXPLORATORIO / CALIBRACIÓN  ·  NO CONFIRMATORIO      │
│   no diseña ninguna capacidad                          │
└────────────────────────────────────────────────────────┘
```

**Fecha:** 2026-09-20 · base `6cf55a4` · no modifica ningún archivo de 1.7

---

# 0 · Por qué esto precede a cualquier diseño

Hasta 1.7 todos los controles del linaje descansan en una sola propiedad:

> `life.py` **no importa el aprendiz**, luego la trayectoria no puede depender de
> lo aprendido, luego todos los brazos viven **literalmente la misma vida** y el
> hash lo demuestra.

Eso es lo que hace que `L17-5 BASELINE-PARITY` pueda decir «mismas transiciones,
sólo difieren en el acceso al comando». Y es lo que se rompe en el instante en que
el estado aprendido toca la política.

**Y tiene que romperse.** Si las trayectorias no divergen, no hay generación
selectiva de experiencia que demostrar. La divergencia **es** el fenómeno.

```
mientras la política es pasiva      exigir PARIDAD DE TRAYECTORIA
cuando la capacidad la modifica     exigir PARIDAD DE CONDICIONES Y AZAR EXÓGENO
                                    y demostrar la cadena con lesión + yugo + trasplante
```

---

# 1 · Qué azar se puede acoplar entre trayectorias que divergen

## 1.1 · La propuesta: acoplar por la **variante uniforme**, no por la acción

S0 hoy emite un acto. La forma que conserva el máximo de paridad lógicamente
posible es que S0 emita una **variante uniforme** `u_t ∼ U(0,1)` y que cada brazo la
mapee por su propia política:

```
LESIÓN   a_t = F⁻¹_uniforme(u_t)
FULL     a_t = F⁻¹_{π(·|O_t, C_18)}(u_t)
```

Con eso:

```
π = uniforme   ⇒  las acciones son IDÉNTICAS, paso a paso
π ≠ uniforme   ⇒  divergen exactamente donde el selector tiene algo que decir
```

**La paridad se recupera exactamente allí donde el selector calla**, y no se pierde
por construcción sino sólo donde el fenómeno ocurre. Es acoplamiento por números
aleatorios comunes con inversa de la acumulada, y es implementable sin tocar S0:
`EndogenousMotor` ya consume un `Generator` propio; lo único que cambia es qué se
hace con el sorteo.

**Instrumento gratis:** la fracción de pasos en que el mapeo difiere mide *cuánto
intervino el selector de hecho*, no cuánto podría.

## 1.2 · El límite honesto de ese acoplamiento

En cuanto divergen en el paso `t`, `O_{t+1}` difiere, y desde ahí la misma `u` se
mapea sobre estados distintos. **Se obtienen números aleatorios comunes, no
trayectorias comunes.** No hay forma de tener las dos cosas: pedirlas sería pedir
que el selector no hiciera nada.

## 1.3 · Qué más se acopla, y cómo

```
topología y celda natal    [s,0]     acoplable entero · anterior a toda acción
cableado φ                 [s,64]    acoplable entero · fijo al nacer
efecto del mundo B         [s,65]    acoplar por ÍNDICE DE PASO, no por posición
baraja, nulas              [s,2], [s,128+k]   no participan de la vida
```

El de B importa: si se acopla «por situación» en vez de por índice, dos brazos que
visitan celdas distintas consumirían el flujo en desorden y el gemelo dejaría de
ser gemelo.

---

# 2 · La unidad pareada

Sigue siendo **el mundo/semilla**. Lo que cambia es que dentro de cada semilla ya no
hay dos condiciones sino cuatro:

```
              mundo A          mundo B
FULL          selector activo  selector activo
LESIÓN        C_18 = 0 → S0    C_18 = 0 → S0
```

El endpoint debe ser un contraste **dentro de la semilla**. Nunca la transición: eso
ya estaba sellado en 1.7 y con política endógena es aún más importante, porque las
transiciones dejan de ser intercambiables entre brazos.

---

# 3 · El yugo de experiencia, sin fugas

FULL genera su trayectoria selectiva. Esa experiencia se entrega a un aprendiz
idéntico **sin selector**.

**Tres vectores de fuga, y el tercero no es obvio:**

```
1  el yugado recibe SÓLO los tripletes (O, A, O'). Nunca el selector, nunca sus
   conteos, nunca la señal de necesidad.

2  arranca del MISMO M_0^W. Si arrancara de otro sitio, la diferencia mediría
   herencia y no experiencia.

3  el banco de evaluación NO puede haber sido producido por la política bajo
   prueba.
```

El tercero es el que rompería el experimento en silencio. En 1.7 el banco POST venía
del mismo S0 uniforme y por eso era neutral. Con política endógena, si FULL genera
su propio POST, **está eligiendo también en qué lo examinan**: sesgaría la
evaluación hacia justo lo que decidió muestrear.

```
el banco POST debe generarlo S0 UNIFORME después del freeze,
idéntico para todos los brazos
```

Eso mantiene intacta la propiedad que hizo interpretable a 1.6 y 1.7: se evalúa
sobre futuro que el ser no vio **y que no escogió**.

---

# 4 · Separar «consiguió mejor experiencia» de «aprende mejor»

La cadena que propusiste, con lo que hay que añadirle para que cierre:

```
A · LESIÓN        C_18 = 0 → S0, mismo snapshot, mundos gemelos, azar acoplado
                  ¿tener C_18 cambia la experiencia conseguida?     ΔD_E

B · YUGO          la experiencia de FULL a un aprendiz sin selector
                  si también aprende más  ⇒  la ventaja estaba en la EXPERIENCIA

C · TRASPLANTE    a FULL se le da experiencia de S0, sin dejarle seleccionar
                  si su ventaja desaparece  ⇒  C_18 necesita ACTUAR para producirla
```

```
C_18  →  Δπ  →  Δexperiencia  →  Δaprendizaje
```

**Lo que hay que añadir:** el aprendiz del yugo tiene que ser **el mismo código, y
demostrablemente el mismo** — copia byte a byte verificada contra un blob de git, o
identidad de objeto. Es el idioma que el linaje ya usa para las fusiones. Sin eso,
`B` no separa nada: cualquier diferencia podría venir del aprendiz.

---

# 5 · Qué sustituye a `BASELINE-PARITY`

```
ANTES (1.7)   mismo M_0^W · MISMAS TRANSICIONES · difieren sólo en el acceso al comando
AHORA         mismo M_0^W · MISMO CÓDIGO DE APRENDIZ · mismo mundo · mismo azar exógeno
              las transiciones DIFIEREN, y esa diferencia es la medición
```

Propuesta de nombre: **`EXPERIENCE-ATTRIBUTION`**.

La paridad se muda de *los datos* a *(estado inicial, aprendiz, mundo, azar
exógeno)*. Lo que antes se eliminaba, ahora se mide.

## 5.1 · Un modo de fallo nuevo, que sólo existe con política endógena

Un selector puede **ganar degenerando**: quedarse muestreando un contexto para
siempre sube `D_E` en ese contexto y destruye la cobertura en todos los demás.

Consecuencia: **`EXPOSURE` deja de ser instrumento y pasa a ser endpoint con
criterio de dos lados.** No basta con «visitó más lo que le faltaba»; hace falta que
no haya abandonado el resto. Y el cuarteto de 1.7 —`E_rate`, `E_total`, `C_OA`,
`N(o,a)`— ya está construido para decirlo.

---

# 6 · Qué gates de 1.7 sobreviven

| gate | destino | por qué |
|---|---|---|
| `L17-0` LINEAGE | **sobrevive** | es sobre el árbol, no sobre la política |
| `L17-1` WORLD-PAIR | **sobrevive** | es sobre el mundo; el gemelo sigue haciendo falta |
| `L17-2` ACTION-PROVENANCE | **cambia de sentido** | los actos ya no salen sólo de S0. Debe pasar a: *la variante uniforme salió de S0 y el mapeo es la π declarada* |
| `L17-3` EFFERENCE-PURITY | **sobrevive** | el canal sigue siendo comando opaco anterior a la consecuencia |
| `L17-4` INCREMENTAL-INVARIANT | **sobrevive, extendido** | `C_18 = 0 ⇒ π = S0` y la lesión devuelve a 1.7 exactamente |
| `L17-5` BASELINE-PARITY | **deja de tener sentido** | sustituido por `EXPERIENCE-ATTRIBUTION` |
| `L17-6` EXPOSURE | **sobrevive y asciende** | de instrumento a endpoint, con criterio de dos lados |
| `L17-7` ACTION-ACQUISITION | **sobrevive en forma** | cambia qué se contrasta, no cómo |
| `L17-8` NULL-WORLD | **sobrevive** | el aprendiz sigue pudiendo inventar ventaja |
| `L17-9` ACTION-NECESSITY | **sobrevive** | destruir la correspondencia debe seguir matando la ventaja |
| `L17-10` OPAQUE-MAPPING | **sobrevive** | y se vuelve más exigente: la π tampoco puede ver `φ` |
| `L17-11` INTERNAL-LOCALIZATION | **sobrevive** | la lesión debe aislar `C_18` y dejar `M_0^W` y `C_17` intactos |
| `L17-12` PASSIVITY-REPLAY | **se parte en dos** | *evaluar no modifica al ser* sobrevive; *el ser no influye en su trayectoria* **deja de ser cierto por diseño** y hay que retirarlo |

Gates nuevos que la transición hace necesarios, sin diseñarlos todavía:

```
EXPERIENCE-ATTRIBUTION      lesión + yugo + trasplante, la cadena entera
EVALUATION-NOT-SELECTED     el banco POST lo produce S0, no la política bajo prueba
COUPLING-INTEGRITY          la variante uniforme es común y el acoplamiento por
                            índice de paso es verificable
NO-DEGENERATE-SAMPLING      el selector no gana abandonando el resto del espacio
```

---

# 7 · La doctrina que queda propuesta

> Mientras la política es pasiva, exigir **paridad de trayectoria**. Cuando una
> capacidad nueva cambia causalmente la política, exigir **paridad de condiciones y
> azar exógeno**, y demostrar la cadena mediante **lesión + yugo + trasplante**.

Con dos añadidos que salen de aquí:

```
· acoplar por la variante uniforme, no por la acción: recupera la paridad
  exactamente donde el selector calla, y localiza la divergencia donde actúa

· el banco de evaluación nunca lo produce la política bajo prueba
```

**No es un detalle de 1.8.** Desde el momento en que el organismo empieza a escoger
su experiencia, dos organismos experimentalmente distintos ya no deberían vivir la
misma vida — y eso afecta a todos los decimales que vengan después.

---

# 8 · Lo que queda sin resolver

```
la forma de π(A|O, C_18) y si el sesgo es aditivo, multiplicativo o de temperatura
cómo se declara «reducible» de forma que el suelo del aliasing no la contamine
si el selector debe poder apagarse solo, y con qué
qué presupuesto hace justicia a la escasez sin volver trivial el problema
si LESIÓN debe ser C_18=0 o S0 puro, que no son lo mismo si π tiene forma propia
```

Ninguna de ellas es mía. Todas preceden al diseño de la capacidad.

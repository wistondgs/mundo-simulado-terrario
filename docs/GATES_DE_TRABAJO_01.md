# Gates de trabajo

Estos gates no son normas de estilo. Cada uno existe porque un fallo concreto costó algo concreto,
y cada uno tiene un comando que lo comprueba. Un gate que dependa de recordarlo no es un gate: eso
ya se intentó y cedió bajo prisa.

Complementan los invariantes de gobierno científico I-01…I-14 del documento canónico de misión.
Aquellos dicen qué cuenta como conocimiento; éstos dicen **en qué orden trabajar** para no
fabricarlo por accidente.

---

## G1 · Documentación antes que construcción

**Antes de tocar un subsistema, se consulta la cartografía. Si está desactualizada, se lee el
código y se actualiza primero.**

```bash
python scripts/cartografia_check.py
```

Sale `0` si todo lo que la cartografía describe sigue como estaba; sale `1` listando las secciones
obsoletas y **qué fichero** las invalidó. Tras releer y reescribir una sección:

```bash
python scripts/cartografia_check.py --write
```

### El fallo que previene

Construir sobre código no leído. En la noche del 17 de septiembre se edificó el Contrato de Acción
v2, el rollout pareado y el examen de capacidad sobre un código que no se había leído. Después la
cartografía invalidó tres cosas:

| Lo que se creyó | Lo que decía el código | Dónde |
|---|---|---|
| el examen entrega el canal causal en el índice 0 | el runtime pone occupancy en 0 y desplaza los canales del objeto a 1..3 | `state.py:104-108` |
| «modelo del mundo» y «planificador» son dos mecanismos | la rama está condicionada a los dos flags: es una | `a4_advanced.py:517` |
| los experimentos corren en D4T | corren en el banco, que no ejecuta el ciclo de oportunidades que D4T declara | `controller.py:193` vs `sandbox_runtime.py:104` |

Las tres eran legibles antes de escribir una línea de experimento.

### Por qué hashes y no buenas intenciones

Un documento no puede decir por sí solo si sigue siendo cierto. Un hash sí. El manifiesto convierte
la cartografía en **caché invalidable** en vez de notas que envejecen en silencio — el mismo patrón
que ya hace funcionar el inventario de RNFE, y el mismo que `protected_file_hashes` usa para las
fuentes protegidas.

La lista de ficheros por sección **se deriva del propio documento**, que ya cita `fichero:línea` en
todas partes. Un manifiesto mantenido aparte se desincroniza del texto que describe, que es
exactamente el fallo que este gate existe para impedir.

---

## G2 · Alcance del defecto antes de la reparación

**Antes de actuar sobre un defecto, enumerar qué rutas de ejecución lo alcanzan.** La lista entra
en el mensaje del commit.

```bash
grep -rn "NombreDeLaClase\|nombre_de_la_funcion" terrario/ scripts/ --include=*.py
```

### El fallo que previene

Se paró un rollout en marcha y se relanzó por el acoplamiento de RNG del `OpportunityLifecycle`.
Ese mecanismo **sólo lo construye `ExperimentController`**, así que no estaba en la ruta del banco
donde corría el experimento. Costó diez minutos de cómputo y una afirmación falsa —«el último
bloqueo antes del rollout»— que hubo que corregir después.

**Al fallar:** si la lista de rutas afectadas no incluye la del experimento en curso, no se para el
experimento.

---

## G3 · El instrumento se falsa por su entrada, no sólo por su salida

**Todo instrumento que sintetice su entrada la construye con la misma función que el runtime, o
lleva un test que compara su salida contra la del runtime campo por campo.**

### El fallo que previene

El examen de P1 tenía tres controles de falsación y los tres pasaban:

```
oráculo       → 1.0
anti-oráculo  → 0.0
empate        → NOT_EVALUABLE
```

Los tres validaban la **puntuación**. Ninguno miraba el **formato de entrada**. Un oráculo sobre
observaciones malformadas sigue puntuando 1.0, porque el oráculo lee el mundo, no la observación.
El agujero tenía la forma exacta del bug.

**Al fallar:** el instrumento no es reportable, aunque sus controles de salida pasen.

Este gate se aplicó a sí mismo sobre G4 y encontró un fallo: la primera versión marcaba seis
mecanismos como colaterales cuando la mayoría eran consecuencia legítima de quitar el objetivo. Un
gate que siempre dispara se ignora, que es otra forma de no existir.

---

## G4 · Intervención pura antes de atribuir

**Contar invocaciones por mecanismo bajo la configuración base y bajo la ablación, con la misma
semilla y las mismas observaciones.**

```bash
python scripts/purity_check.py use_world_model
python scripts/purity_check.py --all
```

Clasifica tres cosas distintas:

| Lectura | Significado | ¿Impura? |
|---|---|---|
| **DESACTIVADO** | otro mecanismo queda enteramente sin ejecutar | **sí** — su ejecución estaba condicionada al mismo flag |
| **DESVIADO** | el conteo de otro mecanismo sube | **sí** — otra ruta tomó el relevo |
| *(menos llamadas)* | baja pero sigue activo | no — compatible con que el objetivo lo llamara dentro de su propio trabajo; **compatible con pureza, no prueba de ella** |

### El fallo que previene

El tamizado reportó dos hallazgos significativos: «modelo del mundo +6.33 comidas» y «planificador
+6.67». Son la misma intervención. Barrido completo hoy:

```
8 de 10 intervenciones puras
2 impuras: use_planner, use_world_model
```

`use_world_model=False` **desactiva el planificador** (40 invocaciones → 0) y **desvía** conducta
hacia `policy_head` (97 → 120), porque sin planner cada decisión muestrea de la política en vez de
la mitad de las veces. Ninguna de las dos cosas era visible desde el resultado: el número era
plausible, el efecto grande y el signo el esperado.

**Al fallar:** el efecto se marca `NON_IDENTIFIABLE`. No se atribuye.

Es la forma operativa de **I-09**: la primera divergencia causal debe ocurrir en el mecanismo
declarado.

---

## G5 · Declarar ruta de ejecución y versión de semántica

**Todo artefacto declara qué runtime lo produjo (`Sandbox` / `Controller` / `Causal`) y bajo qué
versión de semántica del mundo.**

### El fallo que previene

El tamizado, P0, los gemelos y P1 corrieron sobre `SandboxService` —que no ejecuta el ciclo de
oportunidades que el escenario declara— y ningún artefacto lo decía. Hubo que reconstruirlo después
leyendo código.

**Al fallar:** el artefacto no entra a evidencia.

Es **I-05** con el requisito de versionado que el documento canónico añade. Depende de que
`WORLD_RUNTIME_PARITY` cierre: hoy no hay una versión de semántica que declarar porque hay tres.

---

## G6 · Staging explícito

**Se prepara por ruta. Nunca `git add -A`.**

### El fallo que previene

1.2 GB de datos de corrida versionados en cuatro commits. `.gitignore` cubría `.sandbox/` y los
directorios de banco se llamaban `.sandbox-<nombre>`, que ese patrón no alcanza. `.git` pesa 339 MB
y los blobs siguen en la historia.

Reparado el patrón (`.sandbox-*/`). La historia sigue pesando: limpiarla es una reescritura y es
decisión aparte.

---

## Orden de aplicación

```
G1  antes de escribir código      ¿está la cartografía al día para este subsistema?
G2  antes de reparar              ¿qué rutas alcanzan este defecto?
G3  antes de reportar un número   ¿el instrumento está falsado por su entrada?
G4  antes de atribuir un efecto   ¿la intervención mueve sólo lo que declara?
G5  antes de sellar               ¿bajo qué runtime y qué semántica?
G6  antes de commitear            ¿qué estoy preparando exactamente?
```

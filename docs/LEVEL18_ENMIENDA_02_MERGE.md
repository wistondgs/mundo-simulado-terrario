# Enmienda 02 al oráculo de `LEVEL1.8` · semántica de `merge` y reversibilidad

**Fecha:** 2026-09-20 · **Oráculo enmendado:** `32531ef` §5
**Sellada ANTES de escribir una línea de `merge`** · ninguna semilla `180…` abierta
El oráculo no se reescribe. Aditiva.

---

# 1 · El hueco

`32531ef` §5 promete un mecanismo «capaz de crear, **separar y fusionar** estados
por evidencia predictiva». El learner `acb6b14` **no implementa fusión en
absoluto**, y ninguno de los diecisiete gates lo detectó.

Es el mismo patrón que `AN-4` en 1.7: el oráculo promete una propiedad y no existe
contrato ejecutable que la certifique.

# 2 · Por qué esto precede a adjudicar el split prematuro

El primer split ocurre en `t = 10`, lo que parece temprano. **No se adjudica
todavía.** Hay un confundido estructural encima: el mecanismo puede separar y no
puede deshacer.

```
split en t = 10             SOSPECHOSO · NO ADJUDICADO
refinamiento irreversible   DEFECTO REAL
```

Mientras un refinamiento sea irreversible, no se puede saber cuánta de la
sobrefragmentación —90 estados para 19 situaciones— viene de aceptar demasiado y
cuánta de no poder retractarse.

# 3 · Qué significa `merge`, exactamente

**No es una fusión cualquiera entre estados.** Es el **inverso causal de un split
previamente realizado**:

```
si     z  →  {z_1, …, z_k}
merge  {z_1, …, z_k}  →  z
```

Mantiene la jerarquía y evita una búsqueda combinatoria entre todos los estados.

## 3.1 · El criterio es el mismo código prequencial · sin constantes nuevas

```
PROHIBIDO   MERGE_THRESHOLD · MIN_SUPPORT · PATIENCE · COOLDOWN · MAX_STATES
```

Para cada split aceptado se conserva el contraste entre dos hipótesis sombra que
reciben **exactamente los mismos datos**:

```
favor(z)  =  código acumulado de la hipótesis COLAPSADA
           − código acumulado de la hipótesis REFINADA

favor > 0   la distinción paga su complejidad   → mantener
favor ≤ 0   ya no la paga                       → FUSIONAR
```

**Empate ⇒ el modelo más simple.** El `≤` no es un umbral: es la desigualdad que
resuelve el empate a favor de la representación que codifica con menos.

## 3.2 · La evidencia NO se reinicia tras el split

Ésta es la parte que hay que sellar antes de escribirla, porque la alternativa
parece inocente y no lo es.

```
favor(z) se INICIALIZA con el balance que justificó el split
         y CONTINÚA acumulando con la experiencia posterior
```

Si el comparador arrancara de cero tras separar, la penalización de complejidad
haría que casi todo split se deshiciera de inmediato, y el mecanismo oscilaría sin
que la evidencia tenga nada que ver. Es una decisión **sobre una misma hipótesis a
lo largo del tiempo**:

```
evidencia a favor del split  →  evidencia posterior  →  mantener o revertir
```

## 3.3 · Qué debe ocurrir al colapsar

```
masa        C(z) = Σ_i C(z_i)          conservada dentro de la tolerancia sellada
routing     ninguna ruta puede seguir apuntando a un descendiente inexistente
resultado   funcionalmente equivalente a no haber mantenido esa distinción
```

**No se puede borrar evidencia para que el merge parezca bueno.**

# 4 · El gate que falta · `L18-17 REFINEMENT-REVERSIBILITY`

Ninguno de los diecisiete puede contener honestamente esta propiedad. Se añade
prospectivamente.

```
antes    REQUIRED_GATES = L18-0 … L18-16    17
ahora    REQUIRED_GATES = L18-0 … L18-17    18
```

**No se conserva artificialmente el número.** El número no importa; importa que toda
propiedad que el protocolo exige viva **dentro de la ruta congelada**.

## 4.1 · Las fixtures que se sellan ahora

```
F1  split luego refutado
    evidencia que justifica separar · después evidencia que vuelve
    indistinguibles a los hijos        ⇒  DEBE fusionar

F2  split verdaderamente necesario
    la evidencia posterior mantiene distribuciones distintas
                                       ⇒  NO debe fusionar

F3  conservación
    Σ_i C(z_i) → C(z) sin pérdida ni fabricación de masa

F4  routing tras el merge
    ninguna ruta apunta a un hijo que ya no existe

F5  etiquetas
    renombrar los hijos no cambia la decisión
```

# 5 · Cronología canónica

```
32531ef       oráculo PRE-CÓDIGO · 16 gates
acb6b14       primer learner · negativo
e105cff       Enmienda 01 · baseline continuo + L18-16 · 17 gates
f0222f2       diagnóstico · autómata absorbente localizado
1a35caa       routing reparado · sobrefragmentación destapada
Enmienda 02   merge y reversibilidad especificados ANTES de implementarlos · 18 gates
```

Se conserva así. **No se dirá después que los dieciocho gates fueron preregistrados
antes del learner**: el oráculo científico precedió completamente al mecanismo, y
durante calibración —antes de cualquier confirmatorio— se añadieron
prospectivamente `L18-16` y `L18-17`.

# 6 · La predicción falsable que esta enmienda permite

Si el defecto principal es la irreversibilidad, con `merge` correcto debería verse:

```
splits acumulados         pueden seguir siendo altos
estados ACTIVOS           dejan de crecer sin límite
deterioro +0.017 → −0.115 se reduce o desaparece
```

Y si aun con merge correcto sobreviven 60–90 estados y el rendimiento cae, entonces
el problema está en la **regla que acepta splits**, y recién ahí procede estudiar
por qué `t = 10` pasa el código prequencial.

**Esta enmienda se sella sin haber mirado el rendimiento de ninguna
implementación de `merge`.**

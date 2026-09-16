# CORPUS-V04-ANALISIS-01 · qué cambia la generación v0.4

**Estatus:** análisis de sesión, no normativo.
**Fecha:** 2026-09-16 (tarde).
**Fuente analizada:** `/home/wis/Documentos/teoria de la inteligencia` — corpus vivo del
investigador, fuera del repositorio. El snapshot versionado
(`theory_snapshots/theory-f59dbb6d6ee3850c`) está congelado desde el 9 de septiembre y **no**
contiene nada de esto.
**Qué es v0.4:** `CORPUS_GAPS_v0.4.md` y `CORPUS_INTEGRITY_PATCH_v0.2.md`, ejecución de C-3 y
C-4 de `ORIENTACIONES-CORPUS v1`. 43 registros en `ACQUISITION_MANIFEST_v0.4.csv`, 59 hashes en
`SHA256SUMS_v0.4.txt`, 0 duplicados byte a byte contra el corpus existente.

---

## 0. El gate de v0.4 es honesto, y conviene subrayarlo

> «adquirir una fuente no cambia la cobertura»

v0.4 termina en `CORPUS EXPANSION INCOMPLETE` y deja las familias tocadas en
`SOURCES_ACQUIRED_NOT_EXTRACTED`. Ninguna celda de `COVERAGE_MATRIX` se mueve hasta que haya
claims extraídos contra texto. Es la misma disciplina que `hipótesis ≠ evidencia` en los
invariantes del manifiesto, aplicada un escalón antes: **documentación disponible ≠ conocimiento
incorporado.**

---

## 1. `HISTORY_DEPENDENCE` es la columna que faltaba

`CORPUS_A_ALGORITMO_01` §4 sostiene que al corpus le falta un compromiso observable por claim, y
que sólo ~27 de 189 claims pueden llevarlo. La familia nueva de v0.4 llega con eso ya hecho.

Su criterio es operacional de entrada:

```
P(R' | H₁, D') ≠ P(R' | H₀, D')
```

que es **literalmente el Gate H2** de `PROCESO_DE_TRABAJO_01` §8 — «H_experiencia vs H_control,
sin inyectar el scar, ambos llevados a O*».

Y las 15 fuentes están seleccionadas **por el control que cada una declara**, no por tema:

| control declarado | descarta |
|---|---|
| especificidad de estímulo; deshabituación | fatiga, adaptación sensorial |
| retorno al basal antes del segundo reto | activación residual tomada por memoria |
| control verdaderamente aleatorio | cambio no asociativo tomado por asociativo |
| orden invertido asimétrico | respuesta fija (instinto) |
| dependencia del intervalo, con inversión de signo | historia como efecto monótono |
| knockouts que separan arrastre de re-inducción | mecanismo único de memoria |
| transferencia a una célula que no vio el estímulo | historia como estado no transferible |

Eso no es una lista de lecturas: es una tabla de ablaciones. Es exactamente lo que la aduana 1
exige y lo que 133 claims `CONCEPTUAL_ARGUMENT` no pueden dar.

**Lo que NO cambia.** Los bloques 3 (experiencia) y 4 (memoria) **siguen en Clase B**: Terrario
no tiene canal de memoria, y el eslabón roto vive en RNFE. Lo que cambia es el lado fuente: el
bloqueo pasa de **doble** —sin criterio operacional y sin canal— a **simple**: con criterio, sin
canal. Es un avance real y acotado, y conviene no confundirlo con haberlos desbloqueado.

---

## 2. Homeostasis biológica aterriza sobre los dos hallazgos de hoy

13 fuentes adquiridas, de las que dos grupos tocan decisiones abiertas en este repositorio:

**Fitzgerald & Bean 2018**, registrado como *rival obligatorio: regulación sin set point fijo*.
Es la literatura de la decisión que ADR-002 deja pendiente —elegir cuál de las tres fronteras de
viabilidad es `𝒱`— y sostiene que la pregunta puede estar mal planteada si se asume un umbral
único. `VARIABLES_ESENCIALES_Y_REORGANIZACION_01` §2 documenta que hoy hay tres: muerte del mundo
en `energy <= 0`, umbral del organismo en `0.5`, y η del observador en ≈ `0.23`.

**Di Paolo 2000 · Iizuka & Di Paolo 2008 · Manicka & Di Paolo 2009**, registrados como
ultraestabilidad ashbiana en robot y hardware. Es el **Caso 3 de ADR-001** —reorganización cuando
`V_R` resulta insuficiente— ya realizado por alguien, con implementación. Es el precedente
operacional más cercano a lo único que el marco corregido exige y que Terrario no mide:
`dV_R/dt`.

Verificación del hueco que hace v0.4, y que confirma lo que decía el triaje: en
`CONCEPTS_RAW_v0.1`, `CONCEPTS_RAW_PATCH_v0.3` y `CONCEPT_CANONICAL_MAP_v0.2` **no hay ningún
concepto que contenga `homeost*` ni `allosta*`**. La única entrada que nombra variables
esenciales es `CON-0076 stability`, de Ashby.

---

## 3. Ashby estaba, y el problema era el registro

`CORPUS_ACQUISITION_LIST_02` encabezaba su orden de compra con *Design for a Brain*. v0.4
verifica que el texto **ya está en el disco**: 2.ª ed. 1960, `ARC-001` = `ADOA-001`, 304 pp. Lo
que estaba mal es que `MISSING_AND_RESTRICTED.md` lo marca `RESTRICTED` por un 404.

La recomendación acertó en el qué y falló en el cómo: no era una compra, era una desincronía de
ficha. Corregido en el documento original con la marca visible, sin borrar el texto previo.

Posición de Ashby a nivel primario, según v0.4: **completa** — *An Introduction to Cybernetics*
(TI-0049 = ADOA-002), *Design for a Brain* (ARC-001/ADOA-001), Conant & Ashby 1970 (ADOA-004).
Lo que falta es el **linaje alrededor** de Ashby, no Ashby: Wiener 1948, Rosenblueth–Wiener–
Bigelow 1943, Powers 1973, Maturana–Varela 1980 — ninguno con copia legal.

**Consecuencia para el orden de compra:** con Ashby fuera de la lista, la primera pasa a ser
**Nelson & Narens 1990**, porque v0.4 no tocó metacognición y el pilar 2 sigue en cero.

---

## 4. Higiene que v0.4 pide y nadie ha ejecutado

- `adaptation_recovery_corpus_v0.1.zip` y su copia `(1)` son idénticos (md5 `358916b2…`) y
  **ninguno es un ZIP legible**: falta el directorio central. `QUARANTINED_CORRUPT_ARCHIVE`. La
  copia válida es `…_REPACKED.zip`.
- `Autonomous_Development_…_v0.1.zip` (54 documentos) está superado por `v0.1.1` (65).
- `acquisition_v0.4/_to_delete/` conserva un `.part` de una descarga interrumpida.
- La ficha TI-0048 debe apuntar a ARC-001/ADOA-001.

Dos resoluciones de `CORPUS_INTEGRITY_PATCH_v0.1` apuntaban a reposts docentes (UCSD, Columbia):
identidad bibliográfica correcta, sin base legal de redistribución. v0.2 las descarta y aplica el
mismo criterio a DEV-012 (Piaget 1964, CUNY), que pasa a `NO_LEGAL_COPY`. **El corpus se corrige
a sí mismo hacia arriba, no hacia abajo** — es la primera vez que veo aquí un patch que endurece
su propio estándar en lugar de relajarlo para cerrar un hueco.

---

## 5. Lo que está en la carpeta y no es corpus

Los dos ficheros más recientes de `corpus de cibernetica/` —`RNFE f2.3 (2).txt` (17:11) y
`f 2.4 para mezcla (1).txt` (17:09)— son blueprints de arquitectura de RNFE. Proponen MFE, TFI,
memoria IFS–FDE, perceptores fractales, H-Net con chunking dinámico, teoría de viabilidad,
haces sobre coberturas discretas, reescritura tipada de grafos, dinámica replicador–mutador y
CVaR.

No tienen procedencia, ni hash, ni claims, ni gate. No son corpus, y no deberían entrar por esa
puerta.

El contraste es el hallazgo, y es del mismo día: **v0.4 adquiere 43 documentos y termina
declarando que no incorporó conocimiento; los dos `.txt` incorporan seis dominios matemáticos
sin haber medido nada.** Es la causa de proceso que ya diagnosticó `PROCESO_DE_TRABAJO_01` —
«se añadieron mecanismos más rápido de lo que se cerraron ciclos»— en su forma más literal.

Un detalle que sí merece registro: `f 2.4` dice «añado teoría de viabilidad dinámica». Converge
con ADR-001 de forma independiente. Pero converge en el vocabulario, no en el instrumento: nada
en esos dos ficheros mide `𝒱ₜ`, y `VARIABLES_ESENCIALES_Y_REORGANIZACION_01` establece que la
viabilidad todavía no tiene autoridad causal sobre la reorganización en el código que existe.

---

## 6. Qué queda establecido

1. v0.4 es la primera aportación al corpus que llega con criterio operacional incluido, y por eso
   es la primera que podría alimentar un instrumento en vez de una hipótesis.
2. No desbloquea ningún bloque del triaje: cambia el lado fuente, no la superficie de señal.
3. Dos decisiones abiertas —cuál es `𝒱` (ADR-002) y cómo medir `dV_R/dt` (ADR-001)— ahora tienen
   literatura con implementación detrás, que antes no tenían.
4. El pilar metacognitivo sigue en cero y ha pasado a ser la primera carencia de la lista.
5. Nada de esto entra en el snapshot versionado hasta que haya extracción T1. Hoy el repositorio
   y el corpus vivo del investigador **están desincronizados por una generación entera.**

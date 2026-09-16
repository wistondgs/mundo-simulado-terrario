# GENESIS-RNFE-RELATIONSHIP-01

**Encargo:** «busca algo que se llama genesis y analiza».
**Alcance honesto:** reconocimiento de ~20 minutos sobre un proyecto de 89.000 líneas. Es un
mapa, no una auditoría. Para lo segundo existen ya los agentes `cartografo-canon`,
`cartografo-codigo-real` y `brecha-canon-real`, escritos para exactamente eso.
**Solo lectura.** No se tocó nada fuera de este repositorio.

---

## 1. Qué es Genesis

`/home/wis/Desarrollo/RNE_v16-genesis-v2`, rama **`genesis/v2-foundation`**. Es **RNFE v16**, no
un proyecto aparte: Genesis es la línea de trabajo dentro de él (`lab/genesis`, `tests/genesis`,
259 commits todos con prefijo `feat(genesis)` en los últimos meses).

| | Genesis / RNFE v16 | Terrario |
|---|---:|---:|
| Python (runtime+lab+engines) | **89.136** líneas · 413 módulos | 25.146 · 134 |
| Funciones de test | **1.779** | 530 |
| Commits | **259** | 96 |
| Vida | 2026-04-16 → 2026-09-07 (**5 meses**) | 2026-09-08 → 2026-09-16 (**8 días**) |
| Normativa | `canon/` 13 archivos · `contracts/` 23 · `governance/adr/` | `docs/` 132, sin canon formal |
| Historia git compartida | **ninguna** — repositorios independientes | |

Hay además una familia: `RNE_v16`, `RNE_v16_analysis`, `RNE_v16_worktrees`, `rnfe.v15`.

## 2. Su canon dice, palabra por palabra, el objetivo que declaraste hoy

`canon/normative/CANON_RNFE_v3_2_rc1.md`, versión 3.2.0-rc1, fecha **2026-03-24**, owner `Wis`,
con cadena `depends_on` y `supersedes`:

> RNFE queda definido como un **organismo cibernético digital autoevolutivo**, no humanoide,
> orientado a inteligencia general adaptable, con cierre triádico, continuidad identitaria,
> viabilidad dinámica, memoria viva multiescala, ecología de razón gobernada y herencia
> certificada.

Hoy describiste tu objetivo como «un ser cibernético autopoiético, metacognitivo y
autoevolutivo». **Es la misma frase**, escrita hace seis meses en un documento normativo tuyo.
No era una aspiración: era la cita de un proyecto que existe.

Y su tesis rectora es notable:

> *un proyecto de frontera necesita axiomas duros muy pocos y muy firmes, pero necesita
> arquitectura provisional explícita y **laboratorio falsable amplio**.*

Retén esa última frase. Vuelve en §5.

## 3. El solapamiento con Terrario es grande y no está declarado

`lab/genesis` son 19.723 líneas repartidas así:

| Concepto | Terrario | Genesis `lab/genesis` |
|---|---|---|
| Preregistro | `preregistration/` ≈ 2.000 líneas | **`acquisition/v3_preregistration.py` 1.272** (va por la V3) |
| Fork causal | `lab/causal.py`, solo `A0×D0` | `causal/{snapshot,cfi,isolation}.py` |
| Intervenciones | registro con `C00`, `C01_SHAM`, una de prueba | `intervention/{kernel,receipts,replay}.py` |
| Evidencia | `EvidenceGraph`, `evidence_publication.py` | `evidence/{ledger,events,artifacts}.py` |
| Procedencia | `referencegraph/`, `crossgraph/` | `provenance/{nodes,edges,risk}.py` |
| Verificación | `verify()` dentro de execution | **`verifiers/` 2.925 líneas**, con router y differential |
| Replay | contrato documentado | `replay/verifier.py` |
| Retención y cuarentena | **no existe** | `retention/`, `security/quarantine.py` |
| Campañas confirmatorias | **no existe** | `acquisition/{v2,v3}_campaign.py`, `battery.py`, `complete_frontier.py` |

Traducido sin rodeos: **aproximadamente la mitad del código de Terrario reimplementa, con ocho
días y a un cuarto de escala, una capa epistémica que existe desde hace cinco meses en el
repositorio de al lado, con el triple de profundidad de pruebas.**

Y `docs/TERRARIO_ARCHITECTURE_AUDIT.md:92` registró «Genesis / RNFE — no se halló integración
operacional actual — **MISSING**». Es correcto como hecho y engañoso como conclusión: no falta
un componente, existe un repositorio hermano que nadie declaró.

## 4. Pero hay una diferencia real, y es la que justifica que Terrario exista

Genesis es **un organismo**: `runtime/organism`, `runtime/reality`, `engines/hnet`, `mamba_ssm`.
Es el sujeto de estudio.

Terrario es un **banco comparativo**: 5 arquitecturas × 8 entornos, con ablación entre niveles.

**No se puede ablacionar un organismo contra sí mismo.** Para preguntar «¿qué componente es
necesario para qué exigencia ambiental?» hacen falta varias arquitecturas corriendo el mismo
mundo con la misma semilla. Genesis, estructuralmente, no puede hacer eso; Terrario sí, y anoche
se demostró: 40/40 celdas ejecutables.

Es decir: **el valor propio de Terrario es la matriz A×D y el simulador. No la capa epistémica.**

## 5. La jerarquía real, corregida por el investigador (2026-09-16)

```
RNFE  (Red Neuronal Fractal Evolutiva)
  └── Genesis            subproducto
        └── Terrario     subproducto
```

Terrario **no** es un repositorio hermano sin declarar. Es una reducción deliberada de alcance,
y el motivo lo dio su autor: *«me sentía perdido, no sabía por dónde comenzar; tengo la noción
básica pero necesito explícitamente la noción científica»*.

Eso corrige la lectura de §3 y §4. Terrario no duplica por descuido: **es el caso mínimo
reproducible** que se construye cuando el sistema principal está demasiado enredado para
formular una pregunta limpia. Es la misma maniobra que aislar un fallo en un repro de veinte
líneas, o que un modelo de juguete en física. Es buena práctica, no deriva.

## 6. Lo que eso implica, y es la conclusión que importa

Si Terrario existe para obtener la **noción científica explícita**, entonces:

> **El producto de Terrario es el método, no la evidencia.**

Su entregable no es un hallazgo sobre inteligencia. Es un **ciclo científico completo,
demostrado de punta a punta y transferible a Genesis**: pregunta → diseño → matriz → preregistro
sellado → cuatro firmas → ejecución → verificación → resultado en el libro de evidencia.

De ahí se sigue lo único que de verdad hay que decidir:

**Terrario no necesita crecer. Necesita terminar una vez.**

Y «una vez» es hoy definible con precisión, porque todas las piezas existen y anoche se
verificaron:

| Pieza | Estado |
|---|---|
| Matriz A×D ejecutable | ✅ 40/40 |
| Cadena de preregistro y compuertas | ✅ tutorial de 16 pasos en verde |
| Verificación de integridad | ✅ `PASS` |
| Dos hipótesis rivales de la literatura | ✅ `H-RIVAL-CAREY`, Derex X12 |
| Advertencia de pureza declarada | ✅ documentada |
| **Un resultado científico** | ❌ **`scientific_results: 0`** |

Falta exactamente **un** paso, y no es de ingeniería: es ejecutar el ciclo con una pregunta
pequeña y firmarlo.

Hecho eso, el método vuelve a Genesis y Terrario ha cumplido. Las opciones A/B/C de la versión
anterior de este documento se disuelven: la pregunta no es cómo integrar dos capas epistémicas,
sino **qué workflow probado se lleva Genesis de vuelta**.

## 7. Lo que NO puedo afirmar todavía

- Si la capa epistémica de Genesis es **funcionalmente superior** o solo más grande. 1.779
  funciones de test sugieren lo primero, pero no lo verifiqué.
- Si `v3_preregistration` cubre las cuatro compuertas humanas de Terrario o resuelve otro
  problema con el mismo nombre.
- El estado real de RNFE frente a su canon. Existe `docs/analysis/00_INDEX.md` descrito como
  «auditoría línea-por-línea del código (estado real)», y los agentes para reconstruirla.

Antes de decidir A, B o C conviene correr `brecha-canon-real` sobre RNFE y saber qué promete el
canon que el código todavía no cumple. Decidir la relación entre los dos proyectos sin ese dato
sería exactamente el tipo de salto que ambos sistemas existen para impedir.

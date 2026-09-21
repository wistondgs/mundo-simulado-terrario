# Atlas 08 · Estado real del repositorio

**2026-09-21** · depositado en `CARTOGRAFIA_TERRARIO_01.md` **§XLV**.

**Ensamblado, no re-medido.** Los Atlas 01–07 ya midieron subsistema por
subsistema qué está vivo y qué no. Lo único que faltaba era un censo mecánico
global; es lo único nuevo. El resto se cita.

---

## 1 · El censo

`scripts/censo_orfandad.py` — grafo de imports por AST, tres estados:

| Árbol | Módulos | Sin importador | Sólo tests |
|---|---:|---|---|
| **Terrario** `terrario/` | 156 | **4** · 371 líneas | **16** · 2 898 líneas |
| **genesis-v2** `runtime/` + `lab/` | 369 | **37** · 5 182 líneas | **74** · 17 562 líneas |
| `lab/` medido **desde dentro** | — | 2 · 18 líneas | 14 · 3 743 líneas |

Esa última fila dice algo que el Atlas 05 ya había medido de otra forma:
**`lab/genesis` está bien conectado consigo mismo y no lo alcanza nadie desde
fuera.** La orfandad es una propiedad del observador, no del módulo.

## 2 · El instrumento mintió cuatro veces antes de acertar

Cada punto ciego era un idioma normal de Python, y **cada versión respondía con
total aplomo**:

```
1. contar `__init__.py` como destino      → paquetes enteros «huérfanos»
2. ignorar `from paquete import modulo`   → `instrument_registry` huérfano, con
                                            `evidence_admission` importándolo
3. excluir `__init__.py` como IMPORTADOR  → A0–A5 «huérfanos», y su factoría
                                            vive precisamente ahí
4. no resolver reexportaciones            → el lazo de vida entero «sólo tests»
```

Publicar la primera versión habría metido en el Atlas la frase «el kernel del
lazo de vida sólo lo usan los tests» — falsa, y con el mismo tono de seguridad
que el resto del documento. La lista vive en la cabecera del guion, para que la
próxima medición empiece donde ésta acabó.

## 3 · Las seis categorías

**Vivo** · consumidor fuera de tests **y** filas o corridas
: el paso autoritativo y sus tres superficies · el preregistro (141 sellados,
708 de auditoría, 45 de exposición) · `Reading` y `evidence_admission`, nueve
consumidores · el linaje 1.0–1.4 y la fusión · el lazo ρₜ con rollback
ejecutable y ledger de Λ.

**Roto** · falla hoy
: `catalogue()` y `describe_selection()` levantan `KeyError`;
`GET /api/agent-concepts` caído; tres pruebas en rojo desde `fd725e3`.

**Incompleto** · construido y sin cerrar
: 1.8 sin presupuesto seleccionable, confirmatorio intacto · la campaña canónica
de Genesis, 1 de 6 tareas · `MODEL_PARAMETER`, declarada y vacía.

**Huérfano** · construido, probado, sin consumidor
: `lab/genesis` entero — 19 861 líneas, 70 tests, cero importadores externos ·
`lab/genesis/retention`, el juicio de no-regresión · `crossgraph/d2trace.py`,
la pieza que uniría Reference→Scenario, **sin un solo llamador ni test** ·
`world/scenario.py`, 150 líneas con otro `load_scenario` que es el que se usa ·
22 tablas `ref_*` y 9 `cross_*` vacías.

**Duplicado** · dos implementaciones de lo mismo
: `find_target`, extraído de dos copias idénticas… y hay una **cuarta** en
`verify_reproducibility.py` · dos `load_scenario` · dos contabilidades de
capacidad que no se tocan · dos disciplinas de RNG opuestas.

**Sólo documentado** · se afirma y no existe
: `CI-VERDAD`, **0 coincidencias** en los dos árboles · «un G1 promovido es G0
más esa habilidad», docstring sin función · el ciclo de madurez de conceptos,
tres enums desconectados · `no_interference`, nombrado por el canon y nunca
definido.

## 4 · La deuda declarada también caduca

§XXVIII es una de las **doce secciones que el gate no puede vigilar**.
Comprobadas tres de sus afirmaciones:

| Afirmación | Hoy |
|---|---|
| la rama omnisciente de `_find_target` es inalcanzable | **caduca** — el contrato de acción escribe `target_id` |
| `policy_head.greedy` no se llama | **se sostiene** |
| los cuatro `reset` no los llama ningún loop | **caduca** — los cuatro se llaman |

Dos de tres. Es la **segunda** sección no vigilada que se encuentra desfasada, y
van **dos de dos comprobadas**.

## 5 · Lo que no se sabe

1. **K2** · Las otras diez secciones no vigiladas. Dos de dos salieron
   desfasadas; extrapolar no es medir.
2. **K2** · Cuántos de los 37 huérfanos de genesis-v2 son código vendido o
   histórico legítimo. El censo no distingue «nadie lo usa» de «nadie debe
   usarlo».
3. **K2** · Si los 74 módulos «sólo tests» son laboratorio deliberado —como
   `lab/genesis`— o integración pendiente. Es la pregunta del Atlas 05 a escala
   de árbol.

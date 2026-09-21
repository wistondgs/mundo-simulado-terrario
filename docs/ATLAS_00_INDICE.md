# Atlas del proyecto · índice

**Qué es.** Una serie de informes de lectura de implementación —no de
documentación, no de nombres— hasta cubrir el programa entero. Cada volumen se
deposita como sección de la cartografía **del árbol que describe** —para que su
gate pueda vigilarlo— y se entrega como informe en `docs/` de Terrario y se entrega como un
informe general. Un volumen sólo se da por hecho cuando afirma mecanismos con
`fichero:línea` verificado y con lo no resuelto declarado como K2/K3 en vez de
rellenado.

## El programa vive en cuatro árboles, no en uno

Esto es lo primero que hay que saber, y explica por qué varios puntos del
contrato de conocimiento no podían contestarse desde este repositorio:

| Árbol | Qué es | Python | HEAD |
|---|---|---:|---|
| `/home/wis/mundo simulado terrario` | **Terrario** · aparato experimental y organismo A0–A5 | 149 fich · 30 703 líneas | `7051d7f` 2026-09-21 |
| `/home/wis/Desarrollo/RNE_v16-genesis-v2` | **Genesis v2** · el árbol vivo | 876 fich · 172 048 líneas | `23947ff` 2026-09-18 |
| `/home/wis/Desarrollo/RNE_v16` | **RNE v16** · organismo, rama anterior | 721 fich · 135 061 líneas | `6630258` 2026-07-30 |
| `/home/wis/dev/rnfe.v15` | **RNFE v15** · histórico | 587 fich · 106 341 líneas | `36cb2a29` 2026-07-03 |

≈ 443 000 líneas de Python en total. El Atlas no se hace de una vez y decir lo
contrario sería la primera afirmación falsa del documento.

## Volúmenes

| # | Volumen | Cubre | Árbol | Estado |
|---|---|---|---|---|
| **01** | **Capa de conocimiento** | corpus · teoría · hipergrafos · fábrica de hipótesis · memoria · composición | Terrario | **HECHO** · §XXXIX + `INFORME_CAPA_CONOCIMIENTO_02.md` |
| **02** | **El organismo** | runtime percepción→estado→decisión→acción→consecuencia→aprendizaje · linaje A0–A5 | Terrario | **HECHO** · §XL + `ATLAS_02_ORGANISMO.md` |
| **03** | **Sistema experimental** | mundos · runners · preregistro · lesiones · controles · métricas · gates · CAS · ledger · semillas | Terrario | **HECHO** · §XLI + `ATLAS_03_SISTEMA_EXPERIMENTAL.md` |
| **04** | **Capacidades demostradas** | 1.0–1.8 en ocho worktrees · los diez pasaportes · qué está demostrado y qué sólo contabilizado | Terrario + 8 worktrees | **HECHO** · §XLIII + `ATLAS_04_CAPACIDADES.md` |
| **05** | **Genesis** | `lab/genesis/` · qué entra, qué transforma, qué produce, quién lo consume | genesis-v2 | **HECHO** · `CARTOGRAFIA_GENESIS_01.md` §VII + `ATLAS_05_GENESIS.md` |
| 06 | **RNE / RNFE** | CI-VERDAD · CADENA-CAUSAL · Retention Ledger · integración · reparaciones abiertas | genesis-v2 `runtime/` | parcial · §I–§VI de `CARTOGRAFIA_GENESIS_01.md` ya lo cubren |
| 07 | **Evidencia, canon y autoridad** | experimento→resultado→almacenamiento→teoría→hipergrafo→siguiente pregunta · qué manda ante contradicción · qué gates están activos | los cuatro | pendiente |
| 08 | **Estado del repositorio** | vivo · roto · incompleto · huérfano · duplicado · sólo documentado | los cuatro | pendiente |

La **arquitectura global ejecutable** —la relación real entre Terrario, Genesis
y RNE— no es un volumen propio: se contesta cuando 02, 05 y 06 estén leídos, y
antes de eso cualquier diagrama sería documentación repetida.

## Regla de admisión

Lo mismo que rige la cartografía: una sección se da por hecha cuando lo que
afirma se puede comprobar abriendo el fichero en la línea citada, o ejecutando
la orden que se transcribe. Lo que no se pudo leer se marca **K1**; lo que no se
sabe, **K2**; lo que exige evidencia externa, **K3**. Ninguno de los tres se
rellena.

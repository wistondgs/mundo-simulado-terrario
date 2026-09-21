# Atlas 07 · Evidencia, canon y autoridad

**2026-09-21** · Terrario `d5e22bd` · genesis-v2 `8f506a7`
Depositado en **dos mitades**, cada una donde su gate puede vigilarla:
`CARTOGRAFIA_TERRARIO_01.md` **§XLIV** (afirmaciones científicas) y
`CARTOGRAFIA_GENESIS_01.md` **§IX** (el canon y el organismo).

> Cuando código, canon, campaña, ledger, hipergrafo y documentación discrepan,
> **¿qué fuente tiene autoridad sobre qué tipo de afirmación?**

---

## 1 · Qué está arbitrado en código, y qué sólo declarado

| Clase de afirmación | Autoridad | ¿Arbitrada en código? |
|---|---|---|
| qué significa científicamente una métrica | `instrument_registry` | **sí** — falla cerrado, tres códigos |
| si un número puede ser evidencia | `evidence_admission` | **sí**, y repregunta aunque el preregistro ya preguntara |
| qué vale una lectura ausente | `Reading` | **sí** — `float()` levanta salvo OK |
| qué se prometió medir | preregistro sellado | **sí** — máquina de siete estados |
| qué escribe un parámetro adaptativo | un único materializador | **sí** (Genesis §III) |
| **qué gates tiene una campaña** | el oráculo sellado | **no** — la divergencia oráculo↔informe no la ve nada |
| **qué afirma el mapa sobre el código** | la cartografía | **parcial** — hash y cita; el contenido de la línea no |
| **qué capacidad está demostrada** | — | **no** — dos contabilidades que no se tocan |
| **qué dice el canon** | `canon/normative/` | **no** — ningún programa lo parsea |

La regla que emerge no es «manda el código»:

> **El código manda sobre lo que un artefacto ES. El oráculo sellado manda sobre
> lo que una campaña PROMETIÓ. Ninguno manda sobre el otro.** La incoherencia
> aparece cuando un tercero —un informe, una sección del mapa— narra ambos y
> nadie comprueba que coincidan.

## 2 · El criterio para separar divergencia de incoherencia

**Legítima** cuando el sistema **puede nombrar las dos cosas y decir cuál
aplica**:

| Caso | Por qué |
|---|---|
| dos márgenes con el mismo nombre | el mapa nombra ambos y dice cuál decide qué |
| contrato de acción T0 = no-op | deliberado, para que el control quede byte-idéntico |
| endpoints `PENDIENTE-*` | declaran el hueco en vez de sustituirlo |
| 1.5 congelado sólo como diseño | con condición de descongelación escrita |
| aislamiento de `lab/genesis` | **K2**: indeterminado, no incoherente |

**Incoherencia** cuando dos afirmaciones pretenden ser la misma y ninguna
instancia decide:

| Caso | Qué falla |
|---|---|
| inventario de gates de 1.2, 1.3 y fusión | el oráculo sella N, el informe reporta M |
| §XXVII sobre `prediction_error` | el mapa afirma lo contrario del código desde `fd725e3` |
| `use_curiosity` en el catálogo de A4 | `catalogue()` levanta `KeyError` |
| `PR-INSTRUMENT-001` | regla emitida y no registrada |
| `canon/historical/` con `status: normative` | estante y campo se contradicen |
| `no_interference` | el ledger persiste una afirmación que nadie computó |

**No es cuestión de gravedad.** `PENDIENTE-*` es un hueco grande y sano; una
renumeración de gate es pequeña y enferma.

## 3 · Una autoridad puede estar construida, probada e inalcanzable

`PR-INSTRUMENT-001` se emitía desde cuatro sitios sin estar en `RULES`, y
`_finding` hace `RULE_BY_ID[rule_id]` — así que lanzaba `KeyError` en vez de
devolver un hallazgo bloqueante. Falla ruidoso, no permisivo: nada inseguro
pasó. Pero disparaba **exactamente cuando un endpoint primario no tiene
instrumento**, que es lo primero de cualquier preregistro confirmatorio.

Sobrevivió porque los 28 tests de la autoridad la ejercitan **directamente** y
ninguno recorría la ruta de validación.

> **Una autoridad se verifica por la ruta que la invoca, no por sus propios
> tests.**

## 4 · Por qué se pudo cerrar en estricto

`0 scientific_results · 0 empirical_evidence · 0 artefactos METRIC_RESULT` sobre
238 trazas selladas. **Nunca se publicó evidencia científica**, así que
endurecer la frontera no rompió ningún carril.

Es un hecho de autoridad: **el proyecto pudo elegir su regla estricta porque aún
no había resultados que la regla invalidara.** Esa ventana se cierra sola con el
primer resultado publicado.

## 5 · El canon: autoridad documental sostenida por citación

`AGENTS.md` declara `canon/normative/` fuente de verdad. Once documentos con
frontmatter —`status`, `version`, `owner`, `depends_on`, `supersedes`— en cuatro
estantes.

**Ningún programa lo parsea.** Ocho ficheros mencionan `canon/`, todos en
comentarios que lo citan como justificación. No hay gate que compruebe que el
código respeta el canon, ni que el canon describa el código.

Y el estante y el campo ya se contradicen una vez: `canon/historical/CANON_RNFE_v3_1.md`
se declara `status: normative`. Nada decide cuál gana.

## 6 · El caso completo · `no_interference`

La mejor cadena de autoridad rota del proyecto, y **bien documentada**:

```
1. el canon lo NOMBRA en experimental y provisional… y no lo define en normative
2. el esquema lo EXIGE            no_interference INTEGER NOT NULL
3. el organismo lo AFIRMA         nace True por defecto
4. nadie lo LEE                   todas las apariciones son persistencia
5. el código se NIEGA a fingirlo  «NO CONFIAR EN ESTE VALOR» en el registro
6. y estampa su DESMENTIDO        metadata: no_interference_computed = False
```

El ledger transporta a la vez la afirmación y su desmentido, y la decisión
pendiente está escrita: o se define el criterio y se computa, o se retira la
columna — migrar a nullable es caro porque es `NOT NULL`.

**Lo notable no es el defecto: es que la cadena entera está nombrada.** Ésa es
la forma que debería tener toda incoherencia conocida.

## 7 · Dónde sí hay autoridad ejecutada

Una, y sirve de contraejemplo: **un único punto materializa un parámetro
adaptativo**. Las cuatro fuentes producen intenciones; el materializador valida
el conjunto entero antes de escribir nada y deja ledger con procedencia y
hashes.

Cuando la autoridad se ejecuta en vez de declararse, produce un registro que se
puede auditar **sin creerle a nadie**.

## 8 · Lo que no se sabe

1. **K2** · Cuántas secciones del mapa afirman cosas ya falsadas, como §XXVII.
2. **K2** · Si algún informe de campaña contradice su oráculo fuera del
   inventario de gates. Nadie ha cruzado medido contra sellado salvo en 1.4.
3. **K2** · Qué gana cuando el estante del canon y su `status` discrepan.
4. **K2** · Cuántas columnas más persisten una propiedad que nadie computa.
5. **K1** · Qué pasa con la regla estricta de admisión el día que exista el
   primer resultado publicado.

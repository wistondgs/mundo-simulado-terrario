# Programa de adquisición causal de capacidad

`ENGINEERING_SANDBOX_NOT_EVIDENCE` · ningún preregistro firmado

## 0. El cambio de objeto científico

Deja de ser el rendimiento acumulado. La variable fundamental pasa a ser la cadena:

```
Experiencia → Cambio interno → Ganancia predictiva → Ganancia de decisión → Realización conductual
```

y cada eslabón tiene que poder romperse a propósito.

## 1. P0 · ACTION-CONTRACT-V2 — CERRADO

La hipótesis original de falta de expresividad quedó **falsada**: T0 representa todas las
intenciones de consumo estudiadas (`R = 1.0` sobre 1894 intenciones en 3000 estados exógenos).
T1 no mejora el desempeño final, pero transforma un fallo opaco en uno causalmente localizable:

```
T0: fallo de referencia   →   T1: referencia válida + fallo de alcance
```

Resultado central, **16 de 16 parejas**: `Δ valid-reference (mediana) = +0.598`, sin efecto
detectable posterior en discriminación, evidencia informativa, aprendizaje, supervivencia ni
energía.

**Decisión.** T0 permanece como comportamiento por defecto. T1 permanece como **instrumento
científico/diagnóstico**, no como «mejora de inteligencia».

### Limitación que debe viajar con el resultado

Estas corridas ocurrieron bajo la **semántica efectiva de `SandboxService`**, donde
`OpportunityLifecycle` no se ejecuta. Por tanto no son «efecto en el D4T declarado», sino
**efecto en D4T bajo el runtime Sandbox actual**. La divergencia de runtimes queda como P0.5.

## 2. P1 · CAPABILITY-ACQUISITION-01 — tres niveles de afirmación

El diseño L/F/S es más fuerte que comparar dos agentes libres, y `L − F` no pregunta si
cualquier estado interno puede transportar conocimiento: pregunta **qué capacidad adicional
aparece por la actualización paramétrica**. Es una afirmación más estrecha y más limpia.

| Nivel | Condición | Significa |
|---|---|---|
| 1 · Adquisición paramétrica | `L_post > F_post` | la actualización de parámetros produjo información funcional |
| 2 · Asignación correcta de crédito | `L_post > S_post` | no basta con actualizar: importa la correspondencia experiencia↔consecuencia |
| 3 · Adquisición generalizable | la ventaja sobrevive entidades, valores perceptivos y distractores nunca vistos | capacidad generalizada |

### Alcance real de P1, nombrado por adelantado

El organismo experimenta exactamente dos vectores: `x₀ = 0.82 → +1` y `x₀ = 0.18 → −1`. El
examen usa `x₀ ∈ [0.86, 0.98]` y `[0.02, 0.14]`. Si pasa, ha generalizado **más allá de los dos
prototipos vistos**, y eso ya es aprendizaje generalizable.

Lo que **no** demuestra: que haya inducido la regla latente `x₀ ≥ 0.7 ⇒ +`, `x₀ ≤ 0.3 ⇒ −`. Una
cabeza continua puede aprender una superficie suave alrededor de dos prototipos y acertar fuera
de ellos sin haber identificado el criterio. Por tanto:

> **P1 prueba generalización perceptiva fuera de prototipos, no inducción abstracta de una regla.**

Eso es P1.1.

### Cómo leerlo: tres ganancias, no una

```
G_P = (Pred_L,post − Pred_L,pre) − (Pred_F,post − Pred_F,pre)
G_S = (Sel_L,post  − Sel_L,pre)  − (Sel_F,post  − Sel_F,pre)
G_R = (Real_L,post − Real_L,pre) − (Real_F,post − Real_F,pre)
```

| Patrón | Diagnóstico |
|---|---|
| `G_P > 0, G_S > 0, G_R > 0` | circuito completo de adquisición funcional |
| `G_P > 0, G_S ≈ 0` | aprende una propiedad del mundo, pero la decisión no la usa |
| `G_P > 0, G_S > 0, G_R ≈ 0` | cognición adquirida, realización conductual bloqueada |
| `G_P ≈ 0` | la actualización paramétrica no adquiere la regularidad medida |
| `L ≈ S` | el resultado no depende de la asignación de consecuencia — **alarma seria** |
| mejora `seen`, no `held_out` | memorización / ajuste local |
| mejora `held_out`, falla `decorrelated` | atajo perceptivo por distractor |
| mejoran los tres bancos | primera evidencia fuerte de capacidad paramétrica y generalizable |

### Auditoría del control S

Las seis condiciones, verificadas sobre el lote en ejecución:

| Condición | Estado |
|---|---|
| mismas observaciones | ✓ reproducidas verbatim |
| mismas acciones | ✓ forzadas, log-prob recalculada bajo la política de cada gemelo |
| mismos outcomes y conteos | ✓ la permutación conserva la multiplicidad exacta |
| mismo soporte temporal | ✓ misma longitud |
| **correspondencia rota** | ✓ **0 de 7 eventos informativos conservó su paso** |

Las 986 de 1000 posiciones que «mantienen valor» son el coste metabólico repetido: ahí no hay
correspondencia que romper. Riesgo residual: con ~7 eventos informativos en ~1000 huecos, la
probabilidad de que alguno caiga en su propio índice es ~0.7 %. Un **derangement por corrida**,
con verificación por corrida, entra en P1.1 — no se toca el lote en ejecución.

## 2.1 Resultado de P1 · 8 semillas, 1200 pasos, 400 sondas por banco

```
PREDICCIÓN, banco reservado          azar = 0.5
  media ANTES      0.4888
  media DESPUÉS L  0.5012      (learner, actualizaciones ON)
  media DESPUÉS F  0.4909      (frozen,  actualizaciones OFF)
  media DESPUÉS S  0.5159      (shuffled-credit)

  G_P = +0.0103   signos +4/−3
```

| Banco | G_P | G_S | G_R | G_P del control S |
|---|---|---|---|---|
| reservado | +0.0103 (+4/−3) | +0.0031 (+6/−1) | 0.0 | **+0.0250** |
| decorrelado | +0.0097 (+3/−4) | +0.0078 (+4/−4) | 0.0 | **+0.0163** |
| valores vistos | +0.0238 (+5/−3) | −0.0153 (+3/−4) | 0.0 | +0.0184 |

### Veredicto

**No se detecta adquisición de capacidad.** Dos filas de tu tabla diagnóstica se cumplen a la vez:

- `G_P ≈ 0` — la actualización paramétrica no adquiere la regularidad medida. Todos los brazos
  quedan en azar, y los signos se reparten casi por igual.
- **`L ≈ S`** — y peor: **el control de crédito barajado termina por encima del learner** en los
  tres bancos de predicción. Lo poco que se mueve **no depende de la asignación correcta de
  consecuencia**. Es deriva, no aprendizaje.

### Causa próxima, medida y no especulada

El rollout cerrado dio `n_informative` con **mediana 6.0** por corrida de 1200 pasos. El
organismo recibe **seis ejemplos etiquetados por vida**. Ninguna arquitectura adquiere una
regularidad perceptiva con seis ejemplos.

El cuello no es el learner. Es la **hambruna de exposición informativa**, y esa hambruna tiene
dos fuentes ya medidas:

- el canal de acción — 98.5 % de desperdicio referencial bajo T0, 59 % de alcance bajo T1 (P0);
- el mundo del banco es **estrictamente agotable** porque `OpportunityLifecycle` no se ejecuta
  (P0.5).

P0, P0.5 y P1 dejan de ser tres hallazgos sueltos y se convierten en una sola afirmación:
**el organismo no aprende porque casi nunca llega a tocar la regularidad que debería aprender.**

### Defecto del examen, nombrado

`G_R ≡ 0` en todas las celdas **por construcción**, no por resultado. Bajo T0 el examen de
realización resuelve la dirección favorable sin consultar al organismo: mide una propiedad del
contrato, no del ser, y da 1.0 para cualquier agente antes y después. Debe reconstruirse sobre la
elección **propia** del organismo. Entra en P1.1.

## 3. Backlog

| | Trabajo | Estado |
|---|---|---|
| **P0** | ACTION-CONTRACT-V2 | **CERRADO** — T1 queda diagnóstico |
| **P1** | CAPABILITY-ACQUISITION-01 | **ACTIVO** — no tocar salvo defecto que invalide causalidad |
| **P0.5** | WORLD-RUNTIME-PARITY-01 | siguiente bloqueo de infraestructura |
| **P1.1** | LATENT-RULE-GENERALIZATION-01 | familia continua, frontera latente, distractores independientes |
| **P2** | CAPABILITY-LOCALIZATION-01 | cirugía de estado y mapa de almacenamiento |
| **P3** | FEATURE-IDENTITY-SWAP | ¿aprende una correlación o aprende a encontrar regularidades? |
| **P4** | RULE-REVERSAL-01 | plasticidad, incertidumbre, revisión, recuperación |
| **P5** | AUTONOMOUS-ACQUISITION-01 | sin stream igualado: que el organismo consiga su propia experiencia |
| **P6** | LEARNING-TO-LEARN-01 | ¿haber aprendido reduce la muestra necesaria? |

## 4. P0.5 · la deuda que no puede aparcarse

Existen de hecho **dos físicas**:

```
D4T_DECLARED  ≠  D4T_SANDBOX_EXECUTED
```

`WORLD-RUNTIME-PARITY-01` debe responder, para **cada regla declarativa** del escenario:

```
¿declarada?  ¿la ejecuta ExperimentController?  ¿la ejecuta SandboxService?  ¿la reproduce el replay?
```

y producir una matriz de conformidad. La meta no es parchear: es que

```
WorldDefinition → una sola semántica ejecutable
```

consumida por todas las rutas, en vez de dos implementaciones paralelas que *intentan* obedecer
el mismo escenario. No se toca durante P1.

## 5. Lo que P1 debe llegar a ser

Si `G_P > 0`, no basta con decir «`energy_head` mejoró». Hay que rastrear la transmisión:

```
percepto x
   ↓  representación del modelo del mundo
   ↓  predicción de energía
   ↓  valoración del planificador
   ↓  preferencia de política
   ↓  interacción seleccionada
```

Ése sería el primer **causal capability trace** de Terrario: poder señalar **dónde deja de
propagarse** la información aprendida. Si `energy_head` mejora y la política no cambia, ya
sabemos exactamente dónde construir.

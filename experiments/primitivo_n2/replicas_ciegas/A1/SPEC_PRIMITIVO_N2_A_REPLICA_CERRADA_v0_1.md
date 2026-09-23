# ESPECIFICACIÓN PRIMITIVO · N=2 · VERSIÓN A — RÉPLICA CERRADA

**Versión:** v0.1 · **Fecha:** 2026-09-22
**Estado:** PROPUESTO (redactado por IA; lo aprueba el investigador)
**Propósito:** que una implementación independiente reproduzca, desde este texto y sin ver el código de referencia, todos los valores determinísticos del instrumento exhaustivo N=2.

Los identificadores C1–C11 coinciden con las convenciones del instrumento de referencia. La Versión B abre C5, C7, C8, C9 y C11.

---

## 0. Reglas para quien replica

1. No leer el código de referencia ni sus salidas antes de entregar las propias.
2. Implementar sólo desde este documento, en cualquier lenguaje.
3. Si una definición admite más de una lectura, no resolverla en silencio: elegir una, anotarla en el registro de ambigüedades (sección 13) y seguir.
4. Este documento no contiene valores esperados, salvo dos vectores de calibración (sección 9).
5. Entregables: `por_sistema.jsonl`, `resumen.json`, registro de ambigüedades, lenguaje y versión usados.

---

## 1. Estados y dinámicas (C1, C2)

- Dos variables binarias x1, x2. Estado s ∈ {0,1,2,3}, con s = 2·x1 + x2.
- Una dinámica es una función F: {0,1,2,3} → {0,1,2,3}, escrita como la tupla (F(0), F(1), F(2), F(3)). Hay 4⁴ = 256.
- Se enumeran en orden lexicográfico de la tupla, desde (0,0,0,0) hasta (3,3,3,3).
- Iterar F equivale a actualización sincrónica de ambas variables.
- ⊕ sobre estados es el XOR bit a bit de la codificación de 2 bits.

## 2. Particiones y cortes (C3)

- Particiones binarias del estado: P1(s) = x1, P2(s) = x2, P3(s) = x1 ⊕ x2.
- Un corte es un par ordenado de particiones (a, b):
  - C12 = (P1, P2) — el corte dado;
  - C13 = (P1, P3);
  - C23 = (P2, P3).

## 3. Perturbaciones (C4)

Para un corte (a, b), m_a es el único m ∈ {1,2,3} tal que, para todo s, a(s ⊕ m) ≠ a(s) y b(s ⊕ m) = b(s). m_b se define igual, intercambiando a y b.

Las máscaras deben derivarse de esta definición; están únicamente determinadas. Reportarlas en `resumen.json` → `controles`.

## 4. Dependencia estructural (C5)

En un corte (a, b), para i, j ∈ {a, b}:

d(i, j) = verdadero si existe algún estado s tal que i(F(s)) ≠ i(F(s ⊕ m_j)).

Se evalúa sobre los 4 estados, no sólo sobre los estados de atractor.

- `grafo` = [d(a,a), d(a,b), d(b,a), d(b,b)], en ese orden.
- `cruzada`:
  - "separable" si d(a,b) y d(b,a) son falsos;
  - "mutua" si ambos son verdaderos;
  - "unidir" en cualquier otro caso.

## 5. Atractores (C6)

- Desde cada estado s se itera F hasta que un estado se repite. Los estados del ciclo así cerrado forman un atractor, identificado por su **conjunto** de estados.
- El conjunto de atractores de F es el conjunto de ciclos distintos obtenidos desde los 4 estados.
- `atractores`: cada atractor como lista ascendente de estados. La lista de atractores se ordena lexicográficamente (comparación elemento a elemento; si una lista es prefijo de otra, va primero la más corta).
- `periodos`: tamaños de los atractores, en orden ascendente.

## 6. Robustez (C7)

En un corte (a, b):

- Se consideran todos los pares (s, m) con s perteneciente a algún atractor A y m ∈ {m_a, m_b}.
- Un par es exitoso si el atractor alcanzado desde s ⊕ m es exactamente A.
- Robustez = pares exitosos / pares totales.

Formato: fracción reducida "p/q"; si q = 1, sólo "p". Ejemplos: "0", "1", "3/4".

## 7. Scheduler (C8), sólo en C12

Reglas locales: f1(s) = x1(F(s)), f2(s) = x2(F(s)).

- `sinc`: la propia F.
- `sec12`: desde (x1, x2), primero x1' = f1(x1, x2); luego x2' = f2(x1', x2).
- `sec21`: primero x2' = f2(x1, x2); luego x1' = f1(x1, x2').

Salidas:
- los atractores de las tres dinámicas, con el formato de la sección 5;
- `atractores_distintos`: verdadero si el conjunto de atractores de sinc difiere del de sec12 o del de sec21;
- `ciclo_muere_sin_reloj`: verdadero si algún atractor de sinc de tamaño ≥ 2 no es atractor ni de sec12 ni de sec21.

## 8. Lesión (C9), sólo en C12

Lesionar x1 produce la dinámica G con x2(G(s)) = x2(F(s)) y:
- `congelar`: x1(G(s)) = x1(s);
- `fijar0`: x1(G(s)) = 0.

Lesionar x2 es análogo.

Veredicto: verdadero si la unión de los estados de todos los atractores de G difiere de la unión correspondiente de F.

## 9. Salida por sistema

`por_sistema.jsonl`: 256 líneas en el orden de enumeración. Cada línea es un objeto JSON con exactamente estas claves:

- `F`
- `atractores`
- `dependencias` → `C12`, `C13`, `C23` → `cruzada`, `grafo`
- `lesion` → `x1`, `x2` → `congelar`, `fijar0`
- `periodos`
- `robustez` → `C12`, `C13`, `C23`
- `scheduler` → `atractores_distintos`, `ciclo_muere_sin_reloj`, `sec12`, `sec21`, `sinc`
- `tipo_C12`
- `tipo_S4`

Serialización canónica:
- claves ordenadas por punto de código Unicode en todos los niveles;
- sin espacios; separadores `,` y `:`;
- booleanos `true` / `false`; sólo ASCII;
- líneas separadas por `\n`, con `\n` final.

Con esta serialización el SHA-256 del archivo es comparable, pero la comparación oficial es campo por campo (sección 12).

**Vectores de calibración.** Son los únicos valores esperados de este documento:

```
{"F":[0,0,0,0],"atractores":[[0]],"dependencias":{"C12":{"cruzada":"separable","grafo":[false,false,false,false]},"C13":{"cruzada":"separable","grafo":[false,false,false,false]},"C23":{"cruzada":"separable","grafo":[false,false,false,false]}},"lesion":{"x1":{"congelar":true,"fijar0":false},"x2":{"congelar":true,"fijar0":false}},"periodos":[1],"robustez":{"C12":"1","C13":"1","C23":"1"},"scheduler":{"atractores_distintos":false,"ciclo_muere_sin_reloj":false,"sec12":[[0]],"sec21":[[0]],"sinc":[[0]]},"tipo_C12":[0,0,0,0],"tipo_S4":[0,0,0,0]}
{"F":[0,2,1,3],"atractores":[[0],[1,2],[3]],"dependencias":{"C12":{"cruzada":"mutua","grafo":[false,true,true,false]},"C13":{"cruzada":"unidir","grafo":[true,true,false,true]},"C23":{"cruzada":"unidir","grafo":[true,true,false,true]}},"lesion":{"x1":{"congelar":true,"fijar0":true},"x2":{"congelar":true,"fijar0":true}},"periodos":[1,1,2],"robustez":{"C12":"0","C13":"1/4","C23":"1/4"},"scheduler":{"atractores_distintos":true,"ciclo_muere_sin_reloj":true,"sec12":[[0],[3]],"sec21":[[0],[3]],"sinc":[[0],[1,2],[3]]},"tipo_C12":[0,2,1,3],"tipo_S4":[0,1,3,2]}
```

## 10. Tipos (C10)

Conjugación de F por una permutación p de los estados: la dinámica G tal que G(p(s)) = p(F(s)) para todo s.

- `tipo_S4`: la tupla lexicográficamente mínima entre las conjugaciones de F por las 24 permutaciones.
- `tipo_C12`: ídem, sólo sobre las 8 permutaciones de la forma
  (x1, x2) ↦ (x1 ⊕ n1, x2 ⊕ n2) o (x1, x2) ↦ (x2 ⊕ n1, x1 ⊕ n2), con n1, n2 ∈ {0,1}.

## 11. Agregados → `resumen.json`

Pesos uniformes 1/256; logaritmos en base 2. Los conteos por categoría incluyen las tres categorías de `cruzada`, también con valor 0.

### 11.1 Sección `deterministico`

| Campo | Definición |
|---|---|
| `n_dinamicas` | número de registros |
| `tipos_S4`, `tipos_C12` | número de valores distintos de cada tipo |
| `cruzada_en_C12` | conteo de dinámicas por categoría de `cruzada` en C12 |
| `separable_en_algun_corte` | dinámicas con "separable" en al menos un corte |
| `mutua_en_los_3_cortes` | dinámicas con "mutua" en los tres cortes |
| `categoria_cambia_con_el_corte` | dinámicas cuyas tres categorías no son todas iguales |
| `con_al_menos_un_atractor` | dinámicas con uno o más atractores |
| `robustez_cambia_con_el_corte` | dinámicas cuyas tres robusteces no son todas iguales |
| `scheduler_puntos_fijos_distintos` | dinámicas cuyo conjunto de atractores de tamaño 1 en sinc difiere del de sec12 o del de sec21 |
| `scheduler_atractores_distintos` | dinámicas con `atractores_distintos` verdadero |
| `con_ciclo_sincronico_por_cruzada` | entre las dinámicas con algún atractor de tamaño ≥ 2, conteo por `cruzada` en C12 |
| `ciclo_muere_sin_reloj_por_cruzada` | entre las dinámicas con `ciclo_muere_sin_reloj` verdadero, conteo por `cruzada` en C12 |
| `lesion_veredicto_difiere_congelar_vs_fijar0` | pares (dinámica, variable) cuyos veredictos difieren entre las dos semánticas |
| `lesion_casos` | número de pares (dinámica, variable) |
| `perfiles_consecuencia_K` | valores distintos de K (ver 11.2) |
| `perfiles_robustez_C12` | valores distintos de la robustez en C12 |
| `H_K_bits` | H(K) |
| `vocabularios` | ver 11.2 |

### 11.2 Vocabularios contra consecuencias (C11)

**Vocabularios V** (particiones de las 256 dinámicas):
- `grafo_dependencias_C12`: etiqueta = `grafo` en C12;
- `cruzada_C12`: etiqueta = `cruzada` en C12;
- `tipo_S4`: etiqueta = `tipo_S4`.

**Consecuencias T:**
- `K` = (periodos, robustez en C12);
- `solo_robustez_C12`;
- `solo_periodos`.

**Medidas de información:**
- H(V) = −Σ p·log₂ p sobre las clases de V.
- I(V;T) = Σ p(v,t)·log₂[p(v,t) / (p(v)·p(t))].
- E[I]: información mutua esperada bajo permutación aleatoria con marginales fijos. Con N = 256, a_i los tamaños de clase de V y b_j los de T:

\[
E[I]=\sum_i\sum_j\sum_{n=\max(1,\,a_i+b_j-N)}^{\min(a_i,\,b_j)}\frac{n}{N}\log_2\frac{N\,n}{a_i\,b_j}\cdot\frac{a_i!\,b_j!\,(N-a_i)!\,(N-b_j)!}{N!\,n!\,(a_i-n)!\,(b_j-n)!\,(N-a_i-b_j+n)!}
\]

  Se recomienda calcular los factoriales en escala logarítmica.
- AMI_max = (I − E[I]) / (max(H(V), H(T)) − E[I]).

**Por cada V se reporta:**
- `clases`;
- `clases_con_colision_en_K`: clases de V que contienen dos o más valores distintos de K;
- `clases_con_colision_en_robustez`: ídem para la robustez en C12;
- `colision_garantizada_por_conteo`: verdadero si las clases de V son menos que los valores distintos de K;
- `H_V_bits`;
- para cada T: `I_bits`, `E_I_permutacion_exacta_bits`, `AMI_max`.

### 11.3 Monte Carlo (opcional)

- Permutar al azar las etiquetas de V entre las 256 dinámicas, R ≥ 10.000 veces.
- Reportar media, desvío y p = (1 + #{I_nula ≥ I}) / (R + 1).
- No se exige coincidencia exacta con la referencia: la media debe quedar a menos de 4·desvío/√R de la E[I] exacta.

## 12. Controles → `resumen.json`, sección `controles`

Si alguno falla, hay un error antes de interpretar cualquier resultado.

1. **Finitud.** Toda dinámica tiene al menos un atractor.
2. **Puntos fijos y scheduler.** Los atractores de tamaño 1 son los mismos en sinc, sec12 y sec21. Es un teorema: si f1(s) = x1 y f2(s) = x2, cualquier orden secuencial deja s fijo, y a la inversa.
3. **Simetría entre cortes.** Para x ∈ {C12, C13, C23}, deben ser idénticos:
   - los conteos de `cruzada`;
   - H(robustez_x);
   - I(grafo_x ; robustez_x);
   - I(tipo_S4 ; robustez_x).

   Razón: las permutaciones de estados llevan cualquier corte a cualquier otro, y la conjugación es una biyección de las 256 dinámicas.
4. **Ancla externa.** `tipos_S4` debe coincidir con el término n = 4 de OEIS A001372 (endofunciones no etiquetadas). Consultarlo directamente en la fuente.
5. **Guardia de consecuencias intrínsecas.** La robustez calculada con las tres máscaras {1,2,3} (perturbar hacia cualquier otro estado) debe ser constante dentro de cada clase `tipo_S4`. Reportar verdadero o falso.
6. **Máscaras derivadas.** Los pares (m_a, m_b) de cada corte.

## 13. Registro de ambigüedades

Por cada punto donde el texto admitió más de una lectura:
- sección;
- lecturas posibles;
- lectura elegida;
- si la elección puede afectar algún campo de salida.

## 14. Comparación (la hace el investigador, no quien replica)

- **Criterios de igualdad.** Enteros, booleanos, listas y fracciones: igualdad exacta. Reales: |Δ| ≤ 1e-6 (la referencia redondea a 6 decimales). La referencia omite categorías con conteo 0: tratarlas como 0.
- **Localización.** `por_sistema.jsonl` se compara línea por línea, en orden de enumeración. Se reportan la primera F discordante y su primer campo discordante.
- **Resolución.** Toda divergencia se resuelve volviendo al texto de esta especificación, sin presumir que la referencia tiene razón. Puede ser:
  - ERROR_REPLICA;
  - ERROR_REFERENCIA;
  - AMBIGUEDAD_SPEC: se corrige la especificación y ambas implementaciones vuelven a correr.
- **Resultado:**
  - REPLICADO: todo coincide;
  - REPLICADO_CON_CORRECCIONES: hubo divergencias, resueltas y documentadas;
  - NO_REPLICADO.

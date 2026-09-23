# Revisión previa de implementación — A1

## Reconstrucción operativa C1–C11

- **C1–C2.** El dominio es `S = {0,1,2,3}`; un estado codifica
  `2*x1+x2`. Cada dinámica es una 4-tupla de salidas de `S`, enumerada en
  producto lexicográfico base 4. XOR opera sobre esos enteros de dos bits.
- **C3.** Se emplean las tres funciones binarias `P1=x1`, `P2=x2` y
  `P3=x1 xor x2`, y los cortes ordenados C12, C13 y C23.
- **C4.** Para cada corte se buscan exhaustivamente, entre 1, 2 y 3, las dos
  máscaras definidas por cambio de una partición y conservación de la otra.
- **C5.** Cada una de las cuatro aristas se prueba en los cuatro estados;
  `grafo` conserva exactamente el orden `(a,a),(a,b),(b,a),(b,b)`.
- **C6.** Se sigue cada órbita hasta su primera repetición, se identifica el
  ciclo por su conjunto, y se canoniza mediante listas ascendentes y orden
  lexicográfico de listas.
- **C7.** Para cada estado de cada atractor y ambas máscaras del corte se
  calcula el atractor de destino; la razón se reduce y se serializa como
  fracción entera o irreducible.
- **C8.** C12 usa F síncrona y dos actualizaciones secuenciales construidas
  con las reglas locales evaluadas en los estados intermedios indicados.
- **C9.** Se crean las cuatro dinámicas lesionadas y se comparan las uniones
  de sus atractores con la unión de F.
- **C10.** Se enumeran las 24 permutaciones de estados y las ocho
  transformaciones afines/intercambios permitidos; cada conjugación se
  representa como tupla y se toma el mínimo lexicográfico.
- **C11.** Los conteos usan 256 equiprobables. Entropía, información mutua y
  la esperanza hipergeométrica exacta se calculan con logaritmos en base 2;
  los vocabularios y consecuencias se forman como tuplas inmutables.

## Invariantes y casos borde

- Toda función finita tiene al menos un ciclo; un atractor no depende del
  estado desde que se descubrió.
- Las máscaras de un corte deben ser únicas y distintas de cero.
- Una fracción de robustez tiene denominador positivo y numerador entre cero
  y denominador.
- La conjugación conserva el tipo de grafo funcional; una actualización
  secuencial conserva todo punto fijo síncrono.
- Todos los valores JSON son enteros, listas, cadenas o booleanos: nunca
  flotantes en `por_sistema.jsonl`.

## Ambigüedades encontradas

No hay ambigüedad de valor en C1–C11. La forma interna de `resumen.json` y
`CONTROL_REPORT.json` no se fija como un esquema de claves exhaustivo. Se
usarán nombres descriptivos, JSON canónico y números de punto flotante
redondeados a seis decimales en resultados informacionales; esto es una
convención **FORMAL_ONLY** porque no modifica los datos por sistema ni las
definiciones matemáticas.

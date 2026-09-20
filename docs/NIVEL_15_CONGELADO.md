# Nivel 1.5 · CONGELADO

**2026-09-20.** Selección de información bajo capacidad temporal limitada.

```
ESTADO           CONGELADO · sólo diseño
CÓDIGO           ninguno · no hay rama, carpeta ni implementación
CAMPAÑA          no ejecutada
MOTIVO           el mapa causal v3 lo aparca hasta que exista presión endógena
```

Se congela por decisión de Wis, tras el `MAPA_GLOBAL_HABILIDADES_AGENTE_CIBERNETICO_v3`,
que reordena el proyecto alrededor de generar experiencia antes de organizarla.

---

## 1 · Por qué se congela, y qué lo descongelaría

La memoria selectiva no se descarta: **le falta la necesidad**. En el diseño
actual la escasez la impone el experimentador --«tenés cuatro mensajes»--, no la
produce el organismo.

```
CONDICIÓN DE DESCONGELACIÓN

   experiencia útil generada por el organismo  >  capacidad disponible para conservarla
```

Sólo entonces la restricción de memoria deja de ser una tarea impuesta y pasa a
ser una insuficiencia del ser.

## 2 · El archivo canónico

`docs/level15_congelado/` contiene el paquete **v4** íntegro, con su cadena de
supersesiones y sus huellas. Las doce sumas verifican.

```
orden de autoridad   08 supersesión v4 → 07 v3 → 06 v2 → 01…05 entregables
manifiestos v1/v2/v3 congelados como registro histórico
```

## 3 · Lo decidido DESPUÉS de v4 · sólo existía en la conversación

Esto es lo que este documento existe para no perder.

### 3.1 · Mecanismo congelado

```
ORDEN DEL ENSAYO
  1. x ~ Uniforme{0..15}
  2. z = ε-greedy sobre V_E[x]            se escribe · aún no hay consulta
  3. tick
  4. q ~ P_régimen{G, P, J}               la consulta aparece AHORA
  5. a = ε-greedy sobre V_D[(z,q)]
  6. r = 1[a = respuesta correcta] ∈ {0,1}
  7. V_E[x][z] ← V_E[x][z] + α·(r − V_E[x][z])
     V_D[(z,q)][a] ← V_D[(z,q)][a] + α·(r − V_D[(z,q)][a])
     exactamente una celda por tabla

ACTUALIZACIÓN    V ← (1−α)·V + α·r          α = 0.05
INICIALIZACIÓN   V_E y V_D = 0.5            V_D se crea perezosamente
DESEMPATES       índice ascendente          verificado irrelevante
ε(t) PRINCIPAL   0.32 − 0.30·(t/N)          lineal
ε(t) ALTERNATIVO 0.10 constante
```

**Corrección de etiqueta:** durante todo el piloto llamé a la exploración
`0.30→0.02`. La función real arranca en **`0.32`**. Toda la evidencia se corrió
con `0.32 − 0.30·(t/N)`.

### 3.2 · `V₀` es portante, no un hiperparámetro

```
      α      V₀       R_G      R_P      R_J
   0.005    0.0      0/20     0/20     0/20      ← catastrófico
    0.01    0.0      0/20     2/20     2/20      ← catastrófico
    0.05    0.0     12/20    17/20    14/20
     0.1    0.0     19/20    20/20    20/20
   0.005    0.5     18/20    19/20    20/20
    0.05    0.5     20/20    20/20    20/20      ← congelado
     0.1    0.5     20/20    20/20    20/20
```

Con `V₀ = 0` y recompensa en `{0,1}`, el primer acierto en cualquier `(x,z)` deja
esa celda por encima de todas las no probadas y la política se clava. **`V₀ = 0`
es fixture negativa conocida, no una variante.**

### 3.3 · La exploración no decide la clase

```
programa                      R_G      R_P      R_J
0.32→0.02 (principal)        18/20    19/20    20/20
constante 0.10               17/20    18/20    19/20
0.50→0.01                    19/20    18/20    18/20
constante 0.30               19/20    19/20    19/20
```

`EXPLORATION_DEPENDENT_REPRESENTATION` no dispara.

### 3.4 · El clasificador, auditado dirigido

```
si Σr = 16 → H1 · si Σp = 16 → H2 · si Σj = 16 → H3 · si no → OTHER
```

El primer test fue **vacuo**: dos millones de codificadores al azar y ninguno
alcanzó la condición, que tiene probabilidad `~6·10⁻⁹`. Rehecho dirigido, sobre
casos que sí pueden alcanzarla:

```
los 24 renombrados de la partición por filas      → H1 · invariante
73 396 perturbaciones a distancia 1–4             → 0 falsos positivos
150 000 perturbaciones desde las tres canónicas   → 0 con dos sumas a 16
híbridos a mano (4 casos)                         → OTHER los cuatro
```

`Σr = 16` fuerza la estructura exacta; las tres clases son mutuamente excluyentes.

### 3.5 · Semillas

```
QUEMADAS en diseño       20260920 · 777 · 31337
                         20260920 colisiona con la ventana de 1.0; colisión de
                         ETIQUETA, sin efecto: generadores y papeles distintos

RESERVADAS confirmatoria 130000011 … 130000026   16 primarias
                         130000011 … 130000033   span completo con los +7
                         160 claves efectivas · 0 repeticiones · verificado exhaustivo

La reserva se mantiene aunque el nivel esté congelado: si alguna vez se
descongela, la ventana debe seguir limpia.
```

## 4 · Lo que sobrevive al congelamiento

Tres cosas de 1.5 **no** quedan aparcadas, porque no dependen del constructo:

**La prueba de existencia del constructo** --techos `1/8`, `1/8`, `1/10`, el lema
del banco balanceado con `L̄ ≥ 1/3`, el selector ideal en `7/60`, las nueve `H₃`
isomorfas-- es matemática verificada y vale con independencia de si el
experimento se corre.

**Los tres contratos anti-fuga**, que son patrón reutilizable: el descodificador
sólo ve `(z,q)`; una actualización por tabla y por ensayo, con `Σ = nº de ensayos`
como invariante contable; tablas de sólo lectura entre retener y responder.

**La tercera capa del libro mayor** --la disposición-- documentada en
`EJE_ADQUISICION_VS_SUMINISTRO_01.md`. La evidencia de `V₀` nació aquí y
gobierna cualquier nivel futuro.

## 5 · Qué NO se afirma

No se afirma que el organismo pueda aprender selección de memoria. **La campaña
confirmatoria no se ejecutó.** Lo único medido es evidencia de diseño, con las
semillas quemadas, y como tal está clasificada: `PILOT / DISCOVERY`.

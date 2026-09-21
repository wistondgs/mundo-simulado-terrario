# Enmienda 01 al oráculo de `LEVEL1.8` · el comparador, y el gate que faltaba

**Fecha:** 2026-09-20 · **Oráculo enmendado:** `32531ef` §7 y §9
**Momento:** durante implementación y calibración · **ninguna semilla `180…` abierta**
**El oráculo no se reescribe.** Aditiva.

---

# 1 · Defecto A · `C17-ONLY` estaba sin definir

`32531ef` §7 dice:

```
C17-ONLY    el modelo de 1.7 sin estado    ← baseline del endpoint
```

y **no dice si sigue aprendiendo durante la fase A**. Toda la diferencia entre un
falso positivo y un resultado honesto vive en esa ambigüedad.

## 1.1 · Medido, no supuesto

```
contra C17 CONGELADO      ΔL = +0.23 · +0.28   con CERO estados creados
contra C17 CONTINUO       ΔL = −0.15 … −0.42   con 10–15 estados
```

Con el predecesor congelado, el endpoint suma **beneficio del estado predictivo**
más **beneficio de haber recibido más evidencia**. Es exactamente el confundido que
`NO-ACTION` destapó en 1.7.

## 1.2 · Lo que queda fijado

```
C17-ONLY   parte del MISMO snapshot de C_17
           recibe LAS MISMAS transiciones de la fase A
           tiene LAS MISMAS oportunidades de actualización
           NO tiene Z

la única diferencia permitida entre los dos brazos es la capacidad de
representar y desambiguar estado
```

```
ENDPOINT   ΔL = L_POST(C17-ONLY continuo) − L_POST(C18)
```

La pregunta no cambia. Se aclara el comparador que la hace identificable.

## 1.3 · Resultados previos

```
todo lo calculado contra C_17 congelado queda etiquetado
NO VÁLIDO PARA EL ENDPOINT
```

Se conserva como registro del confundido, en `acb6b14` y en este documento.

---

# 2 · Defecto B · **faltaba el gate**

Al ir a escribir la fixture que exige `C17-ONLY` continuo, aparece que **ninguno de
los dieciséis certifica la paridad del comparador**. 1.7 tenía `L17-5
BASELINE-PARITY` justamente por esto, y no se trasladó.

Un oráculo que fija el comparador y no lo hace falsificable deja la puerta abierta
a que un futuro runner lo congele sin que nada lo detecte.

## 2.1 · El gate nuevo

```
L18-16  BASELINE-PARITY
        C17-ONLY y C18 parten del mismo C_17, ven las mismas transiciones,
        tienen el mismo número de oportunidades de actualización, y difieren
        SÓLO en la capacidad de organizar Z
```

## 2.2 · Consecuencia sobre el conjunto sellado

```
antes    REQUIRED_GATES = L18-0 … L18-15     16
ahora    REQUIRED_GATES = L18-0 … L18-16     17
```

**Esto endurece el contrato; no lo afloja.** Un gate añadido antes de cualquier
semilla confirmatoria y por enmienda fechada es fortalecimiento prospectivo, no
rescate posterior. `verify_ledger` pasa a exigir diecisiete, y su test que recorre
los gates uno a uno los cubre todos automáticamente.

---

# 3 · Por qué esto es corrección prospectiva legítima

```
ocurre ANTES de cualquier semilla 180…
ocurre durante implementación y calibración
NO toca el claim máximo autorizado
NO cambia el endpoint científico, sólo define su comparador
HACE el contrato más estricto, nunca más laxo
```

---

# 4 · Lo que esta enmienda NO decide

El learner mínimo pierde contra el comparador correcto —`ΔL` de −0.15 a −0.42, peor
con más presupuesto— y eso **no** significa que la capacidad adjudicada sea
imposible. Significa sólo:

> este mecanismo mínimo, tal como está, pierde contra el baseline correcto.

La hipótesis de que la culpa es la **dilución del prior** al repartir masa entre
ramas sigue siendo hipótesis. El diagnóstico que la decide es `ORACLE-PARTITION`
contra `C17-ONLY` continuo, y se ejecuta después de esta enmienda.

---

# 5 · `ORACLE-PARTITION` · el diagnóstico que decide, ejecutado tras la enmienda

Mismo `C_17` heredado, misma conservación de masa, mismo baseline continuo, mismas
transiciones, mismo presupuesto. El oráculo aporta **sólo la organización**.

```
T_18    L(C17 continuo)   L(ORACLE-PARTITION)      ΔL
1024         0.8499              0.2696         +0.5803
4096         0.6456              0.0859         +0.5598
```

```
┌──────────────────────────────────────────────────────────────────┐
│  ORACLE-PARTITION GANA CLARAMENTE                                │
│  la arquitectura de herencia y conservación SÍ puede convertir   │
│  una partición correcta en ventaja                               │
│  ⇒ el problema está en CÓMO SE DESCUBRE Z, no en la herencia     │
└──────────────────────────────────────────────────────────────────┘
```

## 5.1 · Dos correcciones a mi propio razonamiento

**La hipótesis de dilución era al revés.** Probé dos repartos que parecían
conservar masa: uniforme entre los `N` estados (diluye por ~17, la regla de mi
learner) y por observación `C_17[o]/k_o` (diluye por ~2). Predije que diluir menos
sería mejor. **Es al contrario**: la uniforme da `+0.58` y la de menos dilución
`+0.13`. Con el prior débil la evidencia del oráculo domina; con el prior fuerte
tira hacia la tabla aliasada.

Por tanto **la dilución del prior NO explica el fallo del learner.** La causa sigue
sin identificar, y no la voy a suponer otra vez.

**Y mi regla alternativa violaba el invariante.** La de «por observación» deja a
cero las filas de observaciones que el mundo no alcanza, donde `C_17` sí tiene masa
de prior: pierde **64 de 5376**. El gate `L18-4` la rechazó con exceso `+2.5e-01`.

```
regla uniforme       PASA   residuo 5.684e-14
regla por observación VIOLA  exceso  +2.500e-01   ← sus ΔL no son usables
```

El único `ΔL` citable es el de la regla que conserva: **+0.58**.

## 5.2 · Consecuencia para el backlog

```
la arquitectura puede expresar la capacidad       ESTABLECIDO
el mecanismo de descubrimiento pierde             ESTABLECIDO
la causa del fallo del descubrimiento             SIN IDENTIFICAR
```

No toco `_refine` hasta saber por qué falla. Auditar la arquitectura de herencia ya
no procede: acaba de demostrarse que no es el cuello de botella.

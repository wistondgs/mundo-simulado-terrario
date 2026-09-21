# Nivel 1.8 · Enmienda 06 — qué ocurre cuando un estado vuelve a separarse

**Micro-enmienda de desambiguación.** Completa una máquina de estados que la
Enmienda 02 dejó incompleta. No decide por `ΔL`, no intenta conservar `T`=16384,
no reduce varianza y no busca menos estados.

---

## 1 · La pregunta que la Enmienda 02 no contesta

§3.1 define `favor(z)` **por split aceptado**; §3.2 dice que se inicializa con el
balance que lo justificó y continúa acumulando, y que es «una decisión sobre una
misma hipótesis a lo largo del tiempo»; §3.3 dice que colapsar debe dejar un
resultado «funcionalmente equivalente a no haber mantenido esa distinción».

Ninguna de las tres dice qué pasa si **un estado con un split todavía abierto
vuelve a separarse**. Ocurre: medido, 16 veces en 600 pasos de ruido, y de 0 a 1
episodio por vida en mundos reales.

La implementación hace hoy dos cosas que la Enmienda 02 no autoriza:

```
_favour[state]         se SOBREESCRIBE          → la evidencia se reinicia
_children[state]       se REEMPLAZA             → los hijos viejos quedan huérfanos
_shadow / _collapsed_prior  se REINICIAN        → la hipótesis colapsada se pierde
las rutas a los hijos viejos NO se borran       → siguen vivos y en uso
```

Un huérfano no está en `_descendants` de nadie, así que **merge no puede
retirarlo jamás**. Medido a `T`=16384:

| semilla | vivos | huérfanos | rutas que aún apuntan a uno |
|---:|---:|---:|---:|
| 150000011 | 30 | 3 | 16 |
| 150000013 | 1 | 0 | 0 |
| 150000015 | 8 | 3 | 0 |
| 150000017 | 7 | **4** | 16 |

---

## 2 · Las tres terminaciones posibles, y por qué dos están excluidas

**(A) Prohibir el re-split.** Un estado con split abierto no vuelve a separarse.
→ **Excluida**: cambiaría el criterio de split y su momento, ambos congelados
desde `acb6b14` y explícitamente intocables en el mandato preconfirmatorio.

**(B) El re-split reemplaza: colapsar primero, separar después.**
→ **Excluida por `L18-17`**: el split abierto tiene `favor > 0` —si fuese ≤ 0 ya
habría colapsado— así que deshacerlo sería exactamente un «justificado deshecho»,
que ese gate declara fallo. No se puede cumplir una parte del sello violando otra.

**(C) El re-split EXTIENDE la misma hipótesis abierta.**
→ **La única compatible con lo ya sellado**, y la que además lee literalmente
§3.2: «una misma hipótesis a lo largo del tiempo».

---

## 3 · Lo que se sella

```
Al refinar un estado que YA tiene un split abierto:

children          los nuevos hijos SE SUMAN a los existentes
                  ninguno queda huérfano · todos siguen siendo descendientes
                  y por tanto siguen siendo retirables por merge

favour            += el balance que justifica el nuevo refinamiento
                  NUNCA se sustituye · RE-SPLIT ≠ RESET DE EVIDENCIA

shadow            CONTINÚA acumulando · es la evidencia de la hipótesis
                  colapsada, que no ha dejado de existir

collapsed_prior   SE CONSERVA el de la PRIMERA separación · es el prior de
                  «no haber separado nunca», y no cambia porque se separe otra vez

routing           las rutas a los hijos previos siguen siendo válidas: esos hijos
                  siguen perteneciendo al mismo refinamiento
```

Y una consecuencia que debe cumplirse y es verificable:

```
tras un colapso, NINGÚN estado vivo puede carecer de padre que lo reconozca
```

---

## 4 · Lo que NO cambia

Criterio prequencial, penalización, criterio de split, momento del split, prior,
reparto de masa, routing, semántica de merge, `C17` continuo, FIXED-DEPTH-1,
O-HISTORY-ONLY, endpoint, estadística V2 y escalera de presupuestos: **congelados**.

La reparación toca exclusivamente la persistencia de la contabilidad del split.
Una trayectoria que nunca ejercite un re-split debe producir **exactamente** el
comportamiento anterior, y eso se demuestra, no se afirma.

---

## 5 · Estado administrativo de la selección anterior

```
ROUND_B_SELECTED_T = 16384
STATUS             = INVALIDATED_FOR_FINAL_SELECTION
CAUSE              = implementation/specification non-conformance
AFFECTED_RULE      = Enmienda 02 §3.2 (persistencia de favor) y §3.3 (colapsabilidad)
EVIDENCE           = LCB95(m) +0.0020 → −0.0005 con la variante conforme
```

El número no se borra. La Ronda B queda **diagnóstica, no válida para selección
final de `T`**. Las 16 vidas `190000011…190000027` quedan consumidas: se han
observado con learner defectuoso y con learner conforme, y el signo del `LCB`.
No se reutilizan.

`180000011…180000074` sigue cerrado.

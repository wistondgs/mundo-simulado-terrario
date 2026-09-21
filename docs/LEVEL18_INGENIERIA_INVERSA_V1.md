# Nivel 1.8 · Ingeniería inversa de `LEARNER-18-v1`

Por qué falló, medido. Ninguna de estas mediciones cambia el veredicto —
`LEARNER-18-v1 = INSUFICIENTE`, cerrado— ni toca el learner. Convierte el fallo
en nodos del hipergrafo con evidencia, en vez de en una lista de ideas.

Ventana `200000011…200000027`, ya consumida por la Ronda C. `T` = 16384.

---

## 1 · El fallo no es organización mala. Es organización AUSENTE.

| | ganan (10) | pierden (6) |
|---|---:|---:|
| estados finales | 12 – 57 | **exactamente 1, las seis** |
| splits | 8 – 24 | 5 – 7 |
| merges | 6 – 16 | **= splits, todos** |
| episodios abiertos al final | 2 – 7 | **0** |
| margen sobre FD1 | +0,010 a +0,092 | −0,028 a −0,057 |
| situaciones del mundo | 7 – 21 | 7 – 21 |

**No hay ningún caso intermedio.** O el organismo establece estructura, o no
establece ninguna y termina siendo `C17` con un solo estado — perdiendo contra
FIXED-DEPTH-1, que tiene cuatro estados **suministrados**.

La bimodalidad hace que ocho instrumentos «discriminen» en una nula por
permutación (`|z|` 2,7 – 3,2), pero **son el mismo hecho visto ocho veces**:
estados, ocupados, máximo, firmas, extensiones, celdas con soporte, hambrientos
e `I(C;Z|O)` valen todos su mínimo cuando sólo hay un estado.

## 2 · No es propiedad del mundo

```
situaciones latentes            7–21 en los dos grupos · |z| = 0.31
vidas que cambian de signo con el presupuesto   3 de 16
    200000015:  1 estado a T=4096  →  26 estados a T=16384
```

Si fuese el mundo, ninguna cambiaría. **El estado de «sin organización» es
escapable**; con más experiencia algunas vidas escapan.

Y la información está ahí, abundante, en las seis perdedoras:

```
200000012  oráculo +0.4051   learner −0.0061   1 estado
200000016  oráculo +0.3129   learner −0.0041   1 estado
200000024  oráculo +0.4486   learner −0.0027   1 estado
200000025  oráculo +0.5310   learner −0.0059   1 estado
200000026  oráculo +0.2043   learner −0.0158   1 estado
200000027  oráculo +0.4181   learner −0.0049   1 estado
```

## 3 · El mecanismo exacto: los dos criterios no están en la misma escala

```
TODO episodio colapsado muere en 0 pasos · nace y se refuta en la misma
actualización · en los DOS grupos

favor inicial mediano     perdedoras 0.0237     ganadoras 0.0811   (3,4×)
```

El split se acepta cuando `código refinado < código colapsado` **por cualquier
margen** —bastan 0,02 nats acumulados—, y el primer incremento de
`_judge_open_split` es típicamente de orden 0,17. Es decir:

> **una distinción sobrevive si su favor inicial le alcanza para aguantar la
> primera observación posterior, y no por la evidencia que la justificó.**

El criterio que CREA y el criterio que DESTRUYE no son conmensurables. La
supervivencia la decide una observación, no una acumulación. Eso explica a la vez
la bimodalidad, que los colapsos duren cero pasos, y que más presupuesto rescate
algunas vidas: con más experiencia, un split llega a nacer con favor mayor.

## 4 · Los nodos, con lo que cada uno tiene detrás

| nodo candidato | evidencia | estatus |
|---|---|---|
| **conmensurabilidad crear/destruir** | favor inicial 0,024 vs 0,081; toda muerte en 0 pasos | **medido · el nodo principal** |
| establecimiento de la primera distinción | bimodalidad total, 6/16 con 1 estado | **medido** |
| estabilidad de hipótesis | subsumido por el anterior: nada llega a ser inestable, muere al nacer | reformulado |
| control de sobrefragmentación | sólo existe en las ganadoras (12–57 estados) | **no es la causa del fallo** |
| asignación de evidencia | `cells_supported` 515 vs 46, pero es la bimodalidad otra vez | sin evidencia propia |
| persistencia estructural | `survival_mean` \|z\| = 0,75 · `first_split` \|z\| = 1,50 | **sin evidencia** |
| uso de experiencia dirigida | el motor es uniforme; no se ejerció | sin ejercitar |
| presión funcional sobre qué historia importa | `Z` no toca la política en 1.8 | sin ejercitar |

## 5 · Lo que NO se hace con esto

No se ajusta el criterio de split ni el de merge de `LEARNER-18-v1`. Esa versión
está cerrada como insuficiente, y su cierre es lo que da valor a estas medidas.
La conmensurabilidad entre crear y destruir es una **decisión de diseño de una
versión siguiente**, que tendrá que sellarse antes de escribirse, como se selló
la Enmienda 02 — y esta vez con la lección de que un criterio de creación y uno
de destrucción escritos por separado pueden no hablar la misma lengua.

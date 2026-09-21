# Hipergrafo · prerrequisitos de C18

Artefacto **independiente** de si 1.8 pasa o falla su confirmatorio. Registra lo
que el experimento enseñó sobre la capacidad, no sobre el veredicto.

**Este documento no afirma posición developmental.** Que 1.8 se haya construido
después de 1.7 es cronología del proyecto, no ontogenia del ser.

---

## CAPACIDAD

```
refinamiento predictivo sensoriomotor
    adquirir de la propia historia (O, A) una organización interna Z que mejore
    P(O'|O,A) más allá de C17 continuo y de una retención fija de un tick
```

---

## REQUISITOS OBSERVADOS · medidos, no supuestos

| requisito | evidencia en el experimento |
|---|---|
| historia temporal (`M_16`) | heredada de 1.6; sin ella no hay masa que repartir |
| eferencia | O-HISTORY-ONLY, el mismo mecanismo ciego al comando, pierde por **+0,676** de margen medio en 16/16 vidas |
| routing temporal | el defecto absorbente dio 0 % de transiciones; reparado, 87,5 % |
| discriminación predictiva | criterio prequencial (MDL), sin constante ajustada |
| split | primer refinamiento en el paso **8,5**, idéntico a los cinco presupuestos |
| reversibilidad / merge | **82–88 %** de los splits se revierten; sin merge el censo crece ×3,9–13,9 |
| conservación de evidencia | `Σ_z C_0(o,a,o'\|z) = C_17(o,a,o')`, rtol 1e-9 |
| scoring prequencial | y **separado del avance de estado**: seguir no es aprender |
| prior heredado de C17 | C17-LESION (mismo mecanismo, prior plano) pierde **0,79 nats** |

---

## NO REQUERIDO EN ESTE EXPERIMENTO

```
política dirigida · objetos · coordenadas · mapa · semántica de mundo
```

Medido, no asumido: `I(C;Z\|O)` corregida por nula es el **1,0–1,6 %** de
`H(C|O)`. La capacidad aparece sin que el estado se parezca a la situación
física.

---

## DEPENDENCIAS AÚN HIPOTÉTICAS

```
presión endógena · valor · selección de experiencia · uso activo del estado
```

Con una razón medida para sospechar que la primera importa: el motor es uniforme
por diseño y la trayectoria es la misma pase lo que pase con lo aprendido. Sobre
esa trayectoria la ventaja **es eficiencia muestral y se lava** —`ΔL` cae de
+0,107 a +0,058 cuando el baseline recibe datos suficientes— y **6 de 16 vidas
no ganan**, en las dos rondas de calibración.

Ésta es la conexión con 1.5, que se congeló por «generar experiencia antes de
organizarla». No resuelve si 1.8 va antes o después; da una magnitud a la
pregunta.

---

## HABILIDADES QUE PODRÍA HABILITAR

```
selección de experiencia · memoria contextual · control contingente ·
exploración dirigida
```

Con la reserva de que ninguna está probada aquí: 1.8 no usa `Z` para decidir
nada. Un estado que mejora la predicción y no toca la política es un
prerrequisito plausible de esas cuatro, no una demostración de ninguna.

---

## DÓNDE FALLÓ la v1 · nodo medido

`LEARNER-18-v1` quedó cerrado como insuficiente, y la ingeniería inversa
localizó el fallo: **el criterio que crea una distinción y el que la destruye no
están en la misma escala.** Un split se acepta por cualquier margen —0,02 nats
bastan— y el primer incremento del juicio posterior es de orden 0,17, así que
toda distinción refutada muere en **cero pasos**. Sobrevive la que nace con favor
suficiente para aguantar una observación, no la que tiene evidencia.

Consecuencia medida: en 6 de 16 vidas el organismo termina con **exactamente un
estado** —organización ausente, no mala— mientras el oráculo gana entre +0,20 y
+0,53 sobre esas mismas trayectorias. No hay casos intermedios, y no es propiedad
del mundo: 3 de 16 vidas cambian de signo con el presupuesto.

Detalle en [LEVEL18_INGENIERIA_INVERSA_V1.md](LEVEL18_INGENIERIA_INVERSA_V1.md).

---

## Lo que el experimento aporta al hipergrafo aunque falle

Un hecho con número: **la organización histórica compra eficiencia de
aprendizaje bajo presupuesto acotado, no una ventaja que crezca con los datos.**
Y un techo: ni con la partición verdadera el mecanismo alcanza más del **16 %**
de la ganancia disponible sobre trayectoria no dirigida.

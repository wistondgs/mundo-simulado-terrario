# Transferencia · vecino más próximo sensorimotor en el banco de Nivel 1

**Clasificación: TRANSFERENCIA. No es una replicación.** Fecha: 2026-09-19.

## Qué distingue esto de una réplica

El proyecto mantiene separadas tres operaciones que es fácil confundir, y la
confusión es cara porque cambia qué se puede afirmar al final:

| Operación | Qué se hace | Qué autoriza a decir |
|---|---|---|
| **Replicación** | Reproducir el experimento ajeno tal como se hizo: su estudio, su entorno, su código, su configuración, sus condiciones, sus controles y sus métricas. Terrario no entra. | «Obtuvimos el fenómeno que ellos reportaron.» |
| **Transferencia** | Meter un mecanismo en **nuestro** mundo y medir qué hace aquí. | «Bajo nuestras condiciones, este mecanismo produce esto.» |
| **Comparación** | Contrastar perfiles: qué aprende cada uno, con cuánta experiencia, con qué recursos. | «Aquí difieren, y así.» |

El orden del proyecto es `REPLICAR → VERIFICAR → COMPRENDER → TRANSFERIR →
COMPARAR`. **Este trabajo es el paso 4 y se hizo antes que el 1.** Queda
registrado y aparcado: es utilizable, pero no sostiene ninguna afirmación sobre
lo que otro grupo obtuvo, porque no se reprodujo ningún experimento de nadie.

**Estudio replicado: NINGUNO.** No hay artículo, ni versión de código, ni
conjunto de datos, ni configuración original que se esté reproduciendo aquí.

## Procedencia del mecanismo

```
nombre en el banco     vecino más próximo (externo)
origen metodológico    Explauto (INRIA/FLOWERS)
familia                nearest-neighbor forward sensorimotor model
exploración            random motor babbling
integración            clean-room, desde la descripción algorítmica publicada
código incorporado     NINGUNO — ni ficheros ni fragmentos
licencia de origen     GPLv3 (dato de procedencia; no se copió código, así que
                       no se heredan sus obligaciones)
clasificación          TRANSFERENCIA
```

Explauto es una biblioteca, no un experimento: no tiene un resultado publicado
concreto que se pueda reproducir sin elegir primero artículo, experimento,
versión y configuración. Ésa es, por sí sola, razón suficiente para que esto no
pueda llamarse réplica.

## Lo que sí quedó construido

Un brazo más del banco de Nivel 1, sometido al mismo flujo de experiencia, los
mismos mundos, las mismas semillas y el mismo instrumento que los seres propios.
La única diferencia con ellos es el mecanismo de aprendizaje:

```
el ser propio       experiencia → conteos Beta-Bernoulli (estadística suficiente)
el carril externo   experiencia → ejemplares, voto por vecino más próximo
```

### Dos decisiones de protocolo, declaradas

1. **Empates.** Con ocho bits binarios los empates a distancia mínima son la
   norma. Votan **todos** los ejemplares a distancia mínima, no uno elegido: si
   votara uno, el resultado dependería del orden de inserción.
2. **Salida probabilística.** `q` = fracción de `MOVED` entre los vecinos
   mínimos. Un vecino más próximo devuelve de suyo una etiqueta dura, y contra
   Brier eso mezclaría el mecanismo de aprendizaje con la forma de la salida.
   Sin ejemplares, `q = 0.5` exacto: ni prior Beta ni suavizado de Laplace. La
   etiqueta dura se conserva aparte, como métrica secundaria de acierto.

### Consecuencia medida de no suavizar

Sin ejemplares el Brier es exactamente `0.25` en las 8 semillas medidas, igual
que el ser propio: ambos parten de la misma ignorancia. Con **un** ejemplar el
carril externo salta a `0.486` de media (rango `0.393`–`0.613`), **peor que la
ignorancia analítica en 8 de 8 semillas**: la única respuesta posible es la
etiqueta dura de ese ejemplar, y acierta la mitad de las veces. Se recupera al
acumular. No es un defecto de la implementación: es lo que significa no darle un
prior a un método que no lo tiene, y la curva lo hace visible en vez de
esconderlo. Medido sobre la configuración reducida (8 disposiciones × 32 pasos).

## Coste, que es parte del resultado

El barrido es lineal sobre toda la memoria: sin índice, sin árbol, sin hash, sin
poda. El coste por consulta es `O(|M|)` y es uno de los números que el
experimento quiere medir. El barrido corre en numpy en lugar de en un bucle de
Python: eso cambia la constante y no el orden — sin ello una campaña de 8.192
ejemplares y 16.384 consultas no termina en tiempo útil y no habría nada que
medir.

## Aislamiento

Añadir el brazo no movió ningún número de los brazos que ya estaban. Verificado
contra los valores medidos en `cc562e0` antes del cambio, y fijado por
`test_adding_the_external_arm_moved_no_number_of_any_previous_arm`.

## Qué haría falta para que esto fuera una réplica

Elegir artículo, experimento, versión de código, versión de datos, entorno,
dependencias, protocolo, condiciones, hiperparámetros, comandos de ejecución y
métricas; correrlo como está; y declarar **toda** desviación respecto del
original. Nada de eso se hizo aquí, y por eso este documento empieza diciendo lo
que no es.

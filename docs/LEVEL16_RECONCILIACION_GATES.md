# `LEVEL1.6` · cierre de deuda del verificador

**Fecha:** 2026-09-20 · posterior a la campaña · **ningún resultado alterado**
**Oráculo:** no tocado · **Vidas:** no vueltas a correr

```
replay contra la tabla committeada en 0503874    filas que difieren: 0 de 16
IC95 inferior +0.6805 · veredicto POSITIVO · gates 12/12 · causal 16/16
suite 89 contratos verdes
```

---

## 0 · Nota sobre «artefactos congelados»

**No existía archivo de artefactos.** La campaña era reproducible por
determinismo, no por archivo, y las 16 huellas de trayectoria nunca se
commitearon —el informe sólo guarda una. Así que el verificador se ejecutó sobre
un **replay determinista validado contra la tabla committeada** del informe
`0503874`, celda por celda, con tolerancia `5e-5`. Cero diferencias.

Queda como deuda de backlog: **persistir los artefactos confirmatorios**, para que
«ejecutar el verificador sobre lo congelado» sea una lectura y no una
reconstrucción.

## 1 · AN-1 · cerrada, y dónde

`SHUFFLE_NOT_DESTRUCTIVE` **no se añade como gate número trece.** Es la
precondición de `L16-8`: «FULL supera a TEMPORAL-SHUFFLED» no afirma nada si el
comparador conserva la temporalidad. La comparación y la validez del comparador se
aprueban o caen juntas, y el oráculo conserva sus doce gates.

```
antes   L16-8: IC95 inferior > 0
ahora   L16-8: IC95 inferior > 0  Y  baraja destructiva en las N vidas
                                  Y  existe auditoría para las N vidas
```

La tercera condición importa: sin ella el gate se aprobaría **por omisión** cuando
nadie le pasara la auditoría. Tiene su propia fixture.

## 2 · AN-12 · un defecto que la reparación destapó, y su corrección

**Reportado antes de corregirlo.** Al conectar el gate, dos vidas fallaron a
`T = 512` con razones 0.520 y 0.512 contra mi umbral fijo `< 0.5`. El umbral
estaba escrito a mano y **depende del tamaño de muestra** —la misma lección de
1.2, repetida por mí.

Distribución nula medida, con permutaciones **honestas** de la propia trayectoria:

```
T       razón de una baraja honesta        ¿sirve 0.5?
        media     p95      máx
 512    0.3803  0.5216  0.5732             NO · una baraja honesta lo supera
1024    0.2476  0.3282  0.3551             sí
4096    0.1065  0.1397  0.1534             sí, con margen 3x
```

**Corrección:** el criterio deja de ser una fracción inventada y pasa a ser la
distribución nula de la propia trayectoria, `null_mean + 4 sd`, generada con ocho
permutaciones de referencia en flujos `[semilla, 3+k]` —que no tocan ni la
trayectoria ni la baraja del brazo. Se autocalibra a cualquier presupuesto.

**Efecto sobre resultados: ninguno.**

```
T        destructivas   gates   veredicto   IC95 inferior
 512         16/16      12/12   POSITIVO      +0.5989
1024         16/16      12/12   POSITIVO      +0.6422
4096         16/16      12/12   POSITIVO      +0.6805      ← idéntico al confirmatorio
```

Y sigue mordiendo donde debe: una permutación identidad da distancia `0.5113`
contra una tolerancia de `0.1714` —fuera por un factor de tres.

## 3 · AN-5 · reconciliación gate por gate

| gate | afirmación que protege | fixture prometida (§13) | fixture real | causa exacta del fallo | estado |
|---|---|---|---|---|---|
| **L16-0** | ninguna capacidad posterior en el árbol | importar una capacidad de 1.4 | directorio `level13` junto al paquete | `PACKAGE.parent/'level13'` existe | **CUMPLIDA** |
| **L16-1** | todo acto salió de la fuente del ser | cinta externa de acciones | `motor_emitted = 0` con pasos vividos · y un segundo módulo que llama `.integers` | emisiones ≠ pasos · emisores ≠ `{motor.py}` | **CUMPLIDA Y AMPLIADA** |
| **L16-2** | el azar motor se serializa | omitir el RNG al serializar | `state()` devuelve sólo `{emitted}` | `restore` levanta `MotorContractError` | **CUMPLIDA** |
| **L16-3** | sin target, recompensa, novedad ni valor | campo reward ficticio | cinco fuentes, una por forma de señal · **y tres inocentes que deben PASAR** | identificador prohibido en el AST | **CUMPLIDA Y AMPLIADA** |
| **L16-4** | A1 no ve acto, eferencia, posición ni Δ | entregar `a_t` o `changed` al modelo | `temporal.py` fabricado que nombra `direction` · más la aduana en ejecución | identificador prohibido · `TemporalContractError` | **CUMPLIDA** |
| **L16-5** | paridad de trayectoria entre brazos | *cambiar una acción de un brazo* | `life.py` fabricado que importa `TemporalModel` | el cuerpo podría leer la tabla | **RECLASIFICADA · redundancia lógica** |
| **L16-6** | había algo que aprender | *mundo estático* | `teachability` forzada a 0 | nats disponibles ≤ 0.05 | **RECLASIFICADA · excluida aguas arriba** |
| **L16-7** | FULL mejora sobre su propio pasado | congelar FULL | FULL congelado **antes** de contar, con pérdidas reales · más el caso sintético por vida | `full == frozen` ⇒ ganancia cero | **CUMPLIDA · reparada hoy** |
| **L16-8** | FULL supera a un SHUFFLED que de verdad baraja | conservar parejas reales en el barajado | permutación identidad · y ausencia de auditoría | distancia fuera de la tolerancia nula · sin auditoría no se aprueba | **CUMPLIDA · reparada hoy (AN-1)** |
| **L16-9** | la competencia reside en el estado | borrar `M_T` sin caída de competencia | intervención sobre un modelo sin estado aprendido | ablacionada = aprendida | **CUMPLIDA** |
| **L16-10** | la evaluación es pasiva | contador incrementado por el evaluador | `log_loss` instrumentada para actualizar | huella o `updates` se mueven | **CUMPLIDA** |
| **L16-11** | BITCOUNT no explica el primario | *(no prometida)* | `probability` inyectada en el control | el primario acepta al control | **AÑADIDA sobre lo prometido** |

### Las dos reclasificaciones, con su demostración

**L16-5 · redundancia lógica.** «Cambiar una acción de un brazo» es imposible: los
brazos reciben una `Life` **ya vivida** y ninguno produce actos. Verificado por
AST: `arms.py` no nombra `next`, `EndogenousMotor`, `motor_stream`, `step`,
`Direction` ni `integers`. La paridad no es un invariante que un brazo pueda
romper —es consecuencia de que exista una sola trayectoria. Se ataca en su lugar
la única precondición que sí puede caer: que el cuerpo llegue a leer la tabla.

**L16-6 · excluida aguas arriba.** Un mundo estático es `N-MUNDO` por el predicado
estructural, y la regla de consumo lo descarta **antes** de vivirlo, así que no
puede llegar a un gate. Verificado construyendo uno a mano: `is_nonworld` lo marca.
La fixture real inyecta la condición directamente en el gate, que es el único
punto donde puede existir.

**No se inventó ninguna fixture para conservar el número.** Diez cumplidas —dos
reparadas hoy—, dos reclasificadas con demostración, una añadida sobre lo
prometido.

## 4 · Qué falsifica realmente cada gate

```
L16-0   que exista en el disco cualquier paquete de un decimal posterior
L16-1   que el número de actos emitidos por el ser difiera de los pasos vividos,
        o que exista más de un emisor de actos en el paquete
L16-2   que una fotografía del motor no baste para reproducir sus actos futuros
L16-3   que el paquete NOMBRE --como identificador, no en prosa-- una señal de
        recompensa, novedad, valor u objetivo
L16-4   que el aprendiz nombre o acepte acto, eferencia, posición o etiqueta de cambio
L16-5   que el cuerpo pueda leer la tabla, o que la trayectoria no se reproduzca
L16-6   que el mundo no ofrezca nats por encima del prior
L16-7   que alguna vida no mejore sobre su propio estado inicial
L16-8   que el intervalo toque el cero, que la baraja conserve temporalidad,
        o que no exista auditoría de la baraja
L16-9   que ablacionar el estado no cueste competencia, o restaurarlo no la devuelva
L16-10  que evaluar mueva la huella o la cuenta de actualizaciones
L16-11  que el control de un parámetro pueda puntuarse en el endpoint primario
```

## 5 · Veredicto del cierre de deuda

```
AN-1    CERRADA    · dentro de L16-8, con fixture negativa por la vía real
AN-5    CERRADA    · reconciliada gate por gate; dos redundancias declaradas
AN-12   CERRADA    · umbral fijo sustituido por la nula de la propia trayectoria
```

Ninguna vida cambió de veredicto. Ninguna cifra confirmatoria se movió. El oráculo
sigue intacto y las vidas no se volvieron a correr.

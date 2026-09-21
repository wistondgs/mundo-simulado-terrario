# Enmienda 03 al oráculo de `LEVEL1.6` · criterio de clasificación de una vida

**Fecha:** 2026-09-20
**Oráculo enmendado:** `9b0d39b` §15
**Estado en que se emite:** suite contractual en verde, campaña confirmatoria **no corrida**
**Motivo:** §15 nombra seis categorías y no da criterio para asignar ninguna.

Aditiva. El oráculo no se edita.

---

## 1 · El hueco

§15 enumera `INVÁLIDO`, `N-MUNDO`, `N-EXPERIENCIA`, `N-PLASTICIDAD`,
`NEGATIVO VERDADERO` y `POSITIVO`, y dice que el informe final debe poder
clasificar cada vida «sin rescatar corridas a posteriori». Sin criterio escrito,
la clasificación se haría mirando los números, que es justo el rescate que la
frase prohíbe.

## 2 · Las tres magnitudes

Todas se leen sobre el **mismo banco POST inmutable**:

```
disponible  =  log 16  -  L(K-SOMBRA)        nats que este mundo puede enseñar
logrado     =  L(FROZEN) - L(FULL)           nats que el ser efectivamente ganó
ventaja     =  L(SHUFFLED) - L(FULL)         nats atribuibles a la temporalidad
```

Más el estado del mecanismo (`updates`, huella `M_T` frente a `M_0`) y el
veredicto de la intervención causal.

## 3 · El criterio, en orden

```
1.  updates == 0  ó  huella(M_T) == huella(M_0)      -> N-PLASTICIDAD
2.  disponible <= 0.05 nats                          -> N-EXPERIENCIA
3.  logrado < 0.25 * disponible                      -> N-EXPERIENCIA
4.  logrado > 0  y  ventaja > 0  y  causal           -> POSITIVO
5.  en cualquier otro caso                           -> NEGATIVO VERDADERO
```

`INVÁLIDO` no se asigna por vida: es un fallo de gate y anula la campaña entera.
`N-MUNDO` tampoco: se decide antes de vivir (Enmienda 01 §3) y esas semillas no
llegan a este punto.

## 4 · De dónde salen los dos números

Ninguno se ajustó a un resultado, porque no hay resultado todavía.

`0.05 nats` es el umbral por debajo del cual el mundo, medido con el cálculo
exacto, no ofrece ventaja apreciable sobre predecir uniforme: `exp(0.05) = 1.05`,
un 5 % de verosimilitud. Por debajo de eso, un nulo en A1 no dice nada del
mecanismo y la vida no debe contarse en su contra.

`0.25` es la fracción de lo disponible por debajo de la cual se considera que la
trayectoria, y no el mecanismo, fue el cuello de botella. Es un cuarto: una
elección declarada, no derivada. Se declara porque el orden de las reglas la hace
consecuente --si la trayectoria capturó al menos un cuarto de lo que había, el
resultado se juzga por mérito en los pasos 4 y 5.

## 5 · La asimetría deliberada

`N-EXPERIENCIA` es **evidencia negativa sobre S0**, no sobre A1: dice que la
política motora uniforme no llevó al ser por donde había que ir. Por eso separarla
de `NEGATIVO VERDADERO` importa, y por eso no se reemplaza la semilla: la vida
corrió, cuenta en el denominador, y su lectura es sobre el sustrato.

## 6 · Alcance

Fija la lectura del resultado. **No** toca el endpoint primario, los brazos, los
gates, el criterio primario de campaña ni la afirmación máxima autorizada.

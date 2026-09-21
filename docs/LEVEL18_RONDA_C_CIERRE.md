# Nivel 1.8 · Ronda C — ningún presupuesto seleccionable

```
LEARNER            conforme con la Enmienda 02, desambiguada por la Enmienda 06
REGLA              v2, IMPORTADA de la Ronda B · no reescrita
VENTANA            200000011…200000027 · virgen · Enmienda 07
RESULTADO          BUDGET SELECTION = NONE
CLÁUSULA           Enmienda 04 §6 · se deja de modificar la estadística
CONFIRMATORIO      180000011…180000074 · CERRADO, intacto
```

---

## 1 · La tabla

| T | L(C17) | L(FD1) | L(C18) | L(ORACLE) | media(m) | **LCB95(m)** | gana | ΔL/0,3427 | LCB95(o) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 | 0,9869 | 0,9814 | 0,9872 | 0,8624 | −0,0058 | −0,0080 | 2/16 | −0,001 | +0,1058 |
| 256 | 0,9522 | 0,9330 | 0,9493 | 0,5989 | −0,0163 | −0,0241 | 2/16 | 0,009 | +0,3149 |
| 1024 | 0,8455 | 0,7995 | 0,7966 | 0,2621 | +0,0029 | −0,0483 | 7/16 | 0,143 | +0,5284 |
| 4096 | 0,6440 | 0,5878 | 0,5763 | 0,0842 | +0,0115 | −0,0322 | 9/16 | 0,198 | +0,5037 |
| 16384 | 0,4483 | 0,4195 | 0,4019 | 0,0224 | +0,0176 | **−0,0055** | 10/16 | 0,135 | +0,3698 |

`(b)` se cumple en los cinco. **`(c)` se cumple en los cinco**, y eso importa: la
suficiencia de experiencia se mide ahora con el oráculo sobre las mismas
trayectorias, y el oráculo **sí** puede explotarlas —hasta `LCB95(o) = +0,53`.

**La cobertura no es el cuello de botella. El mecanismo lo es.**

---

## 2 · Qué se reparó antes de medir, y qué efecto tuvo

El learner no ejecutaba lo que la Enmienda 02 selló: al re-separar un estado con
un split abierto, sobrescribía el favor acumulado y dejaba a los hijos previos
huérfanos —fuera del alcance de merge para siempre, contra §3.3.

```
huérfanos por vida (T=16384)   antes 0–4 de 7 estados vivos   →  ahora 0
localización                   5 vidas sin re-split, bit a bit idénticas
mutantes                       reiniciar el favor mata R1 · reemplazar hijos mata R2
```

El learner conforme **predice algo peor** que el defectuoso, y de forma
consistente: sobre la propia ventana de la Ronda B, `LCB95(m)` pasaba de +0,0020
a −0,0005. La Ronda B quedó por eso invalidada para selección, y su `T`=16384 no
se rescata.

---

## 3 · El veredicto

```
LEARNER-18-v1 = INSUFICIENTE
```

No «1.8 es falso» ni «la capacidad no existe». Lo que los datos dicen es más
estrecho y más útil:

> La capacidad tiene señal y es expresable, pero **este mecanismo no produce una
> ventaja suficientemente estable entre vidas** bajo el contrato estadístico
> seleccionado.

Y lo que queda demostrado en el camino:

| | |
|---|---|
| el oráculo demuestra **posibilidad** | `LCB95(o)` hasta +0,53 |
| la historia **contiene** información | FD1 bate a C17 en los cinco peldaños |
| FD1 **no la agota** | media(m) > 0 desde `T`=1024 |
| el learner **captura una parte** | `ΔL/0,3427` hasta 0,198 |
| lo que falta es **estabilidad** | 10/16 vidas en el mejor peldaño |

---

## 4 · Lo que NO se hace ahora

No hay v3 estadística. No se amplía `N` porque «casi pasa». No se escoge 4096.
No se cambia el `LCB`, ni el comparador, ni el endpoint. No se excluye ninguna
vida. No se abren otras semillas confirmatorias. No se ajusta el split.

Se vuelve al **mecanismo**, con toda la ingeniería inversa acumulada, a preguntar
qué subcapacidad falta: estabilidad de hipótesis, discriminación, control de
complejidad, persistencia, o generación selectiva de experiencia.

Esa pregunta es exactamente la que el hipergrafo tiene que contestar, y ahora
llega con números en vez de con intuición.

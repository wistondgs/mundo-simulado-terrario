# Nivel 1.8 · Enmienda 07 — ventana de calibración para la Ronda C

**Prospectiva.** Se sella antes de generar una sola vida con el learner conforme.

---

## 1 · Por qué hace falta ventana nueva

Las 16 vidas `190000011…190000027` de la Ronda B quedan consumidas: sobre ellas
se ha observado el learner defectuoso, el learner conforme **y el signo del
`LCB`**. Reutilizarlas haría que la regla se aplicase a un dato del que ya se
conoce la respuesta.

```
RONDA A   150000011…150000026   diagnóstica · regla v1 · ningún T
RONDA B   190000011…190000027   diagnóstica · regla v2 · T=16384 INVALIDADO
RONDA C   200000011…200000027   ← ésta · regla v2 INTACTA · learner conforme
```

## 2 · Verificación de virginidad

```
prefijos '20000001' y '20000002'   0 commits en toda la historia
                                   0 ficheros en los seis árboles vivos
'20000003'                         2 commits, y son `20000003` suelto y el
                                   fragmento del float 200000032782555 · ninguna
                                   semilla de la ventana
mundo inválido                     200000013 · 16 vidas válidas consumen
                                   200000011…200000027, dentro de los prefijos limpios
```

Distinta de `150…`, de `190…` y de `180000011…180000074`.

## 3 · Lo único que cambia respecto de la Ronda B

```
learner    ahora conforme con la Enmienda 02, desambiguada por la Enmienda 06
```

Idénticos: escalera `64·256·1024·4096` + agotamiento en 16384, `N`=16, los seis
brazos, el endpoint, el cálculo pareado, `LCB95` con la constante 1.96 ya sellada
en §7 línea 158, la condición de saturación `ΔL/0.3427 < 0.90`, la condición de
cobertura por oráculo y la cláusula de parada de la Enmienda 04 §6.

## 4 · Las tres salidas legítimas

```
A  ningún T        → BUDGET SELECTION = NONE · se activa la parada · no hay v3
                     estadística, no se amplía N, no se busca otro rango:
                     se vuelve al MECANISMO
B  algún T         → el PRIMERO que cumpla, aunque no sea 16384 y aunque otro
                     tenga mayor media · se sella y se va a preconfirmatorio
C  otro defecto    → parar · no interpretar ciencia hasta saber si la corrida vale
```

No se espera ninguna. **`180000011…180000074` sigue cerrado.**

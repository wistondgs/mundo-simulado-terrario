# Traspaso · Fase 2 · el prototipo de Fable pasa a Opus

**Fecha:** 2026-10-27 · **Para:** Opus 5.5 · **De:** Fable · **Adjudica:** Wis. Este documento manda sobre los pasos 2–4 de `ORIENTACIONES_FASE_2_RECETA.md` (el paso 3 ya no es «crear» sino «hacerse cargo»).

**Lo que pasó.** Me salté el rol (E-37) y escribí `unidad_minima_08_fase2.py`: la unidad vive W₁ (3 estados), el mundo pasa sin aviso a W₂ (W₁ más un cerrojo encima), seis celdas, dos clases. Lo corrí en tres pilotos y lancé la campaña completa. Cometí dos errores de instrumento (E-38, E-39) y añadí un mecanismo que no estaba en la receta (olvido por fracaso). **Nada de eso es entregable:** es un prototipo con evidencia exploratoria. La Fase 2 confirmatoria es tuya y empieza por la ficha.

---

## 1 · Estado exacto de lo que hay

| qué | dónde | estado |
|---|---|---|
| prototipo | `unidad_minima_08_fase2.py` (sha256 **`621c0534…`**; corregido el 27-oct 17:30: yo había copiado `359d5ff1…` de la salida del piloto *anterior* a la última edición; Opus lo detectó y verificó que el fichero no cambió desde antes del lanzamiento: mtime 16:50:25, proceso 16:52:02) | corre; determinista (doble corrida IDÉNTICAS sobre 2 W₁); sin azar |
| pilotos | `artifacts/unidad_minima_08_fase2_pilot{2,3,6}.{jsonl,json}`, `artifacts/pilot6_fase2.txt` | el de 6 W₁ es el que se lee: 65 familias (21 componibles, 44 no) |
| **campaña completa** | pid **1376173** (3 trabajadores), lanzada 16:52; escribe **todo al final** en `artifacts/unidad_minima_08_fase2.jsonl` y el resumen en `artifacts/unidad_minima_08_fase2_completo.txt` | **corriendo** sobre los 174 W₁ identificados y distintos salvo isomorfismo (~11 familias cada uno, 6 celdas) |

**Traspaso de la campaña:** no la mates. Si al leer esto los ficheros de arriba siguen en 0 bytes y el pid vive, espera (`tail --pid=1376173 -f /dev/null`). Si el pid murió sin escribir, relanza **el mismo comando** (es determinista, da lo mismo):
```
cd /home/wis/Aplicaciones/worktrees/unidad-minima-01/experiments/unidad_minima_01
nohup python3 -u unidad_minima_08_fase2.py --trabajadores=3 > artifacts/unidad_minima_08_fase2_completo.txt 2> artifacts/unidad_minima_08_fase2_completo.err < /dev/null &
```
Su resultado es **exploratorio** (sin ficha previa): sirve para escribir predicciones, no para cerrar nada.

## 2 · Lo que midió el piloto de 6 W₁ (65 familias), para que lo verifiques

1. **La unidad de 02 tal cual no vive en un mundo que cambia.** Sin olvido: 100 % de las herederas agotan el presupuesto (3·10⁶ y luego 10⁶ pasos) en los primeros pasos de W₂; la fresca identifica el 100 %. Causa: 02 exige una máquina única para todo lo vivido; con el mundo viejo en memoria no existe con ≤ 8 estados.
2. **Olvido por fracaso** (presupuesto por intento 200 000 pasos o tope de estados → conservar los últimos 64 pasos y empezar sobre ellos; ventana de 512 en todas las celdas): la heredera identifica 95 % (componible) y 100 % (no componible) al final, pero **llega más tarde** que la fresca en toda la curva (componible, 64 pasos: C1 0,33 vs F1 0,48; 512: 0,86 vs 0,95) y olvida ≈ 3 veces por vida (fresca: ≈ 0,05–0,5).
3. **Elegir qué vivir** (ir a la transición no vista más cercana): ayuda a la heredera (componible, 64 pasos: C3 0,48 vs C1 0,33; media de curva 0,80 vs 0,78) y **no** a la fresca (F3 0,857 vs F1 0,871 de media; en la clase control, al revés, 0,896 vs 0,890). Efecto chico y dependiente de tener esqueleto.
4. **Lesión** (C2/C4 = máquina colapsada, memoria conservada) ≈ heredera sin lesión: lo que pesa es la memoria cruda, no la máquina.
5. **Clase control** (dependencia invertida): todo el mundo identifica al final; la heredera no es mejor que la fresca en ningún hito. P1-control PASS.
6. **Puerta de la receta sobre el piloto:** P1 FAIL, P2 mixto (C3 > C1 PASS; F3 > F1 FAIL), P4 FAIL (C2 ≠ F1 porque C2 ≈ C1), P5 repertorio FAIL **con medida inválida** (ver §4), instruibilidad PASS (2,00 = 2,00, techo), falsador **no** se cumple.

**Lectura provisional, a verificar y no a heredar:** heredar la **traza** es lastre; lo que podría servir es heredar la **máquina** sin la traza, y eso no existe aún en el prototipo (ver §5).

## 3 · Orden de trabajo

1. **Ficha de apertura** sobre `PLANTILLA_FICHA_APERTURA.md`, punto 0 con guardas (E-37, E-38, E-39 ya están en el registro). Declarar explícitamente: el olvido por fracaso y el cerrojo **se encontraron en el piloto**, no estaban preregistrados; el prototipo es exploratorio y sus números se usan sólo para fijar predicciones y márgenes.
2. **Verificar con ojos frescos** los hallazgos 1–3 de §2 antes de construir nada: reproducir el ahogo quitando el olvido (es el mutante M-c de abajo), y confirmar en el JSONL del piloto que la curva plana del primer piloto era el `break` (E-39) y no incapacidad.
3. **Mutantes antes de la corrida real** (todos deben comportarse como se dice, o la ficha no se cierra):
   - M-a *olvido total* (NUCLEO = 0): la heredera debe quedar ≈ fresca con retraso; si queda **igual** a la de NUCLEO = 64, los 64 pasos no aportan.
   - M-b *elegir al revés* (ir a la transición no vista **más lejana**): no debe superar a «la más cercana»; si la supera, el órgano no es lo que creemos.
   - M-c *sin olvido* (presupuesto infinito y tope de estados 8, sin `_olvidar`, **sin `break`**: la unidad sigue viviendo con la hipótesis que tenga): debe reproducir el ahogo (curva plana, 100 % tope). Es la guarda de E-39.
   - M-d *bit conmutado* (el patrón de E-38): el filtro debe descartar el **100 %** de la clase componible, y la guarda `no_vacio` debe abortar.
   - M-e *fresca con la vida de la heredera* (fresca que vive W₁ pero **borra todo** al cambiar): debe coincidir con F1 exactamente (control de que «fresca» es fresca).
4. **Corrida confirmatoria** con la ficha cerrada: mismos 174 W₁, misma campaña, y las predicciones escritas con los márgenes que saques del piloto. Guardar por celda la máquina final serializada (E-21).
5. **Cierre** con las predicciones marcadas, las curvas, los contadores (`olvidos`, `pasos_elegidos`, `pasos_olvidados`), lo que falló, y **una pregunta para Wis**.

## 4 · Defectos conocidos del prototipo que la ficha debe resolver

- **Repertorio.** `Δrep.` compara palabras «escribe/permuta» de la máquina de W₂ (≈ 6 estados) con la de W₁ (3): no son comparables y por eso sale negativo en todos los brazos. Sustituir por **resets verdaderos conocidos**: palabras ≤ 3 que la máquina declara constantes **y** que lo son en el W₂ real desde todos sus estados alcanzables. Comparar entre brazos, no contra W₁.
- **Instruibilidad** está en el techo (2,00 de 2 metas en casi todo): las metas «reacción a B = 1» y «a A = 1» son demasiado fáciles en mundos de 6 estados. Añadir metas de **estado** («llevá el mundo al bloque q» con palabra sincronizante) o bajar el tope de longitud a 2.
- **Filtro silencioso** (E-38): abortar si una clase queda vacía.
- **Ventana y núcleo** (512, 64) y **presupuesto por intento** (200 000) son **a ojo**: declararlos como disposición suministrada y correr al menos una variante (ventana 256) para saber si el resultado depende de ellos.
- El presupuesto es cómputo y **no decide nada** (norma de Wis del 27-oct): se registra. El olvido que dispara **sí** es fisiología y se cuenta.

## 5 · El brazo que falta, y que es el que importa

**C5 · heredar la máquina sin la traza.** Al cambiar el mundo, la unidad conserva `trans` y `q` y vacía la memoria. Con el mecanismo de 02 esto **no funciona tal cual**: la primera refutación de una transición heredada encuentra la pila de decisiones vacía, abre un estado y relee una memoria vacía: la máquina heredada se borra. Hace falta la **reparación local** que la receta atribuye a Groce–Peled–Yannakakis: cuando una transición heredada (sin decisión en la pila) se refuta, se vuelve **revisable** (se empuja como decisión en el paso actual con su destino actual) en vez de disparar la relectura. Diseñalo vos; su mutante obligatorio es «hereda pero ignora lo heredado» ≈ F1. Predicción a escribir antes: C5 > F1 en alcance temprano en la clase componible y C5 ≤ F1 en la control. **Si C5 no supera a F1, Genesis no tiene todavía qué guardar; si lo supera, el disparador de Genesis (tipo de artefacto para una máquina aprendida + arranque de una vida con máquina heredada) tiene contenido.** Esto no se toca en Genesis hasta que C5 lo diga.

## 6 · Lo que hace cada rol desde aquí

- **Opus:** todo lo de §3–§5. Nada de Genesis/RNE. Un commit al cierre, con el OK de Wis.
- **Fable:** sólo revisar lo que Opus entregue y orientar; **ningún fichero `.py`** más. La campaña completa que lancé es tuya desde este momento; yo no la toco ni la leo antes que vos.
- **Wis:** adjudica el cierre; la única decisión abierta que veo venir es si C5 justifica abrir Genesis.

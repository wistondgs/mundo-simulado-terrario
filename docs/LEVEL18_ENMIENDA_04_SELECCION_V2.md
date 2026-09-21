# Nivel 1.8 · Enmienda 04 — selección de presupuesto, versión 2

**Prospectiva.** Se sella ANTES de generar una sola vida nueva. Corrige dos
condiciones de §10 que la Ronda A demostró mal escritas, sin tocar el endpoint,
sin reinterpretar lo ya fallado y sin reutilizar las vidas que fallaron.

---

## 1. Lo que la Ronda A dejó cerrado, y no se reabre

```
RONDA A    150000011…150000026 · escalera 64·256·1024·4096 + 16384
RESULTADO  ningún T seleccionado
(a)        falla en los CINCO peldaños · tamaño de efecto máximo 0,67 de 2,00
(b)        se cumple en los cinco
(c)        operacionalización defectuosa · falla en cuatro de cinco
```

**«≥ 2 sd entre vidas» se lee como desviación estándar.** Adjudicado tras ver el
resultado y en su contra. La regla resultó ser un requisito de tamaño de efecto
pareado `d ≥ 2`. Es extraordinariamente fuerte; el protocolo lo exigió y no se
cumplió. **4096 no se rescata.**

---

## 2. Por qué (c) estaba mal, y qué mide la nueva

FIXED-DEPTH-1 sostiene 256 celdas y llega a hambre exactamente 0. C18 construye
una representación variable de ~700. Exigir `hambre(C18) ≤ hambre(FD1)` convierte
«cobertura suficiente» en «ten la densidad de evidencia de una representación
mucho más pequeña». Eso no es cobertura: es **rendimiento del mecanismo**, y si
C18 fragmenta hasta empobrecer sus estados, eso pertenece a su resultado, no a un
confusor externo.

Lo que (c) debe contestar es otra cosa:

> ¿proporcionó la trayectoria suficiente información del mundo como para que la
> capacidad pudiera manifestarse?

Y ya existe el instrumento exacto: **ORACLE-PARTITION**, sobre las mismas
trayectorias. Si ni la partición verdadera puede ganar con esa experiencia, la
exposición es insuficiente. Si el oráculo gana ampliamente y el learner no, el
problema es del learner y no de la cobertura.

---

## 3. Las tres condiciones · versión 2

Sobre los deltas **pareados por vida** —los brazos comparten mundo, cableado,
motor, banco y masa heredada:

```
m_i        = L_POST(FIXED-DEPTH-1)_i − L_POST(C18)_i
o_i        = L_POST(C17-ONLY)_i      − L_POST(ORACLE-PARTITION)_i

(a) v2     LCB95( m )  >  0
(b)        sin cambio:  ΔL / 0.3427  <  0.90
(c) v2     LCB95( o )  >  0                    suficiencia de experiencia

LCB95(x)   = media(x) − 1.96 · sd(x, ddof=1) / √N        ← NO es una elección nueva
```

La forma del intervalo **no se escoge aquí**: es literalmente la que §7 línea 158
del oráculo ya había fijado —«← fijado aquí»— para el endpoint primario,
trasplantada al margen pareado. No se elige entre t, bootstrap, BCa, SE o CI
después de ver datos, porque no se elige nada: se reutiliza la constante sellada.

La escalera `64 · 256 · 1024 · 4096`, su orden ascendente, la cláusula de
agotamiento en 16384 y «empate → el menor T» siguen vigentes de la Enmienda 03.

---

## 4. Declaración de conocimiento contaminante

Honestidad obligatoria, porque no se puede desconocer lo ya visto:

> **Sé que la (a) v2 habría seleccionado `T`=4096 sobre los datos de la Ronda A.**
> Es más permisiva que la regla literal que falló.

Ese conocimiento existe y no se borra. Por eso la (a) v2 **no puede aplicarse a
las vidas que fallaron**, y por eso esta enmienda reserva una ventana nueva. La
protección no es olvidar: es que el dato al que se aplica la regla todavía no
existe.

Si la Ronda B seleccionase 4096, ese hecho deberá leerse sabiendo esto.

---

## 5. Ventana de calibración nueva · verificada virgen

```
RONDA B    190000011 … 190000026    16 vidas
VERIFICADO prefijos '19000001' y '19000002' en 0 de 275 commits de toda la
           historia, y en 0 ficheros de los NUEVE árboles de trabajo vivos
           (las 6 apariciones de '1900000' son fragmentos del float
            190000057220459…, no semillas)
DISTINTA   de 150000011…150000026 (Ronda A) y de 180000011…180000074 (confirmatorio)
```

Las 16 vidas de la Ronda A **no se reutilizan** para aplicar la regla nueva, ni
se mezclan con las de la Ronda B, ni se borran: quedan como calibración previa.

---

## 6. Criterio de parada · sellado ahora para que no se negocie después

```
aparece un T    →  se sella en enmienda pre-confirmatoria y se prepara el
                   confirmatorio: congelación, ensayo general con semillas
                   basura, verify_ledger, y sólo entonces 180000011…
NO aparece      →  SE DEJA DE MODIFICAR LA ESTADÍSTICA.
                   Veredicto: «la señal existe, pero el mecanismo todavía no
                   produce una ventaja suficientemente estable entre vidas para
                   certificar 1.8», y se vuelve a desarrollar el MECANISMO.
```

No hay Ronda C con una tercera regla.

---

## 7. Lo que esta enmienda NO hace

- **No cambia el endpoint.** Sigue siendo `ΔL = L_POST(C17-ONLY) − L_POST(C18)`
  con `CI95_inferior > 0`. Es tentador pasar a área bajo la curva o a complejidad
  muestral ahora que se sabe que el efecto es de eficiencia muestral y no
  monótono — y sería conceptualmente mejor. Cambiar el endpoint **después de ver
  la forma de la curva** es exactamente lo que no se hace. Queda anotado como
  diseño de una caracterización futura de esta capacidad, no de 1.8.
- No toca learner, split, merge, prior, masa, routing, scoring, baseline ni gates.
- No abre ninguna semilla `180…`.

---

## 8. Claim admisible mientras tanto

> C18 adquiere una organización histórica que mejora la **eficiencia predictiva
> dentro de determinados presupuestos de experiencia**.

Con su caracterización causal: DEPTH-1 no lo explica todo; el oráculo demuestra
mucho más potencial disponible; el learner captura una fracción; y la ventaja
**disminuye** cuando el baseline recibe experiencia masiva.

Prohibido: «C18 es universalmente mejor que C17», y todo claim de estado latente,
mapa, posición, objetos o representación espacial.

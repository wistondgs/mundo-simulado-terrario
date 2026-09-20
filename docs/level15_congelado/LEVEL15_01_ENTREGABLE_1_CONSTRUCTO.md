# NIVEL 1.5 — ENTREGABLE 1
## Selección de información bajo capacidad temporal limitada
### Constructo, geometría informacional y prueba de existencia

**Estado:** diseño conceptual; no existe código, carpeta ni rama de Nivel 1.5.

## 1. Pregunta científica

> ¿Puede el organismo aprender qué información conservar cuando no puede conservarla toda?

El contenido disponible antes del intervalo es:

\[
X=(G,P)
\]

con:

\[
G\in\{G_0,G_1,G_2,G_3\},\qquad P\in\{P_0,P_1,P_2,P_3\}.
\]

Hay 16 estados equiprobables y 4 bits de información completa. El canal temporal sólo permite cuatro mensajes distinguibles:

\[
Z\in\{Z_0,Z_1,Z_2,Z_3\},\qquad |Z|=4.
\]

Por tanto el presupuesto temporal es de 2 bits: cabe G completo o P completo, pero no el par completo (G,P).

## 2. Hipótesis diagnósticas

Estas hipótesis NO son acciones disponibles para el organismo. Son regiones diagnósticas del espacio completo de encoders \(f:X\to Z\).

- **H1 — direccional:** conservar G completo.
- **H2 — proximidad:** conservar P completo.
- **H3 — conjunta parcial:** conservar un bit balanceado de G y un bit balanceado de P.

Para H3:

\[
Z_3=(\gamma(G),\pi(P))
\]

con \(\gamma\) y \(\pi\) biparticiones balanceadas de conjuntos de cuatro valores.

## 3. Consultas discriminantes

- \(Q_G\): recuperar G exacto.
- \(Q_P\): recuperar P exacto.
- \(Q_J\): recuperar \(J=(\gamma(G),\pi(P))\).

La consulta sólo aparece después de la retención.

## 4. Matriz exacta de pérdidas

Con error 0/1 y decoder Bayes ideal usado sólo para el análisis del constructo:

| Estrategia | Q_G | Q_P | Q_J |
|---|---:|---:|---:|
| H1 | 0 | 3/4 | 1/2 |
| H2 | 3/4 | 0 | 1/2 |
| H3 | 1/2 | 1/2 | 0 |

Ninguna estrategia domina a las otras en todas las consultas.

## 5. Regímenes estacionarios

- \(R_G\): P(Q_G)=4/5, P(Q_P)=P(Q_J)=1/10.
- \(R_P\): P(Q_P)=4/5, P(Q_G)=P(Q_J)=1/10.
- \(R_J\): P(Q_J)=4/5, P(Q_G)=P(Q_P)=1/10.

No hay cambio de régimen dentro de una vida. La detección de cambio se reserva provisionalmente para Nivel 1.6.

## 6. Óptimos analíticos

\[
L^*(R_G)=1/8,
\]

\[
L^*(R_P)=1/8,
\]

\[
L^*(R_J)=1/10.
\]

H1 alcanza el óptimo de R_G, H2 el de R_P y H3 el de R_J.

## 7. Nueve variantes de H3 — VERIFICADO

Existen exactamente tres biparticiones balanceadas no equivalentes por atributo, ignorando complemento. Por tanto existen:

\[
3\times3=9
\]

pares \((\gamma,\pi)\).

Las nueve variantes son isomorfas por relabeling de G y P y producen exactamente la misma matriz de pérdidas H1/H2/H3. No hay una variante J privilegiada.

## 8. Lema combinatorio — VERIFICADO EXHAUSTIVAMENTE

Para cada celda de memoria z, con \(m_z\) estados, y máximos \(r_z,p_z,j_z\) respecto de G, P y J:

\[
r_z+p_z+j_z\le m_z+4.
\]

Se verificaron exhaustivamente los 65.535 subconjuntos no vacíos del banco de 16 estados: cero violaciones. La cota es ajustada; la holgura mínima es 0, por ejemplo en \(m=3,r=2,p=2,j=3\).

Sumando sobre como máximo cuatro mensajes:

\[
Accuracy_G+Accuracy_P+Accuracy_J\le2.
\]

Por tanto, bajo peso uniforme de las tres consultas:

\[
\bar L\ge1/3.
\]

## 9. Precisión sobre la cota de R_G/R_P

La relajación lineal sola permite \(L\ge0.1\); no basta para cerrar \(1/8\). El paso portante es combinatorio: para alcanzar \(\Sigma r=16\), las celdas deben coincidir con las cuatro filas direccionales; eso fuerza \(\Sigma p=4\) y \(\Sigma j=8\). De ahí se obtiene el óptimo global \(1/8\). Por simetría vale para R_P.

## 10. Encoders estocásticos — VERIFICADO

Cualquier canal estocástico \(W(z|x)\) puede escribirse como mezcla convexa de encoders deterministas. La accuracy Bayes ponderada es convexa en W porque es suma de máximos de funciones lineales. Por Jensen:

\[
F(W)\le \max_f F(D_f).
\]

Por tanto ningún encoder estocástico 16→4 supera al mejor encoder determinista.

## 11. Información de Q_J — VERIFICADO

Para G y P uniformes e independientes y \(J=(\gamma(G),\pi(P))\):

\[
H(J)=2\text{ bits},
\]

\[
H(J|G)=H(J|P)=1\text{ bit},
\]

\[
H(J|G,P)=0,
\]

\[
I(J;G)=I(J;P)=1\text{ bit}.
\]

Esto vale para las nueve variantes.

## 12. Selector ideal vs representación fija

Un selector ideal que aprenda una representación distinta por régimen alcanza:

\[
\bar L_{selector}=\frac{1/8+1/8+1/10}{3}=7/60\approx0.116667.
\]

Cualquier representación fija de dos bits, promediada sobre los tres regímenes, cumple:

\[
\bar L_{fijo}\ge1/3.
\]

La relación mínima es:

\[
\frac{L_{fijo}}{L_{selector}}\ge20/7\approx2.857.
\]

**Conclusión:** existe una elección informacional real y falsable bajo capacidad limitada.

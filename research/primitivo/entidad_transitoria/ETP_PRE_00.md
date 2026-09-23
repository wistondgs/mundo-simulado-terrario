# ETP-PRE-00 · Fundación y disección causal preexperimental

Estado: **diseño y procedencia solamente; NO EXPERIMENT EXECUTED.**

## 1. Research question

¿Existe en A una organización transitoria causalmente identificable? Si fuese
afirmativo, ¿qué mecanismos distintos producen onset, contribución
reconstructiva y terminación? No se pregunta cómo construir un proto-orgánulo.

## 2. Observed phenomenon

La pauta reportada es `perturbación → organización no basal → reconstrucción →
retorno a q*`. Describe una sucesión observada, no un objeto ontológico.

## 3. Scope

Sólo C4 y evidencia heredada. Unidades: coordenadas Booleanas, pasos síncronos,
trayectorias e intervenciones explícitas. DATA, AUX, D, E, L y P son categorías
de implementación, no ontología primitiva.

## 4. Non-goals

No agente, aprendizaje, cognición, memoria semántica, optimización auxiliar ni
continuación APD. No modificar Terrario, Genesis, RNFE, reglas, arquitectura
auxiliar ni resultados cerrados. B no se compila.

## 5. Neutral terminology

«Organización transitoria candidata» nombra una pauta no basal sin entidad
demostrada. «Entidad transitoria primitiva» requiere evidencia futura.
«Proto-orgánulo» nombra sólo H3. «Dinámicamente generado» significa ausente
inicialmente y presente tras iterar; no equivale a «emergente».

## 6. Specimen A

A es C4: cuatro `x`, diecisiete auxiliares `d/e/l/p`, 21 variables, blancos
`(0000,0^17)` y `(1111,0^17)`, `q*=0^17`, sincronía estricta y `d_max<=2`.
Las ecuaciones exactas están en [CONTEXT.md](CONTEXT.md). No hay reloj,
scheduler, etiqueta de blanco ni oráculo persistente.

## 7. Specimen B as frozen contrast

B permanece `COORDINATEWISE_HEADROOM_APD_FEASIBLE`: factibilidad proyectada, no
red auxiliar implementada. No se compila, repara ni utiliza para inferir A.

## 8. Closed inherited results

Se preservan DISCOVERY-00..03, RAAC, RDDA y veredictos APD dentro de su scope.
También P-DATA 8/8, P-FULL 42/42, latencias y SELF_START/SELF_HALT reportados.
Una contradicción se reporta con ambas procedencias; no se sobreescribe.

## 9. RAAC != entityhood

RAAC prueba diferencia causal DATA entre `q_t` y `q*` en algún estado autorizado
alcanzado. No prueba frontera, tamaño, persistencia, unidad, modularidad ni H3.
Es un marcador ACTION a localizar, no definición de entidad.

## 10. Supplied/generated taxonomy

| etiqueta | criterio |
| --- | --- |
| SUPPLIED | topología, funciones, coordenadas, blancos o condiciones colocadas explícitamente por diseño. |
| IMPLICIT_IN_RULES | consecuencia lógica codificada por reglas suministradas. |
| DYNAMICALLY_GENERATED | patrón ausente al inicio que aparece al iterar. |
| TRAJECTORY_CONTINGENT | depende de perturbación o trayectoria realizada. |
| CAUSALLY_NECESSARY | intervenirlo cambia el resultado reconstructivo en contexto y alcance declarados. |
| OBSERVED_ONLY | correlación o coocurrencia sin estatus causal resuelto. |

Ninguna etiqueta equivale a entidad o emergencia.

## 11. H0–H3

| hipótesis | significado operacional | compatible con | discriminación / falsificador limpio | no justificaría |
| --- | --- | --- | --- | --- |
| H0 NO ENTITY | actualizaciones locales; frontera del observador. | cascada feed-forward sin corte estable. | cortes alternativos equivalentes; falla ante unidad robusta y lesionable. | frontera natural, módulo o H3. |
| H1 TRANSIENT CAUSAL MODULE | subconjunto coherente, lesionable y selectivo. | onset y acción separables por corte pequeño. | action cut preservando onset; falla si todo efecto es distribuido. | autonomía o H3. |
| H2 DISTRIBUTED TRANSIENT PROCESS | proceso real sin frontera fija. | cortes espaciotemporales contingentes. | transplantes/cortes temporales; falla ante subconjunto fijo robusto. | módulo fijo o H3. |
| H3 PROTO-ORGANELLE | onset, contribución, terminación endógena y unidad causal. | evidencia H1 más terminación/frontera robusta. | gates y controles; falla si falta alguno limpiamente. | intención, finalidad u otras propiedades. |

Las cuatro hipótesis siguen vivas.

## 12. ONSET

Registrar primer `q!=q*`, variables cambiantes, ascendencia desde `x`
perturbado y respuesta a reparación temprana o inducción sin perturbación DATA.
Sin trazas localizadas, esos detalles son `UNKNOWN`.

## 13. MAINTENANCE

Por variable no basal: soporte, regeneración tras retirada, dependencia de daño
y SCC interno. Separar feed-forward de recurrente. Actividad prolongada no
prueba mantenimiento autónomo.

## 14. ACTION / RECONSTRUCTION

Hay contribución reconstructiva cuando intervenir componente/evento cambia que
la trayectoria alcance el blanco completo correcto, con contexto fijado. Separar
`DIRECT_DATA_EFFECT` de `INDIRECT_RECONSTRUCTIVE_EFFECT`; disminuir Hamming un
paso no es requisito. Localizar primer RAAC, aristas `q→x`, contribuyentes y un
corte que preserve onset pero elimine reconstrucción.

## 15. TARGET SELECTION

Las bolas Hamming-1 de `0000` y `1111` son disjuntas: P-DATA contiene
información suficiente para identificar centro. Esto es
`INFORMATION_AVAILABLE`, no `INFORMATION_USED_CAUSALLY`. Dónde se usa
causalmente la dirección correctiva sigue por probar.

## 16. TERMINATION

Comparar T0 recomputación simple; T1 pérdida de soporte; T2 acción destruye
disparador; T3 reset explícito; T4 decaimiento autónomo; T5 atractor; T6
combinación. La cadena sugerida P→x corregida→D/E cero→L se lava→q* es hipótesis
causal, no veredicto.

## 17. Existing evidence

| fuente / población | evidencia usable | informa | no establece |
| --- | --- | --- | --- |
| P-DATA NATURAL_PDATA | 8/8; DATA ~t4; full t7 | cronología y reconstrucción reportadas | frontera o necesidad específica. |
| P-FULL NATURAL_PFULL | 42/42; máximo t9; D/E/L/P | direcciones candidatas | lesión de regla o entidad. |
| E/P freeze, `p=e`, D03, restauración faseada | controles reportados, trazas no localizadas | catálogo a recuperar | números/resultados nuevos. |
| RAAC | diferencia causal reportada | ACTION a localizar | entityhood. |
| complemento/asimetrías | hechos reportados | diseño de robustez | invariancia de entidad. |

D/E/L/P en P-FULL son **state perturbations**, no lesiones.

## 18. Missing evidence

Faltan fuentes para trazas completas P-DATA/P-FULL, primer onset, primer RAAC,
freezes/controles, auditoría FULL_STATE_INTERNALIZATION, tres cierres de 660
preguntas y definiciones operacionales RAAC/RDDA/APD. Todo detalle falta como
`UNKNOWN`.

## 19. Candidate temporal-graph representation

DAG temporal: nodo `(variable,t)`; arista de padre esencial efectivo en `t` al
hijo en `t+1`. Adjuntar valor, población, tipo SUPPLIED/IMPLICIT/DYNAMIC/
CONTINGENT y estatus causal. El objeto puede ser subgrafo espaciotemporal, no
subconjunto fijo. Observar ascendencia, aristas activas, dominadores y cortes.

## 20. Candidate interventions

No se ejecuta ninguna. On-manifold es trayectoria de población natural
declarada; off-manifold, estado impuesto fuera de ella.

| familia | manipulación / fijos / tiempo | manifold | resultado discriminante esperado |
| --- | --- | --- | --- |
| ONSET BLOCK | impedir patrón; x fijo; primer onset | ambos | H1/H3 corte selectivo; H2 distribuido; H0 sin patrón privilegiado. |
| PATTERN INJECTION | imponer q; x basal; pre-onset | off | H1/H3 selectivo; H2 requiere historia; H0 sin unidad. |
| ACTION CUT | onset permitido, cortar q→x | ambos | perder reconstrucción con onset favorece H1/H2/H3. |
| PREMATURE EXTINCTION | basalizar patrón; x libre; pre-corrección | ambos | sensibilidad H1/H3; dependencia distribuida H2. |
| POST-REPAIR CLAMP | sostener q no basal; x correcto | off | separa soporte, reset, decaimiento y atractor. |
| EARLY EXTERNAL REPAIR | restaurar x temprano; q libre | off | prueba si q decae sin disparador. |
| DELAYED REPAIR | sostener x perturbado; q libre | off | prueba dependencia de daño. |
| PATTERN TRANSPLANT | q entre trayectorias; x/tiempo declarados | off | portabilidad contra historia. |
| MISTIMED TRANSPLANT | q temprano/x tardío y recíproco | off | separa patrón de fase/historia. |
| OUTPUT REMAPPING | onset intacto, mapeo correctivo alterado | off | localiza suministro/uso de dirección. |
| SHAM CONTROL | variable irrelevante; fijos/tiempo iguales | ambos | calibra artefacto de intervención. |

Antes de ejecutar, cada protocolo declara coordenadas, fijos, timestep,
elegibilidad, blanco y predicciones H0/H1/H2/H3; esta tabla no los inventa.

Predicciones mínimas por familia (H0 | H1 | H2 | H3), a convertir en criterios
cuantificados antes de correr:

- ONSET BLOCK: corte no privilegiado | bloque selectivo | interrupción de ruta
  distribuida | bloque selectivo más unidad temporal.
- PATTERN INJECTION: no suficiencia especial | patrón suficiente sólo en su
  contexto | depende de fase/historia | suficiencia o respuesta organizada
  compatible con gates.
- ACTION CUT: pérdida no selectiva o variable | onset preservado y pérdida de
  resultado | efecto repartido por varios cortes | misma predicción H1 más
  relación con terminación.
- PREMATURE EXTINCTION: efectos intercambiables | pérdida selectiva | pérdida
  dependiente de segmento temporal | pérdida selectiva y fin endógeno alterado.
- POST-REPAIR CLAMP: no delimita objeto | clamp revela dependencia de soporte o
  reset | depende de trayectoria completa | desacopla acción de terminación
  según gates.
- EARLY EXTERNAL REPAIR: cascada local puede variar | soporte perdido altera
  módulo | proceso cambia con historia | prueba que reparación elimina su
  disparador.
- DELAYED REPAIR: cambios locales no específicos | soporte sostenido prolonga
  módulo | prolonga ruta distribuida | discrimina terminación endógena de
  soporte persistente.
- PATTERN TRANSPLANT: ningún patrón privilegiado | portabilidad condicionada
  del módulo | fracaso o dependencia de historia | portabilidad sólo compatible
  con identidad causal acordada.
- MISTIMED TRANSPLANT: efecto de intervención sin fase especial | sensibilidad
  a fase del módulo | fuerte dependencia temporal distribuida | fase coherente
  requerida por organización transitoria.
- OUTPUT REMAPPING: cambios locales sin localización única | separa módulo de
  dirección suministrada | redistribuye uso de información | puede falsar
  contribución reconstructiva específica.
- SHAM CONTROL: efecto igual al tratamiento cuestiona toda lectura | efecto
  nulo sostiene selectividad | efecto nulo sostiene especificidad distribuida |
  efecto nulo es requisito, no prueba H3.

## 21. Candidate controls

Catalogar sin ejecutar: D03 sin auxiliar y fallo; restauración externa faseada;
fallo periódico `p=e`; freezes E/P; actividad sin reconstrucción;
reconstrucción sin organización temporal autónoma; RDDA como comparación
interimplementación posterior.

## 22. Candidate metrics

No crear «entity score». Mantener `d_H(x,target)`, `d_H(q,q*)`, auxiliares no
basales, tiempo a onset, primer RAAC, DATA_RECOVERY_TIME, FULL_RECOVERY_TIME,
cola, aristas activas, corte mínimo, lesión, inyección, recuperación,
ascendencia y dominadores. Cada métrica necesita calibración/control.

## 23. Representation confounders

Comprobar renombramiento, permutaciones válidas, complemento global aplicable y
sintaxis equivalente. No exigir invariancia bajo recodificaciones no lineales
que alteren aridad esencial o semántica de intervención. DATA/AUX y D/E/L/P
pueden inducir fronteras arbitrarias.

## 24. Design/provenance confounders

Separar diseño suministrado, consecuencia implícita y patrón realizado.
Etiquetar `NATURAL_PDATA`, `NATURAL_PFULL`, `INTERVENTION_REACHABLE` u
`OFF_MANIFOLD`; nunca intercambiarlos. Conservar reglas, trazas, RNG, tiempos y
contratos. Fuentes no localizadas bloquean precisión adicional.

## 25. What would falsify H3

H3 falla limpiamente si no hay onset identificable, ningún patrón/subgrafo tiene
contribución selectiva, terminación exige reset externo o no hay
unidad/frontera robusta bajo representaciones permitidas. El alcance queda
limitado al protocolo calibrado.

## 26. What would support H1/H2

H1 gana apoyo si subconjunto o corte temporal pequeño, estable bajo simetrías,
es lesionable y afecta reconstrucción selectivamente. H2 gana apoyo si el
efecto es real pero distribuido por historia/fase sin frontera fija. Ninguno
basta para H3.

## 27. Candidate proto-organelle gates

Propuestos, no canonizados: G1 onset identificable; G2 lesionabilidad selectiva;
G3 contribución reconstructiva; G4 terminación endógena; G5 frontera no
arbitraria o unidad temporal; G6 robustez bajo simetrías simples. No hay umbral
ni criterio de agregación adjudicado.

## 28. Stop conditions

Detener y devolver a adjudicación si falta trazabilidad de intervención, se
mezclan poblaciones, se altera regla o resultado cerrado, se interpreta sin
control, se contradice evidencia heredada o se intenta emitir H3 sin gates.
ETP-PRE-00 termina antes de correr.

## 29. Smallest valid first experiment

Reemplazado por PRE-01: primero se requiere atlas basal completo. Una vez que
exista autorización posterior, el candidato único es ACTION CUT; EARLY
EXTERNAL REPAIR, ONSET BLOCK y PATTERN INJECTION son manipulaciones distintas,
no brazos de un mismo experimento. PATTERN INJECTION queda posterior por ser
off-manifold. Véase ETP_PRE_01_BASELINE_CAUSAL_ATLAS.md.

## 30. Questions requiring researcher decision before execution

1. ¿Cuáles son los tres MD de las 660 preguntas y sus versiones autoritativas?
2. ¿Qué traza y contrato respaldan cada P-DATA, P-FULL, RAAC, freeze y control?
3. ¿Qué semántica autoriza fijar/remapear coordenadas y qué off-manifold acepta?
4. ¿Qué política define padre esencial efectivo en el DAG?
5. ¿Qué patrón candidato y población se usarán en los tres protocolos?
6. ¿Qué gates, controles y umbrales admitirían eventualmente una lectura H3?

# Nivel 1.5 - paquete de diseño preservado

Estado: **solo diseño; sin rama, carpeta de implementación ni código de Nivel 1.5**.

Documentos incluidos:

1. `LEVEL15_01_ENTREGABLE_1_CONSTRUCTO.md`
2. `LEVEL15_02_ENTREGABLE_2_APRENDIBILIDAD.md`
3. `LEVEL15_03_ENTREGABLE_3_MECANISMO_CAMPANA.md`
4. `LEVEL15_04_AUDITORIA_FUGAS_Y_COORDINACION.md`
5. `LEVEL15_05_ESTADO_Y_DECISION_LOG.md`

Corrección canónica incorporada:

- La expectativa `15-21 %` de óptimos locales se retira para el experimento real de coaprendizaje.
- En el piloto de 100.000 ensayos y 40 repeticiones por régimen: R_G 31/40 llega, 1/40 óptimo local exacto, 8/40 no llega ni es óptimo; R_P 28/40, 4/40, 8/40; R_J 31/40, 4/40, 5/40.
- De 30 fallos, sólo 9 son óptimos locales exactos; 21 son fallos de coordinación encoder-decoder no atrapados en el paisaje del encoder.
- Decoder limitado a `(z,q)`.
- Por ensayo: una actualización de encoder y una de decoder; no reevaluación contrafactual.
- Encoder y decoder son read-only entre retención y respuesta; cualquier escritura en ese intervalo es fuga temporal.
- No se preregistra explicación causal para la mayor dificultad de R_P.

`SHA256SUMS.txt` contiene las huellas de los documentos preservados.

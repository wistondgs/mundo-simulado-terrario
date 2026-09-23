# PRIMITIVO N=2

Línea experimental de réplica ciega. Su estado actual es **GATE A — RÉPLICAS
CIEGAS PENDIENTES**.

## Qué está disponible aquí

- `replicas_ciegas/A1/`: workspace ciego de A1, inicialmente con sólo los dos
  archivos permitidos.
- `replicas_ciegas/A2/`: workspace ciego de A2, inicialmente con sólo los dos
  archivos permitidos.
- `custodia_zip/`: ZIP originales congelados de A1 y A2; no debe adjuntarse al
  workspace de un replicador.
- `control/`: paquete no ciego del investigador, preservado aparte de A1 y A2.

Los ZIP originales se conservan bajo `custodia_zip/`. Cada workspace contiene
la extracción legible mínima; ésta no sustituye al ZIP como objeto congelado
de custodia.

## Reglas de custodia

- A1 y A2 contienen sólo `TASK.txt` y la SPEC A cerrada.
- No exponer a los replicadores B, el código de referencia, resultados ni la
  conversación de control.
- B sigue bloqueada hasta que Gate A evalúe las dos réplicas.
- No ejecutar ni modificar las réplicas desde esta carpeta.

## Integridad de los paquetes ciegos

| Paquete | SHA-256 | Estado |
| --- | --- | --- |
| A1 | `99e6d56d0ea5378f59dffdd6038105361ab118cb71e8ded9d38024ef0f56a87f` | congelado para réplica ciega |
| A2 | `a29aa4bf871884b86b31287086f4648da90c8616a94453a8d9168696eefcffc1` | congelado para réplica ciega |
| Control | `79dc8eeadc9190220d66f21eeb002b1f72c8d274d6f74ed07398a667722d05a7` | incorporado como objeto no ciego separado |

La SPEC A declarada es
`f19324cd5039cc6f83176a77afe8ff23b07e817e1a1471e5e56d05823515a430` y
su estado es `FROZEN_FOR_BLIND_REPLICATION`.

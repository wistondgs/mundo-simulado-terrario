"""`LEVEL-FACTORY-01` · la parte mecánica del ciclo de adquisición.

Lo que esta fábrica automatiza es **lo que ya se hizo mal al menos una vez**, y
sólo eso. Cada comprobador de aquí nace de un defecto medido en una campaña
real, no de una simetría que se ve bonita en un diagrama:

| comprobador | defecto que lo origina | dónde |
|---|---|---|
| `catalog`  | 1.5 necesita `M` y `PSI`, que viven en ramas hermanas | descubierto a mano tras 1.4 |
| `seeds`    | cada linaje reescribe a mano la unión de las semillas ya gastadas | `test_level14_lineage.py` |
| `gates`    | el guion evaluó 7 gates donde el preregistro sellaba 11, y gastó `L14-11` en las sondas | `68d852d` |
| `vacuity`  | `assert sin_asignar == sin_asignar`: compara una lista consigo misma | informe 1.4 §7 |

La fábrica **no** ejecuta ciencia. No diseña constructos, no decide oráculos y
no interpreta resultados. Recibe árboles de campaña ya escritos y dice si su
contabilidad se sostiene.
"""

__all__ = ["catalog", "seeds", "gates", "vacuity"]

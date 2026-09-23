# Notas de implementación — A1

`replica.py` separa las transformaciones elementales (bits, particiones,
máscaras y funciones), el análisis de una dinámica (atractores, dependencia,
robustez, scheduler, lesión y tipos), y la agregación C11. `test_replica.py`
comprueba las propiedades estructurales antes de la enumeración. La escritura
JSON usa codificación ASCII, claves ordenadas y separadores canónicos.

No se emplea Monte Carlo: E[I] se evalúa por la distribución
hipergeométrica exacta especificada.

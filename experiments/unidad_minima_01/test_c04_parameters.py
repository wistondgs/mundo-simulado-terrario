"""Non-confirmatory C04 parameter contract."""
from __future__ import annotations

import unittest

from unidad_minima_08_fase2 import NUCLEO, PRESUPUESTO_PASOS, VENTANA, UnidadFase2
from unidad_minima_09_fase2 import UnidadC5


class C04ParametersTest(unittest.TestCase):
    def test_c04_values_are_owned_by_each_organism(self):
        organism = UnidadC5(n_max=8, presupuesto=2_000_000, ventana=512, nucleo=256)
        self.assertEqual((organism.presupuesto_efectivo, organism.ventana_efectiva, organism.nucleo_efectivo),
                         (2_000_000, 512, 256))

    def test_historical_defaults_remain_frozen(self):
        historical = UnidadFase2(n_max=8)
        self.assertEqual((historical.presupuesto_efectivo, historical.ventana_efectiva, historical.nucleo_efectivo),
                         (PRESUPUESTO_PASOS, VENTANA, NUCLEO))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
import unittest

import replica


class StructuralTests(unittest.TestCase):
    def test_domain_and_enumeration(self):
        dynamics = list(replica.all_dynamics())
        self.assertEqual(len(dynamics), 256)
        self.assertEqual(dynamics[0], (0, 0, 0, 0))
        self.assertEqual(dynamics[-1], (3, 3, 3, 3))

    def test_masks_are_unique_and_expected(self):
        self.assertEqual(replica.MASKS, {"C12": (2, 1), "C13": (3, 1), "C23": (3, 2)})

    def test_attractor_canonicalization_and_trajectory(self):
        self.assertEqual(replica.attractors((0, 2, 1, 3)), [[0], [1, 2], [3]])
        self.assertEqual(replica.attractor_reached((0, 2, 1, 3), 1), (1, 2))

    def test_fraction_and_json_serialization(self):
        self.assertEqual(replica.fraction_string(6, 8), "3/4")
        self.assertEqual(replica.canonical_json({"z": True, "a": [1, 2]}), '{"a":[1,2],"z":true}')

    def test_calibration_vectors(self):
        expected = [
            '{"F":[0,0,0,0],"atractores":[[0]],"dependencias":{"C12":{"cruzada":"separable","grafo":[false,false,false,false]},"C13":{"cruzada":"separable","grafo":[false,false,false,false]},"C23":{"cruzada":"separable","grafo":[false,false,false,false]}},"lesion":{"x1":{"congelar":true,"fijar0":false},"x2":{"congelar":true,"fijar0":false}},"periodos":[1],"robustez":{"C12":"1","C13":"1","C23":"1"},"scheduler":{"atractores_distintos":false,"ciclo_muere_sin_reloj":false,"sec12":[[0]],"sec21":[[0]],"sinc":[[0]]},"tipo_C12":[0,0,0,0],"tipo_S4":[0,0,0,0]}',
            '{"F":[0,2,1,3],"atractores":[[0],[1,2],[3]],"dependencias":{"C12":{"cruzada":"mutua","grafo":[false,true,true,false]},"C13":{"cruzada":"unidir","grafo":[true,true,false,true]},"C23":{"cruzada":"unidir","grafo":[true,true,false,true]}},"lesion":{"x1":{"congelar":true,"fijar0":true},"x2":{"congelar":true,"fijar0":true}},"periodos":[1,1,2],"robustez":{"C12":"0","C13":"1/4","C23":"1/4"},"scheduler":{"atractores_distintos":true,"ciclo_muere_sin_reloj":true,"sec12":[[0],[3]],"sec21":[[0],[3]],"sinc":[[0],[1,2],[3]]},"tipo_C12":[0,2,1,3],"tipo_S4":[0,1,3,2]}'
        ]
        for f, want in zip(((0, 0, 0, 0), (0, 2, 1, 3)), expected):
            self.assertEqual(replica.canonical_json(replica.analyze(f)), want)

    def test_scheduler_fixed_points_for_all_functions(self):
        for f in replica.all_dynamics():
            sync = {tuple(a) for a in replica.attractors(f) if len(a) == 1}
            sec12, sec21 = replica.scheduler_dynamics(f)
            self.assertEqual(sync, {tuple(a) for a in replica.attractors(sec12) if len(a) == 1})
            self.assertEqual(sync, {tuple(a) for a in replica.attractors(sec21) if len(a) == 1})

    def test_conjugation_preserves_s4_type(self):
        f = (0, 2, 1, 3)
        original = replica.type_of(f, replica.PERMUTATIONS)
        for p in replica.PERMUTATIONS:
            self.assertEqual(replica.type_of(replica.conjugate(f, p), replica.PERMUTATIONS), original)

    def test_information_basics(self):
        labels = ["a", "a", "b", "b"]
        self.assertAlmostEqual(replica.entropy(labels), 1.0)
        self.assertAlmostEqual(replica.mutual_information(labels, labels), 1.0)


if __name__ == "__main__":
    unittest.main()

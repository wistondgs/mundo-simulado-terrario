#!/usr/bin/env python3
"""Cuánta dependencia acción→consecuencia hay en la clase de mundos del Nivel 1.

No implementa ninguna capacidad nueva: mide el **mundo**, con la maquinaria ya
congelada de 1.6, para que el decimal siguiente pueda sellar tamaños de efecto
por semilla antes de que exista un aprendiz. Es la doctrina B-4 de 1.6 aplicada
hacia adelante.

    D_W(mundo)  =  I(A_t ; O_{t+1} | O_t)
                =  H(O_{t+1}|O_t) − H(O_{t+1}|O_t, A_t)

bajo la distribución de referencia `p_ref(o,a) = p_estacionaria(o) · 1/4`, que es
la que S0 produce: caminata uniforme con rebote, cadena simétrica sobre celdas,
luego estacionaria uniforme sobre el componente natal.

También verifica el gemelo A/B **al nivel del kernel de estados**, que es lo
único que permite llamarlo gemelo físico:

    T_B(s'|s,a)  =  (1/4) Σ_b T_A(s'|s,b)      para toda a

La primera versión de este script comparaba `conditional.mean(axis=1)` con
`twin.mean(axis=1)`, que es cierto **por construcción**: demostraba un kernel
observacional fabricado para ser gemelo, no un mundo B. Corregido. De las cuatro
comprobaciones de abajo, dos son tautológicas y se marcan como tales; las dos que
prueban algo son que la estacionaria coincide y que `I(O;O')` se conserva exacta
mientras `I(A;O'|O)` cae a cero, ambas calculadas desde el kernel de estados a
través del mapa de observación.

    python scripts/medir_dependencia_accion.py
"""

from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, ".")

from terrario.level1.world import DELTA, Direction  # noqa: E402
from terrario.level16.seeds import consume_seeds  # noqa: E402
from terrario.level16.structure import _signature  # noqa: E402
from terrario.level16.temporal import OBSERVATION_INDEX  # noqa: E402
from terrario.level16.world import build_world  # noqa: E402


def reachable_kernels(seed: int):
    """Los núcleos exactos del mundo de esa semilla, desde la topología.

    Devuelve `P(o'|o,a)`, `P(o'|o)`, `p(o)`, `H(O'|C)` y el tamaño del componente.
    `H(O'|C)` es el techo antes del aliasing: como `P(o'|c,a)` es determinista,
    coincide con `I(A;O'|C)`.
    """
    grid = build_world(seed)
    seen = {grid.position}
    stack = [grid.position]
    while stack:
        row, col = stack.pop()
        for direction in Direction:
            destino = (row + DELTA[direction][0], col + DELTA[direction][1])
            if grid.cells[destino] == 0 and destino not in seen:
                seen.add(destino)
                stack.append(destino)

    cells = sorted(seen)
    signature = {cell: OBSERVATION_INDEX[_signature(grid, cell)] for cell in cells}

    def landing(cell, direction):
        destino = (cell[0] + DELTA[direction][0], cell[1] + DELTA[direction][1])
        return destino if grid.cells[destino] == 0 else cell

    conditional = np.zeros((16, 4, 16))
    per_observation = np.zeros(16)
    for cell in cells:
        origen = signature[cell]
        per_observation[origen] += 1
        for direction in Direction:
            conditional[origen, int(direction),
                        signature[landing(cell, direction)]] += 1
    for origen in range(16):
        if per_observation[origen]:
            conditional[origen] /= per_observation[origen]

    p_observation = per_observation / per_observation.sum()
    marginalised = conditional.mean(axis=1)

    entropy_given_cell = 0.0
    for cell in cells:
        nxt = np.zeros(16)
        for direction in Direction:
            nxt[signature[landing(cell, direction)]] += 0.25
        entropy_given_cell += (1 / len(cells)) * -sum(p * np.log(p)
                                                      for p in nxt if p > 0)

    return conditional, marginalised, p_observation, entropy_given_cell, len(cells)


def conditional_mutual_information(conditional, marginalised, p_observation):
    """`I(A; O' | O)` bajo `p_ref(o,a) = p(o) · 1/4`."""
    total = 0.0
    for origen in range(16):
        if p_observation[origen] == 0:
            continue
        for action in range(4):
            for target in range(16):
                p = conditional[origen, action, target]
                q = marginalised[origen, target]
                if p > 0 and q > 0:
                    total += p_observation[origen] * 0.25 * p * np.log(p / q)
    return float(total)


def sensory_mutual_information(marginalised, p_observation):
    """`I(O; O')` --la magnitud del Nivel 1.6-- con la misma referencia."""
    marginal = p_observation @ marginalised
    return float(sum(
        p_observation[o] * marginalised[o, j] * np.log(marginalised[o, j] / marginal[j])
        for o in range(16) if p_observation[o] > 0
        for j in range(16) if marginalised[o, j] > 0 and marginal[j] > 0))


def state_kernel(seed: int):
    """`T_A(s'|s,a)` sobre el componente natal, con la firma de cada celda."""
    grid = build_world(seed)
    seen = {grid.position}
    stack = [grid.position]
    while stack:
        row, col = stack.pop()
        for direction in Direction:
            destino = (row + DELTA[direction][0], col + DELTA[direction][1])
            if grid.cells[destino] == 0 and destino not in seen:
                seen.add(destino)
                stack.append(destino)
    cells = sorted(seen)
    index = {cell: i for i, cell in enumerate(cells)}
    kernel = np.zeros((len(cells), 4, len(cells)))
    for cell in cells:
        for direction in Direction:
            destino = (cell[0] + DELTA[direction][0], cell[1] + DELTA[direction][1])
            landing = destino if grid.cells[destino] == 0 else cell
            kernel[index[cell], int(direction), index[landing]] = 1.0
    signature = np.array([OBSERVATION_INDEX[_signature(grid, c)] for c in cells])
    return kernel, signature


def observational_from_states(kernel, signature, stationary):
    """Proyectar un kernel de estados al espacio sensorial. Vale para A y para B."""
    n = len(signature)
    numerator = np.zeros((16, 4, 16))
    denominator = np.zeros(16)
    for s in range(n):
        origen = signature[s]
        denominator[origen] += stationary[s]
        for a in range(4):
            for s2 in np.nonzero(kernel[s, a])[0]:
                numerator[origen, a, signature[s2]] += stationary[s] * kernel[s, a, s2]
    conditional = np.zeros((16, 4, 16))
    p_observation = np.zeros(16)
    for origen in range(16):
        if denominator[origen] > 0:
            conditional[origen] = numerator[origen] / denominator[origen]
            p_observation[origen] = denominator[origen]
    return conditional, conditional.mean(axis=1), p_observation


def verify_physical_twin(seed: int) -> None:
    """Construir el mundo B FÍSICO y comprobar las cuatro propiedades."""
    kernel_a, signature = state_kernel(seed)
    kernel_b = np.repeat(kernel_a.mean(axis=1)[:, None, :], 4, axis=1)
    n = len(signature)

    # la cadena marginal es simétrica => estacionaria uniforme. Se comprueba.
    marginal_a = kernel_a.mean(axis=1)
    assert np.allclose(marginal_a, marginal_a.T), "la cadena marginal debe ser simétrica"
    stationary = np.full(n, 1.0 / n)

    ca, ma, pa = observational_from_states(kernel_a, signature, stationary)
    cb, mb, pb = observational_from_states(kernel_b, signature, stationary)

    print(f"  semilla {seed}  ({n} celdas)")
    print("    [tautológico] T_B(.|s,a_i) == T_B(.|s,a_j)        "
          f"{all(np.allclose(kernel_b[:, i, :], kernel_b[:, j, :]) for i in range(4) for j in range(4))}")
    print("    [tautológico] sum_a T_A/4 == sum_a T_B/4          "
          f"{np.allclose(kernel_a.mean(axis=1), kernel_b.mean(axis=1))}")
    print("    [prueba algo] I(O;O') conservada exacta           "
          f"{np.isclose(sensory_mutual_information(ma, pa), sensory_mutual_information(mb, pb), atol=0, rtol=0)}"
          f"   ({sensory_mutual_information(ma, pa):.4f} -> {sensory_mutual_information(mb, pb):.4f})")
    print("    [prueba algo] I(A;O'|O) anulada                   "
          f"{conditional_mutual_information(ca, ma, pa):.4f} -> "
          f"{conditional_mutual_information(cb, mb, pb):.3e}")


def main() -> None:
    encabezado = "D_W = I(A;O'|O)"
    print(f"{'semilla':>10} {'celdas':>7} {encabezado:>16} {'H(O.|C)':>9} "
          f"{'I(O;O.)':>9} {'razon':>7}")
    disponible, sensorial, tamanos = [], [], []
    for seed in consume_seeds().lives:
        conditional, marginalised, p_observation, h_cell, n = reachable_kernels(seed)
        dw = conditional_mutual_information(conditional, marginalised, p_observation)
        ioo = sensory_mutual_information(marginalised, p_observation)
        disponible.append(dw)
        sensorial.append(ioo)
        tamanos.append(n)
        print(f"{seed:>10} {n:>7} {dw:>16.4f} {h_cell:>9.4f} {ioo:>9.4f} "
              f"{dw / ioo:>7.3f}")

    disponible = np.array(disponible)
    sensorial = np.array(sensorial)
    tamanos = np.array(tamanos)
    print(f"\nD_W       media {disponible.mean():.4f}  sd {disponible.std(ddof=1):.4f}"
          f"  min {disponible.min():.4f}  max {disponible.max():.4f}")
    print(f"I(O;O')   media {sensorial.mean():.4f}   <- lo disponible en 1.6")
    print(f"\nestratos (la inversion respecto de 1.6):")
    for etiqueta, mascara in (("<=3 celdas", tamanos <= 3), (">6 celdas", tamanos > 6)):
        if mascara.any():
            print(f"  {etiqueta:>11}  D_W {disponible[mascara].mean():.4f}"
                  f"   I(O;O') {sensorial[mascara].mean():.4f}"
                  f"   razon {np.mean(disponible[mascara]/sensorial[mascara]):.3f}")

    print("\n=== gemelo A/B, al nivel del kernel de ESTADOS ===")
    for seed in (140000011, 140000014, 140000025):
        verify_physical_twin(seed)


if __name__ == "__main__":
    main()

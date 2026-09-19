"""OBSERVABILITY-INTEGRATION-01 · dar al organismo el campo que ya recibe y tira.

`Observation` sella cuatro campos y A4 consume uno. `mask` tiene cero usos en
`a4_advanced.py`, y es el campo que dice qué celdas de la ventana caen DENTRO de
la rejilla: `1.0` dentro, `0.0` fuera. Medido, en un mundo 5x5 vacío el
organismo produce **una sola vista para las 25 celdas**; con la máscara serían
25. `P(s_{t+1}|s_t,a_t)` sobre una observación constante es una función
constante, por perfecto que sea el modelo.

**Legitimidad.** La máscara no es estado privilegiado. No lleva coordenadas
absolutas, ni identidades, ni nada fuera de la ventana: sólo dónde termina el
mundo. Ver una pared es percepción egocéntrica, y un organismo situado la tiene.
Su contenido informativo es exactamente la distancia al borde en cada dirección
--y nada más, porque en este motor los objetos no ocluyen.

**Por qué tres brazos y no dos.** Añadir un plano cambia la dimensión de entrada
del encoder. Comparar «A4 viejo» contra «A4 con máscara» confundiría la
información de la máscara con una arquitectura y unos parámetros distintos. Los
tres brazos tienen la MISMA arquitectura ampliada, los MISMOS pesos heredados y
los MISMOS pesos nuevos al nacer; difieren sólo en qué información lleva el
plano:

    ZERO   el plano existe y está vacío
    SHAM   el plano lleva una máscara permutada: misma forma y misma
           distribución marginal, correspondencia con el mundo destruida
    TRUE   el plano lleva la máscara correcta

Los pesos del canal nuevo nacen en CERO, así que al nacer los tres organismos
son funcionalmente idénticos entre sí y al A4 original: el plano nuevo no puede
alterar ni un logit. La pregunta no es si nacen distintos -- es si durante la
experiencia el organismo aprende a explotar lo que el plano le ofrece.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import torch

MaskArm = Literal["ZERO", "SHAM", "TRUE"]
ARMS: tuple[MaskArm, ...] = ("ZERO", "SHAM", "TRUE")


def expand_encoder_input(agent: Any, extra_planes: int = 1) -> None:
    """Ampliar el encoder en `extra_planes` canales que nacen INERTES.

    Se copia el peso original en los canales heredados y se pone a cero el del
    canal nuevo. Mientras ese peso valga cero, la salida de la convolución es
    idéntica sea cual sea el contenido del plano nuevo, así que la equivalencia
    al nacer no es una esperanza: es una identidad aritmética.
    """
    conv = agent.encoder.conv[0]
    old_weight = conv.weight.data
    out_ch, in_ch, kh, kw = old_weight.shape
    new_weight = torch.zeros(out_ch, in_ch + extra_planes, kh, kw,
                             dtype=old_weight.dtype, device=old_weight.device)
    new_weight[:, :in_ch] = old_weight

    expanded = torch.nn.Conv2d(in_ch + extra_planes, out_ch, kernel_size=(kh, kw),
                               padding=conv.padding, stride=conv.stride,
                               bias=conv.bias is not None)
    expanded.weight.data = new_weight
    if conv.bias is not None:
        expanded.bias.data = conv.bias.data.clone()
    agent.encoder.conv[0] = expanded
    agent.encoder.in_channels = in_ch + extra_planes


def sham_mask(mask: np.ndarray, *, salt: int = 0) -> np.ndarray:
    """La máscara con su correspondencia destruida y su marginal intacta.

    Permutación DETERMINISTA por la forma y la sal, no por el contenido: dos
    observaciones distintas reciben la misma permutación, de modo que el brazo
    SHAM ve exactamente los mismos valores que TRUE, en el mismo número, y
    colocados donde no significan nada. Si TRUE supera a SHAM, la ventaja es de
    la correspondencia con el mundo y no de tener un plano más.
    """
    flat = np.asarray(mask, dtype=np.float32).reshape(-1)
    rng = np.random.default_rng([salt, flat.size])
    return flat[rng.permutation(flat.size)].reshape(mask.shape)


@dataclass(frozen=True)
class MaskedObservation:
    """Una observación con el plano extra ya montado sobre los canales."""

    channels: np.ndarray
    mask: np.ndarray
    agent_energy: float
    time_fraction: float

    @property
    def obs_hash(self) -> str:
        h = hashlib.sha256()
        h.update(np.ascontiguousarray(self.channels).tobytes())
        h.update(f"{self.agent_energy},{self.time_fraction}".encode())
        return h.hexdigest()


def present(observation: Any, arm: MaskArm, *, salt: int = 0) -> MaskedObservation:
    """Montar el plano del brazo sobre los canales que el encoder recibirá."""
    channels = np.asarray(observation.channels, dtype=np.float32)
    mask = np.asarray(observation.mask, dtype=np.float32)
    if arm == "ZERO":
        plane = np.zeros_like(mask)
    elif arm == "SHAM":
        plane = sham_mask(mask, salt=salt)
    elif arm == "TRUE":
        plane = mask
    else:
        raise ValueError(f"brazo desconocido: {arm!r}; hay {ARMS}")
    stacked = np.concatenate([channels, plane[None, ...]], axis=0)
    return MaskedObservation(stacked, mask, float(observation.agent_energy),
                             float(observation.time_fraction))


def distinct_views(observations: list[Any], arm: MaskArm, *, salt: int = 0) -> int:
    """Cuántas observaciones distintas ve un brazo. Es G0: el aliasing crudo."""
    return len({present(o, arm, salt=salt).channels.tobytes() for o in observations})

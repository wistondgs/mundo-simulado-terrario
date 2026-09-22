#!/usr/bin/env python3
"""N1.0 · preregistro v3. V1 y V2 quedan intactos.

V2 described arms B and C and sealed code that could not run them: the
runner carried an `override_token` hook and nothing implemented it, and
there was no read lesion anywhere in the tree. The seal was incomplete --
it pinned the mechanism and the instrument and left the interventions
unpinned.

Caught before a single confirmatory seed was spent, which is the only
reason it is cheap. Nothing statistical or procedural changes: V3 is V2's
analysis with the interventions and the campaign runner added to the sealed
set, so what runs the campaign is pinned by the same hash as what it runs.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

import n10_preregistration as v1        # noqa: E402
import n10_preregistration_v2 as v2     # noqa: E402

DESTINO = RAIZ / "docs" / "N10_CAMPAIGN_MANIFEST_V3.json"
SCHEMA = "terrario.n10-preregistration/v3"

#: Lo que V2 no selló y la campaña necesita para existir.
AÑADIDOS = ("terrario/lab/n10_arms.py",
            "scripts/n10_confirmatory.py",
            "scripts/n10_preregistration_v3.py")


def construir() -> dict:
    base = v2.construir()
    ficheros = tuple(base["sealed_code"]) + AÑADIDOS
    archivos = {p: v1.digest(RAIZ / p) for p in ficheros}
    m = dict(base)
    m.update({
        "schema": SCHEMA, "revision": 3,
        "supersedes": {
            "revisions": [1, 2],
            "artifacts": ["docs/N10_CAMPAIGN_MANIFEST_V1.json",
                          "docs/N10_CAMPAIGN_MANIFEST_V2.json"],
            "status": "SUPERSEDED, both preserved unedited",
            "reason": "V2 described arms B and C and sealed code that could "
                      "not run them: the runner carried an override_token "
                      "hook nothing implemented, and no read lesion existed. "
                      "The seal pinned the mechanism and the instrument and "
                      "left the interventions unpinned. Nothing statistical "
                      "or procedural changed."},
        "sealed_code": archivos,
        "sealed_code_root_hash": hashlib.sha256(
            json.dumps(archivos, sort_keys=True).encode()).hexdigest(),
        "arms_implementation": {
            "module": "terrario/lab/n10_arms.py",
            "A_COMPLETE": "no intervention",
            "B_MEMORY_READ_LESION": "the token keeps being written and stays "
                                    "observable between decisions; only the "
                                    "read at choice time is blocked. Not an "
                                    "ablation",
            "C_HISTORY_SHUFFLED": "a sealed permutation substitutes the token "
                                  "the policy reads; world, consequences, "
                                  "learned table and decision ids untouched",
            "construction": "every arm is a clone of the SAME frozen "
                            "snapshot; three independent trainings are "
                            "forbidden and parity is asserted before "
                            "intervening"},
        "runner": {"script": "scripts/n10_confirmatory.py",
                   "aborts_if": "the live code root hash differs from the "
                                "sealed one, or the tree is dirty — before "
                                "any seed is spent"},
    })
    return m


if __name__ == "__main__":
    m = construir()
    if "--write" in sys.argv:
        DESTINO.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
        def h(p):
            return hashlib.sha256((RAIZ / "docs" / p).read_bytes()).hexdigest()
        print(f"V3 escrito: {DESTINO.relative_to(RAIZ)}")
        print(f"  código sellado  {len(m['sealed_code'])} ficheros")
        print(f"  raíz            {m['sealed_code_root_hash']}")
        print(f"  V3 sha256       {h('N10_CAMPAIGN_MANIFEST_V3.json')}")
        print(f"  V2 sha256       {h('N10_CAMPAIGN_MANIFEST_V2.json')}  (intacto)")
        print(f"  V1 sha256       {h('N10_CAMPAIGN_MANIFEST_V1.json')}  (intacto)")
    else:
        print(json.dumps(m, indent=2, ensure_ascii=False))

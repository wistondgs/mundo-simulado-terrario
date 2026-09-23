#!/usr/bin/env python3
"""Verificación separada de los registros A2, sin importar replica_a2.py."""
import itertools, json, sys
from fractions import Fraction

P = ((0, 0, 1, 1), (0, 1, 0, 1), (0, 1, 1, 0))
MASK = {"C12": (2, 1), "C13": (3, 1), "C23": (3, 2)}
CUT = {"C12": (0, 1), "C13": (0, 2), "C23": (1, 2)}

def cyc(f, s):
    z = []
    while s not in z:
        z.append(s); s = f[s]
    return tuple(sorted(z[z.index(s):]))

def allcyc(f): return [list(x) for x in sorted({cyc(f, s) for s in range(4)})]
def xy(s): return s >> 1, s & 1
def st(a, b): return 2*a+b

def schedule(f, mode):
    o=[]
    for q in range(4):
        a,b=xy(q)
        if mode == 12:
            a=xy(f[st(a,b)])[0]; b=xy(f[st(a,b)])[1]
        else:
            b=xy(f[st(a,b)])[1]; a=xy(f[st(a,b)])[0]
        o.append(st(a,b))
    return tuple(o)

def main(path):
    rows=[json.loads(x) for x in open(path, encoding="ascii")]
    assert len(rows)==256
    for f, r in zip(itertools.product(range(4), repeat=4), rows):
        assert r["F"] == list(f) and r["atractores"] == allcyc(f)
        for name,(a,b) in CUT.items():
            ma,mb=MASK[name]
            d=[any(P[i][f[s]] != P[i][f[s^m]] for s in range(4)) for i,m in ((a,ma),(a,mb),(b,ma),(b,mb))]
            # Recompute the two off-diagonal terms with their specified input masks.
            d[1]=any(P[a][f[s]] != P[a][f[s^mb]] for s in range(4))
            d[2]=any(P[b][f[s]] != P[b][f[s^ma]] for s in range(4))
            z="separable" if not d[1] and not d[2] else "mutua" if d[1] and d[2] else "unidir"
            assert r["dependencias"][name] == {"cruzada":z,"grafo":d}
            good=tot=0
            for at in r["atractores"]:
                for s,m in itertools.product(at,(ma,mb)):
                    tot+=1; good += cyc(f,s^m)==tuple(at)
            assert r["robustez"][name] == str(Fraction(good,tot))
        assert r["scheduler"]["sinc"] == allcyc(f)
        assert r["scheduler"]["sec12"] == allcyc(schedule(f,12))
        assert r["scheduler"]["sec21"] == allcyc(schedule(f,21))
    print("PASS validacion_independiente: 256 registros, C3-C8 verificados")

if __name__ == "__main__": main(sys.argv[1])

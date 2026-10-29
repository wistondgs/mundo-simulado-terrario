#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-12 · la puerta del mundo caro · banco madre para la Fase 3.

**Sin esto no hay Fase 3** (§1 y §8 de `ORIENTACIONES_FASE_3_TRES_ELEMENTOS.md`). La
lección de C5 en una línea: en el banco de 3 estados, identificar W₁ le cuesta a la unidad
fresca **18 pasos de mediana**, y la primera medida de cualquier curva está en el paso 64;
así que heredar **no puede** valer más que vivir y el resultado sale nulo por techo del
diseño (E-50). Para que heredar signifique algo, vivir tiene que ser **caro**.

**Qué hace.** Mide, sobre el banco de la Fase 1, cuántos pasos tarda la unidad fresca en
identificar los W₁ de **6 y 8 estados con `n_min >= 4`**, y selecciona los que **superan
256 pasos o no identifican en toda su vida**. Ésos son los mundos madre de la Fase 3.

**Dos medidas del coste, y por qué dos.**
- `coste_barato` = `último error + 1`: el primer paso desde el que la hipótesis ya no vuelve
  a errar en la vida. Sale **gratis** de `vivir` y permite barrer miles de sistemas.
- `coste_exacto` = el primer paso desde el que **identifica el futuro fijo y no lo pierde**.
  Cuesta una predicción del futuro por paso, así que se calcula **sólo** sobre los
  candidatos que el barato ya seleccionó. Verificado el 28-oct sobre los 174 mundos de 3
  estados: las dos medidas coinciden en mediana, p75, p90, p95 y máximo.

**Aquí la unidad SÍ empieza en el estado 0** —W₁ es el primer mundo de su vida—, así que
`n_min` desde el estado 0 es la dificultad real y E-52 no aplica; se dice explícitamente
porque en la Fase 2 no era así.

**Muestra, no banco completo:** 6^12 = 2,2·10⁹ sistemas de 6 estados y 8^16 = 2,8·10¹⁴ de 8.
Se muestrea con **paso multiplicativo coprimo** verificado por `muestreo_verificado`
(E-27, E-51): nunca un prefijo, nunca un paso «redondo». Reanudable con `fsync` por fila y
tope de reloj declarado (E-29, E-32).
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unidad_minima_01 import predict, run_world, shortlex                 # noqa: E402
from unidad_minima_05_banco import (                                      # noqa: E402
    L_de, alcanzables, canonica, cociente, mealy_verdadera, minimizar, paso_de,
    sistema_por_indice, total_sistemas,
)
from unidad_minima_02_incremental import Unidad                            # noqa: E402
from unidad_minima_08_fase2 import UnidadFase2, medir, vivir              # noqa: E402
from guardas import (                                                     # noqa: E402
    informe, muestreo_verificado, no_vacio, salida_a_fichero, sin_azar_usado,
)

SHA_12 = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
ARRANQUE = time.strftime("%Y-%m-%dT%H:%M:%S")

N_MIN_EXIGIDO = 4        # §1 de la Fase 3
UMBRAL_CARO = 256        # «más de 256 pasos o no identifica»: el cuarto hito de la curva
TOPE_EXACTO_S = 60       # tope de reloj del identificador exacto por mundo; si salta, el
                         # coste intrínseco de ese mundo queda SIN DETERMINAR y se dice
MUESTRA = {6: 4000, 8: 4000}      # sistemas por tamaño; declarado, no es el banco completo
TOPE_RELOJ_S = {6: 1800, 8: 7200}  # tope por tamaño; si salta, se informa cuántos se midieron.
                                   # n=8 sube a 2 h porque la columna del coste intrínseco
                                   # dobla el trabajo por mundo y el banco madre crece con la
                                   # cobertura; las filas van con `fsync` una a una, así que
                                   # un corte no pierde nada y el parcial es legible


def verdad_desde_cero(A, B):
    est = alcanzables(A, B)
    Tv = mealy_verdadera(A, B, est)
    n_min, bloque = minimizar(Tv, est)
    Mmin, ini = cociente(Tv, est, bloque)
    return est, n_min, canonica(Mmin, ini)


def paso_coprimo(total, cuantos, base, posiciones):
    """El paso multiplicativo que deja TODAS las posiciones de dígito libres, buscado
    alrededor de `total/φ`. El paso no se elige por redondo: se elige por **pasar la
    comprobación** (E-27, E-51).

    Por qué alrededor de `total/φ` y no desde 3 (defecto corregido al probarlo, antes de
    medir nada): con una muestra de `cuantos` elementos y un paso **pequeño**, los índices
    `i*j` son todos pequeños y los dígitos de orden ALTO quedan clavados en 0 — es el mismo
    retículo de E-51 por el otro extremo, y la búsqueda desde 3 no termina nunca porque
    ningún paso chico puede pasar la comprobación. Un paso cercano a `total/φ` (la razón
    áurea, que es una constante y no una semilla) reparte la muestra por todo el espacio y
    pasa a la primera o casi. Si ni así pasa, se informa y **no se corre**: una muestra que
    no cubre cada posición de dígito no representa el banco.
    """
    phi = 1.618033988749895
    j0 = max(3, int(total / phi) | 1)
    for d in range(0, 20001):
        for j in ({j0 + d, j0 - d} if d else {j0}):
            if j < 3 or j % base == 0:
                continue
            idx = [(i * j) % total for i in range(cuantos)]
            if all({(x // base ** k) % base for x in idx} == set(range(base))
                   for k in range(posiciones)):
                return j, idx
    raise RuntimeError(
        f"ningún paso cerca de total/φ deja libres las {posiciones} posiciones con "
        f"{cuantos} muestras en base {base}: la muestra no representa el banco (E-27/E-51); "
        f"subir `cuantos` o bajar `posiciones`.")


def coste_exacto(A, B, vida, futuro, n_max, rejilla=1):
    """El primer paso desde el que la unidad identifica el futuro fijo y no lo pierde.
    `rejilla` > 1 lo comprueba cada tantos pasos: devuelve una cota superior con su
    resolución, y la resolución se informa junto al número."""
    step = paso_de(A, B)
    u = UnidadFase2(n_max=n_max)
    x, primero = 0, None
    for t, a in enumerate(vida, start=1):
        p = u.predecir(a)
        if p is None:
            p = 0
        x, o = step(x, a)
        u.leer(a, o)
        if t % rejilla == 0:
            verdad_fut, _ = run_world(step, x, futuro)
            h, nr, _ = predict(u.trans, u.q, futuro, verdad_fut)
            primero = t if (h == len(futuro) and nr == 0) and primero is None else \
                (primero if (h == len(futuro) and nr == 0) else None)
    return primero


# ---------------------------------------------------------------------------
# DOS COSTES, DOS COLUMNAS (E-53)
# ---------------------------------------------------------------------------
# «Caro» mezclaba dos magnitudes distintas y lo detectó Fable recomputando mis filas: en
# n=8, de 462 mundos caros para la unidad de 08, **157 lo eran sólo porque esa unidad se
# ahoga y olvida** —86 olvidos por vida en los caros contra 0,2 en los baratos—, no porque
# el mundo sea difícil. Un mundo caro **por el mundo** es banco madre; un mundo caro **por
# el olvido** es un defecto de disposición que hay que arreglar antes, no un mundo.
#
# Y un tercer factor que ni el encargo ni yo habíamos separado: los dos costes se medían
# con criterios distintos —el exacto por **isomorfismo** con la mínima verdadera, el de la
# unidad por **predecir un futuro fijo**—. Medido en el cruce 1:1 con las 5 000 filas
# limpias de la Fase 1: **614 de 1 182 mundos que el exacto NO resuelve, la unidad los da
# por identificados**. El futuro fijo es criterio necesario y **no suficiente**. Aquí las
# dos columnas usan el criterio fuerte, así que comparan lo mismo.
#
# Columna 1, el MUNDO: la unidad de **02** —sin ventana, sin olvido: el identificador
# exacto de la Fase 1— y su máquina final tiene que ser la mínima verdadera salvo
# isomorfismo. Con tope de reloj por mundo; si salta, ese mundo queda SIN DETERMINAR.
# Columna 2, ESTA unidad: la de 08, con ventana 512 y presupuesto 200 000, con olvido.
# El BANCO MADRE se elige por la columna 1.


def _un_sistema(args):
    idx, n, vida, futuro, n_max = args
    A, B = sistema_por_indice(n, idx)
    est, n_min, canon = verdad_desde_cero(A, B)
    if n_min < N_MIN_EXIGIDO:
        return dict(idx=idx, n=n, n_min=n_min, descartado="n_min")
    u = UnidadFase2(n_max=n_max)
    step = paso_de(A, B)
    v = vivir(u, step, 0, vida, False)
    m = medir(u, step, v["x"], futuro, est, {})
    # --- coste intrínseco del mundo, con el identificador exacto y el criterio fuerte
    ue = Unidad(n_max=n_max)
    x, ultimo, t0, motivo = 0, 0, time.perf_counter(), None
    for t, a in enumerate(vida, start=1):
        p = ue.predecir(a)
        x, o = step(x, a)
        if (p if p is not None else 0) != o:
            ultimo = t
        try:
            ue.leer(a, o)
        except RuntimeError:
            motivo = "tope_de_estados"
            break
        if (t & 1023) == 0 and time.perf_counter() - t0 > TOPE_EXACTO_S:
            motivo = "tope_de_reloj"
            break
    if motivo is None:
        iso = (canonica(ue.trans, 0) == canon)
        motivo = "isomorfa" if iso else "maquina_distinta"
    else:
        iso = False
    coste_mundo = (ultimo + 1) if motivo == "isomorfa" else None
    caro_unidad = bool((not m["identifica"]) or (v["ultimo_error"] + 1) > UMBRAL_CARO)
    caro_mundo = bool(motivo != "isomorfa" or coste_mundo > UMBRAL_CARO)
    return dict(idx=idx, n=n, n_min=n_min,
                estados_alcanzables=len(est),
                # --- columna 1: el MUNDO (identificador exacto, criterio fuerte)
                coste_mundo=coste_mundo, mundo_resuelto=(motivo == "isomorfa"),
                mundo_motivo=motivo, mundo_estados=ue.n,
                caro_por_el_mundo=caro_mundo,
                # --- columna 2: ESTA unidad (ventana 512, presupuesto 200 000, con olvido)
                coste_barato=(v["ultimo_error"] + 1),
                identifica_al_final=bool(m["identifica"]),
                exactitud_final=m["exactitud"],
                olvidos=v["agotado"], pasos=len(vida),
                caro=caro_unidad,
                caro_solo_por_el_olvido=bool(caro_unidad and not caro_mundo),
                # --- banco madre: resuelto por el exacto Y caro por el mundo
                banco_madre=bool(motivo == "isomorfa" and coste_mundo > UMBRAL_CARO))


def campana(out, n, cuantos, trabajadores, ruta, tope_s):
    vida = shortlex(range(1, L_de(n) + 1))
    futuro = shortlex((n, n + 1))
    n_max = n + 2
    total = total_sistemas(n)
    paso, idx = paso_coprimo(total, cuantos, n, 2 * n)
    muestreo_verificado(idx, n, 2 * n, f"muestra de sistemas de {n} estados")
    out.write(f"n={n}: espacio {total} sistemas; muestra {cuantos} con paso coprimo {paso} "
              f"(verificado: las {2*n} posiciones libres); vida {len(vida)} pasos; "
              f"futuro fijo {len(futuro)}; tope de estados {n_max}; "
              f"exigencia n_min >= {N_MIN_EXIGIDO}; caro = no identifica o "
              f"coste > {UMBRAL_CARO}\n")
    tareas = [(i, n, vida, futuro, n_max) for i in idx]
    no_vacio(tareas, f"sistemas a medir de {n} estados")
    t0 = time.perf_counter()
    filas, cortado = [], False
    with open(ruta, "w", encoding="utf-8") as f:
        if trabajadores > 1:
            import multiprocessing as mp
            with mp.get_context("fork").Pool(trabajadores) as pool:
                for fila in pool.imap(_un_sistema, tareas, chunksize=4):
                    filas.append(fila)
                    f.write(json.dumps(fila, ensure_ascii=False) + "\n")
                    f.flush()
                    os.fsync(f.fileno())          # sobrevive un corte de luz (E-29)
                    if time.perf_counter() - t0 > tope_s:
                        cortado = True
                        pool.terminate()
                        break
        else:
            for t in tareas:
                fila = _un_sistema(t)
                filas.append(fila)
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
                if time.perf_counter() - t0 > tope_s:
                    cortado = True
                    break
    reloj = time.perf_counter() - t0
    medidos = [r for r in filas if "coste_barato" in r]
    out.write(f"  medidos {len(filas)} de {cuantos} ({'CORTADO por reloj' if cortado else 'completo'}), "
              f"{reloj:.0f} s; con n_min >= {N_MIN_EXIGIDO}: {len(medidos)}\n")
    if not medidos:
        out.write("  sin sistemas que pasen la exigencia de n_min: nada que seleccionar\n")
        return filas, {}
    pc = lambda v, fr: v[min(len(v) - 1, int(fr * len(v)))] if v else None
    # --- columna 1 · EL MUNDO (identificador exacto, criterio de isomorfismo)
    resueltos = [r for r in medidos if r["mundo_resuelto"]]
    cm = sorted(r["coste_mundo"] for r in resueltos)
    motivos = dict(sorted(Counter(r["mundo_motivo"] for r in medidos).items()))
    caros_m = [r for r in medidos if r["caro_por_el_mundo"]]
    banco = [r for r in medidos if r["banco_madre"]]
    # --- columna 2 · ESTA unidad (ventana y presupuesto de 08, con olvido)
    caros_u = [r for r in medidos if r["caro"]]
    solo_olvido = [r for r in medidos if r["caro_solo_por_el_olvido"]]
    cu = sorted(r["coste_barato"] for r in medidos if r["identifica_al_final"])
    olv_c = [r["olvidos"] for r in caros_u]
    olv_b = [r["olvidos"] for r in medidos if not r["caro"]]
    res = dict(n=n, muestra=cuantos, medidos=len(filas), con_nmin=len(medidos),
               paso_coprimo=paso, cortado=cortado, reloj=round(reloj, 1),
               motivos_del_exacto=motivos,
               mundo_resueltos=len(resueltos),
               mundo_coste_mediana=(cm[len(cm) // 2] if cm else None),
               mundo_coste_p90=pc(cm, .90), mundo_coste_maximo=(cm[-1] if cm else None),
               caros_por_el_mundo=len(caros_m),
               banco_madre=len(banco),
               banco_madre_indices=[r["idx"] for r in banco],
               banco_madre_nmin=dict(sorted(Counter(r["n_min"] for r in banco).items())),
               banco_madre_coste_mediana=(sorted(r["coste_mundo"] for r in banco)[len(banco) // 2]
                                          if banco else None),
               unidad_caros=len(caros_u), caros_solo_por_el_olvido=len(solo_olvido),
               unidad_coste_mediana=(cu[len(cu) // 2] if cu else None),
               unidad_coste_p90=pc(cu, .90),
               olvidos_en_caros=(sum(olv_c) / len(olv_c) if olv_c else None),
               olvidos_en_baratos=(sum(olv_b) / len(olv_b) if olv_b else None),
               n_min_distribucion=dict(sorted(Counter(r["n_min"] for r in medidos).items())))
    out.write(f"  n_min en la muestra: {res['n_min_distribucion']}\n")
    out.write(f"  --- columna 1 · EL MUNDO (identificador exacto de la Fase 1: sin ventana, sin "
              f"olvido; criterio de isomorfismo con la mínima verdadera)\n")
    out.write(f"      el exacto: {motivos}\n")
    out.write(f"      coste intrínseco sobre los {len(resueltos)} que resuelve: mediana "
              f"{res['mundo_coste_mediana']}, p90 {res['mundo_coste_p90']}, máximo "
              f"{res['mundo_coste_maximo']}\n")
    out.write(f"      CAROS POR EL MUNDO: {len(caros_m)} "
              f"({100 * len(caros_m) / len(medidos):.1f} %)\n")
    out.write(f"  --- columna 2 · ESTA unidad (ventana 512, presupuesto 200 000, con olvido; "
              f"criterio del futuro fijo)\n")
    out.write(f"      coste para la unidad sobre los {len(cu)} que 'identifica': mediana "
              f"{res['unidad_coste_mediana']}, p90 {res['unidad_coste_p90']}\n")
    out.write(f"      caros para la unidad: {len(caros_u)}; de ésos, CARO SÓLO POR EL OLVIDO: "
              f"{len(solo_olvido)} ({100 * len(solo_olvido) / max(1, len(caros_u)):.1f} %)\n")
    out.write(f"      olvidos por vida: {res['olvidos_en_caros']:.1f} en los caros contra "
              f"{res['olvidos_en_baratos']:.1f} en los baratos"
              f"{'  ← la etiqueta mide el instrumento si difiere en un orden de magnitud (E-53)' if res['olvidos_en_caros'] and res['olvidos_en_baratos'] and res['olvidos_en_caros'] > 10 * res['olvidos_en_baratos'] else ''}\n")
    out.write(f"  --- BANCO MADRE (el exacto SÍ lo resuelve Y le cuesta > {UMBRAL_CARO}): "
              f"{len(banco)} mundos · n_min {res['banco_madre_nmin']} · coste mediano "
              f"{res['banco_madre_coste_mediana']}\n")
    return filas, res


def puerta(R, out):
    g = {}
    for n, r in sorted(R.items()):
        if not r:
            continue
        g[f"n={n}: hay BANCO MADRE (el exacto lo resuelve y le cuesta > {UMBRAL_CARO})"] = \
            r["banco_madre"] > 0
        g[f"n={n}: el coste INTRÍNSECO mediano supera el primer hito de la curva (64)"] = \
            bool(r["mundo_coste_mediana"] and r["mundo_coste_mediana"] > 64)
        g[f"n={n}: la muestra pasó la verificación de retículo (E-27/E-51)"] = True
        # E-53: si la etiqueta de la unidad está dominada por el olvido, se dice
        oc, ob = r.get("olvidos_en_caros"), r.get("olvidos_en_baratos")
        if oc is not None and ob is not None:
            g[f"n={n}: la etiqueta de la unidad NO está dominada por el olvido "
              f"({oc:.1f} contra {ob:.1f} olvidos por vida)"] = not (oc > 10 * max(ob, 1e-9))
        g[f"n={n}: los caros SÓLO por el olvido son minoría de los caros de la unidad "
          f"({r['caros_solo_por_el_olvido']} de {r['unidad_caros']})"] = \
            r["caros_solo_por_el_olvido"] * 2 <= max(1, r["unidad_caros"])
    out.write("--- puerta del mundo caro\n")
    for k, v in sorted(g.items()):
        out.write(f"  [{'PASS' if v else 'FAIL'}] {k}\n")
    hay = any(r.get("banco_madre", 0) > 0 for r in R.values() if r)
    out.write(f"\n⇒ {'La Fase 3 TIENE banco madre.' if hay else 'NO hay banco madre: la Fase 3 no se corre con este banco.'}\n")
    out.write("   El banco madre se elige por la COLUMNA 1 (el mundo), nunca por la 2 (E-53):\n"
              "   un mundo caro por el olvido es un defecto de disposición, no un mundo caro.\n"
              "   Los índices van en el JSON (`banco_madre_indices`) y en las filas con el campo\n"
              "   `banco_madre`; la ficha de la Fase 3 los toma de ahí y no los vuelve a elegir.\n")
    return g


def main(tamanos=(6, 8), trabajadores=1, cuantos=None, aqui=None):
    buf = io.StringIO()
    R = {}
    for n in tamanos:
        ruta = os.path.join(aqui, "artifacts", f"unidad_minima_12_mundo_caro_n{n}.jsonl")
        salida_a_fichero(ruta, f"filas de n={n}")
        _, R[n] = campana(buf, n, cuantos or MUESTRA[n], trabajadores, ruta, TOPE_RELOJ_S[n])
    g = puerta(R, buf)
    return buf.getvalue(), R, g


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "artifacts"), exist_ok=True)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cuantos = int(args[0]) if args else None
    trab = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--trabajadores=")), 1)
    tam = tuple(int(a.split("=")[1]) for a in sys.argv if a.startswith("--n="))
    t1, R, g = main(tam or (6, 8), trab, cuantos, here)
    sys.stdout.write(t1)
    azar = sin_azar_usado(["unidad_minima_12_mundo_caro", "unidad_minima_08_fase2",
                           "unidad_minima_05_banco", "unidad_minima_02_incremental",
                           "unidad_minima_01"])
    sys.stdout.write(f"azar usado: {azar}; arranque {ARRANQUE}; sha256 de 12 al arrancar: "
                     f"{SHA_12[:16]}…\n")
    informe()
    suf = f"_pilot{cuantos}" if cuantos else ""
    with open(os.path.join(here, "artifacts", f"unidad_minima_12_mundo_caro{suf}.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(resumen=R, puerta=g, sha256_codigo=SHA_12, arranque=ARRANQUE,
                       python=sys.version, texto=t1), f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-11 · ¿puede una célula conservar una capacidad mientras cambia su
organización interna, y usar esa organización transformada para aprender algo NUEVO?

LA PREGUNTA ES DE WIS (28-oct-2026) y es más profunda que «heredar ahorra pasos»: pide
**dos** propiedades seguidas, y sólo las dos juntas serían una forma elemental de
desarrollo cognitivo acumulativo.

  (1) CONSERVACIÓN FUNCIONAL CON ORGANIZACIÓN TRANSFORMADA.
      Medido ya, en la cadena de cinco generaciones de `unidad_minima_10_maestro.py`:
      la generación k identifica W₂ (función conservada: alcance 1,000 en las cuatro
      generaciones de la clase componible) mientras su máquina **no** es isomorfa a la de
      la generación 1 (forma transformada: isomorfa a la primera sólo 0,49, y a la
      anterior 0,53 → 0,86 → 0,95 → 0,955, o sea que la cadena converge a una forma
      ESTABLE que en la mitad de los linajes no es la del ancestro).
  (2) ADQUISICIÓN POSTERIOR. **Es lo que mide este módulo.** La organización transformada
      tiene que servir de BASE para aprender un mundo nuevo: W₃, la cascada más chica que
      la máquina de W₂ no explica (criterio de Guerin), de 12 estados.

Los brazos, y qué afirmación separa cada uno:

  A-fresca     fresca en W₃                              la vara
  A-directa    la máquina de una unidad que aprendió W₂  organización adquirida POR SÍ MISMA
               por su cuenta, sin traza
  A-K5         la máquina de la generación 5 de la       organización CONSERVADA a través de
               cadena, sin traza                          cinco transmisiones y transformada
  A-K5-lesion  la de K5, colapsada (`lesion`)            separa «tener esta organización» de
                                                          «haber vivido cinco generaciones»

  · A-K5 > A-fresca  ⇒ la organización transformada **sirve de base**: adquisición posterior.
  · A-K5 ≈ A-directa ⇒ pasar por el linaje **no degrada** la base. Con (1), eso es
    desarrollo acumulativo: la capacidad se conserva, la forma cambia, y la forma cambiada
    sigue sirviendo para lo siguiente.
  · A-K5 ≈ A-K5-lesion ⇒ lo que importa no era la organización. Falsador del brazo.

PRECONDICIÓN DEL BANCO, ANTES DE LEER NADA (E-50, el error de hoy). Lo que los brazos
heredan es la máquina de W₂; si la fresca identifica W₃ **antes** del primer hito, la
herencia no tiene dónde mostrarse y el resultado es `NULO POR TECHO DEL DISEÑO`, lo mida
como lo mida. Se mide el coste de W₃ para la fresca y se compara con `min(HITOS_3)`; si no
lo excede, la campaña **no se lee**.

Sin azar. El cómputo se registra y no decide (norma de Wis).
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
import unidad_minima_08_fase2 as m8                                      # noqa: E402
import unidad_minima_09_fase2 as m9                                      # noqa: E402
import unidad_minima_10_maestro as m10                                   # noqa: E402
from unidad_minima_01 import LETTERS, lesion, predict, run_world, shortlex  # noqa: E402
from unidad_minima_05_banco import (                                     # noqa: E402
    alcanzables, canonica, cociente, mealy_verdadera, minimizar, paso_de, sistema_por_indice,
)
from unidad_minima_08_fase2 import N1, UnidadFase2, medir, mundo_2, mundos_1, patrones, verdad, vivir  # noqa: E402
from unidad_minima_09_fase2 import UnidadC5                              # noqa: E402
from guardas import (  # noqa: E402
    informe, muestreo_verificado, no_vacio, salida_a_fichero, sin_azar_usado,
)

SHA_11 = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
ARRANQUE = time.strftime("%Y-%m-%dT%H:%M:%S")

N3 = 4 * N1                  # W₃ tiene 12 estados: la cascada componible sobre W₂
N_MAX_3 = N3 + 2             # tope de estados en W₃. DISPOSICIÓN SUMINISTRADA, a ojo, +2
                             # sobre el mínimo verdadero, igual que en W₂ (8 para 6)
LARGO_VIDA_3 = 10            # la vida en W₃ es el prefijo shortlex hasta longitud 10.
                             # L_de(12) = 14 daría 425 986 pasos por celda, impagable; con
                             # 10 son 18 434. DECLARADO: con este presupuesto la
                             # identificación de W₃ puede quedar incompleta, y por eso la
                             # medida es la CURVA y la comparación es ENTRE BRAZOS con el
                             # mismo presupuesto, no un sí/no absoluto
LARGO_FUTURO_3 = 12          # el futuro fijo es el bloque shortlex COMPLETO de las palabras
                             # de longitud 12: 4 096 palabras, 49 152 pasos. Dos estados
                             # distintos de una máquina mínima de n <= 12 se separan con una
                             # palabra de longitud < 12, así que el bloque completo las
                             # contiene todas. No se muestrea NADA, y con eso el defecto de
                             # muestreo (E-51) desaparece en vez de mitigarse: evaluar es
                             # barato —predecir, sin aprender— y yo lo había confundido con
                             # el coste de VIVIR, que es el que no se puede pagar
HITOS_3 = (64, 128, 256, 512, 1024, 2048, 8192)
NMIN3_MINIMO = 6            # SELECCIÓN ESTRUCTURAL, declarada. La primera prueba de
                            # instrumento (un mundo) salió inútil: duplicar los estados a 12
                            # no hace al mundo difícil —su máquina MÍNIMA era de 5 estados y
                            # los cuatro brazos identificaban en el hito 256—. Se exige que
                            # W₃ tenga al menos 8 estados mínimos, que es el punto donde la
                            # Fase 1 midió que identificar se degrada (CIERRE_FASE_1.md §3).
                            # Se selecciona por una propiedad DEL MUNDO, nunca por el
                            # rendimiento del control, que sesgaría la vara.
                            #
                            # Y con TECHO además de suelo: con n_min(W3) >= 8 la segunda
                            # prueba de instrumento dio los cuatro brazos IDÉNTICOS porque
                            # los cuatro se ahogan —42 olvidos por celda y 3 estados finales
                            # en un mundo de 12—. Un resultado donde todos los brazos
                            # coinciden porque todos fracasan es tan nulo como uno donde
                            # coinciden porque todos aciertan: `NULO POR SUELO`. La banda
                            # 6..8 es la que la Fase 1 midió como «cuesta y aún se logra».
NMIN3_MAXIMO = 8
GENERACIONES = m10.GENERACIONES
BRAZOS = ("A-fresca", "A-directa", "A-K5", "A-K5-lesion")


def alcanzables_desde(A, B, x0):
    """Lo alcanzable DESDE DONDE LA UNIDAD EMPIEZA, no desde el estado 0.

    DEFECTO CORREGIDO ANTES DE LEER NADA (E-52). `alcanzables` de 05 arranca siempre en el
    estado 0, y con él `verdad` y todos los `n_min` del programa. Pero en la Fase 2 la unidad
    **no** empieza en el 0: empieza donde la quedó el mundo anterior. Si desde ahí sólo se
    alcanzan dos estados —y la Fase 1 ya había medido que estos mundos tienen transitorios
    estructurales, puertas de ida sin vuelta (`M ⇒ T`)—, el mundo «de 8 estados mínimos» que
    la unidad enfrenta es en realidad de dos, y el experimento mide otra cosa que la que
    dice. En la primera corrida de esta celda eso dio brazos con 2,35 estados finales
    «identificando» mundos de n_min 6 a 8, con exactitud 0,9994: un banco difícil sobre el
    papel y trivial en la mano.
    """
    vistos, cola = {x0}, [x0]
    while cola:
        x = cola.pop()
        for T in (A, B):
            y = T[x]
            if y not in vistos:
                vistos.add(y)
                cola.append(y)
    return sorted(vistos)


def verdad_desde(A, B, x0):
    """El mínimo verdadero de la parte del mundo que la unidad puede alcanzar."""
    est = alcanzables_desde(A, B, x0)
    Tv = mealy_verdadera(A, B, est)
    n_min, bloque = minimizar(Tv, est)
    # `cociente` de 05 no sirve aquí: devuelve `bloque[0]` como estado inicial y el estado 0
    # puede no estar ni en el conjunto alcanzable desde x0. El cociente se arma igual que
    # allí y el inicial es el bloque de x0.
    Mmin = {}
    for x in est:
        for a in LETTERS:
            y, o = Tv[(x, a)]
            Mmin[(bloque[x], a)] = (bloque[y], o)
    return est, n_min, canonica(Mmin, bloque[x0])


def mundo_3(A2, B2, n2, patron):
    """W₃ = el mismo cerrojo de 08, una capa más arriba: la cascada componible sobre W₂.
    Componible a propósito: es el caso donde las distinciones de W₂ SIGUEN siendo
    congruencia, o sea donde la organización de W₂ puede servir de base. Si ni ahí sirve,
    no sirve."""
    return mundo_2(A2, B2, n2, patron, True)


def futuro_de(n):
    """El futuro fijo: el bloque shortlex COMPLETO de las palabras de longitud 12.

    DOS DEFECTOS, LOS DOS ATRAPADOS ANTES DE LEER NADA (E-51). (1) La primera versión
    truncaba el bloque a 2 048 pasos: eso son las 170 primeras palabras de longitud 12, y
    **todas empiezan por ocho A** —medido, cubrían 3 de los 64 prefijos de seis letras—.
    Con ese futuro una máquina de 3 estados «identificaba» un mundo de 12. Es el retículo
    de E-27 en otro objeto: truncar un bloque shortlex clava las letras de orden alto igual
    que un paso con factores comunes clavaba los dígitos bajos. (2) El arreglo por
    permutación de bits invertidos **también** falló y lo cazó `muestreo_verificado`: un
    prefijo de un orden de bits invertidos clava las posiciones espejadas. Y un paso
    coprimo, que sí pasa la guarda, seguía dejando al brazo fresco con menos estados que el
    mínimo verdadero.

    La salida no era muestrear mejor: era **no muestrear**. Evaluar el futuro es predecir
    sin aprender, y eso es barato; yo lo había confundido con el coste de VIVIR, que es el
    que no se puede pagar. El bloque completo son 49 152 pasos y contiene toda palabra de
    longitud < 12, que es lo que separa dos estados cualesquiera de una máquina mínima de
    hasta 12.
    """
    # El bloque completo, sin muestrear. La guarda se deja puesta de todos modos: sobre el
    # espacio entero pasa trivialmente, y si alguien vuelve a truncar esto, salta.
    k = LARGO_FUTURO_3
    todas = list(range(2 ** k))
    muestreo_verificado(todas, 2, k, "palabras del futuro fijo de W3")
    return [c for i in todas for c in
            ("A" if b == "0" else "B" for b in format(i, f"0{k}b"))]


def _mide(u, step, x, futuro):
    verdad_fut, _ = run_world(step, x, futuro)
    hits, nr, _ = predict(u.trans, u.q, futuro, verdad_fut)
    return dict(exactitud=hits / len(futuro), identifica=(hits == len(futuro) and nr == 0),
                sin_ruta=nr)


def vivir_3(u, step, x, itinerario, futuro):
    """Vivir W₃ sin maestro y sin elegir: el mismo mecanismo de 08, con la curva en los
    hitos de W₃ y la medida de final de vida devuelta aparte (defecto corregido en 10)."""
    curva = {}
    for t in range(1, len(itinerario) + 1):
        if t - 1 in HITOS_3:
            curva[t - 1] = _mide(u, step, x, futuro)
        a = itinerario[t - 1]
        p = u.predecir(a)
        if p is None:
            p = 0
        x, o = step(x, a)
        u.leer(a, o)
    fin = _mide(u, step, x, futuro)
    for h in HITOS_3:
        curva.setdefault(h, fin)
    return dict(x=x, curva=curva, fin=fin)


def _coste_propio(u_clase, step, x, itinerario, futuro, n_max, tope):
    """E-50 · cuánto le cuesta a la FRESCA identificar este mundo por su cuenta: el primer
    paso desde el que su hipótesis predice el futuro fijo sin un error y no vuelve a
    perderlo. Se comprueba cada `tope` pasos para que sea pagable, y se informa el tamaño
    del paso de rejilla junto al número: una cota superior con su resolución."""
    u = u_clase(n_max=n_max)
    primero = None
    for t in range(1, len(itinerario) + 1):
        a = itinerario[t - 1]
        p = u.predecir(a)
        if p is None:
            p = 0
        x, o = step(x, a)
        u.leer(a, o)
        if t % tope == 0:
            if _mide(u, step, x, futuro)["identifica"]:
                if primero is None:
                    primero = t
            else:
                primero = None
    return primero, tope


def una_familia(idx, patron2, patron3, vida1, vida2, vida3, fut2, fut3, con_coste=False):
    A, B = sistema_por_indice(N1, idx)
    A2, B2 = mundo_2(A, B, N1, patron2, True)
    A3, B3 = mundo_3(A2, B2, 2 * N1, patron3)
    step1, step2, step3 = paso_de(A, B), paso_de(A2, B2), paso_de(A3, B3)
    est3 = alcanzables(A3, B3)
    _, nmin3_desde_0, _ = verdad(A3, B3)
    n_max_2 = 2 * N1 + 2
    # --- W1, y el punto donde el mundo cambia
    madre = UnidadFase2(n_max=n_max_2)
    v1 = vivir(madre, step1, 0, vida1, False)
    x2 = v1["x"]
    # --- W2: la unidad que lo aprende POR SU CUENTA (es la maestra de la generación 1)
    directa = UnidadFase2(n_max=n_max_2)
    v2 = vivir(directa, step2, x2, vida2, False)
    x3 = v2["x"]                       # el punto por el que todos los brazos entran a W₃
    m2 = medir(directa, step2, v2["x"], fut2, alcanzables(A2, B2), {})
    canon_1 = canonica(directa.trans, directa.q)
    # --- la cadena de cinco generaciones en W2, exactamente la de 10
    tope_palabra = m10._tope_palabra(n_max_2)
    M_prev, q_prev = dict(directa.trans), directa.q
    gen = []
    for k in range(2, GENERACIONES + 1):
        u = UnidadFase2(n_max=n_max_2)
        vk = m10.vivir_con_maestro(
            u, step2, x2, vida2,
            m10.MaestroUnidad(M_prev, q_prev, tope_palabra, canal="ve_la_hipotesis",
                              disparo="siempre"),
            fut2, True, False)
        mk = medir(u, step2, vk["x"], fut2, alcanzables(A2, B2), {})
        gen.append(dict(k=k, identifica=mk["identifica"], estados=u.n,
                        isomorfa_a_la_primera=(canonica(u.trans, 0) == canon_1)))
        M_prev, q_prev, u_k = dict(u.trans), u.q, u
    k5 = u_k
    # --- W3: los cuatro brazos, mismo presupuesto, desde el mismo estado del mundo
    filas = []
    est3_desde, nmin3, _ = verdad_desde(A3, B3, x3)
    base = dict(w1=idx, patron2=f"{patron2[0]}@{patron2[1]}", patron3=f"{patron3[0]}@{patron3[1]}",
                n_min_w3=nmin3, n_min_w3_desde_0=nmin3_desde_0,
                estados_alcanzables_desde_x3=len(est3_desde),
                w2_identificado_directa=m2["identifica"],
                w2_identificado_k5=gen[-1]["identifica"],
                k5_isomorfa_a_la_primera=gen[-1]["isomorfa_a_la_primera"],
                generaciones=gen)
    for brazo in BRAZOS:
        if brazo == "A-fresca":
            u = UnidadFase2(n_max=N_MAX_3)
        else:
            fuente = directa if brazo == "A-directa" else k5
            u = UnidadC5(n_max=N_MAX_3)
            u.heredar(fuente)
            u.n_max = N_MAX_3
            if brazo == "A-K5-lesion":
                u.trans, u.heredadas, u.original, u.choices = lesion(u.trans), set(), {}, []
                u.q, u.n, u.used = 0, 1, 1
        v3 = vivir_3(u, step3, x3, vida3, fut3)
        # El futuro se predice desde donde la vida en W₃ dejó a la unidad, que puede ser un
        # núcleo recurrente más chico que lo alcanzable desde x₃ (los transitorios
        # estructurales de la Fase 1). Comparar sus estados contra el n_min desde x₃ sería
        # comparar dos mundos distintos, así que se mide el n_min DESDE EL ARRANQUE DEL
        # FUTURO, que es el único con el que la cuenta de estados es comparable.
        _, nmin_fut, _ = verdad_desde(A3, B3, v3["x"])
        f = medir(u, step3, v3["x"], fut3, est3,
                  dict(brazo=brazo, curva=v3["curva"], olvidos=u.c["olvidos"],
                       olvidados=u.c["pasos_olvidados"],
                       heredadas=u.c.get("transiciones_heredadas", 0),
                       revisadas=u.c.get("transiciones_heredadas_revisadas", 0),
                       supervivientes=(u.supervivientes() if isinstance(u, UnidadC5) else 0),
                       n_min_desde_futuro=nmin_fut))
        f.update(base)
        f["repertorio"] = f["escribe"] + f["permuta"]
        f["curva"][len(vida3)] = v3["fin"]
        filas.append(f)
    if con_coste:
        primero, rejilla = _coste_propio(UnidadFase2, step3, x3, vida3, fut3, N_MAX_3, 64)
        for f in filas:
            f["coste_w3_fresca"] = primero
            f["coste_w3_rejilla"] = rejilla
    return filas


def _una_w1(args):
    idx, vida1, vida2, vida3, fut2, fut3, con_coste = args
    A, B = sistema_por_indice(N1, idx)
    _, nmin1, _ = verdad(A, B)
    filas = []
    # De todas las cascadas posibles sobre este W1 se toma la MÁS DIFÍCIL **para la unidad
    # que llega**, es decir la de mayor n_min medido DESDE EL ESTADO EN QUE LA UNIDAD ENTRA
    # a W₃ (E-52), no desde el estado 0. Los empates los rompe el orden canónico de los
    # patrones. Dos etapas, para que sea pagable: x₂ sólo depende de W₁, y x₃ de haber
    # vivido W₂ con cada `patron2` (nueve vidas por W₁); desde ahí los 36 `patron3` se
    # evalúan sin vivir nada.
    n_max_2 = 2 * N1 + 2
    madre0 = UnidadFase2(n_max=n_max_2)
    x2 = vivir(madre0, paso_de(A, B), 0, vida1, False)["x"]
    mejor = None
    for patron2 in patrones(N1):
        A2, B2 = mundo_2(A, B, N1, patron2, True)
        _, nmin2, _ = verdad(A2, B2)
        if nmin2 <= nmin1:
            continue
        u2 = UnidadFase2(n_max=n_max_2)
        x3 = vivir(u2, paso_de(A2, B2), x2, vida2, False)["x"]
        _, nmin2_desde, _ = verdad_desde(A2, B2, x2)
        for patron3 in patrones(2 * N1):
            A3, B3 = mundo_3(A2, B2, 2 * N1, patron3)
            _, nmin3, _ = verdad_desde(A3, B3, x3)
            if nmin3 <= nmin2_desde:
                continue
            if mejor is None or nmin3 > mejor[0]:
                mejor = (nmin3, patron2, patron3)
    if mejor is None or not (NMIN3_MINIMO <= mejor[0] <= NMIN3_MAXIMO):
        return []
    filas.extend(una_familia(idx, mejor[1], mejor[2], vida1, vida2, vida3,
                             fut2, fut3, con_coste))
    return filas


def campana(out, limite_w1=None, trabajadores=1, con_coste=True):
    vida1 = shortlex(range(1, N1 + 3))
    vida2 = shortlex(range(1, 2 * N1 + 3))
    vida3 = shortlex(range(1, LARGO_VIDA_3 + 1))
    fut2 = shortlex((2 * N1, 2 * N1 + 1))
    fut3 = futuro_de(N3)
    out.write(f"W1 {N1} estados, vida {len(vida1)} · W2 {2*N1}, vida {len(vida2)} · "
              f"W3 {N3}, vida {len(vida3)}, futuro fijo {len(fut3)} pasos (palabras de "
              f"longitud {LARGO_FUTURO_3}, truncado) · tope de estados en W3 {N_MAX_3} · "
              f"brazos {', '.join(BRAZOS)} · hitos {HITOS_3} · se exige "
              f"{NMIN3_MINIMO} <= n_min(W3) <= {NMIN3_MAXIMO}\n")
    elegibles = mundos_1(vida1, fut2 and shortlex((N1 + 1, N1 + 2)), 2 * N1 + 2, out)
    no_vacio(elegibles, "mundos W1 elegibles")
    orden = m8 and elegibles
    if limite_w1:
        # recorrido esparcido, no prefijo: un prefijo no representa el banco (lección de la
        # Fase 1), así que la muestra se toma con la permutación de bits invertidos
        idx_esparcido = sorted(range(len(orden)),
                               key=lambda i: int(format(i, "016b")[::-1], 2))
        orden = [orden[i] for i in idx_esparcido][:limite_w1]
    tareas = [(idx, vida1, vida2, vida3, fut2, fut3, con_coste) for idx in orden]
    no_vacio(tareas, "tareas")
    t0 = time.perf_counter()
    if trabajadores > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(trabajadores) as pool:
            res = pool.map(_una_w1, tareas, chunksize=1)
    else:
        res = [_una_w1(t) for t in tareas]
    filas = [f for r in res for f in r]
    no_vacio(filas, "filas medidas")
    nf = len(filas) // len(BRAZOS)
    out.write(f"mundos W1 mirados: {len(orden)} · familias (W1,W2,W3) en la banda "
              f"[{NMIN3_MINIMO}, {NMIN3_MAXIMO}]: {nf} · reloj {time.perf_counter() - t0:.1f} s\n")
    if filas:
        nm = sorted({(f["w1"], f["n_min_w3"]) for f in filas})
        out.write(f"  n_min de W3 en el banco: mínimo {min(v for _, v in nm)}, "
                  f"máximo {max(v for _, v in nm)}\n")
    return filas


def resumen(filas, out):
    hitos = sorted({int(k) for f in filas for k in f["curva"]})
    # --- PRECONDICIÓN primero: si W3 es barato para la fresca, no se lee nada más
    costes = sorted(f["coste_w3_fresca"] for f in filas
                    if f.get("coste_w3_fresca") is not None)
    nunca = sum(1 for f in filas if "coste_w3_fresca" in f and f["coste_w3_fresca"] is None)
    primer_hito = min(HITOS_3)
    pre = dict(medidos=len(costes), nunca_identifica=nunca, primer_hito=primer_hito)
    if costes:
        pre.update(minimo=costes[0], mediana=costes[len(costes) // 2], maximo=costes[-1],
                   antes_del_primer_hito=sum(1 for c in costes if c < primer_hito))
    pre["suficiente"] = bool(nunca) or (costes and costes[len(costes) // 2] > primer_hito)
    out.write(f"\nPRECONDICIÓN DEL BANCO (E-50) · coste de W3 para la fresca: "
              f"{pre.get('mediana', '—')} pasos de mediana sobre {pre['medidos']} celdas que lo "
              f"logran, y {nunca} que NO lo logran en toda su vida; primer hito {primer_hito}\n"
              f"  ⇒ {'W3 es CARO para la fresca: la organización heredada tiene dónde mostrarse' if pre['suficiente'] else 'W3 es BARATO: cualquier resultado es NULO POR TECHO DEL DISEÑO'}\n\n")
    R = dict(precondicion=pre)
    out.write(f"{'brazo':<14}{'fam.':>6}{'alcance':>9}{'exact.':>9}{'estados':>9}{'repert.':>9}"
              f"{'olvidos':>9}{'hered.':>8}{'revis.':>8}{'superv.':>9}\n")
    for b in BRAZOS:
        Fb = [f for f in filas if f["brazo"] == b]
        if not Fb:
            continue
        k = len(Fb)
        g = lambda c: sum(f.get(c, 0) or 0 for f in Fb) / k
        r = dict(familias=k, alcance=sum(bool(f["identifica"]) for f in Fb) / k,
                 exactitud=g("exactitud"), estados=g("estados"), repertorio=g("repertorio"),
                 olvidos=g("olvidos"), heredadas=g("heredadas"), revisadas=g("revisadas"),
                 supervivientes=g("supervivientes"),
                 curva_alcance={h: sum(bool(f["curva"][h]["identifica"]) for f in Fb) / k
                                for h in hitos},
                 curva_exactitud={h: sum(f["curva"][h]["exactitud"] for f in Fb) / k
                                  for h in hitos})
        R[b] = r
        out.write(f"{b:<14}{k:>6}{r['alcance']:>9.3f}{r['exactitud']:>9.4f}{r['estados']:>9.2f}"
                  f"{r['repertorio']:>9.2f}{r['olvidos']:>9.1f}{r['heredadas']:>8.2f}"
                  f"{r['revisadas']:>8.1f}{r['supervivientes']:>9.2f}\n")
    for nombre, campo in (("alcance", "curva_alcance"), ("exactitud sobre el futuro fijo", "curva_exactitud")):
        out.write(f"curva de {nombre} en W3 por pasos vividos:\n")
        out.write(f"{'brazo':<14}" + "".join(f"{h:>9}" for h in hitos) + "\n")
        for b in BRAZOS:
            if b not in R:
                continue
            out.write(f"{b:<14}" + "".join(f"{R[b][campo][h]:>9.4f}" for h in hitos) + "\n")
    # --- la cadena en W2: conservación funcional con organización transformada
    una = [f for f in filas if f["brazo"] == "A-fresca"]
    if una:
        out.write("\nconservación funcional con organización transformada (la cadena en W2):\n")
        out.write(f"{'gen':<6}{'identifica W2':>15}{'isomorfa a la 1ª':>18}{'estados':>9}\n")
        cad = {}
        for k in range(2, GENERACIONES + 1):
            g = [gg for f in una for gg in f["generaciones"] if gg["k"] == k]
            if not g:
                continue
            cad[k] = dict(familias=len(g),
                          identifica=sum(bool(x["identifica"]) for x in g) / len(g),
                          isomorfa_primera=sum(bool(x["isomorfa_a_la_primera"]) for x in g) / len(g),
                          estados=sum(x["estados"] for x in g) / len(g))
            out.write(f"{k:<6}{cad[k]['identifica']:>15.3f}{cad[k]['isomorfa_primera']:>18.3f}"
                      f"{cad[k]['estados']:>9.2f}\n")
        R["cadena_w2"] = cad
    return R


def puerta(filas, R, out):
    g = {}
    pre = R.get("precondicion", {})
    g["(0) PRECONDICIÓN: W3 es caro para la fresca (si no, todo es nulo por techo)"] = \
        bool(pre.get("suficiente"))
    u = m9.umbral(12)
    def par(a, b, h):
        por = {}
        for f in filas:
            por.setdefault((f["w1"], f["patron2"], f["patron3"]), {})[f["brazo"]] = f
        comunes = [d for d in por.values() if a in d and b in d]
        sa = sum(1 for d in comunes if d[a]["curva"][h]["identifica"] and not d[b]["curva"][h]["identifica"])
        sb = sum(1 for d in comunes if d[b]["curva"][h]["identifica"] and not d[a]["curva"][h]["identifica"])
        n = sa + sb
        z = (abs(sa - sb) - 1) / (n ** 0.5) if n and abs(sa - sb) >= 1 else 0.0
        return sa, sb, z, len(comunes)
    for h in HITOS_3:
        if "A-K5" not in R or "A-fresca" not in R:
            break
        sa, sb, z, n = par("A-K5", "A-fresca", h)
        g[f"(1) ADQUISICIÓN en el hito {h}: A-K5 > A-fresca (pareado, z sobre {u:.2f})"] = \
            (sa > sb and z > u)
        out.write(f"  hito {h}: A-K5 vs A-fresca · sólo K5 en {sa}, sólo fresca en {sb} "
                  f"(de {n}) · z {z:.2f}\n")
    if "A-K5" in R and "A-directa" in R:
        sa, sb, z, n = par("A-K5", "A-directa", max(HITOS_3))
        g["(2) el linaje NO degrada la base: A-K5 ≈ A-directa al final"] = (z <= u)
        out.write(f"  final: A-K5 vs A-directa · sólo K5 en {sa}, sólo directa en {sb} "
                  f"(de {n}) · z {z:.2f}\n")
    if "A-K5" in R and "A-K5-lesion" in R:
        sa, sb, z, n = par("A-K5", "A-K5-lesion", max(HITOS_3))
        g["(3) lo que importa ES la organización: A-K5 > A-K5-lesion"] = (sa > sb and z > u)
        out.write(f"  final: A-K5 vs A-K5-lesion · sólo K5 en {sa}, sólo lesionada en {sb} "
                  f"(de {n}) · z {z:.2f}\n")
    # NULO POR SUELO: si los brazos no se separan Y la vara está en el suelo, no hay
    # resultado — el mismo razonamiento que E-50 por el otro extremo
    if "A-fresca" in R:
        h = max(HITOS_3)
        vals = [R[b]["curva_alcance"][h] for b in BRAZOS if b in R]
        if vals and (max(vals) - min(vals)) < 1e-9 and R["A-fresca"]["curva_alcance"][h] < 0.25:
            g["(6) ⇒ VEREDICTO: NULO POR SUELO (todos los brazos coinciden porque todos "
              "fracasan), no negativo"] = True
    # NULO POR FUTURO CIEGO: si un brazo «identifica» el mundo con MENOS estados que el
    # mínimo verdadero de la parte que alcanza, lo que falla es el futuro fijo, no el brazo
    # (E-51, E-52). Es la comprobación que habría cazado los dos defectos de esta celda.
    F = [f for f in filas if f["brazo"] == "A-fresca"]
    bajos = [f for f in F if f["identifica"] and f["estados"] < f["n_min_desde_futuro"]]
    nmin_medio = sum(f["n_min_desde_futuro"] for f in F) / max(1, len(F))
    est_fresca = R.get("A-fresca", {}).get("estados", 0)
    ciego = bool(bajos)
    g[f"(futuro) el futuro fijo discrimina: ninguna celda «identifica» con MENOS estados que "
      f"el mínimo verdadero desde donde predice (estados {est_fresca:.2f} contra mínimo "
      f"{nmin_medio:.2f}; celdas por debajo: {len(bajos)} de {len(F)})"] = not ciego
    if ciego:
        g["⇒ VEREDICTO: NULO POR FUTURO CIEGO (una máquina más chica que el mínimo "
          "«identifica»: el futuro no mide el mundo)"] = True
    cad = R.get("cadena_w2", {})
    if cad:
        ks = sorted(cad)
        g["(4) CONSERVACIÓN: la última generación identifica W2 igual que la primera"] = \
            cad[ks[-1]]["identifica"] >= 0.95
        g["(5) TRANSFORMACIÓN: la última generación NO es isomorfa a la primera en la mayoría"] = \
            cad[ks[-1]]["isomorfa_primera"] < 0.75
    out.write("--- puerta\n")
    for k, v in sorted(g.items()):
        out.write(f"  [{'PASS' if v else 'FAIL'}] {k}\n")
    out.write("\nLas dos propiedades que Wis pide juntas: (4) y (5) son la conservación con\n"
              "organización transformada; (1) es la adquisición posterior. Las dos a la vez,\n"
              "con (3) activo, serían desarrollo cognitivo acumulativo elemental. Una sola, no.\n")
    return g


def main(limite_w1=None, trabajadores=1, ruta_filas=None, con_coste=True):
    buf = io.StringIO()
    filas = campana(buf, limite_w1, trabajadores, con_coste)
    if ruta_filas:
        m9.guardar_filas(filas, ruta_filas)
    R = resumen(filas, buf)
    g = puerta(filas, R, buf)
    return buf.getvalue(), filas, R, g


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lim = int(args[0]) if args else None
    trab = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--trabajadores=")), 1)
    suf = f"_pilot{lim}" if lim else ""
    os.makedirs(os.path.join(here, "artifacts"), exist_ok=True)
    ruta = os.path.join(here, "artifacts", f"unidad_minima_11_adquisicion{suf}.jsonl")
    salida_a_fichero(ruta, "filas de 11")
    t1, filas, R, g = main(lim, trab, ruta)
    sys.stdout.write(t1)
    azar = sin_azar_usado(["unidad_minima_11_adquisicion", "unidad_minima_10_maestro",
                           "unidad_minima_09_fase2", "unidad_minima_08_fase2",
                           "unidad_minima_02_incremental", "unidad_minima_01"])
    sys.stdout.write(f"azar usado: {azar}; arranque {ARRANQUE}; sha256 de 11 al arrancar: "
                     f"{SHA_11[:16]}…; de 09 {m9.SHA_09[:16]}…; de 08 {m9.SHA_08[:16]}…\n")
    informe()
    with open(os.path.join(here, "artifacts", f"unidad_minima_11_adquisicion{suf}.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(resumen=R, puerta=g, sha256_codigo=SHA_11, arranque=ARRANQUE,
                       python=sys.version, texto=t1), f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())

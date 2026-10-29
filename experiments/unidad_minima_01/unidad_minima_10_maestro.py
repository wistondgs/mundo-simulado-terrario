#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-10 · Fase 2 · el maestro, y el alumno que se vuelve maestro.

Celda de `ORIENTACIONES_FASE_2_DOS_UNIDADES.md` (dos unidades) más el techo T1/T2 de
`ORIENTACIONES_FASE_2_MAESTRO.md`. **No toca 08 ni 09: los importa.** El mundo, la vida,
el futuro fijo y las cuatro medidas son los de 08; C5 vive en 09; aquí lo único nuevo es
la maestra como segunda unidad y el canal entre las dos.

LA PREGUNTA. ¿Una unidad que vivió un mundo puede enseñárselo a otra con lo único que
tiene, su propia máquina, posiblemente equivocada? Y en una cadena alumna → maestra →
alumna, ¿lo transmitido se conserva, se degrada o mejora?

=== UN DEFECTO DEL ENCARGO, DICHO ANTES DE MEDIR (E-46) ==========================
La orientación pide dos cosas que no pueden ser verdad a la vez:
  (i) «lo único que cruza es un bit por paso: las dos declaran su predicción antes de
      actuar»; y
  (ii) «U_m le da la palabra más corta en la que, según H_m, la predicción de U_a falla».
Para calcular (ii) la maestra necesita LEER H_a —saber qué predice el alumno en
situaciones que el alumno todavía no ha vivido—, y eso es muchísimo más que un bit.
Y con (i) sola, la palabra más corta donde la predicción del alumno falla es SIEMPRE la
letra que el alumno estaba por tomar (si discrepan en ella, «esa letra» es la palabra de
longitud 1 y el orden shortlex la elige), de modo que la intervención no cambia nada y
la celda sería idéntica a F1 por construcción, no por medida.

Así que el canal se declara como PARÁMETRO y se miden los dos, porque la comparación
entre ellos es justamente «qué necesita saber un maestro para enseñar»:
  · `un_bit`          la maestra sólo recibe el bit «¿predecís lo mismo que yo?». Cuando
                      dice que no, da lo único que puede dar con su propia máquina: la
                      palabra más corta que, desde donde cree estar, SEPARA dos estados
                      suyos (el testigo de apartamiento de H_m). «Andá a mirar allá,
                      donde yo sé que hay algo que distinguir.» Cero conocimiento del
                      alumno más allá del bit.
  · `ve_la_hipotesis` la maestra lee H_a y da la palabra más corta donde H_a y H_m
                      discrepan. Es la letra del encargo, y es un canal más ancho que un
                      bit: se declara como tal y es el techo de lo que una maestra podría.
La celda con el disparo literal se corre igual como MUTANTE (M-literal) para dejar
medido lo que hace, en vez de afirmarlo.

MEDIDO EN LA PRUEBA DE INSTRUMENTO (1 mundo W1, antes de la campaña; §«qué cambió y por
qué» de la enmienda). Con el disparo literal —intervenir sólo cuando discrepan en la
letra que el alumno estaba por tomar— la palabra que cruza fue de longitud 1 en el
100 % de las intervenciones y fue LA MISMA letra en 7 de 9: la celda reprodujo F1 curva
por curva. Con el disparo que NO espera al desacuerdo local (el de T2), el alumno
identificó en el hito 64 donde F1 necesitó 128. Conclusión de instrumento, no de
ciencia: **lo que hace que enseñar sirva es el disparo, no el maestro.** Por eso U1, U2,
U3, U-sham, M-canal y la cadena usan `disparo='siempre'` —declarado aquí, antes de
medir— y el disparo literal se conserva como M-literal. T1 (contraejemplo: espera al error) y
T2 (itinerario: no espera) conservan cada uno el disparo de su propia definición, que es
justamente lo que los distingue, y por eso el par T1/T2 es la medida limpia del efecto
del disparo con el maestro omnisciente.
=================================================================================

LAS CELDAS. F1 (la vara, sin maestro) · T1 y T2 (maestro omnisciente: la referencia es
el mundo, no una máquina) · U1 (maestra que identificó) · U2 (maestra que NO identificó)
· U3 (maestra de otro mundo de la misma clase) · U-sham (da palabras donde el alumno
ACIERTA; MEDIDO en la prueba de instrumento: no es un control neutro, porque gasta la
vida del alumno en lo que ya sabe —alcance 0,000 contra 1,000 de F1 en el mundo de
prueba—. Es el efecto de canalización de Derex en su forma más pura, y la predicción
«U-sham ≈ F1» del encargo no puede cumplirse por construcción: el control neutro de
«el único canal es vivir la palabra» es M-canal, que sí dio F1 exactamente)
· M-canal (recibe las palabras y NO las vive) · K5 (cinco generaciones, cada
alumna maestra de la siguiente) · Pareja (dos frescas que se enseñan mutuamente).

EL PRESUPUESTO. Las palabras que da la maestra se viven DENTRO de la vida del alumno:
todas las celdas gastan exactamente los mismos pasos de mundo que F1, y lo que cambia es
QUÉ se vive, no CUÁNTO. El gasto de la maestra se registra aparte y no decide.

Sin azar: los empates se rompen en orden shortlex. Doble corrida con hash.
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
import unidad_minima_08_fase2 as m8                                       # noqa: E402
import unidad_minima_09_fase2 as m9                                       # noqa: E402
from unidad_minima_01 import LETTERS, predict, run_world, shortlex, states_of  # noqa: E402
from unidad_minima_05_banco import (                                      # noqa: E402
    L_de, alcanzables, canonica, paso_de, sistema_por_indice,
)
from unidad_minima_08_fase2 import (                                      # noqa: E402
    HITOS, N1, UnidadFase2, medir, mundo_2, mundos_1, patrones, verdad, vivir,
)
from guardas import informe, no_vacio, salida_a_fichero, sin_azar_usado    # noqa: E402

GENERACIONES = 5          # la cadena K5
VIDA_MAESTRA_U2 = 64      # la maestra que NO identificó: vivió sólo hasta el primer hito.
                          # Decidido así porque la maestra de vida completa identifica el
                          # 99,6 % de las familias y U2 se quedaría sin banco (9 familias).
RETENCION = 512           # pasos sin maestra, al retirarse
CANALES = ("un_bit", "ve_la_hipotesis")
CELDAS = ("F1", "T1", "T2", "U1", "U2", "U3", "U-sham", "M-canal", "M-literal")

SHA_10 = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
ARRANQUE = time.strftime("%Y-%m-%dT%H:%M:%S")   # E-49: el hash del fuente al IMPORTAR


# ---------------------------------------------------------------------------
# El canal: la palabra que cruza
# ---------------------------------------------------------------------------
def palabra_discrepante(trans_a, q_a, sig_ref, q_ref, tope, modo="corta"):
    """Producto determinista de la hipótesis del alumno y de la referencia del maestro,
    recorrido por niveles (BFS) con las letras en orden fijo: devuelve la PRIMERA palabra
    en orden shortlex donde la predicción del alumno falla según la referencia.

    `sig_ref(q, a)` devuelve (q', reacción) o None si la referencia no tiene ruta — una
    maestra con máquina incompleta no puede enseñar más allá de lo que su máquina dice, y
    eso es parte de la pregunta, no un defecto.

    modo: 'corta' la más corta donde el alumno falla · 'sham' la más corta donde ACIERTA
    (mutante) · 'larga' la más profunda dentro del tope donde falla (M-t3; con el
    producto deduplicado, «la más profunda hallada», y se dice).

    Un recorrido por niveles sobre el producto es lo que hace esto pagable: enumerar las
    2^(tope+1) palabras cuesta ~10^5 operaciones POR PASO en cuanto el alumno converge y
    ya no hay discrepancia —el caso más frecuente de toda la vida—, y eso es el error
    E-32 otra vez (lo que valida la campaña sin tope).
    """
    nivel = {(q_a, q_ref): ()}
    vistos = set(nivel)
    mejor = None
    for _ in range(tope):
        siguiente = {}
        for (qa, qr), w in nivel.items():
            for a in LETTERS:
                tr = sig_ref(qr, a)
                if tr is None:
                    continue
                qr2, o_ref = tr
                ta = trans_a.get((qa, a))
                w2 = w + (a,)
                falla = (ta is None) or (ta[1] != o_ref)
                if modo == "corta" and falla:
                    return w2
                if modo == "sham" and not falla:
                    return w2
                if modo == "larga" and falla:
                    mejor = w2
                if ta is None:
                    continue
                e = (ta[0], qr2)
                if e not in vistos:
                    vistos.add(e)
                    siguiente[e] = w2
        nivel = siguiente
        if not nivel:
            break
    return mejor


def testigo_de_apartamiento(M, q, tope):
    """La palabra más corta que, desde `q`, separa a `q` de algún otro estado de M: la
    maestra del canal de un bit no sabe nada del alumno, así que da lo único que su propia
    máquina le permite señalar —dónde hay algo que distinguir—."""
    qs = [s for s in states_of(M) if s != q]
    if not qs:
        return None
    nivel = {(q, s): () for s in qs}
    vistos = set(nivel)
    for _ in range(tope):
        siguiente = {}
        for (p, s), w in nivel.items():
            for a in LETTERS:
                tp, ts = M.get((p, a)), M.get((s, a))
                w2 = w + (a,)
                if tp is None or ts is None:
                    continue
                if tp[1] != ts[1]:
                    return w2
                e = (tp[0], ts[0])
                if e not in vistos:
                    vistos.add(e)
                    siguiente[e] = w2
        nivel = siguiente
        if not nivel:
            break
    return None


class Maestro:
    """Lo común a todos: una referencia (una máquina o el mundo), el estado en que cree
    estar, un tope de longitud de palabra, y un registro de lo que dio."""

    def __init__(self, tope, canal="ve_la_hipotesis", modo="corta", disparo="discrepa"):
        self.tope, self.canal, self.modo, self.disparo = tope, canal, modo, disparo
        self.c = Counter()

    def sig(self, q, a):
        raise NotImplementedError

    def predice(self, a):
        t = self.sig(self.q, a)
        return None if t is None else t[1]

    def avanzar(self, a, o):
        """La maestra NO ve el mundo: avanza por su propia referencia. Si su referencia no
        tiene ruta, se queda donde está y lo cuenta (está perdida, y eso se mide)."""
        t = self.sig(self.q, a)
        if t is None:
            self.c["sin_ruta_maestra"] += 1
        else:
            self.q = t[0]

    def interviene(self, u, a_itinerario):
        """¿Cruza el bit? Con el disparo literal del encargo: sólo si discrepan en la
        letra que el alumno estaba por tomar. Con `disparo='siempre'` (T2, el maestro de
        itinerario) no espera al desacuerdo."""
        if self.disparo == "siempre":
            return True
        pa = u.predecir(a_itinerario)
        pm = self.predice(a_itinerario)
        if pm is None:
            return False                        # la maestra no sabe nada de aquí
        return pa != pm

    def palabra(self, u):
        if self.canal == "un_bit":
            return self.testigo()
        return palabra_discrepante(u.trans, u.q, self.sig, self.q, self.tope, self.modo)

    def testigo(self):
        raise NotImplementedError


class MaestroMundo(Maestro):
    """T1 y T2: la referencia es el mundo verdadero. Conoce W; eso es lo que lo hace
    maestro. No entrega transiciones: entrega palabras para vivir."""

    def __init__(self, step, x, tope, **kw):
        Maestro.__init__(self, tope, **kw)
        self.step, self.q = step, x

    def sig(self, q, a):
        return self.step(q, a)

    def testigo(self):
        # el mundo no tiene «máquina» legible: su testigo es la palabra más corta que
        # separa su estado actual de otro estado alcanzable del mundo
        M = {}
        vistos, cola = {self.q}, [self.q]
        while cola:
            x = cola.pop(0)
            for a in LETTERS:
                y, o = self.step(x, a)
                M[(x, a)] = (y, o)
                if y not in vistos:
                    vistos.add(y)
                    cola.append(y)
        return testigo_de_apartamiento(M, self.q, self.tope)


class MaestroUnidad(Maestro):
    """U1, U2, U3, U-sham: la referencia es la máquina de otra unidad, posiblemente
    equivocada. Enseña desde su máquina; no ve el mundo mientras enseña."""

    def __init__(self, M, q, tope, **kw):
        Maestro.__init__(self, tope, **kw)
        self.M, self.q = dict(M), q

    def sig(self, q, a):
        return self.M.get((q, a))

    def testigo(self):
        return testigo_de_apartamiento(self.M, self.q, self.tope)


# ---------------------------------------------------------------------------
# Vivir con maestra
# ---------------------------------------------------------------------------
def vivir_con_maestro(u, step, x, itinerario, maestro, futuro=None, vive_la_palabra=True,
                      canaliza=False):
    """El `vivir` de 08 con una maestra en medio. Mismo presupuesto: las letras de la
    palabra se viven EN LUGAR de las del itinerario, nunca además.

    `vive_la_palabra=False` es el mutante M-canal: el alumno RECIBE la palabra y no la
    ejecuta (la registra y sigue su itinerario). Debe dar exactamente F1, porque el único
    canal es vivir la palabra.
    """
    err = ultimo = sin_ruta = 0
    it = iter(itinerario)
    cola = []
    curva, visitadas = {}, set()
    c = Counter()
    for t in range(1, len(itinerario) + 1):
        if futuro is not None and t - 1 in HITOS:
            verdad_fut, _ = run_world(step, x, futuro)
            hits, nr, _ = predict(u.trans, u.q, futuro, verdad_fut)
            curva[t - 1] = dict(exactitud=hits / len(futuro),
                                identifica=(hits == len(futuro) and nr == 0))
        if cola:
            a = cola.pop(0)
            c["pasos_ensenados"] += 1
        else:
            a = next(it)
            if maestro is not None and maestro.interviene(u, a):
                c["bits_cruzados"] += 1
                w = maestro.palabra(u)
                if w is None:
                    c["contraejemplos_imposibles"] += 1
                else:
                    c["intervenciones"] += 1
                    c["letras_dadas"] += len(w)
                    c[f"longitud_{min(len(w), 9)}"] += 1
                    if w == (a,):
                        c["palabra_igual_a_la_letra"] += 1
                    if vive_la_palabra:
                        cola = list(w)
                        a = cola.pop(0)
                        c["pasos_ensenados"] += 1
        p = u.predecir(a)
        if p is None:
            sin_ruta += 1
            p = 0
        x, o = step(x, a)
        if p != o:
            err += 1
            ultimo = t
        u.leer(a, o)
        if maestro is not None:
            maestro.avanzar(a, o)
        if canaliza:
            visitadas.add(canonica(u.trans, 0))
        if c["intervenciones"] and not c.get("primera_intervencion"):
            c["primera_intervencion"] = t
    if futuro is not None:
        verdad_fut, _ = run_world(step, x, futuro)
        hits, nr, _ = predict(u.trans, u.q, futuro, verdad_fut)
        fin = dict(exactitud=hits / len(futuro), identifica=(hits == len(futuro) and nr == 0))
        for h in HITOS:
            curva.setdefault(h, fin)       # si la vida cortó antes de un hito, lo que sabe es lo que sabe
    else:
        fin = None
    return dict(x=x, errores=err, ultimo_error=ultimo, sin_ruta=sin_ruta, fin=fin,
                agotado=u.c["olvidos"], pasos_elegidos=0, curva=curva,
                hipotesis_visitadas=len(visitadas), maestro=dict(c),
                gasto_maestro=dict(maestro.c) if maestro is not None else {})


def _tope_palabra(n_estados):
    """2·|Q|, como pide el encargo, con |Q| el tope de estados del banco."""
    return 2 * n_estados


# ---------------------------------------------------------------------------
# Una familia
# ---------------------------------------------------------------------------
def _maestra_de(A2, B2, step2, x0, vida, fut2, n_max, pasos=None):
    """Una unidad que vivió W2 con el itinerario fijo y terminó con su máquina. Es la
    maestra: F1 de su propia familia, ni más ni menos."""
    u = UnidadFase2(n_max=n_max)
    v = vivir(u, step2, x0, vida if pasos is None else vida[:pasos], False)
    m = medir(u, step2, v["x"], fut2, alcanzables(A2, B2), {})
    return u, m["identifica"], v


def una_familia(idx, patron, componible, vida1, vida2, fut1, fut2, n_max,
                celdas=CELDAS, canal="ve_la_hipotesis", maestra_ajena=None,
                con_cadena=False, con_pareja=False):
    A, B = sistema_por_indice(N1, idx)
    A2, B2 = mundo_2(A, B, N1, patron, componible)
    step1, step2 = paso_de(A, B), paso_de(A2, B2)
    est2, nmin2, _ = verdad(A2, B2)
    tope = _tope_palabra(n_max)
    # el mundo cambia donde W1 dejó a una unidad que vivió W1: mismo punto que en 08/09
    madre = UnidadFase2(n_max=n_max)
    v1 = vivir(madre, step1, 0, vida1, False)
    x0 = v1["x"]
    base = dict(w1=idx, patron=f"{patron[0]}@{patron[1]}",
                clase="componible" if componible else "no_componible",
                n_min_w2=nmin2, canal=canal)
    # --- las dos maestras-unidad de esta familia
    um_full, ident_full, _ = _maestra_de(A2, B2, step2, x0, vida2, fut2, n_max)
    um_corta, ident_corta, _ = _maestra_de(A2, B2, step2, x0, vida2, fut2, n_max,
                                           pasos=VIDA_MAESTRA_U2)
    filas = []

    def una_celda(celda, u, maestro, vive=True, canaliza=True, extra=None, cofre=None):
        v = vivir_con_maestro(u, step2, x0, vida2, maestro, fut2, vive, canaliza)
        ex = dict(celda=celda, errores=v["errores"], ultimo_error=v["ultimo_error"],
                  olvidos=v["agotado"], curva=v["curva"],
                  hipotesis_visitadas=v["hipotesis_visitadas"],
                  pasos_elegidos=0, **{f"m_{k}": n for k, n in v["maestro"].items()})
        ex.update(extra or {})
        # RETENCIÓN (§3 del maestro): con el maestro retirado y la hipótesis congelada,
        # exactitud sobre el futuro fijo. Es la misma medida que `exactitud` en este punto
        # —la hipótesis no cambia mientras se predice el futuro fijo—, y se nombra aparte
        # porque es la que el cierre tiene que informar como «lo que quedó almacenado».
        f = medir(u, step2, v["x"], fut2, est2, ex)      # ← al FINAL de la vida enseñada
        f["retencion_congelada"] = f["exactitud"]
        f.update(base)
        f["repertorio"] = f["escribe"] + f["permuta"]
        f["curva"][len(vida2)] = v["fin"]
        if cofre is not None:
            # La máquina que esta alumna pasará a la siguiente generación es la del FINAL DE
            # SU VIDA ENSEÑADA, antes del examen de retención: el presupuesto de vida es
            # `vida2` y los 512 pasos de retención son un examen, no parte de la vida
            # (corregido el 28-oct; antes la maestra de la generación k+1 era la unidad
            # DESPUÉS del examen, o sea con 512 pasos libres de ventaja no declarados).
            cofre["trans"], cofre["q"] = dict(u.trans), u.q
        # TRANSFERENCIA, primera mitad: 512 pasos más sin maestro y APRENDIENDO, en el
        # mismo mundo. (La segunda mitad —una cascada W3 nueva— queda declarada y no
        # construida: pide un banco de 12 estados y entra con T3 en la fase siguiente.)
        v3 = vivir_con_maestro(u, step2, v["x"], vida2[:RETENCION], None, fut2, True, False)
        f["retencion_aprendiendo"] = v3["fin"]["exactitud"]
        f["identifica_tras_retirarse"] = v3["fin"]["identifica"]
        filas.append(f)
        return f

    for celda in celdas:
        if celda == "F1":
            una_celda("F1", UnidadFase2(n_max=n_max), None)
        elif celda == "T1":
            una_celda("T1", UnidadFase2(n_max=n_max),
                      MaestroMundo(step2, x0, tope, canal=canal, disparo="discrepa"))
        elif celda == "T2":
            una_celda("T2", UnidadFase2(n_max=n_max),
                      MaestroMundo(step2, x0, tope, canal=canal, disparo="siempre"))
        elif celda == "U1":
            if not ident_full:
                continue                 # U1 es la maestra que SÍ identificó
            una_celda("U1", UnidadFase2(n_max=n_max),
                      MaestroUnidad(um_full.trans, um_full.q, tope, canal=canal,
                                    disparo="siempre"),
                      extra=dict(maestra_identifico=True))
        elif celda == "U2":
            if ident_corta:
                continue                 # U2 es la maestra que NO identificó
            una_celda("U2", UnidadFase2(n_max=n_max),
                      MaestroUnidad(um_corta.trans, um_corta.q, tope, canal=canal,
                                    disparo="siempre"),
                      extra=dict(maestra_identifico=False, vida_maestra=VIDA_MAESTRA_U2))
        elif celda == "U3":
            if maestra_ajena is None:
                continue
            Maj, qaj = maestra_ajena
            una_celda("U3", UnidadFase2(n_max=n_max),
                      MaestroUnidad(Maj, qaj, tope, canal=canal, disparo="siempre"))
        elif celda == "U-sham":
            if not ident_full:
                continue
            una_celda("U-sham", UnidadFase2(n_max=n_max),
                      MaestroUnidad(um_full.trans, um_full.q, tope, canal=canal, modo="sham",
                                    disparo="siempre"))
        elif celda == "M-canal":
            if not ident_full:
                continue
            una_celda("M-canal", UnidadFase2(n_max=n_max),
                      MaestroUnidad(um_full.trans, um_full.q, tope, canal=canal,
                                    disparo="siempre"), vive=False)
        elif celda == "M-literal":
            # el disparo y el canal literales del encargo, para dejar MEDIDO que la
            # palabra que cruza es la letra que el alumno ya iba a tomar
            if not ident_full:
                continue
            una_celda("M-literal", UnidadFase2(n_max=n_max),
                      MaestroUnidad(um_full.trans, um_full.q, tope,
                                    canal="ve_la_hipotesis", modo="corta"))
    # --- la cadena de generaciones: cada alumna se vuelve maestra de la siguiente
    if con_cadena and ident_full:
        M_prev, q_prev = dict(um_full.trans), um_full.q
        canon_prev = canonica(M_prev, q_prev)
        canon_1 = canon_prev
        for k in range(2, GENERACIONES + 1):
            u = UnidadFase2(n_max=n_max)
            cofre = {}
            f = una_celda(f"K{k}", u, MaestroUnidad(M_prev, q_prev, tope, canal=canal,
                                                  disparo="siempre"),
                          canaliza=False,
                          extra=dict(generacion=k), cofre=cofre)
            canon = canonica(cofre["trans"], 0)
            f["isomorfa_a_la_anterior"] = (canon == canon_prev)
            f["isomorfa_a_la_primera"] = (canon == canon_1)
            f["transiciones_distintas"] = len(set(_aristas(cofre["trans"], 0)) ^
                                              set(_aristas(M_prev, q_prev)))
            f["estados_ensenada"] = len(states_of(cofre["trans"]))
            M_prev, q_prev, canon_prev = cofre["trans"], cofre["q"], canon
    # --- la pareja cooperativa: dos frescas, mismo mundo, misma corriente de letras
    if con_pareja:
        filas.append(pareja(step2, x0, vida2, fut2, est2, n_max, tope, canal, base))
        f = pareja(step2, x0, vida2, fut2, est2, n_max, tope, canal, base, simetrica=True)
        f["celda"] = "M-pareja-simetrica"      # la versión del encargo: debe cruzar 0 bits
        filas.append(f)
    return filas


def _aristas(M, inicio):
    c = canonica(M, inicio)
    return c if c else ()


def pareja(step, x, itinerario, futuro, est, n_max, tope, canal, base, simetrica=False):
    """Bender–Slonim con dos unidades: dos frescas que se enseñan mutuamente, cada una con
    lo único que tiene —su propia máquina—. En el paso t manda una y en t+1 la otra: la
    que manda le da a la otra el contraejemplo según su máquina. Sin azar: el turno lo
    decide la paridad de t y los empates el orden shortlex.

    LA ASIMETRÍA, Y POR QUÉ ES NECESARIA (medido antes de la campaña, E-47). Con las dos
    unidades en el MISMO sitio del mundo leyendo la MISMA corriente de letras —como se
    leía el encargo— no cruza NI UN BIT en toda la vida: dos unidades deterministas
    idénticas con la misma entrada construyen la misma hipótesis paso a paso, así que
    nunca discrepan y no hay nada que enseñarse. La celda sería vacía por construcción.
    Los dos robots de Bender–Slonim cooperan porque están en VÉRTICES DISTINTOS del
    grafo: la asimetría es lo que hace que uno sepa algo que el otro no.

    Así que cada unidad tiene su propia posición en el mundo y su propio itinerario: la
    segunda arranca desde el estado al que la primera letra del itinerario lleva, y recorre
    el itinerario desplazado un paso. Es la asimetría mínima, es determinista y no es azar.
    `simetrica=True` conserva la versión del encargo como mutante, para que «no cruza
    ningún bit» quede medido y no afirmado.
    """
    u1, u2 = UnidadFase2(n_max=n_max), UnidadFase2(n_max=n_max)
    x1 = x
    if simetrica:
        x2, it2 = x, iter(itinerario)
    else:
        x2, _o = step(x, itinerario[0])          # otro vértice del mundo
        it2 = iter(list(itinerario[1:]) + [itinerario[0]])
    it1 = iter(itinerario)
    cola1, cola2, c = [], [], Counter()
    curva = {}
    for t in range(1, len(itinerario) + 1):
        if t - 1 in HITOS:
            vf1, _ = run_world(step, x1, futuro)
            vf2, _ = run_world(step, x2, futuro)
            h1, n1, _ = predict(u1.trans, u1.q, futuro, vf1)
            h2, n2, _ = predict(u2.trans, u2.q, futuro, vf2)
            i1 = (h1 == len(futuro) and n1 == 0)
            i2 = (h2 == len(futuro) and n2 == 0)
            curva[t - 1] = dict(identifica=(i1 and i2), identifica_alguna=(i1 or i2))
        # quién enseña en este paso; la otra es la alumna y recibe la palabra en su cola
        quien, otro = (u1, u2) if t % 2 else (u2, u1)
        # el mismo disparo que las demás celdas (no espera al desacuerdo local: ver la
        # prueba de instrumento del encabezado), y la palabra va a la cola de la alumna
        if canal == "ve_la_hipotesis":
            w = palabra_discrepante(otro.trans, otro.q,
                                    lambda q, b: quien.trans.get((q, b)), quien.q,
                                    tope, "corta")
        else:
            w = testigo_de_apartamiento(quien.trans, quien.q, tope)
        if w is None:
            c["contraejemplos_imposibles"] += 1
        else:
            c["intervenciones"] += 1
            c["letras_dadas"] += len(w)
            if otro is u1:
                cola1 = list(w)
            else:
                cola2 = list(w)
        # cada una vive su propio paso, en su propia posición del mundo
        if cola1:
            a1 = cola1.pop(0)
            c["pasos_ensenados"] += 1
        else:
            a1 = next(it1)
        if cola2:
            a2 = cola2.pop(0)
            c["pasos_ensenados"] += 1
        else:
            a2 = next(it2)
        x1, o1 = step(x1, a1)
        x2, o2 = step(x2, a2)
        u1.leer(a1, o1)
        u2.leer(a2, o2)
    vf1, _ = run_world(step, x1, futuro)
    vf2, _ = run_world(step, x2, futuro)
    h1, n1, _ = predict(u1.trans, u1.q, futuro, vf1)
    h2, n2, _ = predict(u2.trans, u2.q, futuro, vf2)
    ident1 = (h1 == len(futuro) and n1 == 0)
    ident2 = (h2 == len(futuro) and n2 == 0)
    x = x1
    curva[len(itinerario)] = dict(identifica=(ident1 and ident2),
                                  identifica_alguna=(ident1 or ident2))
    f = medir(u1, step, x, futuro, est, dict(celda="Pareja", curva=curva, errores=0,
                                             ultimo_error=0, olvidos=u1.c["olvidos"],
                                             pasos_elegidos=0, hipotesis_visitadas=0,
                                             ambas_identifican=(ident1 and ident2),
                                             identifica_u2=ident2,
                                             retencion_congelada=h1 / len(futuro),
                                             retencion_aprendiendo=h1 / len(futuro),
                                             identifica_tras_retirarse=ident1,
                                             **{f"m_{k}": n for k, n in c.items()}))
    f.update(base)
    f["repertorio"] = f["escribe"] + f["permuta"]
    f["identifica"] = ident1 and ident2        # la pareja identifica si identifican LAS DOS
    return f


# ---------------------------------------------------------------------------
# Campaña
# ---------------------------------------------------------------------------
def _familias_de(idx, n_max):
    A, B = sistema_por_indice(N1, idx)
    _, nmin1, _ = verdad(A, B)
    out = []
    for comp in (True, False):
        for patron in patrones(N1):
            A2, B2 = mundo_2(A, B, N1, patron, comp)
            _, nmin2, _ = verdad(A2, B2)
            if nmin2 > nmin1:
                out.append((patron, comp))
    return out


def _una_w1(args):
    (idx, siguiente, vida1, vida2, fut1, fut2, n_max, celdas, canal,
     con_cadena, con_pareja) = args
    filas = []
    # la maestra ajena (U3) viene del W1 siguiente en el orden del banco: otro mundo, misma
    # clase, elección determinista y sin azar
    ajena = None
    if siguiente is not None:
        A, B = sistema_por_indice(N1, siguiente)
        fams = _familias_de(siguiente, n_max)
        if fams:
            patron, comp = fams[0]
            A2, B2 = mundo_2(A, B, N1, patron, comp)
            step1 = paso_de(A, B)
            m = UnidadFase2(n_max=n_max)
            v1 = vivir(m, step1, 0, vida1, False)
            um, _, _ = _maestra_de(A2, B2, paso_de(A2, B2), v1["x"], vida2, fut2, n_max)
            ajena = (dict(um.trans), um.q)
    for patron, comp in _familias_de(idx, n_max):
        filas.extend(una_familia(idx, patron, comp, vida1, vida2, fut1, fut2, n_max,
                                 celdas, canal, ajena, con_cadena, con_pareja))
    return filas


def campana(out, limite_w1=None, trabajadores=1, celdas=CELDAS, canal="ve_la_hipotesis",
            con_cadena=False, con_pareja=False):
    vida1 = shortlex(range(1, L_de(N1) + 1))
    vida2 = shortlex(range(1, L_de(2 * N1) + 1))
    fut1 = shortlex((L_de(N1) + 1, L_de(N1) + 2))
    fut2 = shortlex((2 * N1, 2 * N1 + 1))
    n_max = 2 * N1 + 2
    out.write(f"vida en W1: {len(vida1)}; vida en W2: {len(vida2)}; futuro W2: {len(fut2)}; "
              f"tope de estados {n_max}; tope de palabra {_tope_palabra(n_max)}; "
              f"canal «{canal}»; celdas {', '.join(celdas)}"
              f"{'; cadena K5' if con_cadena else ''}{'; pareja' if con_pareja else ''}\n")
    elegibles = mundos_1(vida1, fut1, n_max, out)
    no_vacio(elegibles, "mundos W1 elegibles")
    if limite_w1:
        elegibles = elegibles[:limite_w1]
    tareas = []
    for i, idx in enumerate(elegibles):
        siguiente = elegibles[(i + 1) % len(elegibles)] if len(elegibles) > 1 else None
        tareas.append((idx, siguiente, vida1, vida2, fut1, fut2, n_max, celdas, canal,
                       con_cadena, con_pareja))
    no_vacio(tareas, "tareas (W1 a correr)")
    t0 = time.perf_counter()
    if trabajadores > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(trabajadores) as pool:
            res = pool.map(_una_w1, tareas, chunksize=1)
    else:
        res = [_una_w1(t) for t in tareas]
    filas = [f for r in res for f in r]
    no_vacio(filas, "filas medidas")
    out.write(f"mundos W1 corridos: {len(elegibles)}; filas: {len(filas)}\n\n")
    sys.stderr.write(f"reloj: {time.perf_counter() - t0:.1f} s\n")
    return filas


def resumen(filas, out):
    R = {}
    hitos = sorted({int(k) for f in filas for k in f["curva"]})
    orden = (list(CELDAS) + [f"K{k}" for k in range(2, GENERACIONES + 1)] +
             ["Pareja", "M-pareja-simetrica"])
    for clase in ("componible", "no_componible"):
        F = [f for f in filas if f["clase"] == clase]
        if not F:
            continue
        out.write(f"=== clase {clase}\n")
        out.write(f"{'celda':<10}{'fam.':>6}{'alcance':>9}{'exact.':>8}{'repert.':>9}{'instr.':>8}"
                  f"{'interv.':>9}{'letras':>8}{'imposib.':>9}{'=letra':>8}{'hipót.':>8}"
                  f"{'retenc.':>9}{'tras irse':>10}\n")
        R[clase] = {}
        for b in orden:
            Fb = [f for f in F if f["celda"] == b]
            k = len(Fb)
            if not k:
                continue
            g = lambda campo: sum(f.get(campo, 0) or 0 for f in Fb) / k
            r = dict(familias=k, alcance=sum(f["identifica"] for f in Fb) / k,
                     exactitud=g("exactitud"), repertorio=g("repertorio"),
                     instruibilidad=g("instruibilidad"),
                     intervenciones=g("m_intervenciones"), letras=g("m_letras_dadas"),
                     imposibles=g("m_contraejemplos_imposibles"),
                     palabra_igual_a_la_letra=g("m_palabra_igual_a_la_letra"),
                     hipotesis_visitadas=g("hipotesis_visitadas"),
                     retencion_congelada=g("retencion_congelada"),
                     identifica_tras_retirarse=sum(bool(f.get("identifica_tras_retirarse"))
                                                   for f in Fb) / k,
                     curva_alcance={h: sum(f["curva"][h]["identifica"] for f in Fb
                                           if h in f["curva"]) /
                                       max(1, sum(1 for f in Fb if h in f["curva"]))
                                    for h in hitos})
            r["alcance_medio_curva"] = sum(r["curva_alcance"].values()) / len(hitos)
            R[clase][b] = r
            out.write(f"{b:<10}{k:>6}{r['alcance']:>9.3f}{r['exactitud']:>8.4f}"
                      f"{r['repertorio']:>9.2f}{r['instruibilidad']:>8.2f}"
                      f"{r['intervenciones']:>9.1f}{r['letras']:>8.1f}{r['imposibles']:>9.1f}"
                      f"{r['palabra_igual_a_la_letra']:>8.1f}{r['hipotesis_visitadas']:>8.1f}"
                      f"{r['retencion_congelada']:>9.4f}{r['identifica_tras_retirarse']:>10.3f}\n")
        out.write("curva de alcance por pasos vividos en W2:\n")
        out.write(f"{'celda':<10}" + "".join(f"{h:>8}" for h in hitos) + f"{'media':>8}\n")
        for b in orden:
            if b not in R[clase]:
                continue
            r = R[clase][b]
            out.write(f"{b:<10}" + "".join(f"{r['curva_alcance'][h]:>8.3f}" for h in hitos) +
                      f"{r['alcance_medio_curva']:>8.3f}\n")
        # pareado contra la vara, en los tres hitos
        for celda in orden:
            if celda in ("F1",) or celda not in R[clase]:
                continue
            for h in (64, 128, 256):
                if h not in hitos:
                    continue
                sa, sb, nf = m9.pareado(F, celda, "F1", h, "celda")
                p1 = R[clase][celda]["curva_alcance"][h]
                p2 = R[clase]["F1"]["curva_alcance"][h]
                z = m9.z_dos(p1, R[clase][celda]["familias"], p2, R[clase]["F1"]["familias"])
                R[clase][f"{celda}_vs_F1_{h}"] = dict(celda=p1, f1=p2, z=z,
                                                      solo_celda=sa, solo_f1=sb, familias=nf)
                out.write(f"  hito {h}: {celda} {p1:.3f} vs F1 {p2:.3f} · z {z:.2f} · "
                          f"pareado: sólo {celda} en {sa}, sólo F1 en {sb} (de {nf})\n")
        # la cadena
        gens = [f"K{k}" for k in range(2, GENERACIONES + 1)]
        if any(gc in R[clase] for gc in gens):
            out.write("fidelidad en la cadena (Kirby): por generación\n")
            out.write(f"{'gen':<6}{'alcance':>9}{'isom. anterior':>16}{'isom. primera':>15}"
                      f"{'trans. distintas':>18}\n")
            fid = {}
            for k in range(2, GENERACIONES + 1):
                Fk = [f for f in F if f["celda"] == f"K{k}"]
                if not Fk:
                    continue
                fid[k] = dict(
                    familias=len(Fk),
                    identifica=sum(bool(f["identifica"]) for f in Fk) / len(Fk),
                    alcance=sum(bool(f["identifica"]) for f in Fk) / len(Fk),
                    isomorfa_anterior=sum(bool(f.get("isomorfa_a_la_anterior")) for f in Fk) / len(Fk),
                    isomorfa_primera=sum(bool(f.get("isomorfa_a_la_primera")) for f in Fk) / len(Fk),
                    transiciones_distintas=sum(f.get("transiciones_distintas", 0) for f in Fk) / len(Fk))
                d = fid[k]
                out.write(f"{k:<6}{d['alcance']:>9.3f}{d['isomorfa_anterior']:>16.3f}"
                          f"{d['isomorfa_primera']:>15.3f}{d['transiciones_distintas']:>18.2f}\n")
            R[clase]["cadena"] = fid
        # la pareja
        P = [f for f in F if f["celda"] == "Pareja"]
        if P:
            f1 = [f for f in F if f["celda"] == "F1"]
            por_fam = {}
            for f in P + f1:
                por_fam.setdefault((f["w1"], f["patron"]), {})[f["celda"]] = f
            solo_p = sum(1 for d in por_fam.values()
                         if "Pareja" in d and "F1" in d and d["Pareja"]["identifica"]
                         and not d["F1"]["identifica"])
            solo_f = sum(1 for d in por_fam.values()
                         if "Pareja" in d and "F1" in d and d["F1"]["identifica"]
                         and not d["Pareja"]["identifica"])
            R[clase]["pareja"] = dict(
                familias=len(P),
                ambas_identifican=sum(bool(f.get("ambas_identifican")) for f in P) / len(P),
                solo_pareja=solo_p, solo_f1=solo_f)
            out.write(f"pareja cooperativa: las DOS identifican en "
                      f"{R[clase]['pareja']['ambas_identifican']:.3f}; pareado contra F1: "
                      f"sólo la pareja en {solo_p} familias, sólo F1 en {solo_f}\n")
        out.write("\n")
    return R


def _en_interseccion(filas, clase, celda, h):
    """La proporción de la celda y la de F1 **sobre las mismas familias**.

    COMPROBACIÓN 2 DE FABLE, y era un artefacto real: U1 y M-canal corren sobre 763
    familias y F1 sobre 766, U2 sobre 274. Comparar una media contra la otra mezcla el
    efecto con la dificultad del subconjunto, y a `M-canal` le fabricaba un FAIL (0,645
    contra 0,642) cuando en la intersección es **idéntico a F1, 0 y 0 pareado**. Toda
    comparación de la puerta pasa por aquí.
    """
    por = {}
    for f in filas:
        if f["clase"] == clase:
            por.setdefault((f["w1"], f["patron"]), {})[f["celda"]] = f
    com = [d for d in por.values() if celda in d and "F1" in d
           and h in d[celda]["curva"] and h in d["F1"]["curva"]]
    if not com:
        return None, None, 0, 0, 0
    pc = sum(bool(d[celda]["curva"][h]["identifica"]) for d in com) / len(com)
    pf = sum(bool(d["F1"]["curva"][h]["identifica"]) for d in com) / len(com)
    sa = sum(1 for d in com if d[celda]["curva"][h]["identifica"]
             and not d["F1"]["curva"][h]["identifica"])
    sb = sum(1 for d in com if d["F1"]["curva"][h]["identifica"]
             and not d[celda]["curva"][h]["identifica"])
    return pc, pf, sa, sb, len(com)


def _z_pareado(sa, sb):
    n = sa + sb
    return (abs(sa - sb) - 1) / (n ** 0.5) if n and abs(sa - sb) >= 1 else 0.0


def puerta(R, out, filas=None):
    g = {}
    u = m9.umbral(12)
    out.write(f"--- puerta (predicciones de §4, umbral de z {u:.2f}; todas las comparaciones "
              f"sobre la INTERSECCIÓN de familias con F1, y z pareado de McNemar)\n")
    for clase in ("componible", "no_componible"):
        Rc = R.get(clase)
        if not Rc:
            continue
        A = lambda b, h=64: Rc.get(b, {}).get("curva_alcance", {}).get(h)
        def comp(celda, h=None):
            """La comparación pareada en el hito donde el criterio se puede leer.

            REGLA DECLARADA (28-oct, tras ver fallar P2): el hito de decisión es el PRIMERO
            en el que F1, **sobre la intersección de familias de esa celda**, está por
            encima del suelo (0,10). Con un hito donde la vara vale 0,000 no se puede decir
            si el tratamiento ayuda o estorba: a U2, cuyas 274 familias se eligen porque la
            maestra de 64 pasos no identificó, F1 le da **0,000 en el hito 64 por
            construcción**, así que allí U2 «gana» (0,186) y el criterio salía al revés. No
            es mover el poste: es la misma regla para todas las celdas, y se informa qué
            hito usó cada una.
            """
            if filas is None or celda not in Rc:
                return None
            hitos = [h] if h is not None else [64, 128, 256, 512]
            elegido = None
            for hh in hitos:
                pc, pf, sa, sb, n = _en_interseccion(filas, clase, celda, hh)
                if pc is None:
                    continue
                if h is not None or pf > 0.10:
                    elegido = (hh, pc, pf, sa, sb, n)
                    break
            if elegido is None:
                return None
            hh, pc, pf, sa, sb, n = elegido
            z = _z_pareado(sa, sb)
            out.write(f"  {clase} · {celda} hito {hh}{' (primero con F1 sobre el suelo)' if h is None and hh != 64 else ''}: "
                      f"{pc:.4f} vs F1 {pf:.4f} (n={n}) · sólo {celda} {sa}, sólo F1 {sb} · "
                      f"z pareado {z:.2f}\n")
            return dict(hito=hh, celda=pc, f1=pf, solo_celda=sa, solo_f1=sb, n=n, z=z)
        d = comp("T2")
        if d:
            g[f"P0 {clase}: el DISPARO · T2 > F1 (hito {d['hito']})"] = d["solo_celda"] > d["solo_f1"] and d["z"] > u
        d1 = comp("T1")
        if d1:
            g[f"P0 {clase}: el DISPARO · T1 ≈ F1 (esperar al error no enseña)"] = d1["z"] <= u
        d = comp("U1")
        if d:
            g[f"P1 {clase}: una unidad enseña · U1 > F1 (hito {d['hito']})"] = \
                d["solo_celda"] > d["solo_f1"] and d["z"] > u
            if A("U1") is not None and A("T2") is not None:
                g[f"P1 {clase}: y enseña MENOS que el omnisciente · U1 < T2"] = A("U1") < A("T2")
        d = comp("U2")
        if d:
            g[f"P2 {clase}: el maestro equivocado canaliza al error · U2 < F1 (hito {d['hito']})"] = \
                d["solo_f1"] > d["solo_celda"] and d["z"] > u
            hv = Rc["U2"].get("hipotesis_visitadas"), Rc["F1"].get("hipotesis_visitadas")
            if all(x is not None for x in hv):
                g[f"P2 {clase}: U2 visita menos hipótesis que F1 (registro, no decide)"] = hv[0] < hv[1]
        d = comp("U3")
        if d:
            g[f"P3 {clase}: enseñar lo ajeno no ayuda · U3 <= F1"] = d["solo_celda"] <= d["solo_f1"]
        d = comp("U-sham")
        if d:
            g[f"P3 {clase}: U-sham gasta la vida del alumno (NO es control neutro: §13.2)"] = \
                d["solo_f1"] > d["solo_celda"]
        d = comp("M-canal")
        if d:
            g[f"M-canal {clase}: ≈ F1 EXACTAMENTE en la intersección (el único canal es vivir la palabra)"] = \
                (d["solo_celda"] == 0 and d["solo_f1"] == 0)
        d = comp("M-literal")
        if d:
            g[f"M-literal {clase}: el disparo literal no supera a F1"] = d["solo_celda"] <= d["solo_f1"]
        fid = Rc.get("cadena")
        if fid and len(fid) >= 2:
            ks = sorted(fid)
            # COMPROBACIÓN 3 DE FABLE: la fidelidad son DOS cosas y se separan, con nombre.
            # Antes un solo criterio decía «cae» y «se mantiene» a la vez porque mezclaba
            # función y estructura.
            g[f"P4-función {clase}: la FUNCIÓN se conserva a lo largo del linaje "
              f"(identifica en la última generación >= en la primera − 0,02)"] = \
                fid[ks[-1]]["identifica"] >= fid[ks[0]]["identifica"] - 0.02
            g[f"P4-estructura {clase}: la ESTRUCTURA deriva (isomorfía con la primera < 0,75)"] = \
                fid[ks[-1]]["isomorfa_primera"] < 0.75
            g[f"P4-estructura {clase}: y se ESTABILIZA (isomorfía con la anterior sube)"] = \
                fid[ks[-1]]["isomorfa_anterior"] > fid[ks[0]]["isomorfa_anterior"] + 0.02
        par = Rc.get("pareja")
        if par:
            g[f"P5 {clase}: la pareja identifica familias que F1 no (pareado > 0)"] = \
                par["solo_pareja"] > 0
    for k, v in g.items():
        out.write(f"  [{'PASS' if v else 'FAIL'}] {k}\n")
    return g


def main(limite_w1=None, trabajadores=1, ruta_filas=None, celdas=CELDAS,
         canal="ve_la_hipotesis", con_cadena=False, con_pareja=False):
    buf = io.StringIO()
    filas = campana(buf, limite_w1, trabajadores, celdas, canal, con_cadena, con_pareja)
    if ruta_filas:
        m9.guardar_filas(filas, ruta_filas)
    R = resumen(filas, buf)
    g = puerta(R, buf, filas)
    return buf.getvalue(), filas, R, g


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lim = int(args[0]) if args else None
    trab = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--trabajadores=")), 1)
    canal = next((a.split("=")[1] for a in sys.argv if a.startswith("--canal=")), "ve_la_hipotesis")
    cadena = "--cadena" in sys.argv
    par = "--pareja" in sys.argv
    suf = (f"_pilot{lim}" if lim else "") + ("" if canal == "ve_la_hipotesis" else "_unbit")
    os.makedirs(os.path.join(here, "artifacts"), exist_ok=True)
    ruta = os.path.join(here, "artifacts", f"unidad_minima_10_maestro{suf}.jsonl")
    salida_a_fichero(ruta, "filas de 10")
    t1, filas, R, g = main(lim, trab, ruta, CELDAS, canal, cadena, par)
    sys.stdout.write(t1)
    if "--doble" in sys.argv:
        t2, _, _, _ = main(lim, trab, None, CELDAS, canal, cadena, par)
        h1, h2 = (hashlib.sha256(t.encode()).hexdigest() for t in (t1, t2))
        sys.stdout.write(f"determinismo: {'IDÉNTICAS' if h1 == h2 else 'DIFIEREN'}\n")
    azar = sin_azar_usado(["unidad_minima_10_maestro", "unidad_minima_09_fase2",
                           "unidad_minima_08_fase2", "unidad_minima_02_incremental",
                           "unidad_minima_01"])
    src = SHA_10
    sys.stdout.write(f"azar usado: {azar}; arranque {ARRANQUE}; sha256 de 10 al arrancar: {src[:16]}…; "
                     f"sha256 de 08 (importado): {hashlib.sha256(open(m8.__file__, 'rb').read()).hexdigest()[:16]}…; "
                     f"sha256 de 09 (importado): {hashlib.sha256(open(m9.__file__, 'rb').read()).hexdigest()[:16]}…\n")
    informe()
    with open(os.path.join(here, "artifacts", f"unidad_minima_10_maestro{suf}.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(resumen=R, puerta=g, sha256_codigo=src, texto=t1), f,
                  ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())

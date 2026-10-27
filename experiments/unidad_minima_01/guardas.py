#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""guardas · las guardas de banco de trabajo, en código y no en prosa.

`ERRORES_Y_GUARDAS.md` sólo actúa cuando alguien abre una ficha. Mis tres últimos
errores ocurrieron **entre** fichas, en comandos sueltos: un `pkill` cuyo patrón
coincidió con su propia shell, una tubería que se tragó cuarenta minutos de salida,
y un «ninguno» leído sobre una lista vacía. Una guarda que vive en código actúa
aunque nadie abra la libreta; una que vive en prosa, no.

Cada función cuenta cuántas veces ha saltado, en `artifacts/guardas_contadores.json`,
para que el cierre de fase pueda decir qué guardas sirven y cuáles callan. Una guarda
que no salta en dos fases se revisa: o el error ya no es posible y la entrada se cierra
«resuelta por construcción», o la guarda no detecta y hay que rehacerla.

Uso mínimo:
    from guardas import no_vacio, muestreo_verificado, salida_a_fichero, estrato_de, matar_por_pid
"""
from __future__ import annotations

import json
import os
import signal
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
CONTADORES = os.path.join(AQUI, "artifacts", "guardas_contadores.json")


class GuardaViolada(AssertionError):
    """Se levanta cuando una guarda detecta exactamente lo que vigila."""


def _contar(guarda, salto):
    """Registra una consulta a la guarda y si saltó. Nunca estorba al que la llama."""
    try:
        os.makedirs(os.path.dirname(CONTADORES), exist_ok=True)
        d = {}
        if os.path.exists(CONTADORES):
            try:
                d = json.load(open(CONTADORES, encoding="utf-8"))
            except ValueError:
                d = {}
        e = d.setdefault(guarda, {"consultada": 0, "salto": 0, "ultimo_salto": None})
        e["consultada"] += 1
        if salto:
            e["salto"] += 1
            e["ultimo_salto"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        json.dump(d, open(CONTADORES, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except OSError:
        pass


def no_vacio(coleccion, nombre, minimo=1):
    """E-30 · Una verificación sobre cero elementos no es una verificación.

    Devuelve el número de elementos, para que quien informa use ESE número y no una
    constante escrita a mano. El «ninguno» que no viene con su recuento no es un
    resultado: es una cadena.
    """
    n = len(coleccion)
    salto = n < minimo
    _contar("no_vacio", salto)
    if salto:
        raise GuardaViolada(
            f"«{nombre}» tiene {n} elementos y hacen falta al menos {minimo}. "
            f"Cualquier conclusión sobre esto sería un falso verde (E-30).")
    return n


def muestreo_verificado(indices, base, posiciones, nombre="muestra"):
    """E-27 · Una submuestra de un espacio indexado por dígitos puede recorrer un
    retículo en vez del espacio. Comprueba que cada posición de dígito toma TODOS sus
    valores a lo largo de la muestra.

    `indices` es la muestra completa (no su prefijo: los dígitos altos salen fijos por
    efecto de prefijo y eso sería un falso positivo). Devuelve la lista de posiciones
    restringidas, vacía si está limpia.
    """
    no_vacio(indices, f"{nombre}: índices")
    vistos = [set() for _ in range(posiciones)]
    for idx in indices:
        i = idx
        for pos in range(posiciones - 1, -1, -1):
            vistos[pos].add(i % base)
            i //= base
    mal = [(pos, sorted(v)) for pos, v in enumerate(vistos) if len(v) < base]
    _contar("muestreo_verificado", bool(mal))
    if mal:
        raise GuardaViolada(
            f"«{nombre}»: {len(mal)} de {posiciones} posiciones de dígito restringidas "
            f"(base {base}): {mal[:6]}. El paso comparte factores con la base y la muestra "
            f"es un retículo, no el espacio (E-27).")
    return mal


def salida_a_fichero(ruta, etiqueta="", permitir_efimero=False):
    """E-29 · Un proceso que puede durar más que su tope no escribe por una tubería que
    almacena (`tail`, `head`, `sort`): si el tope lo mata, la salida se pierde entera.

    Devuelve un fichero abierto en modo línea-a-línea. Úsalo y llama a `.flush()` tras
    cada hito, o invoca el programa con `python3 -u`.
    """
    # Esta guarda es PREVENTIVA POR CONSTRUCCIÓN, no detectora: no hay nada que
    # detectar, hay algo que no se puede hacer mal si se usa esto. Por eso nunca
    # «salta», y eso NO es un síntoma de que no sirva. La regla de podar guardas
    # calladas (§5 del paquete del 26-oct) tiene que distinguir las dos clases, o
    # terminará borrando justamente las que funcionan mejor.
    # 26-oct · AMPLIADA tras caer en la variante que no cubría: escribí a un fichero,
    # pero en el directorio temporal de la sesión, que se borra al terminarla. Perdí la
    # salida igual que con una tubería. «A fichero» no basta: tiene que ser a un sitio
    # DURABLE, al lado del artefacto. Esta parte sí detecta, así que la guarda es mixta.
    EFIMERO = ("/tmp/", "/var/tmp/", "/dev/shm/", "/run/")
    absoluta = os.path.abspath(ruta)
    efimero = absoluta.startswith(EFIMERO) or "/scratchpad" in absoluta
    _contar("salida_a_fichero", efimero)
    if efimero and not permitir_efimero:
        raise GuardaViolada(
            f"«{absoluta}» está en un directorio temporal que no sobrevive a la sesión. "
            f"Una salida que no dura no es custodia: escribe al lado del artefacto, en el "
            f"árbol. Si de verdad es desechable, pasa permitir_efimero=True y dilo.")
    _contar("salida_a_fichero[constructiva]", False)
    os.makedirs(os.path.dirname(os.path.abspath(ruta)) or ".", exist_ok=True)
    f = open(ruta, "a", encoding="utf-8", buffering=1)
    if etiqueta:
        f.write(f"# {etiqueta} · {time.strftime('%Y-%m-%dT%H:%M:%S')}\n")
        f.flush()
    return f


def estrato_de(fila, campo="estrato"):
    """E-23 · La pertenencia a un estrato se deriva de un CAMPO de la fila, nunca de su
    posición en el fichero ni de su orden de llegada — y menos aún después de haber
    cambiado deliberadamente el orden de recorrido.
    """
    salto = campo not in fila
    _contar("estrato_de", salto)
    if salto:
        raise GuardaViolada(
            f"la fila no lleva el campo «{campo}», así que su estrato sólo podría "
            f"deducirse de su posición, que es exactamente el error E-23. "
            f"Campos presentes: {sorted(fila)[:12]}")
    return fila[campo]


def matar_por_pid(pid, espera=3.0):
    """E-26 · Matar por patrón (`pkill -f`) puede coincidir con la propia shell del que
    llama, que lleva el patrón en su línea de órdenes; el comando se mata a sí mismo y
    lo que venía después no se ejecuta, en silencio. Se mata por PID.
    """
    salto = (pid == os.getpid() or pid == os.getppid())
    _contar("matar_por_pid", salto)
    if salto:
        raise GuardaViolada(
            f"PID {pid} es este proceso o su padre: matarlo es el error E-26.")
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return "ya no existía"
    fin = time.time() + espera
    while time.time() < fin:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return "terminado con SIGTERM"
        time.sleep(0.1)
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return "terminado con SIGTERM"
    return "terminado con SIGKILL"


def sin_azar_usado(modulos, nombre="nuestros módulos"):
    """E-07 corregida el 27-oct · comprobar USO de azar, no su importación.

    El error: el artefacto registraba «random importado: SÍ» y la frase «sin random» dejó
    de ser verificable. Pero `random` estaba en sys.modules porque lo importa `statistics`
    —que nosotros usamos para un cuantil normal— y también `tempfile`. Ninguna línea
    nuestra llama a `random`. Comprobar la importación mide a las dependencias; lo que hay
    que medir es si NOSOTROS lo usamos.

    Se analiza el ÁRBOL SINTÁCTICO, no el texto. La primera versión usaba una expresión
    regular y se cazó a sí misma: encontró `import random` dentro de una cadena de su
    propio mutante. Una guarda que da falsos positivos se acaba ignorando, y eso es peor
    que no tenerla. La regex nombraba el mecanismo (un patrón de texto); el AST nombra la
    propiedad (un uso real en el código).

    Devuelve la lista de usos, vacía si está limpia.
    """
    import ast as _ast
    usos = []
    for ruta in modulos:
        try:
            arbol = _ast.parse(open(ruta, encoding="utf-8").read())
        except (OSError, SyntaxError):
            continue
        for nodo in _ast.walk(arbol):
            if isinstance(nodo, _ast.Import):
                for a in nodo.names:
                    if a.name.split(".")[0] == "random":
                        usos.append((os.path.basename(ruta), nodo.lineno, f"import {a.name}"))
            elif isinstance(nodo, _ast.ImportFrom):
                if (nodo.module or "").split(".")[0] == "random":
                    usos.append((os.path.basename(ruta), nodo.lineno, f"from {nodo.module} import …"))
            elif isinstance(nodo, _ast.Attribute):
                v = nodo.value
                if isinstance(v, _ast.Name) and v.id == "random":
                    usos.append((os.path.basename(ruta), nodo.lineno, f"random.{nodo.attr}"))
    _contar("sin_azar_usado", bool(usos))
    if usos:
        raise GuardaViolada(
            f"«{nombre}» usa azar en {len(usos)} sitio(s): {usos[:5]}. La afirmación "
            f"«determinista» no se sostiene.")
    return usos


def informe(out=sys.stdout):
    """Lo que el cierre de fase necesita: qué guardas saltaron y cuáles callaron."""
    if not os.path.exists(CONTADORES):
        out.write("sin contadores todavía\n")
        return {}
    d = json.load(open(CONTADORES, encoding="utf-8"))
    out.write(f"{'guarda':<24}{'consultada':>11}{'saltó':>7}  último salto\n")
    for k, v in sorted(d.items()):
        out.write(f"{k:<24}{v['consultada']:>11}{v['salto']:>7}  {v['ultimo_salto'] or '—'}\n")
    calladas = [k for k, v in d.items() if v["salto"] == 0 and "[constructiva]" not in k]
    constructivas = [k for k in d if "[constructiva]" in k]
    if calladas:
        out.write(f"CALLADAS Y DETECTORAS (revisar: o el error ya no es posible, o no "
                  f"detectan): {', '.join(calladas)}\n")
    if constructivas:
        out.write(f"CONSTRUCTIVAS (no saltan por diseño; su silencio no es síntoma): "
                  f"{', '.join(constructivas)}\n")
    return d


if __name__ == "__main__":
    # Mutantes de las guardas: una guarda que no puede fallar no es guarda.
    print("=== mutantes de las guardas ===")
    ok = {}

    try:
        no_vacio([], "lista vacía")
        ok["no_vacio detecta la lista vacía"] = False
    except GuardaViolada:
        ok["no_vacio detecta la lista vacía"] = True
    ok["no_vacio deja pasar lo no vacío"] = (no_vacio([1, 2, 3], "tres") == 3)

    T = 8 ** 16
    limpio = [(r * 173961102589771) % T for r in range(2000)]
    sucio = [r * 10 ** 10 for r in range(2000)]
    try:
        muestreo_verificado(limpio, 8, 16, "paso coprimo")
        ok["muestreo_verificado deja pasar el limpio"] = True
    except GuardaViolada:
        ok["muestreo_verificado deja pasar el limpio"] = False
    try:
        muestreo_verificado(sucio, 8, 16, "paso 10^10")
        ok["muestreo_verificado detecta el retículo"] = False
    except GuardaViolada:
        ok["muestreo_verificado detecta el retículo"] = True

    try:
        estrato_de({"n": 8, "idx": 1}, "estrato")
        ok["estrato_de detecta la fila sin campo"] = False
    except GuardaViolada:
        ok["estrato_de detecta la fila sin campo"] = True
    ok["estrato_de devuelve el campo"] = (estrato_de({"estrato": "limpia"}) == "limpia")

    try:
        matar_por_pid(os.getpid())
        ok["matar_por_pid se niega a suicidarse"] = False
    except GuardaViolada:
        ok["matar_por_pid se niega a suicidarse"] = True

    try:
        salida_a_fichero("/tmp/prueba_guardas/salida.txt")
        ok["salida_a_fichero detecta el destino efímero"] = False
    except GuardaViolada:
        ok["salida_a_fichero detecta el destino efímero"] = True
    import tempfile as _tf
    _d = _tf.mkdtemp(dir=AQUI)
    try:
        f = salida_a_fichero(os.path.join(_d, "ok.txt"), "mutante")
        f.close()
        ok["salida_a_fichero deja pasar el destino durable"] = True
    except GuardaViolada:
        ok["salida_a_fichero deja pasar el destino durable"] = False
    import shutil as _sh
    _sh.rmtree(_d, ignore_errors=True)

    import tempfile as _t2
    _f = os.path.join(_t2.mkdtemp(dir=AQUI), "usa_azar.py")
    open(_f, "w").write("import random\nx = random.random()\n")
    try:
        sin_azar_usado([_f], "fichero que sí usa azar")
        ok["sin_azar_usado detecta el uso real"] = False
    except GuardaViolada:
        ok["sin_azar_usado detecta el uso real"] = True
    _g = os.path.join(os.path.dirname(_f), "solo_importa_dependencia.py")
    open(_g, "w").write("from statistics import NormalDist\n# random entra por statistics\n")
    try:
        sin_azar_usado([_g], "fichero limpio")
        ok["sin_azar_usado NO se queja de la dependencia"] = True
    except GuardaViolada:
        ok["sin_azar_usado NO se queja de la dependencia"] = False
    import shutil as _s2
    _s2.rmtree(os.path.dirname(_f), ignore_errors=True)

    for k, v in ok.items():
        print(f"  [{'OK' if v else 'ROTO'}] {k}")
    print(f"LAS GUARDAS {'SIRVEN' if all(ok.values()) else 'ESTÁN ROTAS'}\n")
    informe()
    sys.exit(0 if all(ok.values()) else 1)

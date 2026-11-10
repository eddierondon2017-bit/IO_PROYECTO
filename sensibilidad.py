# sensibilidad.py: desde tabla final
from fractions import Fraction
from modelo import fmt


def rango(lo, hi):
    a = "sin limite" if lo is None else fmt(lo)
    b = "sin limite" if hi is None else fmt(hi)
    return a, b


def calcular(p, r):
    if getattr(r, "indices_holgura", None) is not None:
        raise ValueError("El analisis de sensibilidad requiere una base sin filas redundantes; no se muestran precios sombra ambiguos.")
    n, T, dz, base = p.n, r.T, r.dz, r.base
    ncols = len(dz)
    sobj = 1 if p.objetivo == "max" else -1
    uz = p.unidad_z

    # rango de cada cj
    costos = []
    for k in range(n):
        lo = hi = None
        if k in base:
            i = base.index(k)
            for j in range(ncols):
                if j in base or T[i][j] == 0:
                    continue
                lim = dz[j] / T[i][j]
                if T[i][j] > 0:
                    lo = lim if lo is None else max(lo, lim)
                else:
                    hi = lim if hi is None else min(hi, lim)
        else:
            hi = -dz[k]
        c = p.costos[k]
        if p.objetivo == "max":
            cmin = None if lo is None else c + lo
            cmax = None if hi is None else c + hi
        else:
            cmin = None if hi is None else c - hi
            cmax = None if lo is None else c - lo
        a, b = rango(cmin, cmax)
        costos.append({
            "variable": p.nombres[k], "actual": fmt(c), "minimo": a, "maximo": b,
            "frase": f"Mientras el costo de {p.nombres[k]} este entre {a} y {b} {uz}, "
                     f"la base actual sigue siendo optima (cambiando solo este costo)."})

    # precio sombra y rango de cada bi
    rests = []
    for k, rest in enumerate(p.restricciones):
        idx = [i for i, (orig, s) in enumerate(r.filas) if orig == k]
        precio = sum(sobj * r.filas[i][1] * (-dz[n + i]) for i in idx)
        col = [sum(r.filas[i][1] * T[a][n + i] for i in idx) for a in range(len(T))]
        lo = hi = None
        for a in range(len(T)):
            if col[a] == 0:
                continue
            lim = -T[a][-1] / col[a]
            if col[a] > 0:
                lo = lim if lo is None else max(lo, lim)
            else:
                hi = lim if hi is None else min(hi, lim)
        b0 = rest["b"]
        bmin = None if lo is None else b0 + lo
        bmax = None if hi is None else b0 + hi
        holg = Fraction(0)
        if rest["signo"] != "=" and (n + idx[0]) in base:
            holg = T[base.index(n + idx[0])][-1]
        a, b = rango(bmin, bmax)
        if precio == 0:
            frase = (f"{rest['nombre']} tiene precio sombra cero (holgura {fmt(holg)}); "
                     f"cambiar solo su lado derecho entre {a} y {b} mantiene z constante.")
        else:
            frase = (f"Una unidad mas de {rest['nombre']} cambia z en {fmt(precio)} {uz} "
                     f"mientras su valor este entre {a} y {b}.")
        rests.append({
            "restriccion": rest["nombre"], "actual": fmt(b0), "precio_sombra": fmt(precio),
            "minimo": a, "maximo": b, "holgura": fmt(holg),
            "activa": "si" if holg == 0 else "no", "frase": frase})
    return {"costos": costos, "restricciones": rests}
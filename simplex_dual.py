# simplex_dual.py: metodo dual
from fractions import Fraction
from modelo import fmt

MAX_IT = 200


class Resultado:
    def __init__(self):
        self.estado = ""   # optimo, infactible, no_dual_factible, no_termina
        self.mensajes = []
        self.tablas = []
        self.x = []
        self.z = None
        self.T = []        # tabla final
        self.dz = []       # cj - zj final
        self.base = []
        self.filas = []    # (restriccion origen, signo)
        self.cw = []
        self.nombres_cols = []


def preparar(p):
    # todo a forma <=
    filas = []
    for k, r in enumerate(p.restricciones):
        if r["signo"] in ("<=", "="):
            filas.append((list(r["coef"]), r["b"], k, 1))
        if r["signo"] in (">=", "="):
            filas.append(([-c for c in r["coef"]], -r["b"], k, -1))
    return filas


def guardar(res, titulo, T, dz, base, cw, nota):
    # foto de tabla
    w = sum(cw[base[i]] * T[i][-1] for i in range(len(T)))
    res.tablas.append({
        "titulo": titulo,
        "columnas": res.nombres_cols + ["RHS"],
        "base": [res.nombres_cols[b] for b in base],
        "filas": [[fmt(v) for v in fila] for fila in T],
        "zrow": [fmt(v) for v in dz] + [fmt(w)],
        "nota": nota,
    })


def resolver(p):
    res = Resultado()
    filas = preparar(p)
    m, n = len(filas), p.n
    ncols = n + m
    res.nombres_cols = list(p.nombres) + [f"s{i + 1}" for i in range(m)]
    res.filas = [(f[2], f[3]) for f in filas]

    # tabla inicial
    T = []
    for i, (coef, b, _, _) in enumerate(filas):
        ident = [Fraction(1) if j == i else Fraction(0) for j in range(m)]
        T.append(list(coef) + ident + [b])
    sg = 1 if p.objetivo == "max" else -1
    cw = [sg * c for c in p.costos] + [Fraction(0)] * m
    dz = list(cw)
    base = [n + i for i in range(m)]
    res.cw = cw

    # dual factible?
    if any(dz[j] > 0 for j in range(n)):
        # Si no arranca dual, no rechazamos un problema valido.
        from arranque_dos_fases import resolver_con_dos_fases
        return resolver_con_dos_fases(p, res, filas, guardar)

    it = 0
    while True:
        # fila pivote: RHS mas negativo
        r, menor = None, Fraction(0)
        for i in range(m):
            if T[i][-1] < menor:
                menor, r = T[i][-1], i
        titulo = f"Tabla {it}" + (" (inicial)" if it == 0 else "")
        if r is None:
            guardar(res, titulo + " (final)", T, dz, base, cw, "Todos los RHS son no negativos: optimo")
            res.estado = "optimo"
            break
        # columna pivote: razon minima
        cand = [j for j in range(ncols) if T[r][j] < 0]
        if not cand:
            guardar(res, titulo, T, dz, base, cw,
                    f"Fila {res.nombres_cols[base[r]]} con RHS negativo y sin coeficientes negativos: infactible")
            res.estado = "infactible"
            res.mensajes.append("Problema infactible: una restriccion no se puede cumplir.")
            break
        razon = {j: dz[j] / T[r][j] for j in cand}
        minimo = min(razon.values())
        empate = [j for j in cand if razon[j] == minimo]
        c = empate[0]
        pivote = T[r][c]
        nota = (f"Sale {res.nombres_cols[base[r]]} (RHS {fmt(T[r][-1])}). "
                f"Entra {res.nombres_cols[c]} (razon {fmt(minimo)}). Pivote = {fmt(pivote)}.")
        if len(empate) > 1:
            nota += " Empate de razones (degeneracion)."
            res.mensajes.append(f"Tabla {it}: empate de razones, se eligio la primera columna.")
        guardar(res, titulo, T, dz, base, cw, nota)
        # pivotear
        T[r] = [v / pivote for v in T[r]]
        for i in range(m):
            if i != r and T[i][c] != 0:
                f = T[i][c]
                T[i] = [a - f * b for a, b in zip(T[i], T[r])]
        f = dz[c]
        dz = [a - f * b for a, b in zip(dz, T[r][:ncols])]
        base[r] = c
        it += 1
        if it > MAX_IT:
            res.estado = "no_termina"
            res.mensajes.append("Demasiadas iteraciones: posible ciclaje.")
            break

    res.T, res.dz, res.base = T, dz, base
    if res.estado == "optimo":
        res.x = [Fraction(0)] * n
        for i, b in enumerate(base):
            if b < n:
                res.x[b] = T[i][-1]
        w = sum(cw[base[i]] * T[i][-1] for i in range(m))
        res.z = w if p.objetivo == "max" else -w
        if any(T[i][-1] == 0 for i in range(m)):
            res.mensajes.append("Solucion degenerada: una variable basica vale cero.")
        if any(dz[j] == 0 for j in range(ncols) if j not in base):
            res.mensajes.append("Posibles optimos alternativos (un cj - zj no basico es cero).")
    return res
# modelo.py: datos y validacion del modelo de pl
from fractions import Fraction

MAX_VARS = 8
MAX_REST = 8
SIGNOS = ("<=", ">=", "=")


class Problema:
    # contenedor simple para el modelo de pl
    def __init__(self, objetivo, nombres, unidades, costos, restricciones, unidad_z=""):
        self.objetivo = objetivo            # min o max
        self.nombres = nombres              # nombres de las variables de decision
        self.unidades = unidades            # unidades de medida
        self.costos = costos                # coeficientes cj en z (Fraction)
        self.restricciones = restricciones  # lista de dicts: nombre, coef, signo, b
        self.unidad_z = unidad_z

    @property
    def n(self):
        # retorna el numero de variables de decision
        return len(self.costos)


def fmt(x):
    # formatea las variables de decision y z a texto sin decimales innecesarios
    if x is None:
        return "-"
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    return f"{float(x):.4f}".rstrip("0").rstrip(".")


def leer_numero(valor, donde, errores):
    # convierte las entradas a Fraction para no perder precision en las variables
    texto = str(valor).strip().replace(",", ".")
    if texto == "" or texto.lower() in ("nan", "none"):
        errores.append(f"{donde}: campo vacio")
        return None
    try:
        return Fraction(texto)
    except (ValueError, ZeroDivisionError):
        errores.append(f"{donde}: '{valor}' no es un numero")
        return None


def construir_problema(datos):
    # valida y empaqueta las variables de decision y restricciones
    errores = []
    if datos.get("objetivo") not in ("min", "max"):
        errores.append("El objetivo debe ser min o max")
    vars_ = datos.get("variables", [])
    rests = datos.get("restricciones", [])
    if not 1 <= len(vars_) <= MAX_VARS:
        errores.append(f"Variables: de 1 a {MAX_VARS}")
    if not 1 <= len(rests) <= MAX_REST:
        errores.append(f"Restricciones: de 1 a {MAX_REST}")
    if errores:
        return None, errores

    nombres, unidades, costos = [], [], []
    # aca procesa los nombres y costos cj de cada variable de decision
    for i, v in enumerate(vars_):
        nombres.append(str(v.get("nombre", "")).strip() or f"x{i + 1}")
        unidades.append(str(v.get("unidad", "")).strip())
        costos.append(leer_numero(v.get("costo", ""), f"Costo de x{i + 1}", errores))

    filas = []
    # aca procesa la matriz de coeficientes aij para las variables de decision y los lados derechos bi
    for j, r in enumerate(rests):
        et = f"Restriccion {j + 1}"
        coef = r.get("coef", [])
        if len(coef) != len(vars_):
            errores.append(f"{et}: faltan coeficientes")
            continue
        fila = [leer_numero(c, f"{et}, x{k + 1}", errores) for k, c in enumerate(coef)]
        b = leer_numero(r.get("b", ""), f"{et}, lado derecho", errores)
        signo = r.get("signo")
        if signo not in SIGNOS:
            errores.append(f"{et}: elija el signo")
        if None not in fila and all(c == 0 for c in fila):
            errores.append(f"{et}: todos los coeficientes son cero")
        nombre = str(r.get("nombre", "")).strip() or f"R{j + 1}"
        filas.append({"nombre": nombre, "coef": fila, "signo": signo, "b": b})

    if errores:
        return None, errores
    return Problema(
        datos["objetivo"],
        nombres,
        unidades,
        costos,
        filas,
        str(datos.get("unidad_z", "")).strip()
    ), []
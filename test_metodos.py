# test_metodos.py: pruebas automaticas
# correr: pytest
import json
import os
from fractions import Fraction

import metodo_grafico as mg
import sensibilidad
import simplex_dual as sd
from modelo import construir_problema

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ejemplos.json")
with open(RUTA, encoding="utf-8") as f:
    EJ = json.load(f)


def problema(nombre):
    p, errores = construir_problema(EJ[nombre])
    assert errores == []
    return p


def test_grafico_caso_real():
    r = mg.resolver(problema("Ever Ace (caso real)"))
    assert r.estado == "optimo"
    v = [v for v in r.vertices if v.es_optimo][0]
    assert (v.x1, v.x2, v.z) == (5310, 204, 4362444)
    assert len(r.vertices) == 4


def test_dual_caso_real():
    r = sd.resolver(problema("Ever Ace (caso real)"))
    assert r.estado == "optimo"
    assert r.x == [5310, 204] and r.z == 4362444
    assert len(r.tablas) >= 2


def test_dual_tres_variables():
    r = sd.resolver(problema("Prueba mezcla 3 variables"))
    assert r.estado == "optimo" and r.z == 26


def test_infactible_los_dos():
    p = problema("Prueba infactible")
    assert mg.resolver(p).estado == "infactible"
    assert sd.resolver(p).estado == "infactible"


def test_grafico_alternativos():
    r = mg.resolver(problema("Prueba optimos alternativos (max)"))
    assert r.estado == "alternativos"
    assert sum(v.es_optimo for v in r.vertices) == 2


def test_grafico_no_acotado():
    assert mg.resolver(problema("Prueba no acotado (max)")).estado == "no_acotado"


def test_dual_no_dual_factible():
    r = sd.resolver(problema("Prueba optimos alternativos (max)"))
    assert r.estado == "optimo" and r.z == 16


def test_validacion():
    malo = json.loads(json.dumps(EJ["Ever Ace (caso real)"]))
    malo["variables"][0]["costo"] = "abc"
    malo["restricciones"][1]["b"] = ""
    p, errores = construir_problema(malo)
    assert p is None and len(errores) == 2


def test_sensibilidad_caso_real():
    p = problema("Ever Ace (caso real)")
    s = sensibilidad.calcular(p, sd.resolver(p))
    assert s["costos"][0]["minimo"] == "0" and s["costos"][0]["maximo"] == "1446"
    assert s["costos"][1]["minimo"] == "766" and s["costos"][1]["maximo"] == "sin limite"
    rs = s["restricciones"]
    assert [x["precio_sombra"] for x in rs] == ["766", "680", "0", "0"]
    assert (rs[0]["minimo"], rs[0]["maximo"]) == ("204", "16645")
    assert (rs[1]["minimo"], rs[1]["maximo"]) == ("0", "645")


def test_metodos_coinciden():
    p = problema("Ever Ace (caso real)")
    g = [v for v in mg.resolver(p).vertices if v.es_optimo][0]
    assert g.z == sd.resolver(p).z

def test_ejercicio_36():
    p = problema("Ejercicio de practica (optimo 36)")
    d = sd.resolver(p)
    g = mg.resolver(p)
    assert d.estado == "optimo" and d.z == 36 and d.x == [6, 4]
    assert any(v.es_optimo and v.z == 36 for v in g.vertices)
    assert sensibilidad.calcular(p, d)["costos"]


def test_igualdad():
    datos = {"objetivo":"min", "variables":[{"costo":2},{"costo":1}],
             "restricciones":[{"coef":[1,1],"signo":"=","b":5},
                               {"coef":[1,0],"signo":">=","b":2}]}
    p, errores = construir_problema(datos)
    assert not errores
    r = sd.resolver(p)
    assert r.estado == "optimo" and r.z == 7 and r.x == [2,3]

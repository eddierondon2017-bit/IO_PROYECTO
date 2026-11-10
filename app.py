# app.py: interfaz streamlit estilo evergreen
# correr: streamlit run app.py

import json
import os
import pandas as pd
import streamlit as st

import metodo_grafico as mg
import simplex_dual as sd
from grafico import dibujar
from modelo import MAX_REST, MAX_VARS, construir_problema, fmt
from sensibilidad import calcular

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ejemplos.json")
BLANCO = "Problema nuevo en blanco"
EST_G = {
    "optimo": ("success", "Solucion optima unica."),
    "alternativos": ("warning", "Optimos alternativos."),
    "infactible": ("error", "Problema infactible."),
    "no_acotado": ("error", "Problema no acotado.")
}
EST_D = {
    "optimo": ("success", "Solucion optima encontrada."),
    "infactible": ("error", "Problema infactible."),
    "no_dual_factible": ("warning", "No es dual factible."),
    "no_acotado": ("error", "Problema no acotado."),
    "no_termina": ("error", "No termino.")
}

# En esta parte cambiamos toda la apariencia de la pagina.
# La idea es que se vea como Airbnb o Tesla, pero con
# los colores de Evergreen Marine: verde, blanco y negro.
# Esto no cambia los calculos ni las funciones del proyecto.

st.markdown("""

<style>

/* 1. Colores generales */

:root {
    color-scheme: light !important;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"] {
    background-color: #ffffff !important;
    color: #151515 !important;
    color-scheme: light !important;
}

/* 2. Contenido principal */

.block-container {
    max-width: 1250px !important;
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}

/* 3. Titulos */

h1 {
    color: #087c4a !important;
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    letter-spacing: -1.2px !important;
}

h2, h3, h4 {
    color: #087c4a !important;
    font-weight: 750 !important;
}

p, label {
    color: #151515;
}

/* 4. Campos de entrada blancos */

/* Campos normales de la pagina */

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #ffffff !important;
    color: #151515 !important;
    caret-color: #087c4a !important;
}

/* Celda que estamos editando en las tablas */

[data-testid="stDataEditor"] input,
[data-testid="stDataEditor"] textarea,
[data-testid="stDataFrame"] input,
[data-testid="stDataFrame"] textarea,
[data-baseweb="popover"] input {
    background-color: #171717 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
}

/* 5. Minimizar y maximizar */

[data-testid="stRadio"] label,
[data-testid="stRadio"] label *,
[data-testid="stRadio"] p {
    color: #111111 !important;
    opacity: 1 !important;
}

[data-testid="stRadio"] [role="radiogroup"] {
    gap: 20px !important;
}

[data-testid="stRadio"] input {
    accent-color: #087c4a !important;
}

[data-testid="stRadio"] label {
    background: #ffffff !important;
    padding: 6px 10px !important;
    border-radius: 9px !important;
}

/* 6. Tablas de variables y restricciones */

[data-testid="stDataFrame"],
[data-testid="stDataEditor"] {
    background-color: #ffffff !important;
    color: #151515 !important;
    border: 1px solid #333333 !important;
    border-radius: 13px !important;
    overflow: hidden !important;
    color-scheme: light !important;
}

[data-testid="stDataFrame"] *,
[data-testid="stDataEditor"] * {
    color-scheme: light !important;
}

[data-testid="stDataFrameToolbar"],
[data-testid="stDataEditor"] [data-testid="stElementToolbar"] {
    background-color: #ffffff !important;
}

/* 7. Etiquetas de los formularios */

[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stMarkdownContainer"] p {
    color: #151515;
}

[data-testid="stWidgetLabel"] {
    font-weight: 600 !important;
}

/* 8. Botones verdes */

.stButton > button,
.stFormSubmitButton > button {
    background-color: #087c4a !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 11px 26px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}

.stButton > button *,
.stFormSubmitButton > button * {
    color: #ffffff !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #065d38 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 100, 60, 0.18);
}

/* 9. Tarjetas de resultados */

[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #dddddd !important;
    border-left: 4px solid #087c4a !important;
    border-radius: 14px !important;
    padding: 18px !important;
}

[data-testid="stMetric"] * {
    color: #151515 !important;
}

/* 10. Contenedores y formularios */

[data-testid="stForm"] {
    background-color: #ffffff !important;
    border: 1px solid #dddddd !important;
    border-radius: 20px !important;
    padding: 20px !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
}

/* 11. Pestañas de los metodos */

button[data-baseweb="tab"] {
    color: #333333 !important;
    font-weight: 650 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #087c4a !important;
    border-bottom: 3px solid #087c4a !important;
}

/* 12. Menu lateral */

[data-testid="stSidebar"] {
    background-color: #f7faf8 !important;
    border-right: 1px solid #e5e5e5 !important;
}

/* 13. Decoracion Evergreen Marine */

.block-container::before {
    content: "EVERGREEN MARINE  /  OPERATIONS RESEARCH";
    display: block;
    color: #087c4a;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 3px;
    border-top: 4px solid #087c4a;
    padding-top: 16px;
    margin-bottom: 22px;
}

/* 14. Pie de pagina */

.block-container::after {
    content: "EVERGREEN MARINE  |  IO1 - GRUPO 7es  |  OPTIMIZACION MARITIMA";
    display: block;
    margin-top: 65px;
    padding: 24px 0;
    border-top: 1px solid #dce8e0;
    color: #087c4a;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-align: center;
}

/* 15. Detalles finales */

hr {
    border: none !important;
    height: 1px !important;
    background-color: #d9e8df !important;
}

[data-testid="stAlert"] {
    border-radius: 14px !important;
}

[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #dddddd !important;
    border-radius: 12px !important;
}
/* 16. Edicion de celdas */

[data-testid="stDataEditor"] input:focus,
[data-testid="stDataFrame"] input:focus,
[data-baseweb="popover"] input:focus {
    background-color: #171717 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    color-scheme: dark !important;
}

/* Evitar que el cuadro de edicion herede el fondo blanco */

[data-testid="stDataEditor"] [data-baseweb="input"],
[data-testid="stDataFrame"] [data-baseweb="input"],
[data-baseweb="popover"] [data-baseweb="input"] {
    background-color: #171717 !important;
    color-scheme: dark !important;
}
</style>
""", unsafe_allow_html=True)



@st.cache_data
def cargar():
    # carga los ejemplos precargados del json
    with open(RUTA, encoding="utf-8") as f:
        return json.load(f)


def df_variables(base, n):
    # arma la tabla con los nombres y costos en z de las variables de decision
    vs = base.get("variables", [])
    filas = []
    for i in range(n):
        v = vs[i] if i < len(vs) else {}
        filas.append({
            "Nombre": str(v.get("nombre", "")),
            "Unidad": str(v.get("unidad", "")),
            "Costo en z": str(v.get("costo", ""))
        })
    return pd.DataFrame(filas)


def df_restricciones(base, n):
    # coge las restricciones y arma la matriz con los coeficientes de las variables de decision
    rs = base.get("restricciones") or [{} for _ in range(3)]
    filas = []
    for r in rs:
        fila = {"Nombre": str(r.get("nombre", ""))}
        coef = r.get("coef", [])
        for i in range(n):
            fila[f"x{i + 1}"] = str(coef[i]) if i < len(coef) else ""
        fila["Signo"] = r.get("signo", "<=")
        fila["Lado derecho"] = str(r.get("b", ""))
        filas.append(fila)
    return pd.DataFrame(filas)


def mostrar_tabla(t):
    # muestra las tablas iterativas del simplex dual en pantalla
    st.markdown(f"**{t['titulo']}**")
    if t["nota"]:
        st.caption(t["nota"])
    df = pd.DataFrame(t["filas"] + [t["zrow"]], columns=t["columnas"], index=t["base"] + ["Cj-Zj"])
    st.dataframe(df, use_container_width=True)


def mostrar(p):
    # ejecuta los resultados usando las variables de decision en cada pestaña
    t1, t2, t3, t4 = st.tabs(["Metodo grafico", "Simplex dual", "Sensibilidad", "Comparacion"])
    rg = rd = None

    with t1:
        if p.n != 2:
            st.info("El metodo grafico solo sirve con 2 variables.")
        else:
            rg = mg.resolver(p)
            tipo, txt = EST_G[rg.estado]
            getattr(st, tipo)(f"**{txt}** {mg.interpretar(p, rg)}")
            st.pyplot(dibujar(p, rg))
            # aca muestra las variables de decision x1 y x2 en cada vertice
            st.dataframe([
                {
                    "Vertice": f"V{i + 1}",
                    p.nombres[0]: fmt(v.x1),
                    p.nombres[1]: fmt(v.x2),
                    "z": fmt(v.z),
                    "Activas": ", ".join(v.activas),
                    "Optimo": "*" if v.es_optimo else ""
                } for i, v in enumerate(rg.vertices)
            ], use_container_width=True)
            with st.expander("Paso a paso"):
                for linea in rg.pasos:
                    st.text(linea)

    with t2:
        # calcula el resultado del simplex dual con las variables de decision
        rd = sd.resolver(p)
        tipo, txt = EST_D[rd.estado]
        getattr(st, tipo)(f"**{txt}**")
        for m in rd.mensajes:
            st.warning(m)
        for t in rd.tablas:
            mostrar_tabla(t)
        if rd.estado == "optimo":
            st.dataframe([
                {"Variable": p.nombres[k], "Valor": fmt(v), "Unidad": p.unidades[k]}
                for k, v in enumerate(rd.x)
            ], use_container_width=True)
            st.success(f"z = {fmt(rd.z)} {p.unidad_z}")

    with t3:
        # evalua la sensibilidad de las variables de decision y lados derechos
        if rd is not None and rd.estado == "optimo":
            try:
                s = calcular(p, rd)
            except ValueError as exc:
                st.warning(str(exc))
                s = None
            if s is not None:
                st.caption("Los rangos se calculan cambiando un solo parametro a la vez y conservando la base optima.")
                st.markdown("**Rango de cada costo (cj)**")
                st.dataframe([{k: v for k, v in f.items() if k != "frase"} for f in s["costos"]], use_container_width=True)
                for f in s["costos"]:
                    st.write("- " + f["frase"])
                st.markdown("**Precio sombra y rango de cada lado derecho (bi)**")
                st.dataframe([{k: v for k, v in f.items() if k != "frase"} for f in s["restricciones"]], use_container_width=True)
                for f in s["restricciones"]:
                    st.write("- " + f["frase"])
        else:
            st.info("La sensibilidad necesita una solucion optima del simplex dual.")

    with t4:
        # compara z del grafico contra el dual simplex
        if rg is not None and rd is not None and rd.estado == "optimo" and rg.vertices \
                and rg.estado in ("optimo", "alternativos"):
            zg = [v.z for v in rg.vertices if v.es_optimo][0]
            if zg == rd.z:
                st.success(f"Los dos metodos coinciden: z = {fmt(zg)} {p.unidad_z}")
            else:
                st.error(f"No coinciden: grafico {fmt(zg)} y dual {fmt(rd.z)}")
        else:
            st.info("Se compara cuando hay 2 variables y los dos tienen optimo.")
        st.write(f"Iteraciones del dual: {max(len(rd.tablas) - 1, 0) if rd else '-'}")


# pantalla principal
st.title("EVERGREEN | Optimizacion de recursos")
st.caption("Metodo grafico · Simplex Dual · Analisis de sensibilidad | IO1 - Grupo 7es")

ejemplos = cargar()
nombre = st.selectbox("Ejemplo precargado", [BLANCO] + list(ejemplos), index=1)
base = {} if nombre == BLANCO else ejemplos[nombre]


c1, c2, c3 = st.columns(3)
obj = c1.radio(
    "Objetivo", ["min", "max"], key=f"obj_{nombre}", horizontal=True,
    index=0 if base.get("objetivo", "min") == "min" else 1,
    format_func=lambda v: "Minimizar" if v == "min" else "Maximizar"
)
uz = c2.text_input("Unidad de z (ej. USD)", value=base.get("unidad_z", ""), key=f"uz_{nombre}")
n = int(c3.number_input(
    f"Numero de variables (1 a {MAX_VARS})", 1, MAX_VARS,
    value=len(base.get("variables", [])) or 2, key=f"n_{nombre}"
))


# captura las variables de decision y restricciones
st.markdown("**Variables de Decision** (nombre, unidad y costo en z)")
ed_v = st.data_editor(df_variables(base, n), key=f"v_{nombre}_{n}", hide_index=True, use_container_width=True)

st.markdown(f"**Restricciones** (hasta {MAX_REST}; agregue filas abajo de la tabla)")
ed_r = st.data_editor(
    df_restricciones(base, n), key=f"r_{nombre}_{n}", num_rows="dynamic",
    hide_index=True, use_container_width=True,
    column_config={"Signo": st.column_config.SelectboxColumn("Signo", options=["<=", ">=", "="], required=True)}
)

# pasa la informacion capturada de las variables de decision al resolvedor
if st.button("Resolver", type="primary"):
    datos = {
        "objetivo": obj,
        "unidad_z": uz,
        "variables": [
            {"nombre": r["Nombre"], "unidad": r["Unidad"], "costo": r["Costo en z"]}
            for _, r in ed_v.iterrows()
        ],
        "restricciones": [
            {
                "nombre": r["Nombre"],
                "coef": [r[f"x{i + 1}"] for i in range(n)],
                "signo": r["Signo"],
                "b": r["Lado derecho"]
            }
            for _, r in ed_r.iterrows()
        ],
    }
    
    problema, errores = construir_problema(datos)
    if errores:
        st.error("Revise los datos:")
        for e in errores:
            st.markdown(f"- {e}")
    else:
        try:
            mostrar(problema)
        except Exception as exc:
            st.error(f"Error inesperado: {exc}")
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
    "no_termina": ("error", "No termino.")
}

# configuracion de pagina
st.set_page_config(page_title="IO1 Grupo 7es", layout="wide")

# css para corregir colores de letra y contrastes
st.markdown("""
    <style>
    /* fondo principal */
    .stApp {
        background-color: #F4F7F4;
        color: #1B4332;
    }
    
    /* titulos */
    h1, h2, h3, h4 {
        color: #1E4D2B !important;
        font-weight: 700;
    }
    
    /* solucion al texto que no se ve en etiquetas y radios */
    label, p, span, div[data-aria-hidden="true"] {
        color: #1B4332 !important;
        font-weight: 600;
    }
    
    /* tarjetas */
    .css-card {
        background-color: #FFFFFF;
        padding: 1.25rem;
        border-radius: 10px;
        border-left: 5px solid #52B788;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* boton principal verde */
    div.stButton > button:first-child {
        background-color: #2D6A4F;
        color: #FFFFFF !important;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
    }
    div.stButton > button:first-child:hover {
        background-color: #52B788;
        color: #081C15 !important;
    }
    
    /* pestanas */
    button[data-baseweb="tab"] {
        color: #2D6A4F !important;
        font-weight: 600;
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
            s = calcular(p, rd)
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
st.title("Metodo grafico y Simplex Dual")
st.caption("Proyecto Final Investigacion de Operaciones 1 - Grupo 7es (IO1-82)")

ejemplos = cargar()
nombre = st.selectbox("Ejemplo precargado", [BLANCO] + list(ejemplos), index=1)
base = {} if nombre == BLANCO else ejemplos[nombre]

st.markdown('<div class="css-card">', unsafe_allow_html=True)
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
st.markdown('</div>', unsafe_allow_html=True)

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
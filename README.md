# Proyecto Final IO1 - Grupo 7es (IO1-82)

Metodo grafico y Simplex Dual en Python. Caso real: combustible del buque Ever Ace.
Los metodos estan programados a mano (sin scipy, pulp ni solvers). Los datos se escriben
en la interfaz; los ejemplos viven en `ejemplos.json`.

## Archivos
| Archivo | Para que sirve |
|---|---|
| `app.py` | Interfaz (Streamlit): ingreso, validacion y resultados |
| `modelo.py` | Valida datos y arma el problema |
| `metodo_grafico.py` | Vertices, optimo, casos especiales (2 variables) |
| `grafico.py` | Dibuja rectas, region factible y optimo |
| `simplex_dual.py` | Tablas, pivotes y solucion del dual |
| `sensibilidad.py` | Precios sombra y rangos de cj y bi (desde la tabla final) |
| `ejemplos.json` | Caso real y 4 pruebas (infactible, alternativos, no acotado, 3 variables) |
| `test_metodos.py` | 10 pruebas automaticas |
| `verificacion_externa.py` | Compara con scipy (solo para comprobar) |

## Instalar y ejecutar
```
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
o
```
pip install -r requirements.txt
streamlit run app.py
```
en linux
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
1. Elija un ejemplo o "Problema nuevo en blanco".
2. Escriba variables (nombre, unidad, costo) y restricciones (coeficientes, signo, lado derecho).
3. Clic en **Resolver**: salen pestanas de grafico, simplex dual, sensibilidad y comparacion.

## Pruebas y verificacion
```
pytest
python verificacion_externa.py
```
Tambien se puede comprobar en Excel con Solver (solo para verificar, no dentro del codigo).

## Como funciona el Simplex Dual
1. Si es min, se pasa a max con W = -Z; las restricciones >= se multiplican por -1; las = se parten en dos.
2. Se agregan holguras. Si algun cj - zj de una variable es positivo, el dual no arranca (aviso en pantalla).
3. Sale la fila con RHS mas negativo; entra la columna con razon minima (cj - zj) / coeficiente.
4. Se repite hasta que no haya RHS negativos. Fila negativa sin coeficientes negativos = infactible.
5. Avisos: empate de razones, solucion degenerada y posibles optimos alternativos.

## Limites
- Grafico: exactamente 2 variables, hasta 8 restricciones.
- Dual: hasta 8 variables y 8 restricciones, solo si el problema es dual factible de entrada
  (tipico de minimizar con costos positivos y restricciones >=).

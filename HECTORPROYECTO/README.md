# Base de datos para inversiones (Tkinter + SQLite)

Aplicación de escritorio en Python 3.11 para gestionar clientes inversionistas:
- Pantalla inicial con **cards** por cliente y un card **“+ Crear cliente”**.
- Vista por cliente con capital disponible, **Ingresar/Retirar capital**, tabla **Portafolio actual** (Precio Promedio, Precio Actual, Valor, P&L), acciones **BUY, SELL, PRICE_UPDATE**.
- **Historial colapsable** con filtros por **día** (`YYYY-MM-DD`) o **rango** y **exportar a CSV**.

## Requisitos
- Python 3.11
- Sin dependencias externas (solo `tkinter` y `sqlite3` estándar).

## Estructura

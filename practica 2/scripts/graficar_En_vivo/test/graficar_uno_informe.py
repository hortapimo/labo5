from pathlib import Path
import pandas as pd
import funciones as misf
import matplotlib.pyplot as plt

plt.style.use('estiloGraficos2.mplstyle')

def cargarArchivo(archivo: Path | str, num_bloques: int = 81, puntos_por_bloque: int = 1024) -> list[pd.DataFrame]:
    columnas = ["tiempo [ns]", "canal 1 [mV]", "canal 2 [mV]", "canal 3 [mV]"]
    dataframes = []

    with open(archivo, "r", encoding="utf-8", errors="replace") as f:
        # Saltear el header global inicial (primeras 4 líneas)
        for _ in range(4):
            f.readline()

        for i in range(num_bloques):
            df_bloque = pd.read_csv(
                f,
                nrows=puntos_por_bloque,
                sep=r"\s+",
                header=None,
                names=columnas,
                engine="python"
            )
            dataframes.append(df_bloque)

            # Consumir la línea en blanco y los 2 headers entre bloques
            if i < num_bloques - 1:
                for _ in range(3):
                    f.readline()

    return dataframes

archivo = "run_20260911_131544_idx0_selected.txt"
#archivo2 = "run_20260925_105451_idx11_selected.txt"
#archivo3 = "run_20260925_113849_idx1_selected.txt"
#archivo4 = "run_20260925_115320_idx0_selected.txt"
#archivo5 = "run_20260925_120111_idx0_selected.txt"
#archivo6 = "run_20260925_130253_idx0_selected.txt"
#archivo7 = "run_20260925_132914_idx0_selected.txt"

dataframes = misf.cargarArchivo(archivo) 
df = dataframes[0]
fig, ax = plt.subplots(figsize=(8, 6))
# Graficar (heredando el tamaño de marcador y grosor del .mplstyle)
ax.errorbar(df["tiempo [ns]"], df["canal 1 [mV]"], fmt=".",markersize=5, label='Canal 1 ')
ax.errorbar(df["tiempo [ns]"], df["canal 2 [mV]"], fmt=".",markersize=5, label='Canal 2 ')
ax.errorbar(df["tiempo [ns]"], df["canal 3 [mV]"], fmt=".",markersize=5, label='Canal 3 ')
# --- INICIO DEL ZOOM ---
# Posición del recuadro dentro de la figura: [posición_x, posición_y, ancho, alto]
axins = ax.inset_axes([0.3, 0.1, 0.45, 0.4]) 

# Re-graficamos los datos dentro del recuadro sumando capsize
#axins.errorbar(v, i, xerr=error_sistematico_v, yerr=error_sistematico_i, 
#                fmt="o", capsize=3, alpha=0.8)
axins.errorbar(df["tiempo [ns]"], df["canal 1 [mV]"], fmt=".",markersize=9)
axins.errorbar(df["tiempo [ns]"], df["canal 2 [mV]"], fmt=".",markersize=9)
axins.errorbar(df["tiempo [ns]"], df["canal 3 [mV]"], fmt=".",markersize=9)

# Trazamos la línea vertical también dentro del zoom
#axins.axvline(v_min, color='red', linestyle='--', alpha=0.7)
#axins.axhline(0, color='black', linestyle='--', alpha=0.7)
# Límites de tu zona de interés para el zoom
axins.set_xlim(180,250) 
axins.set_ylim(-140,-20) 
#axins.grid(which="both", alpha=0.3)
#axins.minorticks_on()

# Dibuja las líneas que conectan la zona original con el recuadro
ax.indicate_inset_zoom(axins, edgecolor="black")
# --- FIN DEL ZOOM ---
ax.set_xlabel('t [ns]')
ax.set_ylabel('Voltaje [mV]')
ax.set_xlim(-50,1750)
ax.set_ylim(-140,40)
ax.legend(loc='lower right')
plt.show()

from pathlib import Path
import pandas as pd
import funciones as misf
import matplotlib.pyplot as plt

plt.style.use('estiloGraficos.mplstyle')

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

archivo = "run_20260925_105124_idx0_selected.txt"
archivo2 = "run_20260925_105451_idx11_selected.txt"
archivo3 = "run_20260925_113849_idx1_selected.txt"
archivo4 = "run_20260925_115320_idx0_selected.txt"
archivo5 = "run_20260925_120111_idx0_selected.txt"
archivo6 = "run_20260925_130253_idx0_selected.txt"
archivo7 = "run_20260925_132914_idx0_selected.txt"

dataframes = misf.cargarArchivo(archivo7) 
num = 11
df=dataframes[num]

# 3. Crear y configurar la figura
fig, ax = plt.subplots(figsize=(9, 6))
plt.title(label=f"Data Frame = {num}")
# Graficar (heredando el tamaño de marcador y grosor del .mplstyle)
ax.plot(df["tiempo [ns]"], df["canal 1 [mV]"], marker='o', markersize = 2 , linestyle='', color='#377eb8', label='Canal 1 (u1)')
ax.plot(df["tiempo [ns]"], df["canal 2 [mV]"], marker='o', markersize = 2, linestyle='', color='#e41a1c', label='Canal 2 (u2)')
ax.plot(df["tiempo [ns]"], df["canal 3 [mV]"], marker='o', markersize = 2, linestyle='', color='#4daf4a', label='Canal 3 (u3)')

ax.set_xlabel('Tiempo [ns]')
ax.set_ylabel('Voltaje [mV]')

ax.legend(loc='lower right')

fig.show()

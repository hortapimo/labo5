import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('estiloGraficos.mplstyle')
fps = 15                                  # cuadros por segundo del video
um_por_px = 0.09524703938865117           # micras por píxel (usá 1 para quedarte en píxeles)
error_um_por_px = 0.005           
n_max = 69                   # último paso (frame) hasta donde se grafica y se ajusta
t_min = 3                        # FILTRO  IMPORTANTE: duración mínima (s) de una trayectoria para usarla
solo_completas = False                    # True: usa solo las que llegan hasta n_max (ensamble fijo)
unidad = "um"                             # "um" -> µm² ; "nm" -> nm² ; "px" -> px² (con um_por_px = 1)
ajustar_cada_particula = True             # además del promedio, ajusta cada trayectoria
loglog = False                            # True: ejes logarítmicos

factor = {"um": 1.0, "nm": 1e3, "px": 1.0}[unidad]


def msd_trayectoria(archivo):
    df = pd.read_csv(archivo)             # si no tiene encabezado: header=None
    df = df.iloc[:, :3].dropna()
    frame = df.iloc[:, 0].to_numpy()
    x = df.iloc[:, 1].to_numpy() * um_por_px * factor
    y = df.iloc[:, 2].to_numpy() * um_por_px * factor
    t = (frame - frame[0]) / fps

    # Ec. 29: desplazamiento cuadrático respecto de la posición inicial
    r2 = (x - x[0])**2 + (y - y[0])**2

    # Ec. 30: promedio acumulado de r2(t_i), i = 1..N (se descarta t = 0)
    r2 = r2[1:]
    n = np.arange(1, len(r2) + 1)
    msd = np.cumsum(r2) / n
    #msd=r2
    return t[1:], msd

t,trayectoria= msd_trayectoria("trayectoria_particula11_video_sinLserGod1_1.avi.csv")

fig,ax=plt.subplots()
ax.plot(t,trayectoria)
lineas = np.linspace(t[0],t[-1],8)
for pos in lineas:

    ax.axvline(x=pos, color='red', linestyle='--', linewidth=2, label='Línea en x=5')

ax.set_ylabel(f"MSD [$\mu m$]")
ax.set_xlabel("t [s]")
ax.set_title("MSD de una sola partícula")


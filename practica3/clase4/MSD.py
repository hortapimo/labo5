import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#%% Configuración
carpeta = "trayectorias"                  # carpeta con los .csv del ensamble
patron = os.path.join(carpeta, "*.csv")

fps = 15                                  # cuadros por segundo del video
um_por_px = 0.09524703938865117           # micras por píxel (usá 1 para quedarte en píxeles)
n_max = 75                            # último paso (frame) hasta donde se grafica y se ajusta
t_min = 2.5                               # FILTRO  IMPORTANTE: duración mínima (s) de una trayectoria para usarla
solo_completas = False                    # True: usa solo las que llegan hasta n_max (ensamble fijo)
unidad = "um"                             # "um" -> µm² ; "nm" -> nm² ; "px" -> px² (con um_por_px = 1)
ajustar_cada_particula = True             # además del promedio, ajusta cada trayectoria
loglog = False                            # True: ejes logarítmicos

factor = {"um": 1.0, "nm": 1e3, "px": 1.0}[unidad]

#%% MSD de una trayectoria (Ec. 29 y 30)
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
    return t[1:], msd


#%% Modelo y ajuste: MSD = A * t^n + (v t)^2
def modelo(t, A_, n_, v_):
    return A_ * t**n_ + (v_*t)**2

def ajustar(t, msd):
    p0 = [msd[-1] / t[-1], 1.0, 0]           # A ~ pendiente aproximada, n ~ 1 (difusión normal), v_ deriva
    popt, pcov = curve_fit(modelo, t, msd, p0=p0, bounds=([0, 0, -np.inf], [np.inf, 3, np.inf]))
    err = np.sqrt(np.diag(pcov))
    ss_res = np.sum((msd - modelo(t, *popt))**2)
    ss_tot = np.sum((msd - msd.mean())**2)
    return popt, err, 1 - ss_res / ss_tot


#%% Calcular el MSD de todas las partículas
archivos = sorted(glob.glob(patron))
if not archivos:
    raise FileNotFoundError(f"No se encontraron archivos con el patrón: {patron}")
print(f"Archivos encontrados en '{carpeta}': {len(archivos)}")

n_min = int(np.ceil(t_min * fps))         # pasos mínimos que debe tener una trayectoria
if n_max < n_min:
    raise ValueError(f"n_max ({n_max}) debe ser >= {n_min} pasos ({t_min} s a {fps} fps)")

# Filtrar: se descartan las trayectorias que se pierden antes de t_min
msds, usados = [], []
for archivo in archivos:
    _, msd_k = msd_trayectoria(archivo)
    if len(msd_k) < n_min:
        print(f"Descartada (dura {len(msd_k) / fps:.2f} s < {t_min} s): {os.path.basename(archivo)}")
    elif solo_completas and len(msd_k) < n_max:
        print(f"Descartada (no llega a n_max = {n_max}): {os.path.basename(archivo)}")
    else:
        msds.append(msd_k)
        usados.append(archivo)

if not usados:
    raise ValueError("Ninguna trayectoria cumple el criterio de duración.")
archivos = usados
print(f"Partículas utilizadas: {len(archivos)}")

# matriz (partículas x pasos), con NaN donde la trayectoria ya se perdió
MSD = np.full((len(archivos), n_max), np.nan)
for k, msd_k in enumerate(msds):
    m = min(len(msd_k), n_max)
    MSD[k, :m] = msd_k[:m]

pasos = np.arange(1, n_max + 1)
t_n = pasos / fps                         # tiempo de cada paso
msd_prom = np.nanmean(MSD, axis=0)        # promedio del ensamble en cada paso
n_part = np.sum(~np.isnan(MSD), axis=0)   # cuántas partículas aportan en cada paso


#%% Ajuste del MSD promedio
popt, err, r_cuadrado = ajustar(t_n, msd_prom)
A_fit, n_fit, v_fit= popt
err_A, err_n, err_v= err

print("\n--- Ajuste del MSD promedio ---")
print(f"A = {A_fit:.4g} ± {err_A:.2g}")
print(f"n = {n_fit:.4g} ± {err_n:.2g}")
print(f"v = {v_fit:.4g} ± {err_v:.2g}")
print(f"R² = {r_cuadrado:.5f}")

# Ajuste de cada partícula
if ajustar_cada_particula:
    n_ind = []
    print("\n--- Exponente n por partícula ---")
    for k, archivo in enumerate(archivos):
        ok = ~np.isnan(MSD[k])
        try:
            p, e, r2_k = ajustar(t_n[ok], MSD[k][ok])
            n_ind.append(p[1])
            print(f"{os.path.basename(archivo)}: n = {p[1]:.3f} ± {e[1]:.2g}  (R² = {r2_k:.4f})")
        except Exception as exc:
            print(f"{os.path.basename(archivo)}: no se pudo ajustar ({exc})")
    n_ind = np.array(n_ind)
    print(f"\nn medio entre partículas = {n_ind.mean():.3f} ± {n_ind.std(ddof=1):.3f} (desv. estándar)")


#%% Gráfico (las curvas parten desde t = 0)
# Solo para graficar se agrega el punto (t = 0, msd = 0); el ajuste usa los datos originales

plt.style.use('estiloGraficos.mplstyle')

t_plot = np.r_[0, t_n]
MSD_plot = np.hstack([np.zeros((len(archivos), 1)), MSD])
msd_prom_plot = np.r_[0, msd_prom]
t_fit = np.linspace(0, t_n[-1], 300)      # curva de ajuste suave desde t = 0

fig, ax = plt.subplots(figsize=(6, 5))
for k in range(len(archivos)):
    ax.plot(t_plot, MSD_plot[k], color="#4CAF50", linewidth=1, ms=2, alpha=0.85,
            label=f"Partículas (Total = {len(archivos)})" if k == 0 else None)
ax.plot(t_plot, msd_prom_plot, color="red", linewidth=2.5, ms=4, label="Promedio")
ax.plot(t_fit, modelo(t_fit, *popt), "k-", lw=2,
        label=f"Ajuste: $A t^n + (v t)^2 $, A = {A_fit:.4g} ± {err_A:.2g} , \nn = {n_fit:.2f} ± {err_n:.2f} , v = {v_fit:.2f} ± {err_v:.2f}")

ax.set_xlabel("Tiempo ( s )", fontweight="bold")
ax.set_ylabel(r"Mean Squared Displacement ($\mu$m$^2$)", fontweight="bold")
if loglog:
    # en escala log no se puede mostrar t = 0: se grafica desde el primer paso
    ax.set_xscale("log")
    ax.set_yscale("log")
else:
    ax.set_xlim(0, t_n[-1])
    ax.set_ylim(bottom=0)
ax.grid(alpha=0.3)
ax.legend()
plt.legend(fontsize=10, loc="best")
fig.tight_layout()
plt.show()

#%% Guardar resultados
pd.DataFrame({"paso": pasos, "t_s": t_n, "msd_promedio": msd_prom, "n_particulas": n_part}).to_csv(
    "msd_ensamble.csv", index=False, encoding="utf-8")
fig.savefig("msd_ensamble.png", dpi=200)

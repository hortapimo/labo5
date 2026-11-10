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
error_um_por_px = 0.005           
n_max = 75                            # último paso (frame) hasta donde se grafica y se ajusta
t_min = 2.5                               # FILTRO  IMPORTANTE: duración mínima (s) de una trayectoria para usarla
solo_completas = False                    # True: usa solo las que llegan hasta n_max (ensamble fijo)
unidad = "um"                             # "um" -> µm² ; "nm" -> nm² ; "px" -> px² (con um_por_px = 1)
ajustar_cada_particula = True             # además del promedio, ajusta cada trayectoria
loglog = False                            # True: ejes logarítmicos

factor = {"um": 1.0, "nm": 1e3, "px": 1.0}[unidad]
#%%
archivos = sorted(glob.glob(patron))
if not archivos:
    raise FileNotFoundError(f"No se encontraron archivos con el patrón: {patron}")
print(f"Archivos encontrados en '{carpeta}': {len(archivos)}")

n_min = int(np.ceil(t_min * fps))         # pasos mínimos que debe tener una trayectoria
if n_max < n_min:
    raise ValueError(f"n_max ({n_max}) debe ser >= {n_min} pasos ({t_min} s a {fps} fps)")
#%%
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

#%%
def sacar_tray(archivo):
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
    return x,y

def msd(x, y, n_lags):
    """MSD sobre todos los pares. El error usa N/n pares independientes."""
    N = len(x)
    n_lags = min(n_lags, N - 1)
    lags = np.arange(1, n_lags + 1)
    val = np.empty(n_lags)
    err = np.empty(n_lags)
    for i, n in enumerate(lags):
        d2 = (x[n:] - x[:-n])**2 + (y[n:] - y[:-n])**2
        val[i] = d2.mean()
        err[i] = d2.std(ddof=1) / np.sqrt(max(N / n, 1))
    return lags, val, err


def ajustar(tau, msd_val, con_deriva=True):
    """Ajusta 4 sigma^2 + 4 D tau [+ (v tau)^2] por cuadrados mínimos sin pesos.

    Sin pesos: para difusión 2D el desplazamiento al cuadrado es exponencial, su
    desviación estandar iguala a su media y err(n) = MSD(n) sqrt(n/N), de modo
    que 1/err^2 decae como n^-3. Con pesos, el ajuste queda determinado por los
    primeros retardos temporales, donde la curvatura todavia no se distingue.

    Los puntos del MSD comparten desplazamientos y están correlacionados, de modo que las
    incertezas que devuelve son una cota inferior.
    """
    cols = [np.ones_like(tau), tau] + ([tau**2] if con_deriva else [])
    A = np.vstack(cols).T
    if len(tau) < A.shape[1] + 1:
        raise ValueError(f"{len(tau)} retardos para {A.shape[1]} parametros.")
    coef, *_ = np.linalg.lstsq(A, msd_val, rcond=None)
    res = msd_val - A @ coef
    cov = (res @ res / (len(tau) - A.shape[1])) * np.linalg.pinv(A.T @ A)
    sigma = np.sqrt(max(coef[0], 0)) / 2
    D = coef[1] / 4
    dD = np.sqrt(cov[1, 1]) / 4
    v = np.sqrt(max(coef[2], 0)) if con_deriva else 0.0
    dv = np.sqrt(cov[2, 2]) / (2*v) if con_deriva and v > 0 else np.nan
    return sigma, D, dD, v, dv, coef, cov

def modelo(t, A_, n_, v_):
    return A_ * (t**n_) + (v_*t)**2

def ajustar_2(t, msd, sigma):
    """Ajuste A*t^n + (v t)^2 pesado por las barras de error (se ignoran puntos sin error)."""
    v = np.isfinite(sigma) & (sigma > 0)
    p0 = [msd[-1] / t[-1], 1.0, 0]
    popt, pcov = curve_fit(modelo, t[v], msd[v], p0=p0, sigma=sigma[v], absolute_sigma=True,
                           bounds=([0, 0, -np.inf], [np.inf, 3, np.inf]), maxfev=1e5)
    err = np.sqrt(np.diag(pcov))
    res = msd[v] - modelo(t[v], *popt)
    chi2_red = np.sum((res / sigma[v])**2) / (v.sum() - len(popt))
    #r2 = 1 - np.sum(res**2) / np.sum((msd[v] - msd[v].mean())**2)
    return popt, err, chi2_red

FRACCION_MSD = 0.25
DT = 1 / fps
x_um, y_um = sacar_tray("trayectoria_particula3_video_sinLserGod1_1.avi.csv")
lags, msd_val, msd_err = msd(x_um, y_um, int(FRACCION_MSD*len(x_um)))
tau = lags*DT
sg, D1, dD1, v1, dv1, _, _ = ajustar(tau, msd_val)
popt, errores_p, _ = ajustar_2(tau, msd_val, msd_err)
A, n, vel = popt
A_e, n_e, vel_e = errores_p
#print(f"sigma {sg/um_por_px:.2f} px")
#print(f"D     {D1:.4f} +- {dD1:.4f} um^2/s  ->  eta {eta_de_D(D1):.2f} mPa s")
#print(f"v     {v1:.4f} +- {dv1:.4f} um/s")
print(f"n = ({n:.4f} +- {n_e:.4f}) ")
print(f"velocidad = ({vel:.4f} +- {vel_e:.4f}) um/s")
print(f"A = ({A:.4f} +- {A_e:.4f}) no se")
#%%
fig, ax = plt.subplots(figsize=(7, 5))
ax.errorbar(tau, msd_val, yerr=msd_err, fmt='o', ms=4, color='0.2',
            ecolor='0.75', capsize=0, label='MSD')
tt = np.linspace(0, tau[-1], 300)
ax.plot(tt, 4*sg**2 + 4*D1*tt + (v1*tt)**2, 'r-', lw=1.8,
        label=( f"$D$ =({D1:.4f} $\\pm$ {dD1:.4f}) $\\mu$m$^2$/s"))
ax.set_xlabel(r'$\tau$ [s]')
ax.set_ylabel(r'MSD [$\mu$m$^2$]')
ax.legend()
plt.tight_layout()
#guardar('msd_particula')
plt.show()
#%%
fig, ax = plt.subplots(figsize=(7, 5))
ax.errorbar(tau, msd_val, yerr=msd_err, fmt='o', ms=4, color='0.2',
            ecolor='0.75', capsize=0, label='MSD')
tt = np.linspace(0, tau[-1], 300)
y_fit = modelo(tt,A,n,vel)
ax.plot(tt, y_fit, 'r-', lw=1.8,
        label=( f"$D$ =({D1:.4f} $\\pm$ {dD1:.4f}) $\\mu$m$^2$/s"))
ax.set_xlabel(r'$\tau$ [s]')
ax.set_ylabel(r'MSD [$\mu$m$^2$]')
ax.legend()
plt.tight_layout()
plt.savefig("nuevo_trayectoria_part_3.png")
#guardar('msd_particula')
plt.show()


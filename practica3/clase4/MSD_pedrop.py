import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#%% Configuración
carpeta = "trayectoriasDivididas/sub_trayectorias_7s"                  # carpeta con los .csv del ensamble
patron = os.path.join(carpeta, "*.csv")

fps = 15                                  # cuadros por segundo del video
um_por_px = 0.09524703938865117           # micras por píxel (usá 1 para quedarte en píxeles)
error_um_por_px = 0.005           
n_max = 100                       # último paso (frame) hasta donde se grafica y se ajusta
t_min = 4                        # FILTRO  IMPORTANTE: duración mínima (s) de una trayectoria para usarla
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
    #msd=r2
    return t[1:], msd

#%% Modelo y ajuste: MSD = A * t^n + (v t)^2
usar_offset = True    # True: MSD = A*t^n + (v t)^2 + C  (C >= 0: offset, p.ej. error de localización) ; False: sin offset (C = 0)

def modelo(t, A_, n_, v_, C_=0.0):
    return A_ * t**n_ + (v_*t)**2 + C_

def ajustar(t, msd):
    p0 = [msd[-1] / t[-1], 1.0, 0]           # A ~ pendiente aproximada, n ~ 1 (difusión normal), v_ deriva
    lb, ub = [0, 0, -np.inf], [np.inf, 3, np.inf]
    if usar_offset:                           # se agrega C con C >= 0
        p0, lb, ub = p0 + [0.0], lb + [0], ub + [np.inf]
    popt, pcov = curve_fit(modelo, t, msd, p0=p0, bounds=(lb, ub))
    err = np.sqrt(np.diag(pcov))
    ss_res = np.sum((msd - modelo(t, *popt))**2)
    ss_tot = np.sum((msd - msd.mean())**2)
    if not usar_offset:                       # se devuelve siempre C (= 0 si no se ajusta)
        popt, err = np.r_[popt, 0.0], np.r_[err, 0.0]
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
msd_min = 0.02 #Si en el tiempo final ni si quiera supero este valor se siospecha de que no es una particual sino mugre
for archivo in archivos:
    _, msd_k = msd_trayectoria(archivo)
    if len(msd_k) < n_min:
        print(f"Descartada (dura {len(msd_k) / fps:.2f} s < {t_min} s): {os.path.basename(archivo)}")
    elif solo_completas and len(msd_k) < n_max:
        print(f"Descartada (no llega a n_max = {n_max}): {os.path.basename(archivo)}")
    elif msd_k[-1] < msd_min:#Agrego este filtro para particulas que no se mueven, sospecha de estar midiendo mugre
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
A_fit, n_fit, v_fit, C_fit = popt
err_A, err_n, err_v, err_C = err

print("\n--- Ajuste del MSD promedio ---")
print(f"A = {A_fit:.4g} ± {err_A:.2g}")
print(f"n = {n_fit:.4g} ± {err_n:.2g}")
print(f"v = {v_fit:.4g} ± {err_v:.2g}")
print(f"C = {C_fit:.4g} ± {err_C:.2g}")
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
        label=f"Ajuste: $A t^n + (v t)^2 + C $, A = {A_fit:.2f} ± {err_A:.2f} , \nn = {n_fit:.2f} ± {err_n:.2f} , v = {v_fit:.2f} ± {err_v:.2f} , C = {C_fit:.2f} ± {err_C:.2f}")

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
    "msd_ensamble_ergo.csv", index=False, encoding="utf-8")
fig.savefig("msd_ensamble_ergo.png", dpi=200)


#%% Partícula individual: datos de MSD y ajuste con deriva
# Elegí la partícula por su número en la lista (0, 1, 2, ...) o por un texto del nombre
# del archivo (por ejemplo "particula17"). Solo se pueden elegir las que pasaron el filtro.
"""
particula = 2
 
print("\n--- Partículas disponibles ---")
for k, archivo in enumerate(archivos):
    print(f"[{k}] {os.path.basename(archivo)}")
 
if isinstance(particula, str):
    coincidencias = [k for k, archivo in enumerate(archivos) if particula in os.path.basename(archivo)]
    if not coincidencias:
        raise ValueError(f"Ningún archivo utilizado contiene '{particula}' en su nombre.")
    k_sel = coincidencias[0]
else:
    if not 0 <= particula < len(archivos):
        raise ValueError(f"particula debe estar entre 0 y {len(archivos) - 1}.")
    k_sel = particula
 
ok = ~np.isnan(MSD[k_sel])
t_p = t_n[ok]
msd_p = MSD[k_sel][ok]
 
popt_p, err_p, r_cuadrado_p = ajustar(t_p, msd_p)
A_p, n_p, v_p = popt_p
err_A_p, err_n_p, err_v_p = err_p
 
print(f"\n--- Ajuste de la partícula [{k_sel}] {os.path.basename(archivos[k_sel])} ---")
print(f"A = {A_p:.4g} ± {err_A_p:.2g}")
print(f"n = {n_p:.4g} ± {err_n_p:.2g}")
print(f"v = {v_p:.4g} ± {err_v_p:.2g}")
print(f"R² = {r_cuadrado_p:.5f}")
 
t_fit_p = np.linspace(0, t_p[-1], 300)
 
fig_p, ax_p = plt.subplots(figsize=(6, 5))
ax_p.plot(t_p, msd_p, "o", color="#4CAF50", ms=4, label=f"Datos (partícula {k_sel})")
ax_p.plot(t_fit_p, modelo(t_fit_p, *popt_p), "k-", lw=2,
          label=f"Ajuste: $A t^n + (v t)^2 $, A = {A_p:.4g} ± {err_A_p:.2g} , \nn = {n_p:.2f} ± {err_n_p:.2f} , v = {v_p:.2f} ± {err_v_p:.2f} \nR² = {r_cuadrado_p:.5f}")
 
ax_p.set_xlabel("Tiempo ( s )", fontweight="bold")
ax_p.set_ylabel(r"Mean Squared Displacement ($\mu$m$^2$)", fontweight="bold")
if loglog:
    ax_p.set_xscale("log")
    ax_p.set_yscale("log")
else:
    ax_p.set_xlim(0, t_p[-1])
    ax_p.set_ylim(bottom=0)
ax_p.grid(alpha=0.3)
ax_p.legend(fontsize=10, loc="best")
fig_p.tight_layout()
plt.show()
"""

#%% Partícula individual: datos de MSD y ajuste con deriva
# Elegí la partícula por su número en la lista (0, 1, 2, ...) o por un texto del nombre
# del archivo (por ejemplo "particula17"). Solo se pueden elegir las que pasaron el filtro.
particula = 0
 
print("\n--- Partículas disponibles ---")
for k, archivo in enumerate(archivos):
    print(f"[{k}] {os.path.basename(archivo)}")
 
if isinstance(particula, str):
    coincidencias = [k for k, archivo in enumerate(archivos) if particula in os.path.basename(archivo)]
    if not coincidencias:
        raise ValueError(f"Ningún archivo utilizado contiene '{particula}' en su nombre.")
    k_sel = coincidencias[0]
else:
    if not 0 <= particula < len(archivos):
        raise ValueError(f"particula debe estar entre 0 y {len(archivos) - 1}.")
    k_sel = particula
 
ponderar = True    # True: el ajuste pesa cada punto con su barra de error (1/sigma²)
 
 
def msd_con_error(archivo):
    """Igual que msd_trayectoria, pero devuelve además el error estándar de cada punto.
 
    El MSD en el paso n es el promedio de r2(t_1..t_n); su error es el error estándar
    de la media: std(r2[:n], ddof=1) / sqrt(n). Para n = 1 no está definido (NaN).
    """
    df = pd.read_csv(archivo)             # si no tiene encabezado: header=None
    df = df.iloc[:, :3].dropna()
    x = df.iloc[:, 1].to_numpy() * um_por_px * factor
    y = df.iloc[:, 2].to_numpy() * um_por_px * factor
    r2 = ((x - x[0])**2 + (y - y[0])**2)[1:]
    n = np.arange(1, len(r2) + 1)
    msd = np.cumsum(r2) / n
    sem = pd.Series(r2).expanding().std(ddof=1).to_numpy() / np.sqrt(n)
    return msd, sem
 
 
def ajustar_pesado(t, msd, sigma):
    """Ajuste A*t^n + (v t)^2 pesado por las barras de error (se ignoran puntos sin error)."""
    v = np.isfinite(sigma) & (sigma > 0)
    p0 = [msd[-1] / t[-1], 1.0, 0]
    lb, ub = [0, 0, -np.inf], [np.inf, 3, np.inf]
    if usar_offset:                           # se agrega C con C >= 0
        p0, lb, ub = p0 + [0.0], lb + [0], ub + [np.inf]
    popt, pcov = curve_fit(modelo, t[v], msd[v], p0=p0, sigma=sigma[v], absolute_sigma=True,
                           bounds=(lb, ub))
    err = np.sqrt(np.diag(pcov))
    res = msd[v] - modelo(t[v], *popt)
    chi2_red = np.sum((res / sigma[v])**2) / (v.sum() - len(popt))
    r2 = 1 - np.sum(res**2) / np.sum((msd[v] - msd[v].mean())**2)
    if not usar_offset:                       # se devuelve siempre C (= 0 si no se ajusta)
        popt, err = np.r_[popt, 0.0], np.r_[err, 0.0]
    return popt, err, r2, chi2_red
 
 
ok = ~np.isnan(MSD[k_sel])
t_p = t_n[ok]
msd_p = MSD[k_sel][ok]
_, sem_c = msd_con_error(archivos[k_sel])
sem_p = sem_c[:ok.sum()]                  # mismo recorte que los datos (hasta n_max)
 
if ponderar:
    popt_p, err_p, r_cuadrado_p, chi2_p = ajustar_pesado(t_p, msd_p, sem_p)
else:
    popt_p, err_p, r_cuadrado_p = ajustar(t_p, msd_p)
    chi2_p = np.nan
A_p, n_p, v_p, C_p = popt_p
err_A_p, err_n_p, err_v_p, err_C_p = err_p
 
print(f"\n--- Ajuste de la partícula [{k_sel}] {os.path.basename(archivos[k_sel])} ---")
print(f"A = {A_p:.2f} ± {err_A_p:.2f}")
print(f"n = {n_p:.2f} ± {err_n_p:.2f}")
print(f"v = {v_p:.2f} ± {err_v_p:.2f}")
print(f"C = {C_p:.2f} ± {err_C_p:.2f}")
print(f"R² = {r_cuadrado_p:.2f}")
if ponderar:
    print(f"χ² reducido = {chi2_p:.3g}")
 
t_fit_p = np.linspace(0, t_p[-1], 300)
 
fig_p, ax_p = plt.subplots(figsize=(6, 5))
ax_p.errorbar(t_p, msd_p, yerr=np.nan_to_num(sem_p), fmt="o", color="#4CAF50", ms=4,
              capsize=2, elinewidth=1, label=f"Datos (partícula {k_sel})")
ax_p.plot(t_fit_p, modelo(t_fit_p, *popt_p), "k-", lw=2,
          label=f"Ajuste: $A t^n + (v t)^2 + C $, A = {A_p:.2f} ± {err_A_p:.2f} , \nn = {n_p:.2f} ± {err_n_p:.2f} , v = {v_p:.2f} ± {err_v_p:.2f} , C = {C_p:.2f} ± {err_C_p:.2f} \nR² = {r_cuadrado_p:.2f} , χ² reducido = {chi2_p:.2f}")
 
ax_p.set_xlabel("Tiempo ( s )", fontweight="bold")
ax_p.set_ylabel(r"Mean Squared Displacement ($\mu$m$^2$)", fontweight="bold")
if loglog:
    ax_p.set_xscale("log")
    ax_p.set_yscale("log")
else:
    ax_p.set_xlim(0, t_p[-1])
    ax_p.set_ylim(bottom=0)
ax_p.grid(alpha=0.3)
ax_p.legend(fontsize=10, loc="best")
fig_p.tight_layout()

# --- GUARDAR EN LA CARPETA ---

nombre_imagen = f"msd_particula_{k_sel}_ergo.png"
ruta_guardado = os.path.join(carpeta, nombre_imagen)
fig_p.savefig(ruta_guardado, dpi=300, bbox_inches="tight")
print(f"Figura guardada en: {ruta_guardado}")

plt.show()

#%%
plt.savefig(f"msd_particula_{particula}_ergo.png")



#%% MSD promedio con barras de error (error estándar entre partículas) y ajuste pesado
# Error de cada punto del promedio: s(t) / sqrt(N(t)), con s(t) la desviación estándar
# muestral del MSD entre las partículas que siguen vivas en ese paso y N(t) = n_part.
# Usa la función ajustar_pesado() definida en la celda de partícula individual (más arriba).
import warnings

mostrar_particulas = True      # dibuja las curvas individuales de fondo (tenues)
cada = 3                       # una barra de error cada 'cada' puntos (1 = todas)
guardar_figura = True

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)   # pasos con menos de 2 partículas
    s_t = np.nanstd(MSD, axis=0, ddof=1)
sem_prom = s_t / np.sqrt(n_part)                                # error estándar de la media

popt_e, err_e, r_cuadrado_e, chi2_e = ajustar_pesado(t_n, msd_prom, sem_prom)
A_e, n_e, v_e, C_e = popt_e
err_A_e, err_n_e, err_v_e, err_C_e = err_e

print("\n--- Ajuste pesado del MSD promedio (barras = error estándar entre partículas) ---")
print(f"A = {A_e:.4g} ± {err_A_e:.2g}")
print(f"n = {n_e:.4g} ± {err_n_e:.2g}")
print(f"v = {v_e:.4g} ± {err_v_e:.2g}")
print(f"C = {C_e:.4g} ± {err_C_e:.2g}")
print(f"R² = {r_cuadrado_e:.5f}")
print(f"χ² reducido = {chi2_e:.3g}")

# Para graficar: se agrega el punto (t = 0, msd = 0, error = 0)
t_plot_e = np.r_[0, t_n]
msd_prom_e = np.r_[0, msd_prom]
sem_plot_e = np.r_[0, np.nan_to_num(sem_prom)]
t_fit_e = np.linspace(0, t_n[-1], 300)

fig_e, ax_e = plt.subplots(figsize=(6, 5))
if mostrar_particulas:
    for k in range(len(archivos)):
        ax_e.plot(t_plot, MSD_plot[k], color="#4CAF50", linewidth=1, ms=2, alpha=0.85,
                  label=f"Partículas (Total = {len(archivos)})" if k == 0 else None)
ax_e.errorbar(t_plot_e, msd_prom_e, yerr=sem_plot_e, fmt="o", color="red", ms=4,
              capsize=2, elinewidth=1, errorevery=cada, label="Promedio ± error estándar")
ax_e.plot(t_fit_e, modelo(t_fit_e, *popt_e), "k-", lw=2,
          label=f"Ajuste: $A t^n + (v t)^2 + C $, A = {A_e:.2f} ± {err_A_e:.2f} , \nn = {n_e:.2f} ± {err_n_e:.2f} , v = {v_e:.2f} ± {err_v_e:.2f} , C = {C_e:.2f} ± {err_C_e:.2f} \nχ² reducido = {chi2_e:.2f}")

ax_e.set_xlabel("Tiempo ( s )", fontweight="bold")
ax_e.set_ylabel(r"Mean Squared Displacement ($\mu$m$^2$)", fontweight="bold")
if loglog:
    ax_e.set_xscale("log")
    ax_e.set_yscale("log")
else:
    ax_e.set_xlim(0, t_n[-1])
    ax_e.set_ylim(bottom=0)
ax_e.grid(alpha=0.3)
ax_e.legend(fontsize=10, loc="best")
fig_e.tight_layout()

if guardar_figura:
    fig_e.savefig("msd_ensamble_error_ergo.png", dpi=300, bbox_inches="tight")
    print("Figura guardada en: msd_ensamble_error_ergo.png")

plt.show()


#%% Bootstrap sobre partículas: incertidumbre de A, n y v
# Se remuestrean las partículas (con reemplazo), se recalcula el MSD promedio y se reajusta
# A*t^n + (v t)^2 con la misma función ajustar() de arriba. La dispersión de los parámetros
# entre remuestreos es su incertidumbre, e incluye la variabilidad entre partículas.
import warnings

n_boot = 1000                  # cantidad de remuestreos
semilla = 0                    # para que el resultado sea reproducible
guardar_figuras = True

rng = np.random.default_rng(semilla)
N_part = MSD.shape[0]

params_boot = []
for b in range(n_boot):
    idx = rng.integers(0, N_part, N_part)                      # sorteo de partículas con reemplazo
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)   # pasos sin ninguna partícula viva
        msd_b = np.nanmean(MSD[idx], axis=0)
    val = np.isfinite(msd_b)
    try:
        p_b, _, _ = ajustar(t_n[val], msd_b[val])
        params_boot.append(p_b)
    except Exception:
        pass                                                   # remuestreo cuyo ajuste no converge
params_boot = np.array(params_boot)
params_boot[:, 2] = np.abs(params_boot[:, 2])                  # v entra al cuadrado: solo |v| tiene sentido

nombres = ["A", "n", "v"] + (["C"] if usar_offset else [])
valores = [A_fit, n_fit, abs(v_fit)] + ([C_fit] if usar_offset else [])   # estimación con el ensamble completo
print(f"\n--- Bootstrap ({len(params_boot)} de {n_boot} remuestreos con ajuste válido) ---")
stats_boot = []
for i, nombre in enumerate(nombres):
    p2, p16, p50, p84, p97 = np.percentile(params_boot[:, i], [2.5, 16, 50, 84, 97.5])
    std = params_boot[:, i].std(ddof=1)
    stats_boot.append((p2, p97, std))
    print(f"{nombre} = {valores[i]:.4g} ± {std:.2g}  (desv. estándar bootstrap)"
          f" | mediana {p50:.4g} | 68%: [{p16:.4g}, {p84:.4g}] | 95%: [{p2:.4g}, {p97:.4g}]")

# Banda de incertidumbre de la curva ajustada (percentiles 2.5-97.5 de las curvas bootstrap)
t_fit_b = np.linspace(0, t_n[-1], 200)
curvas_b = np.array([modelo(t_fit_b, *p) for p in params_boot])
banda_lo, banda_hi = np.percentile(curvas_b, [2.5, 97.5], axis=0)

txt_C = f" , C = {C_fit:.2f} ± {stats_boot[3][2]:.2f}" if usar_offset else ""

# Gráfico del ensamble con el ajuste y su banda bootstrap
fig_b, ax_b = plt.subplots(figsize=(6, 5))
for k in range(len(archivos)):
    ax_b.plot(t_plot, MSD_plot[k], color="#4CAF50", linewidth=1, ms=2, alpha=0.85,
              label=f"Partículas (Total = {len(archivos)})" if k == 0 else None)
ax_b.plot(t_plot, msd_prom_plot, color="red", linewidth=2.5, label="Promedio")
ax_b.fill_between(t_fit_b, banda_lo, banda_hi, color="gray", alpha=0.35, label="Banda bootstrap (95%)")
ax_b.plot(t_fit_b, modelo(t_fit_b, *popt), "k-", lw=2,
          label=(f"Ajuste: $A t^n + (v t)^2 + C $, A = {A_fit:.2f} ± {stats_boot[0][2]:.2f} , \n"
                 f"n = {n_fit:.2f} ± {stats_boot[1][2]:.2f} , v = {abs(v_fit):.2f} ± {stats_boot[2][2]:.2f}" + txt_C))

ax_b.set_xlabel("Tiempo ( s )", fontweight="bold")
ax_b.set_ylabel(r"Mean Squared Displacement ($\mu$m$^2$)", fontweight="bold")
if loglog:
    ax_b.set_xscale("log")
    ax_b.set_yscale("log")
else:
    ax_b.set_xlim(0, t_n[-1])
    ax_b.set_ylim(bottom=0)
ax_b.grid(alpha=0.3)
ax_b.legend(fontsize=10, loc="best")
fig_b.tight_layout()
fig_b.savefig("msd_ensamble_bootstrap_ergo")
fig_b.show()
"""
# Histogramas de los parámetros bootstrap
fig_h, axs_h = plt.subplots(1, len(nombres), figsize=(4 * len(nombres), 4))
for i, (nombre, ax_h) in enumerate(zip(nombres, axs_h)):
    ax_h.hist(params_boot[:, i], bins=30, color="#4CAF50", alpha=0.8)
    ax_h.axvline(valores[i], color="k", lw=2, label="Ajuste ensamble")
    ax_h.axvline(stats_boot[i][0], color="k", ls="--", lw=1.2, label="IC 95%")
    ax_h.axvline(stats_boot[i][1], color="k", ls="--", lw=1.2)
    ax_h.set_xlabel(nombre if nombre != "v" else "|v|", fontweight="bold")
    ax_h.set_ylabel("Frecuencia", fontweight="bold")
    ax_h.grid(alpha=0.3)
axs_h[0].legend(fontsize=9)
fig_h.tight_layout()

if guardar_figuras:
    fig_b.savefig("msd_ensamble_bootstrap.png", dpi=300, bbox_inches="tight")
    fig_h.savefig("bootstrap_parametros.png", dpi=300, bbox_inches="tight")
    print("Figuras guardadas: msd_ensamble_bootstrap.png, bootstrap_parametros.png")

plt.show()

"""
# Histogramas de los parámetros bootstrap en grilla 2x2
fig_h, axs_h = plt.subplots(2, 2, figsize=(8, 7))
axs_h = axs_h.flatten()  # Agana la matriz 2x2 para iterar con un solo índice

for i, (nombre, ax_h) in enumerate(zip(nombres, axs_h)):
    ax_h.hist(params_boot[:, i], bins=30, color="#4CAF50", alpha=0.8)
    ax_h.axvline(valores[i], color="k", lw=2, label="Ajuste ensamble")
    ax_h.axvline(stats_boot[i][0], color="k", ls="--", lw=1.2, label="IC 95%")
    ax_h.axvline(stats_boot[i][1], color="k", ls="--", lw=1.2)
    ax_h.set_xlabel(nombre if nombre != "v" else "|v|", fontweight="bold")
    ax_h.set_ylabel("Frecuencia", fontweight="bold")
    ax_h.grid(alpha=0.3)
    if i == 0:
        ax_h.legend(fontsize=9)

# Si por alguna razón nombres tuviera menos de 4 elementos, ocultamos los subplots sobrantes
for j in range(len(nombres), len(axs_h)):
    fig_h.delaxes(axs_h[j])

fig_h.tight_layout()
#%% añado figuras para el informe, unificando el formato. hago que el intervalo sea del 68%
plt.style.use('estiloGraficos.mplstyle')
import warnings
n_boot = 1000                  # cantidad de remuestreos
semilla = 0                    # para que el resultado sea reproducible
guardar_figuras = True

rng = np.random.default_rng(semilla)
N_part = MSD.shape[0]

params_boot = []
for b in range(n_boot):
    idx = rng.integers(0, N_part, N_part)                      # sorteo de partículas con reemplazo
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)   # pasos sin ninguna partícula viva
        msd_b = np.nanmean(MSD[idx], axis=0)
    val = np.isfinite(msd_b)
    try:
        p_b, _, _ = ajustar(t_n[val], msd_b[val])
        params_boot.append(p_b)
    except Exception:
        pass                                                   # remuestreo cuyo ajuste no converge
params_boot = np.array(params_boot)
params_boot[:, 2] = np.abs(params_boot[:, 2])                  # v entra al cuadrado: solo |v| tiene sentido

nombres = ["A", "n", "v"] + (["C"] if usar_offset else [])
valores = [A_fit, n_fit, abs(v_fit)] + ([C_fit] if usar_offset else [])   # estimación con el ensamble completo
P_LO, P_HI = 50 - 68.27/2, 50 + 68.27/2     # 15.865 y 84.135

print(f"\n--- Bootstrap ({len(params_boot)} de {n_boot} remuestreos con ajuste válido) ---")
stats_boot = []
for i, nombre in enumerate(nombres):
    p_lo, p50, p_hi = np.percentile(params_boot[:, i], [P_LO, 50, P_HI])
    err_inf = p50 - p_lo
    err_sup = p_hi - p50
    err_sim = (p_hi - p_lo) / 2          # semiancho del intervalo 68 %: equivale a 1σ
    stats_boot.append((p_lo, p_hi, err_sim))
    print(f"{nombre} = {valores[i]:.4g} ± {err_sim:.2g}  (semiancho 68 % c.l.)"
          f" | mediana {p50:.4g} (-{err_inf:.2g}, +{err_sup:.2g})")
#%%
# Banda de incertidumbre de la curva ajustada (68 %, ±1σ)
t_fit_b = np.linspace(0, t_n[-1], 200)
curvas_b = np.array([modelo(t_fit_b, *p) for p in params_boot])
banda_lo, banda_hi = np.percentile(curvas_b, [P_LO, P_HI], axis=0)

#%% Gráfico del ensamble con el ajuste y su banda bootstrap
from scipy import stats

# Incerteza por punto: error estándar del MSD promedio en cada paso temporal
n_vivas  = np.sum(np.isfinite(MSD), axis=0)
msd_prom = np.nanmean(MSD, axis=0)
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)
    sigma = np.nanstd(MSD, axis=0, ddof=1) / np.sqrt(n_vivas)

ok = np.isfinite(msd_prom) & np.isfinite(sigma) & (sigma > 0) & (n_vivas > 1)
t_ok, y_ok, s_ok = t_n[ok], msd_prom[ok], sigma[ok]

y_mod  = modelo(t_ok, *popt)
resid  = y_ok - y_mod                  # residuos absolutos [µm²]
resid_n = resid / s_ok                 # residuos normalizados (en unidades de σ)

n_par  = len(popt)
gl     = len(t_ok) - n_par             # grados de libertad
chi2   = np.sum(resid_n**2)
chi2_r = chi2 / gl
p_val  = stats.chi2.sf(chi2, gl)       # P(χ² ≥ valor observado)

print(f"χ² = {chi2:.2f} | gl = {gl} | χ²_red = {chi2_r:.2f} | p-valor = {p_val:.3g}")

#%%
fig_b, (ax_b, ax_r) = plt.subplots(
    2, 1, figsize=(8, 7), sharex=True,
    gridspec_kw={"height_ratios": [3, 1], "hspace": 0.05})
for k in range(len(archivos)):
    ax_b.plot(t_plot, MSD_plot[k], color="C0", linewidth=1, alpha=0.85,
              label="7 trayectorias" if k == 0 else None, zorder=1)
ax_b.errorbar(t_plot, msd_prom_plot, fmt=".",color="C1", linewidth=2.5, label="Trayectoria promedio", zorder=2)
ax_b.fill_between(t_fit_b, banda_lo, banda_hi, color="gray", alpha=0.35, label="Incerteza (i.c. 68 %)")
ax_b.plot(t_fit_b, modelo(t_fit_b, *popt), "k-", lw=2,
          label=r"$\chi^2_{\nu}$ = "f"{chi2_r:.1f} | P = {p_val:.1f}", zorder=3)
         # (f"Ajuste: $A t^n + (v t)^2 + C $, A = {A_fit:.2f} ± {stats_boot[0][2]:.2f} , \n"
         #        f"n = {n_fit:.2f} ± {stats_boot[1][2]:.2f} , v = {abs(v_fit):.2f} ± {stats_boot[2][2]:.2f}" + txt_C))
ax_b.plot([],[]," ", label=r"$n_2$ "f"= {n_fit:.1f} ± {stats_boot[1][2]:.1f}")
ax_b.set_ylabel(r"$MSD$ [$\mu$m$^2$]")
if loglog:
    ax_b.set_xscale("log")
    ax_b.set_yscale("log")
else:
    ax_b.set_xlim(0,6)
    ax_b.set_ylim(0,6)
ax_b.grid(alpha=0.3)
ax_b.legend()
ax_r.axhline(0, color="k", lw=1)
ax_r.fill_between(t_fit_b,
                  banda_lo - modelo(t_fit_b, *popt),
                  banda_hi - modelo(t_fit_b, *popt),
                  color="gray", alpha=0.35, label="IC 68 %")    # banda bootstrap respecto del ajuste
ax_r.errorbar(t_ok, resid, fmt="o", ms=3, color="C1",
              ecolor="C3", elinewidth=1, capsize=2)
ax_r.set_xlabel("t [s]")
ax_r.set_ylabel(r"Residuos [$\mu$m$^2$]")
ax_r.grid(alpha=0.3)
ax_b.legend(loc="best")

fig_b.tight_layout()
fig_b.savefig("msd_ensamble_bootstrap_ergo_presentacion.png")
fig_b.show()
#%%
curva_ens = modelo(t_fit_b, *[0.15,1.5,0.00,0.1])
fig_b, ax_b = plt.subplots()
for k in range(len(archivos)):
    ax_b.plot(t_plot, MSD_plot[k], color="C0", linewidth=1, alpha=0.85,
              label="7 trayectorias" if k == 0 else None, zorder=1)
ax_b.errorbar(t_plot, msd_prom_plot, fmt=".",color="C1", linewidth=2.5, label="Trayectoria promedio", zorder=2)
ax_b.fill_between(t_fit_b, banda_lo, banda_hi, color="gray", alpha=0.35, label="Incerteza (i.c. 68 %)")
ax_b.plot(t_fit_b, modelo(t_fit_b, *popt), "k-", lw=3, zorder=3, label="Ajuste de la partícula")#,
          #label=r"$\chi^2_{\nu}$ = "f"{chi2_r:.1f} | P = {p_val:.1f}", zorder=3)
         # (f"Ajuste: $A t^n + (v t)^2 + C $, A = {A_fit:.2f} ± {stats_boot[0][2]:.2f} , \n"
         #        f"n = {n_fit:.2f} ± {stats_boot[1][2]:.2f} , v = {abs(v_fit):.2f} ± {stats_boot[2][2]:.2f}" + txt_C))
ax_b.plot(t_fit_b, curva_ens, c="C4", lw=3,
          label="Ajuste obtenido del ensamble", zorder=3)
#ax_b.plot([],[]," ", label=r"$n_2$ "f"= {n_fit:.1f} ± {stats_boot[1][2]:.1f}")
ax_b.set_xlabel("t [s]")
ax_b.set_ylabel(r"$MSD$ [$\mu$m$^2$]")
if loglog:
    ax_b.set_xscale("log")
    ax_b.set_yscale("log")
else:
    ax_b.set_xlim(0,6)
    ax_b.set_ylim(0,6)
ax_b.grid(alpha=0.3)
ax_b.legend()
fig_b.tight_layout()
fig_b.savefig("msd_ensamble_bootstrap_ergo_presentacion_def.png")
fig_b.show()
print(f"Ajuste: $A t^n + (v t)^2 + C $, A = {A_fit:.2f} ± {stats_boot[0][2]:.2f} , \n"
      f"n = {n_fit:.2f} ± {stats_boot[1][2]:.2f} , v = {abs(v_fit):.2f} ± {stats_boot[2][2]:.2f}" + txt_C)
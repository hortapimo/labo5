import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats

# %%

archivo = "trayectoria_particula17_video_sinLserGod1_1.avi.csv"

# %%
fps = 15           # cuadros por segundo del video (ajustalo)
um_por_px = 0.09524703938865117    # micras por píxel (ajustalo; usá 1 si querés quedarte en píxeles)

df = pd.read_csv(archivo)          # si el archivo no tiene encabezado: header=None
frame = df.iloc[:, 0].to_numpy()
x = df.iloc[:, 1].to_numpy() * um_por_px
y = df.iloc[:, 2].to_numpy() * um_por_px
t = (frame - frame[0]) / fps

# Ec. 29: desplazamiento cuadrático respecto de la posición inicial
r2 = (x - x[0])**2 + (y - y[0])**2

# Ec. 30: promedio acumulado de r2(t_i), para i = 1..n
r2 = r2[1:]                        # i = 1..N (se descarta t = 0)
n = np.arange(1, len(r2) + 1)
msd = np.cumsum(r2) / n
t_n = t[1:]
#%%

d = 2

def modelo(t, A_, n_):
    return A_ * t**n_

# Valores iniciales: A ~ pendiente aproximada, n ~ 1 (difusión normal)
p0 = [msd[-1] / t_n[-1], 1.0]

popt, pcov = curve_fit(modelo, t_n, msd, p0=p0, bounds=([0, 0], [np.inf, 3]))
A_fit, n_fit = popt
err_A, err_n = np.sqrt(np.diag(pcov))

# R² del ajuste
ss_res = np.sum((msd - modelo(t_n, *popt))**2)
ss_tot = np.sum((msd - msd.mean())**2)
r_cuadrado = 1 - ss_res / ss_tot

print(f"A = {A_fit:.4g} ± {err_A:.2g}")
print(f"n = {n_fit:.4g} ± {err_n:.2g}")
print(f"R² = {r_cuadrado:.5f}")

# Gráfico
t_fit = np.linspace(t_n.min(), t_n.max(), 300)
plt.figure(figsize=(7, 5))
plt.plot(t_n, msd, "o", mfc="none", color="red", ms=4, label="Datos")
plt.plot(t_fit, modelo(t_fit, *popt), "-", color="blue", lw=2.5,
         label=f"Ajuste: A·t$^n$, n = {n_fit:.2f}")
plt.xlabel("Time (s)", fontweight="bold")
plt.ylabel(r"Mean Squared Displacement ($\mu$m$^2$)", fontweight="bold")
plt.title("Brownian Motion", fontweight="bold")
plt.xlim(0, t_n.max())
plt.ylim(bottom=0)
plt.grid(True)
plt.legend()
plt.show()

#%%
#%%
d = 2  # dimensiones

def modelo_libre(t, D):
    return 2*d*D*t

def modelo(t, D, v):
    return 2*d*D*t + (v*t)**2

# t_n y msd vienen del bloque anterior
N = len(t_n)

# Ajuste libre (1 parámetro) usando msd
popt_l, pcov_l = curve_fit(modelo_libre, t_n, msd, p0=[msd[-1]/(2*d*t_n[-1])], bounds=(0, np.inf))
rss_l = np.sum((msd - modelo_libre(t_n, *popt_l))**2)

# Ajuste con deriva (2 parámetros), v >= 0 usando msd
popt_d, pcov_d = curve_fit(modelo, t_n, msd, p0=[popt_l[0], 0.01], bounds=([0, 0], [np.inf, np.inf]))
rss_d = np.sum((msd - modelo(t_n, *popt_d))**2)
D_fit, v_fit = popt_d

# Comparación de modelos
aic_l = N*np.log(rss_l/N) + 2*1
aic_d = N*np.log(rss_d/N) + 2*2
F = ((rss_l - rss_d)/1) / (rss_d/(N - 2))
p_valor = stats.f.sf(F, 1, N - 2)

print(f"Libre:  D = {popt_l[0]:.4g}  | RSS = {rss_l:.4g} | AIC = {aic_l:.2f}")
print(f"Deriva: D = {D_fit:.4g}, v = {v_fit:.4g}  | RSS = {rss_d:.4g} | AIC = {aic_d:.2f}")
print(f"F = {F:.3f}, p = {p_valor:.4g}")
if p_valor < 0.05 and aic_d < aic_l:
    print("→ Hay evidencia de deriva.")
else:
    print("→ No hay evidencia clara de deriva (movimiento libre es suficiente).")

# Gráfico del MSD
t_fit = np.linspace(t_n.min(), t_n.max(), 300)
plt.figure(figsize=(7, 5))
plt.plot(t_n, msd, "o", mfc="none", color="blue", ms=4, label="Datos (MSD)")
plt.plot(t_fit, modelo_libre(t_fit, *popt_l), "--", color="green", lw=2, label="Libre")
plt.plot(t_fit, modelo(t_fit, *popt_d), "-", color="red", lw=2.5, label="Con deriva")
plt.xlabel("Time (s)", fontweight="bold")
plt.ylabel(r"Mean Squared Displacement ($\mu$m$^2$)", fontweight="bold")
plt.xlim(0, t_n.max())
plt.ylim(bottom=0)
plt.grid(True)
plt.legend()
plt.show()


#%%
#%%
# 1. Modelos
def modelo_sin_deriva(t, A, n):
    return A * t**n

def modelo_con_deriva(t, A, n, v):
    return A * t**n + (v * t)**2

N = len(t_n)

# Cálculo de barras de error: Error estándar de la media para el promedio acumulado
# Se usa ddof=1 para la desviación estándar muestral. Para el primer punto (i=1), el error es 0.
errores = np.array([np.std(r2[:i], ddof=1) / np.sqrt(i) if i > 1 else 0 for i in range(1, N + 1)])

# 2. Ajuste SIN deriva
p0_sin = [msd[-1] / t_n[-1], 1.0]
popt_sin, pcov_sin = curve_fit(modelo_sin_deriva, t_n, msd, p0=p0_sin, bounds=([0, 0], [np.inf, 3]))
A_sin, n_sin = popt_sin
err_A_sin, err_n_sin = np.sqrt(np.diag(pcov_sin))

# R² Sin deriva
ss_res_sin = np.sum((msd - modelo_sin_deriva(t_n, *popt_sin))**2)
ss_tot = np.sum((msd - np.mean(msd))**2)
r2_sin = 1 - (ss_res_sin / ss_tot)

# 3. Ajuste CON deriva
p0_con = [A_sin, n_sin, 0.01]
popt_con, pcov_con = curve_fit(modelo_con_deriva, t_n, msd, p0=p0_con, bounds=([0, 0, 0], [np.inf, 3, np.inf]))
A_con, n_con, v_con = popt_con
err_A_con, err_n_con, err_v_con = np.sqrt(np.diag(pcov_con))

# R² Con deriva
ss_res_con = np.sum((msd - modelo_con_deriva(t_n, *popt_con))**2)
r2_con = 1 - (ss_res_con / ss_tot)

# Comparación estadística
k1, k2 = 2, 3
F = ((ss_res_sin - ss_res_con) / (k2 - k1)) / (ss_res_con / (N - k2))
p_valor = stats.f.sf(F, k2 - k1, N - k2)

print(f"Sin deriva: R² = {r2_sin:.4f} | A = {A_sin:.4g} ± {err_A_sin:.2g}")
print(f"Con deriva: R² = {r2_con:.4f} | A = {A_con:.4g}, v = {v_con:.4g}")
if p_valor < 0.05:
    print("→ El modelo CON deriva ajusta significativamente mejor (p < 0.05).")
else:
    print("→ No hay mejora significativa usando el modelo con deriva (p >= 0.05).")

# 4. Gráfico estilo "image_cc505e.png"
plt.figure(figsize=(8, 5.5))

# Puntos de datos con barras de error (color oscuro y barras grises)
plt.errorbar(t_n, msd, yerr=errores, fmt='o', color='#333333', ecolor='#aaaaaa', 
             elinewidth=1.5, capsize=3, ms=5, label=r'$\langle \mathrm{MSD} \rangle$')

# Curvas de los modelos
t_fit = np.linspace(0, t_n.max(), 300)

# Etiquetas con los valores de R² y parámetros ajustados
label_sin = f"Sin deriva: $A={A_sin:.3f}   \\pm {err_A_sin:.3f}$ ($R^2={r2_sin:.3f}$)"
label_con = f"Con deriva: $A={A_con:.3f} \\pm {err_A_con:.3f}$ ($R^2={r2_con:.3f}$)"

# Línea roja para el modelo principal y azul punteada para el comparativo
plt.plot(t_fit, modelo_sin_deriva(t_fit, *popt_sin), "-", color="firebrick", lw=2, label=label_sin)
plt.plot(t_fit, modelo_con_deriva(t_fit, *popt_con), "--", color="darkblue", lw=2, label=label_con)

# Formato estético del gráfico (ejes y grilla)
plt.xlabel(r"$\tau$ [s]", fontsize=11)
plt.ylabel(r"MSD [$\mu$m$^2$]", fontsize=11)
plt.xlim(left=-0.05)
plt.ylim(bottom=0)

# Activar ticks menores para que la grilla se vea más densa (estilo papel milimetrado)
plt.minorticks_on()
plt.grid(True, which='major', linestyle='-', linewidth=0.6, alpha=0.7)
plt.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.4)

# Configuración de la leyenda (sin recuadro, esquina superior izquierda)
plt.legend(loc='upper left', frameon=False, fontsize=10)

plt.tight_layout()
plt.show()

#%%
# 1. Modelos
def modelo_sin_deriva(t, A, n):
    return A * t**n

def modelo_con_deriva(t, A, n, v):
    return A * t**n + (v * t)**2

N = len(t_n)

# Cálculo de barras de error: Error estándar de la media para el promedio acumulado
# Se usa ddof=1 para la desviación estándar muestral. Para el primer punto (i=1), el error es 0.
errores = np.array([np.std(r2[:i], ddof=1) / np.sqrt(i) if i > 1 else 0 for i in range(1, N + 1)])

# 2. Ajuste SIN deriva
p0_sin = [msd[-1] / t_n[-1], 1.0]
popt_sin, pcov_sin = curve_fit(modelo_sin_deriva, t_n, msd, p0=p0_sin, bounds=([0, 0], [np.inf, 3]))
A_sin, n_sin = popt_sin
err_A_sin, err_n_sin = np.sqrt(np.diag(pcov_sin))

# R² Sin deriva
ss_res_sin = np.sum((msd - modelo_sin_deriva(t_n, *popt_sin))**2)
ss_tot = np.sum((msd - np.mean(msd))**2)
r2_sin = 1 - (ss_res_sin / ss_tot)

# 3. Ajuste CON deriva
p0_con = [A_sin, n_sin, 0.01]
popt_con, pcov_con = curve_fit(modelo_con_deriva, t_n, msd, p0=p0_con, bounds=([0, 0, 0], [np.inf, 3, np.inf]))
A_con, n_con, v_con = popt_con
err_A_con, err_n_con, err_v_con = np.sqrt(np.diag(pcov_con))

# R² Con deriva
ss_res_con = np.sum((msd - modelo_con_deriva(t_n, *popt_con))**2)
r2_con = 1 - (ss_res_con / ss_tot)

# Comparación estadística
k1, k2 = 2, 3
F = ((ss_res_sin - ss_res_con) / (k2 - k1)) / (ss_res_con / (N - k2))
p_valor = stats.f.sf(F, k2 - k1, N - k2)

print(f"Sin deriva: R² = {r2_sin:.4f} | n = {n_sin:.4g} ± {err_n_sin:.2g}")
print(f"Con deriva: R² = {r2_con:.4f} | n = {n_con:.4g} ± {err_n_con:.2g}, v = {v_con:.4g}")
if p_valor < 0.05:
    print("→ El modelo CON deriva ajusta significativamente mejor (p < 0.05).")
else:
    print("→ No hay mejora significativa usando el modelo con deriva (p >= 0.05).")

# 4. Gráfico
plt.figure(figsize=(8, 5.5))

# Puntos de datos con barras de error
plt.errorbar(t_n, msd, yerr=errores, fmt='o', color='#333333', ecolor='#aaaaaa', 
             elinewidth=1.5, capsize=3, ms=5, label=r'$\langle \mathrm{MSD} \rangle$')

# Curvas de los modelos
t_fit = np.linspace(0, t_n.max(), 300)

# Etiquetas actualizadas para mostrar 'n' y su error en lugar de 'A'
label_sin = f"Sin deriva: $n={n_sin:.3f} \\pm {err_n_sin:.3f}$ ($R^2={r2_sin:.3f}$)"
label_con = f"Con deriva: $n={n_con:.3f} \\pm {err_n_con:.3f}$ ($R^2={r2_con:.3f}$)"

# Líneas de ajuste
plt.plot(t_fit, modelo_sin_deriva(t_fit, *popt_sin), "-", color="firebrick", lw=2, label=label_sin)
plt.plot(t_fit, modelo_con_deriva(t_fit, *popt_con), "--", color="darkblue", lw=2, label=label_con)

# Formato estético del gráfico
plt.xlabel(r"$\tau$ [s]", fontsize=11)
plt.ylabel(r"MSD [$\mu$m$^2$]", fontsize=11)
plt.xlim(left=-0.05)
plt.ylim(bottom=0)

# Grillas y ticks
plt.minorticks_on()
plt.grid(True, which='major', linestyle='-', linewidth=0.6, alpha=0.7)
plt.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.4)

# Configuración de la leyenda
plt.legend(loc='upper left', frameon=False, fontsize=10)

plt.tight_layout()
plt.show()

#%%
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('estiloGraficos.mplstyle')
#%%
tiempo = np.array([5.1,5.1,7,5]) # s
t_e = 0.2 # s
aceleración = 0.005 * 1e3# um s**-2
a_e = aceleración*0.01# um s**-2
velocidad = aceleración * tiempo # um s**-1
v_e = np.sqrt(((tiempo*a_e)**2) + ((aceleración*t_e)**2))
dist_px = 0.094 # um px**-1
d_px_e = 0.005 # um px**-1
pixeles = np.array([31,33,34,34])
diametro = pixeles * dist_px # um
pix_e = 4 # px; voy a probar a no ponerle error al diám que medimos
diam_e = np.sqrt(((dist_px*pix_e)**2) + ((pixeles*d_px_e)**2)) # um
print(diametro)
print(diam_e) 
print(diametro)
print(velocidad)
fig1, ax1 = plt.subplots()
ax1.errorbar(["1", "2", "3", "4",], velocidad,yerr=v_e, fmt="o", label="Datos")
ax1.set_xlabel("N° mediciones")
ax1.set_ylabel(r"$v_{max}$ [$\mu$m $s^{-1}$]")
ax1.legend()
fig1.savefig("VelocidadesMaximas.png")
fig1.show()
#%% veamos ahora el Reynolds y la fuerza
nu = 1300000 # um**2 s**-1; es la viscosidad cinemática del fluido
nu_e = 0 # um**2 s**-1
Re = (diametro * velocidad) / nu # adim
Re_e = np.sqrt((((velocidad/nu) * diam_e)**2) + (((diametro/nu) * v_e)**2) + (((Re/nu) * nu_e)**2)) # adim
fig2, ax2 = plt.subplots()
ax2.errorbar(["1", "2", "3", "4",], Re,yerr=Re_e, fmt="o", label="Datos")
ax2.set_xlabel("N° mediciones")
ax2.set_ylabel("Re")
ax2.legend()
fig2.savefig("Reynolds.png")
fig2.show()

c_d = 24 / Re # adim
cd_e = (c_d / Re) * Re_e

fig3, ax3 = plt.subplots()
ax3.errorbar(["1", "2", "3", "4",], c_d,yerr=cd_e, fmt="o", label="Datos")
ax3.set_xlabel("N° mediciones")
ax3.set_ylabel(r"$C_D$")
ax3.legend()
fig3.savefig("Drag.png")
fig3.show()

rho = 1e-3 * 1e-12 # kg um**-3
area_p = np.pi * ((diametro*0.5)**2) # um**2
areap_e = np.pi * diametro * 0.5 * diam_e # um**2
f_d = 0.5 * c_d * rho * (velocidad**2) * area_p # uN
print(f_d)
d_cd = 0.5 * rho * (velocidad**2) * area_p
d_v = c_d * rho * velocidad * area_p
d_a = 0.5 * c_d * rho * (velocidad**2)
cov_cv = (-c_d/velocidad) * v_e**2                        # Cov(C_D, v)
cov_ca = (-c_d/diametro) * (np.pi*diametro/2) * diam_e**2 # Cov(C_D, A), vía D

var_F = ((d_cd*cd_e)**2 + (d_v*v_e)**2 + (d_a*areap_e)**2
         + 2*d_cd*d_v*cov_cv + 2*d_cd*d_a*cov_ca)
fd_e_cov = np.sqrt(var_F) * 1e6                          # pN
#fd_e = np.sqrt(((d_a * areap_e)**2) + ((d_v * v_e)**2) + ((d_cd * cd_e)**2)) # uN
f_d = f_d * 1e6 # pN
print(np.mean(f_d))
print(np.mean((fd_e_cov/f_d) * 100))
fig4, ax4 = plt.subplots()
ax4.errorbar(["1", "2", "3", "4",], f_d,yerr=fd_e_cov, fmt="o", label="Datos")
ax4.set_xlabel("N° mediciones")
ax4.set_ylabel(r"$F_{arr}$ [pN]")
ax4.legend()
fig4.savefig("FuerzaArrastre.png")
fig4.show()
#%% voy a hacer una cuenta para ver por qué tenemos tanto error
f_d2 = 3*np.pi*nu*velocidad*rho*diametro * 1e6 # pN
rel_vel = (v_e/velocidad) * 100
rel_diam = (diam_e/diametro) * 100
print(np.mean(rel_vel))
print(np.mean(rel_diam))
print(f_d2)
# tomemos un promedio
f_p = np.mean(f_d2) # pN
n = len(velocidad)
n = 1
diam_prom_e = np.sqrt(((dist_px*pix_e)**2)/n + ((np.mean(pixeles)*d_px_e)**2)) # um
d_diam_prom = 3*np.pi*nu*np.mean(velocidad)*rho * 1e6 # pN um**-1
d_vel_prom = 3*np.pi*nu*rho*np.mean(diametro) * 1e6 #  pN s um**-1
v_e_prom = np.mean(v_e) # um s**-1
fp_e = np.sqrt((d_diam_prom * diam_prom_e)**2 + ((d_vel_prom * v_e_prom)**2)/n) #pN
print(f"({f_p:.3f} +- {fp_e:.8f}) pN")


#%% aca esta la misma cuenta pero mas prolijo
n = len(velocidad)
n = 1
k = 3*np.pi*nu*rho * 1e6        # conversión a pN incluida (una sola vez)

v_prom = np.mean(velocidad)     # um/s
D_prom = np.mean(diametro)      # um
f_p = k * v_prom * D_prom       # pN

# Var(D̄): estadístico (baja con n) + sistemático (calibración), en um²
var_D = (dist_px*pix_e)**2 / n + (np.mean(pixeles)*d_px_e)**2

# Var(v̄): t independiente entre mediciones; a compartida (no baja con n), en (um/s)²
var_v = (aceleración*t_e)**2 / n + (np.mean(tiempo)*a_e)**2

dF_dD = k * v_prom              # pN/um
dF_dv = k * D_prom              # pN/(um/s)

fp_e = np.sqrt(dF_dD**2 * var_D + dF_dv**2 * var_v)   # pN
print(f"({f_p:.3f} +- {fp_e:.3f}) pN")
print("Error relativo de F_prom = "f"{(fp_e/ f_p) * 100:.1f} %")
#%% figura de la velocidad y fuerza juntas
x = np.array([1, 2, 3, 4])
desfase = 0.05  # con esto separo los puntos

fig5, ax5 = plt.subplots()
color_v = 'C0' # Azul
ax5.errorbar(x - desfase, velocidad, yerr=v_e, fmt="o", color=color_v, 
             label=r"Datos $v_{max}$")
ax5.set_xlabel("N° mediciones")
ax5.set_ylabel(r"$v_{max}$ [$\mu$m $s^{-1}$]")#, color=color_v)
ax5.set_ylim(23,37)

ax5.tick_params(axis='y')#, labelcolor=color_v)
# Configuramos los números enteros en el eje X para que queden centrados
ax5.set_xticks(x)
ax5.set_xticklabels(["1", "2", "3", "4"])


ax6 = ax5.twinx() # Crea el segundo eje compartiendo el X
color_f = 'C1'    # Naranja
ax6.errorbar(x + desfase, f_d, yerr=fd_e_cov, fmt="o", color=color_f, 
             label=r"Datos $F_{arr}$")
ax6.set_ylabel(r"$F_{arr}$ [pN]")#, color=color_f)
ax6.set_ylim(0.5,1.9)
ax6.tick_params(axis='y')#, labelcolor=color_f)

# --- Leyenda Unificada ---
# Extraemos las referencias de ambos ejes para armar un solo recuadro de leyenda
lineas_1, etiquetas_1 = ax5.get_legend_handles_labels()
lineas_2, etiquetas_2 = ax6.get_legend_handles_labels()
ax5.legend(lineas_1 + lineas_2, etiquetas_1 + etiquetas_2, loc='best')

fig5.tight_layout()
fig5.savefig("VelocidadYFuerza.png")
plt.show()
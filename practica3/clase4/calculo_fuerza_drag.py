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
diametro = np.array([31,33,34,34]) * dist_px # um
diam_e = np.sqrt((0 * dist_px)**2 + (d_px_e)**2) # um; voy a probar a no ponerle error al diám que medimos
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
ax3.errorbar(["1", "2", "3", "4",], Re,yerr=Re_e, fmt="o", label="Datos")
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
fd_e = np.sqrt(((d_a * areap_e)**2) + ((d_v * v_e)**2) + ((d_cd * cd_e)**2)) # uN
f_d = f_d * 1e6 # pN
fd_e = fd_e * 1e6 # pN
print(fd_e/f_d * 100)
fig4, ax4 = plt.subplots()
ax4.errorbar(["1", "2", "3", "4",], f_d,yerr=fd_e, fmt="o", label="Datos")
ax4.set_xlabel("N° mediciones")
ax4.set_ylabel(r"$F_{arr}$ [pN]")
ax4.legend()
fig4.savefig("FuerzaArrastre.png")
fig4.show()
#%% voy a hacer una cuenta para ver por qué tenemos tanto error
f_d2 = 3*np.pi*nu*velocidad*rho*diametro
rel_vel = (v_e/velocidad) * 100
rel_diam = (diam_e/diametro) * 100
print(np.mean(rel_vel))
print(np.mean(rel_diam))
print(f_d2)
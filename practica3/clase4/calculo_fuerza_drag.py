import numpy as np
import matplotlib.pyplot as plt

plt.style.use('estiloGraficos.mplstyle')
#%%
tiempo = np.array([5.1,5.1,7,5]) # s
t_e = 0.2 # s
aceleración = 0.005 # mm s**-2
a_e = aceleración*0 # mm s**-2
velocidad = aceleración * tiempo # mm s**-1
v_e = np.sqrt(((tiempo*a_e)**2) + ((aceleración*t_e)**2))
dist_px = 0.094 # um px**-1
d_px_e = 0.005 # um px**-1
diametro = np.array([31,33,34,34]) * dist_px # um
print(diametro)
print(velocidad)
fig1, ax1 = plt.subplots()
ax1.errorbar(["1", "2", "3", "4",], velocidad*1e3,yerr=v_e*1e3, fmt="o", label="Datos")
ax1.set_xlabel("N° mediciones")
ax1.set_ylabel(r"$v_{max}$ [$\mu$m $s^{-1}$]")
ax1.legend()
fig1.savefig("VelocidadesMaximas.png")
fig1.show()
#%% veamos ahora el Reynolds y la fuerza





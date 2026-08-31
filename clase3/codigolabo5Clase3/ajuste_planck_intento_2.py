import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

plt.style.use('./estiloGraficos.mplstyle')

potencial_corte = np.array([-1.108268151062859, -1.070928290256436, -0.97539635663359, -0.81059875912748, # V
                            -0.7786889645073048, -0.6860455945535144, -0.694819855280932, -0.7189098880885034, 
                            -0.8460413664757194, -0.8308339001990339])#, -0.83448276])
error_potencial = np.array([0.01206897, 0.01034483, 0.00982759, 0.00844828, # V
                            0.00775862, 0.00689655, 0.00696552, 0.00696552, 
                            0.00862069, 0.00889655])#, 0.00834483])
#l_onda = np.array([[[429.3511047, 439.2395325, 441.8809509, 448.93396, 463.5228882, # son todos, pero medimos la mitad
#                     479.2796021, 507.1751404, 518.3876953, 531.2072754, 547.4564819, 
#                     563.767334,  575.357605, 587.2061768, 604.8078003, 617.8804932, 
#                     631.9105835, 642.0559082, 662.1773071, 677.0305786, 690.0621338, 
#                     706.6306152]]])
l_onda = np.array([429.3511047, 463.5228882, 507.1751404, 531.2072754, 563.767334, # nm
                   587.2061768, 617.8804932, 642.0559082, 677.0305786, 706.6306152])

#e_l_onda = np.array([15.7990417, 14.312378, 14.3421326, 18.3772277, # son todos, pero medimos la mitad
#                       35.4029541, 23.7365722, 24.70932, 27.0414428, 30.2957153,
#                       31.0848388, 31.638916, 34.7069092, 34.1239624, 34.6813354,
#                       35.9335938, 39.7402343, 41.2442017, 39.7293702, 42.8649902,
#                       43.9100342])
e_l_onda = np.array([15.7990417, 14.3421326, 35.4029541, 24.70932, 30.2957153, 31.638916, # nm
                     34.1239624, 35.9335938, 41.2442017, 42.8649902]) # uso como error al ancho de banda

c_luz = 299792458 # m s-1
c_luz = c_luz*1e9 # nm s-1
carga_e = 1.602176634 *1e-19 # C
nu = c_luz / l_onda # s-1
e_nu = np.abs((c_luz/(l_onda**2)) * e_l_onda) # s-1
datos_y = carga_e * potencial_corte # lo paso así mas fácil
error_y = carga_e * error_potencial
h_tabulada = 6.62607015*1e-34 # J s-1
def lineal(x,a,b):
    return -1*a*x - b
puntos_x = np.linspace(3*1e14,8*1e14,5)
puntos_y = lineal(puntos_x,h_tabulada,-4*1e-19)
#%%
# CHEQUEAR si los errores en x son despreciables y por ende podemos usar cuadrados mínimos
fig, ax = plt.subplots(figsize=(8,6))
ax.errorbar(nu,datos_y, yerr=error_y, xerr=e_nu,
           fmt="o",label="Datos")
ax.plot(puntos_x, puntos_y, lw=4, alpha=0.8,label="Pendiente ideal")
ax.set_xlabel(r"$\nu$ [$s^{-1}$]")
ax.set_ylabel(r"e$V_0$ [J]")
ax.legend()
fig.tight_layout()
fig.savefig("AjustePlanckPrimerIntento.png")
fig.show()
# dio re mal xd


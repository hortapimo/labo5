import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from numpy.polynomial import Polynomial

plt.style.use('./estiloGraficos.mplstyle')

potencial_corte = np.array([-1.108268151062859, -1.070928290256436, -0.97539635663359, -0.81059875912748, # V
                            -0.7786889645073048, -0.6860455945535144, -0.694819855280932, -0.7189098880885034, 
                            -0.8460413664757194, -0.8308339001990339])

l_onda = np.array([429.3511047, 463.5228882, 507.1751404, 531.2072754, 563.767334, # nm
                   587.2061768, 617.8804932, 642.0559082, 677.0305786, 706.6306152])

c= 2.99e17
frec =c / l_onda #en herts

def ajute(x_datos, y_datos):
    ajuste = Polynomial.fit(x_datos, y_datos, deg=1)
    coef = ajuste.convert().coef
    return ajuste, coef

fig, ax =plt.subplots()
ajuste, coef=ajute(frec, potencial_corte)
ax.scatter(frec, potencial_corte, label="datos")
x= np.linspace(frec[0], frec[-1], 50)
e=1.600217e-19
ax.plot(x, ajuste(x), label=f"h_medida: {-1 * coef[1] * e:.2e} [J*seg]\n h tabulada:{ 6.62e-34}[J*seg]")
ax.legend()




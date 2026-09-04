import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from numpy.polynomial import Polynomial

plt.style.use('./estiloGraficos.mplstyle')

potencial_corte = np.array([-1.12,-1.12, -0.86])

l_onda = np.array([441.8809509, 563.767334,617.880493, ])

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




# -*- coding: utf-8 -*-
"""
Created on Mon Feb  2 22:29:47 2026

@author: LAUTARO
"""
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import scipy as sp
from scipy.stats import chi2
from scipy.optimize import curve_fit

#%%

nombres_columnas = ['longitud_onda', 'intensidad']

df_450 = pd.read_csv('filtrado_450nm.txt',sep = ',',header=None,names=nombres_columnas)

df_500 = pd.read_csv('filtrado_500nm.txt',sep = ',',header=None,names=nombres_columnas)

df_550 = pd.read_csv('filtrado_550nm.txt',sep = ',',header=None,names=nombres_columnas)

df_600 = pd.read_csv('filtrado_600nm.txt',sep = ',',header=None,names=nombres_columnas)

df_650 = pd.read_csv('filtrado_650nm.txt',sep = ',',header=None,names=nombres_columnas)

#%%

#armo mi archivo .txt donde voy a uardar los datos de los ajustes:
encabezado = "longitud_onda_esperada,x0_fit,x0_err,sigma_fit,sigma_err,a_fit,a_err,offset_fit,offset_err\n"

# Usamos 'w' para crear el archivo (o borrarlo si ya existía) y escribir el header
with open('datos_ajustes2.txt', 'w') as f:
    f.write(encabezado)


#%%
casos = [
    (df_450, 450), (df_500, 500), (df_550, 550), 
    (df_600, 600), (df_650, 650)
] #una lista que voy a ir recorriendo con cada dataframe y su longitud de onda en tuplas.

for df,longitud_supuesta in casos:

    def gaussiana(x, a, x0, sigma, offset):
        return a * np.exp(-(x - x0)**2 / (2 * sigma**2)) + offset
    
    #recorto los datos lejos de la campana si quiero, pero hay que ir jugando con esto: (decidí al final no recortarlos)
    lim_inferior = 200
    lim_superior = 1000
    mask = (df['longitud_onda'] >= lim_inferior) & (df['longitud_onda'] <= lim_superior)
    df = df[mask]
    
    # Ahora usamos estos nuevos datos para el ajuste
    x = np.asarray(df['longitud_onda'])
    y = np.asarray(df['intensidad'])
    
    
    #estimaciones de parametros iniciales:
    a_init = np.max(y)             
    x0_init = longitud_supuesta   
    sigma_init = 10.0              
    offset_init = 0
    p0 = [a_init, x0_init, sigma_init, offset_init]
    
    #hago el ajuste:
    popt, pcov = curve_fit(gaussiana, x, y, p0=p0)
    
    a_fit, x0_fit, sigma_fit, offset_fit = popt
    perr = np.sqrt(np.diag(pcov)) #extraigo los errores de las variables de la matriz de covarianza
    a_err, x0_err, sigma_err, offset_err = perr
    
    x_fit = np.linspace(lim_inferior,lim_superior,1000)
    
    y_fit = gaussiana(x_fit,a_fit,x0_fit,sigma_fit,offset_fit)
    
    #hago los gráficos:
    plt.figure(figsize=(10, 8))
    
    plt.scatter(x, y, color='royalblue', label='Datos', s=5, alpha=0.6)
    
    plt.plot(x_fit, y_fit, color='red', label='Ajuste Gaussiano', linewidth=2)
    
    plt.xlabel('Longitud de onda (nm)', fontsize=12)
    plt.ylabel('Intensidad (a.u)', fontsize=12)
    plt.legend()
    plt.grid()
    print(f"Centro del filtro: {x0_fit:.2f} ± {x0_err:.2f} nm")
    print(f"Ancho del filtro (sigma): {sigma_fit:.2f} ± {sigma_err:.4f} nm")
    
    
    #guardo cada figura
    plt.savefig(f'ajuste_{longitud_supuesta}nm.pdf', format='pdf', bbox_inches='tight')
    
    #Abro en modo 'a' (append) para no borrar lo anterior, voy agregando filas al archivo .txt
    with open('datos_ajustes2.txt', 'a') as f:
        f.write(f"{longitud_supuesta}, {x0_fit:.4f}, {x0_err:.4f}, {sigma_fit:.4f}, {sigma_err:.4f}, "
                f"{a_fit:.4f}, {a_err:.4f}, {offset_fit:.4f}, {offset_err:.4f}\n")





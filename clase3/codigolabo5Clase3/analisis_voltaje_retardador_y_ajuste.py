import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from numpy.polynomial import Polynomial

plt.style.use('./estiloGraficos.mplstyle')

def tuki2(archivo):
    df = pd.read_csv(archivo, skiprows=1, sep=",")
    df.columns = ['l', 'I',"d", "k"]
    df['l'] = pd.to_numeric(df['l'], errors='coerce')
    df['I'] = pd.to_numeric(df['I'], errors='coerce')
    df['d'] = pd.to_numeric(df['d'], errors='coerce')
    df['k'] = pd.to_numeric(df['k'], errors='coerce')
    v = df["l"]
    ampl = df["I"]
    fase = df["d"]
    radio = df["k"]
    return v, ampl, fase, radio
#%%
datos = [ ("barrido_420nm_5V.txt","420 nm"),# "CurvaLambda420nm.png"),
          ("barrido_450nm_5V.txt","450 nm"),# "CurvaLambda450nm.png"),
          ("barrido_480nm_5V.txt","480 nm"),# "CurvaLambda480nm.png"),
          ("barrido_510nm_5V.txt","510 nm"),# "CurvaLambda510nm.png"),
          ("barrido_540nm_5V.txt","540 nm"),# "CurvaLambda540nm.png"),
          ("barrido_570nm_5V.txt","570 nm"),# "CurvaLambda570nm.png"),
          ("barrido_600nm_5V.txt","600 nm"),# "CurvaLambda600nm.png"),
          ("barrido_630nm_5V.txt","630 nm"),# "CurvaLambda630nm.png"),
          ("barrido_660nm_5V_2.txt","660 nm"),# "CurvaLambda660nm.png"),
          #("barrido_690nm_5V_2.txt","690 nm"),# "CurvaLambda690nm.png"), al comente porque da muy feo, revisar,
          ("barrido_720nm_5V_2.txt","720 nm")]# "CurvaLambda720nm.png"),  ]
#%%funcion par ainterpolar cero
def modelo_exponencial(x, a, b, c):
    return a * np.exp(b * x) + c

def ajustar_y_cero(x_data, y_data):
    # 1. Ajuste de la curva
    ajuste = Polynomial.fit(x_data, y_data, deg=3)
    raices_todas = ajuste.roots()
    raices_reales = raices_todas[np.isreal(raices_todas)].real
    
    
    return raices_reales, ajuste

def devolver_puntos_alrededor(v,indice_minimo,n_puntos_alrededor =4):
    puntos = []
    for i in range(2*n_puntos_alrededor+1):
        puntos.append(v[indice_minimo-4+i])
    
    
    puntos = np.array(puntos)
    
    return puntos

def raiz_en_intervalo(raices, x_min, x_max):
    raiz_encontrada= False
    for raiz in raices:
        if ((raiz>x_min) and (raiz < x_max)):
            print(f"la raiz vale {raiz}")
            raiz_encontrada= raiz
    return raiz_encontrada

    
#%%

offset = 2.10 # pA
error_offset = 0.01 # pA
potenciales_corte = []
errores_potenciales = []

for (archivo, etiqueta) in datos:
    fig1, ax1 = plt.subplots(figsize=(8,6))
    v, i, _, _ = tuki2(archivo)
    v = np.array(v)
    i = np.array(i) * 1e12 # paso a unidades de pA
    error_sistematico_i = np.abs(i) * 0.01 
    error_sistematico_v = np.abs(v) * 0.01 

    i = i - offset
    error_i = np.sqrt((error_sistematico_i**2) + (error_offset**2))

    indice_minimo = np.argmin(np.abs(i))
    
    
    puntos_v = devolver_puntos_alrededor(v,indice_minimo)
    puntos_i = devolver_puntos_alrededor(i, indice_minimo)
    puntos_err_i =devolver_puntos_alrededor(error_i, indice_minimo)
    puntos_err_v =devolver_puntos_alrededor(error_sistematico_v, indice_minimo)
    
    raices_reales, funcion_ajustada = ajustar_y_cero(puntos_v, puntos_i)
    v_cero = raiz_en_intervalo(raices_reales, puntos_v[0], puntos_v[-1])

    v_min = v[indice_minimo]
    error_v_min = error_sistematico_v[indice_minimo]
    i_min = i[indice_minimo]
    potenciales_corte.append(v_min)
    errores_potenciales.append(error_v_min)
    ax1.errorbar(puntos_v, puntos_i, xerr=puntos_err_v, yerr=puntos_err_i,
                 fmt="o", label=r"$\lambda_{nom}$ = "f"{etiqueta}", alpha=0.8)
    x=np.linspace(puntos_v[0], puntos_v[-1], 50)
    ax1.plot(x,funcion_ajustada(x))
    ax1.plot(v_cero, 0, marker='*', color='red', markersize=16, 
             linestyle='None', label=r"Mínimo: $V_0$ = "f"({v_cero:.2f} ± {error_v_min:.2f}) V")
    
    ax1.set_xlabel("Voltaje [V]")
    ax1.set_ylabel("Corriente [pA]")
    ax1.legend()
    fig1.tight_layout()
    plt.show()

# Convertimos las listas a arrays de numpy para tu futuro análisis
potenciales_corte = np.array(potenciales_corte)
errores_potenciales = np.array(errores_potenciales)
#%%
print(potenciales_corte)
print(errores_potenciales)





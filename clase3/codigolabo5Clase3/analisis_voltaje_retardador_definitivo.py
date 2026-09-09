import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#from scipy.optimize import curve_fit
#from numpy.polynomial import Polynomial

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
          ("barrido_690nm_5V_2.txt","690 nm")]#,# "CurvaLambda690nm.png"),
#          ("barrido_720nm_5V_2.txt","720 nm")]# "CurvaLambda720nm.png"),  ]
#%%    
# volvi a hacer la determinación del voltaje de corte. cambios:
# 1) saque ese offset que le restamos a la corriente, xq vimos que al final no estaba
# 2) el voltaje retardador lo halla buscando el mínimo en módulo de los datos. yo
# creo que es mejor hacer eso, que es menos sofisticado y más sencillo de explicar
# luego en el informe o charla.
# 3) la medición de 690 nm da bien asi que la dejo, y la de 720 la saco xq no tomamos
# su espectro con la fibra óptica entonces no tenemos su incerteza asociada.
potenciales_corte = []
errores_potenciales = []

for (archivo, etiqueta) in datos:
    fig1, ax1 = plt.subplots(figsize=(8,6))
    v, i, _, _ = tuki2(archivo)
    v = np.array(v)
    i = np.array(i) * 1e12 # paso a unidades de pA
    
    error_sistematico_i = np.abs(i) * 0.01 
    error_sistematico_v = np.abs(v) * 0.01 

    indice_minimo = np.argmin(np.abs(i))
    v_min = v[indice_minimo]
    i_min = i[indice_minimo]
    # uso como error la mitad de la dist al punto siguiente.
    if indice_minimo < len(v) - 1:
        error_v_min = np.abs(v[indice_minimo + 1] - v_min) / 2
    else: # para que no se rompa
        error_v_min = np.abs(v_min - v[indice_minimo - 1]) / 2
    
    potenciales_corte.append(v_min)
    errores_potenciales.append(error_v_min)
    
    ax1.errorbar(v, i, xerr=error_sistematico_v, yerr=error_sistematico_i,
                 fmt="o", label=r"$\lambda_{nom}$ = "f"{etiqueta}", alpha=0.8)
    
    ax1.plot(v_min, i_min, marker='*', color='red', markersize=16, 
             linestyle='None', label=f"Mínimo: ({v_min:.2f} ± {error_v_min:.2f}) V")
    
    ax1.set_xlabel("Voltaje [V]")
    ax1.set_ylabel("Corriente [pA]")
    ax1.legend()
    fig1.tight_layout()
    plt.show()

potenciales_corte = np.array(potenciales_corte)
errores_potenciales = np.array(errores_potenciales)
#%%
print(potenciales_corte)
print(errores_potenciales)





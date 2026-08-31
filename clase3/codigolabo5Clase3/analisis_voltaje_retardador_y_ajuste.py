import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
datos = [ ("barrido_420nm_5V.txt","420 nm", "CurvaLambda420nm.png"),
          ("barrido_450nm_5V.txt","450 nm", "CurvaLambda450nm.png"),
          ("barrido_480nm_5V.txt","480 nm", "CurvaLambda480nm.png"),
          ("barrido_510nm_5V.txt","510 nm", "CurvaLambda510nm.png"),
          ("barrido_540nm_5V.txt","540 nm", "CurvaLambda540nm.png"),
          ("barrido_570nm_5V.txt","570 nm", "CurvaLambda570nm.png"),
          ("barrido_600nm_5V.txt","600 nm", "CurvaLambda600nm.png"),
          ("barrido_630nm_5V.txt","630 nm", "CurvaLambda630nm.png"),
          ("barrido_660nm_5V_2.txt","660 nm", "CurvaLambda660nm.png"),
          ("barrido_690nm_5V_2.txt","690 nm", "CurvaLambda690nm.png"),
          ("barrido_720nm_5V_2.txt","720 nm", "CurvaLambda720nm.png"),  ]

#%%
# grafico por separado
offset = 2.10 # pA
error_offset = 0.01 # pA
for (archivo, etiqueta, null) in datos:
    fig1, ax1 = plt.subplots(figsize=(8,6))
    v, i, _, _= tuki2(archivo)
    i = i*1e12 # paso a unidades de pA
    error_sistematico_i = np.abs(i)*0.01 # el manual dice que es el 1%
    error_sistematico_v = np.abs(v)*0.01 # pongo error en x porque no estamos 
                                         # haciendo cuadrados mínimos
    i = i - offset
    error_i = np.sqrt((error_sistematico_i**2) + (error_offset**2))
    ax1.errorbar(v,i,xerr=error_sistematico_v, yerr=error_sistematico_i,
                fmt="o",label=r"$\lambda_{nom}$ = "f"{etiqueta}")
    ax1.set_xlabel("Voltaje [V]")
    ax1.set_ylabel("Corriente [pA]")
    ax1.legend()
    fig1.tight_layout()
    fig1.show()









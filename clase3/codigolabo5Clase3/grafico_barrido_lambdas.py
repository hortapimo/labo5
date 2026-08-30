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
datos = [ ("barrido_420nm_5V.txt","420 nm"),
          ("barrido_450nm_5V.txt","450 nm"),
          ("barrido_480nm_5V.txt","480 nm"),
          ("barrido_510nm_5V.txt","510 nm"),
          ("barrido_540nm_5V.txt","540 nm"),
          ("barrido_570nm_5V.txt","570 nm"),
          ("barrido_600nm_5V.txt","600 nm"),
          ("barrido_630nm_5V.txt","630 nm"),
          ("barrido_660nm_5V_2.txt","660 nm"),
          ("barrido_690nm_5V_2.txt","690 nm"),
          ("barrido_720nm_5V_2.txt","720 nm"),  ]


fig, ax = plt.subplots(figsize=(8,6))
colores = plt.cm.plasma(np.linspace(0, 1, len(datos)))
for (archivo, etiqueta), color in zip(datos, colores):
    v, i, _, _= tuki2(archivo)
    i = i*1e12 # paso a unidades de pA
    error_sistematico_i = np.abs(i)*0.01 # el manual dice que es el 1%
    error_sistematico_v = np.abs(v)*0.01 # pongo error en x porque no estamos 
                                         # haciendo cuadrados mínimos
    ax.errorbar(v,np.abs(i),xerr=error_sistematico_v, yerr=error_sistematico_i,
                fmt="o",label=r"$\lambda_{nom}$ = "f"{etiqueta}", color=color)
ax.axhline(y=0, ls="--",label="Origen", color="red")
ax.set_xlabel("Voltaje [V]")
ax.set_ylabel("Corriente [pA]")
ax.legend()
fig.tight_layout()
fig.show()


#%%
for (archivo, etiqueta) in datos:
    v, i, _, _= tuki2(archivo)
    i = i*1e12 # paso a unidades de pA
    error_sistematico_i = np.abs(i)*0.01
    fig, ax = plt.subplots(figsize=(8,6))
    ax.errorbar(v,i,yerr=error_sistematico_i,
                fmt=".", label=r"$\lambda_{nom}$ = "f"{etiqueta}")
    ax.set_xlabel("Voltaje [V]")
    ax.set_ylabel("Corriente [pA]")
    ax.legend()
    fig.tight_layout()
    #fig.savefig("RuidoBlanco.png")
    fig.show()



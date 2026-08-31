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
v, i, _, _= tuki2("medicionRuidoBlanco.txt")

fig, ax = plt.subplots(figsize=(8,6))

ax.errorbar(v,i*1e12,xerr=np.abs(v)*0.01, yerr=np.abs(i)*0.01*1e12,fmt=".", label="Datos")
ax.set_xlabel("Voltaje [V]")
ax.set_ylabel("Corriente [pA]")
ax.legend()
fig.tight_layout()
fig.savefig("RuidoBlanco.png")
fig.show()








import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
#plt.style.use('./estiloGraficos.mplstyle')


def tuki(archivo: Path):
    data = np.genfromtxt(archivo, skip_header=53, skip_footer=1, usecols=(0,1), delimiter=',')
    return data.T

#%%
def tuki2(archivo):
    df = pd.read_csv(archivo, skiprows=53, sep="\t")
    df.columns = ['l', 'I',"d"]
    df['l'] = pd.to_numeric(df['l'], errors='coerce')
    df['I'] = pd.to_numeric(df['I'], errors='coerce')
    df['d'] = pd.to_numeric(df['d'], errors='coerce')
    v = datos_420["l"]
    ampl = datos_420["I"]
    fase = datos_420["d"] 
    return v, ampl, fase
v, ampl, fase = tuki2("barrido_voltajes_-5_7_420nm_intento2_clase2.txt")

fig, ax = plt.subplots()
ax.errorbar(v,ampl, fmt=".")

ax.set_xlabel("Voltaje [V]")
ax.set_ylabel("Corriente [A]")
plt.show()










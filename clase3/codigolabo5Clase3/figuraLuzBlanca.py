import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
#plt.style.use('./estiloGraficos.mplstyle')


def tuki(archivo: Path):
    data = np.genfromtxt(archivo, skip_header=53, skip_footer=1, usecols=(0,1), delimiter=',')
    return data.T

#%%
#df = pd.read_csv('luz blanca sin filtro 8ms.csv', skiprows=53)
##df.columns = ['l', 'I']
#df['l'] = pd.to_numeric(df['l'], errors='coerce')
lo_antes, ao_antes = tuki("luz blanca sin filtro 8ms.csv")
#lo_luego, ao_luego = tuki("luzBlanca.csv")
ao_antes = ao_antes / np.max(ao_antes)
#ao_luego = ao_luego / np.max(ao_luego)

fig, ax = plt.subplots()
ax.errorbar(lo_antes,ao_antes, fmt=".")
#ax.errorbar(lo_luego,ao_luego, fmt=".")

ax.set_xlabel("longitud de onda [nm]")
ax.set_ylabel("Intensidad")





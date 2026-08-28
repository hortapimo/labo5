import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
plt.style.use('./estiloGraficos.mplstyle')

df = pd.read_csv('luz blanca sin filtro 8ms.csv', skiprows=53)
df2 = pd.read_csv('luzBlanca.csv', skiprows=55, sep=";")
df.columns = ['l', 'I']
df['l'] = pd.to_numeric(df['l'], errors='coerce')
df2.columns = ['l', 'I']
df2['l'] = pd.to_numeric(df2['l'], errors='coerce')


fig, ax = plt.subplots()
ax.plot(df['l'],df['I']/np.max(df['I']))
ax.plot(df2['l'],df2['I']/np.max(df2['I']))
ax.set_xlabel("longitud de onda [nm]")
ax.set_ylabel("Intensidad")





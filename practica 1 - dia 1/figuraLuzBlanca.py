import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
plt.style.use('./estiloGraficos.mplstyle')

df = pd.read_csv('luz blanca sin filtro 8ms.csv', skiprows=53)
df.columns = ['l', 'I']
df['l'] = pd.to_numeric(df['l'], errors='coerce')

fig, ax = plt.subplots()
ax.plot(df['l'],df['I'])
ax.set_xlabel("longitud de onda [nm]")
ax.set_ylabel("Intensidad")





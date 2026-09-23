import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import funciones as misf
nombre="decaimientos1_primerasemana.parquet"
plt.style.use('estiloGraficos.mplstyle')

df=misf.abrir_parquet(nombre)

misf.obtenerInfoDataframe(df)

ndecaimiento=26

medicion =df[df["#decaimiento"] == ndecaimiento]

fig,ax=plt.subplots()
ax.scatter(medicion["tiempo [ns]"], medicion["canal 1 [mV]"], label="canal 1")
ax.scatter(medicion["tiempo [ns]"], medicion["canal 2 [mV]"], label="canal 2")
ax.scatter(medicion["tiempo [ns]"], medicion["canal 3 [mV]"], label="canal 3")
ax.legend()

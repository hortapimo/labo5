import matplotlib
# es para no graficar en vivo, que solo guarde, si queres graficar deja solo el import matplotlib.pyplot as plt
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.ioff()

from pathlib import Path
import pandas as pd
import funciones as misf
nombre="decaimientos.parquet"
plt.style.use('estiloGraficos.mplstyle')

df=misf.abrir_parquet(nombre)

misf.obtenerInfoDataframe(df)
#%%
# ndecaimiento=2

# medicion =df[df["#decaimiento"] == ndecaimiento]

# fig,ax=plt.subplots()
# ax.scatter(medicion["tiempo [ns]"], medicion["canal 1 [mV]"], label="canal 1")
# ax.scatter(medicion["tiempo [ns]"], medicion["canal 2 [mV]"], label="canal 2")
# ax.scatter(medicion["tiempo [ns]"], medicion["canal 3 [mV]"], label="canal 3")
# ax.legend()
#%%

nDecaimiento = df["#decaimiento"].nunique()
nAxis=49
if (nDecaimiento%nAxis ==0):
    if nDecaimiento//nAxis ==0:
        nFiguras=1
    else:
        nFiguras=nDecaimiento//nAxis
else:
    nFiguras=nDecaimiento//nAxis + 1


for i in range(nFiguras):
    print(f"procesando figura {i+1}")
    

    fig,axs=plt.subplots(nrows=7,ncols=7, figsize=(18,9))
    j=0
    for ax_fila in axs:
        k=0
        for ax in ax_fila:
            ndecaimiento=j*7+i*nAxis+k+1
            medicion =df[df["#decaimiento"] == ndecaimiento]
            ax.scatter(medicion["tiempo [ns]"], medicion["canal 1 [mV]"], label="canal 1", s=1)
            ax.scatter(medicion["tiempo [ns]"], medicion["canal 2 [mV]"], label="canal 2",s=1)
            ax.scatter(medicion["tiempo [ns]"], medicion["canal 3 [mV]"], label="canal 3",s=1)
            #ax.legend()
            ax.set_title(f"decaimiento #:{ndecaimiento}")
            k=k+1
        j=j+1
    fig.tight_layout()
    fig.savefig(f"Decaimientos{i*nAxis+1}-{((i+1)*nAxis)}")  
    plt.close(fig)
    
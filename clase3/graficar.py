import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

plt.style.use('./estiloGraficos.mplstyle')

def load_archiv0(name):
    df = pd.read_csv(name, skiprows=1)
    df.columns = ['V', 'Ix','Iy','r']
    df['V'] = pd.to_numeric(df['V'], errors='coerce')
    return df


df=load_archiv0("barrido_450nm_5V.txt")
df2=load_archiv0("barrido_420nm_5V.txt")
df3=load_archiv0("barrido_480nm_5V.txt")
df4=load_archiv0("barrido_510nm_5V.txt")
df5=load_archiv0("barridoFinal_435nm_5V_tapando.txt")


#%% PAra ver el archivo
rng = np.random.default_rng()

def graficar(*tuplasXY,**karg):
    fig, ax = plt.subplots()
    
    for (x,y,label,marker) in tuplasXY:
        ax.scatter(x,y,label=label, marker=marker)
    
    try:
        ax.set_xlabel(karg["xlabel"])
        ax.set_ylabel(karg["ylabel"])    
    except: pass  
 
    ax.legend()
    return fig,ax
    
fig,ax = graficar((df['V'],df['Ix']*1e12,"Medicion 1", "*"),
                  (df2['V'],df2['Ix']*1e12,"Medicion 2", "s"),
                  (df3['V'],df3['Ix']*1e12,"Medicion 3", "d"),
                  (df4['V'],df4['Ix']*1e12,"Medicion 4","o"),
                  (df5['V'],df5['Ix']*1e12,"Ruido","x"),
                  xlabel=rf"$V_f$ [V]", ylabel="I[pA]")
ax.axhline(y=0,color='red', linestyle='--', linewidth=1.5, label='Cero')
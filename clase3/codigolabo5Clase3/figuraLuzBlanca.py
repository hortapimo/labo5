import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.integrate import trapezoid

plt.style.use('./estiloGraficos.mplstyle')
def load_archiv0(name):
    df = pd.read_csv(name, skiprows=53)
    df.columns = ['l', 'I']
    df['l'] = pd.to_numeric(df['l'], errors='coerce')
    return df
    
#df2.columns = ['l', 'I']
#df2['l'] = pd.to_numeric(df2['l'], errors='coerce')

df=load_archiv0("luzBlanca2v.csv")
df2=load_archiv0("luzBlanca3v.csv")
df3=load_archiv0("luzBlanca4v.csv")
df4=load_archiv0("luzBlanca5v.csv")

fig, ax = plt.subplots()
ax.scatter(df['l'],df['I'], label = "2V", s=1)
ax.scatter(df2['l'],df2['I'], label = "3V",s=1)
ax.scatter(df3['l'],df3['I'], label = "4V",s=1)
ax.scatter(df4['l'],df4['I'], label = "5V",s=1)

ax.set_xlabel("longitud de onda [nm]")
ax.set_ylabel("Intensidad")
ax.set_title("Luz Blanca a distintos voltajes")
ax.legend()


#%%
intencidad = np.array([ 
                    trapezoid(df['I'][:-1],df['l'][:-1]),
                    trapezoid(df2['I'][:-1],df2['l'][:-1]),
                    trapezoid(df3['I'][:-1],df3['l'][:-1]),
                    trapezoid(df4['I'][:-1],df4['l'][:-1])
                    ])

voltaje = np.array([2,3,4,5])
fig2, ax2 = plt.subplots()
ax2.scatter(voltaje, intencidad)
ax2.set_xlabel("voltaje [V]")
ax2.set_ylabel("Intencidad")
ax2.set_title(" Ajuste usando integral")

def f(x,a,b):
    return a*x +b
    
par, pcov = curve_fit(f, voltaje, intencidad)
x =np.linspace(voltaje[0], voltaje[-1], 50)
ax2.plot(x,f(x,par[0], par[1]), c="0.2", label=f"Ajuste: {par[0]:.2f} x + {par[1]:.2f} ")
ax2.legend()
#%%

maximos = np.array([np.max(df['I']),np.max(df2['I']),np.max(df3['I']),np.max(df4['I'])])
voltaje = np.array([2,3,4,5])
fig3, ax3 = plt.subplots()
ax3.scatter(voltaje, maximos)
ax3.set_xlabel("voltaje [V]")
ax3.set_ylabel("Intencidad")
ax3.set_title(" Ajuste usando maximos")

def f(x,a,b):
    return a*x +b
    
par, pcov = curve_fit(f, voltaje, maximos)
x =np.linspace(voltaje[0], voltaje[-1], 50)
ax3.plot(x,f(x,par[0], par[1]), c="0.2", label=f"Ajuste: {par[0]:.2f} x + {par[1]:.2f} ")
ax3.legend()

#%%






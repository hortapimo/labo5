import pandas as pd
import matplotlib.pyplot as plt

df=pd.read_csv(f"barridoFinal_435nm_5V_tapando.txt")
df2=pd.read_csv(f"barridoFinal_435nm_5V_colimado.txt")
df3=pd.read_csv(f"barridoFinal_435nm_5V.txt")

fig,ax=plt.subplots()
ax.scatter("voltage", "x",data=df, label="ruido")
ax.scatter("voltage", "x",data=df2, label="colimado")
ax.scatter("voltage", "x",data=df3, label="no colimado")
ax.legend()

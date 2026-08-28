import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df=pd.read_csv("barrido_570nm_5V.txt")
df2=pd.read_csv("barrido_570nm_4V.txt")
df3=pd.read_csv("barrido_570nm_3V.txt")
df4=pd.read_csv("barrido_570nm_2V.txt")


fig,ax=plt.subplots()
ax.scatter("voltage", "x",data=df, label="5V")
ax.scatter("voltage", "x",data=df2, label="4V")
ax.scatter("voltage", "x",data=df3,label="3V")
ax.scatter("voltage", "x",data=df4,label="2V")
ax.grid(which="major")
ax.legend()
ax.grid(which="minor",alpha=0.3)
ax.minorticks_on()
ax.set_xlabel("Voltaje (V)")
ax.set_ylabel("Corriente (A)")
fig.tight_layout()
fig.savefig("570nm_variosVoltajes.png")
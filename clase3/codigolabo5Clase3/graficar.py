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
fig.show()
#%%
# voy a calcular el voltaje de corte y extraer el corrimiento en el eje vertical
# que hay en las mediciones por la corriente residual que hay en el sistema.
# esto lo voy a usar para restarle esta constante a todas las demás mediciones,
# hallando así el voltaje de corte para el resto de curvas que tomamos.

# Unimos las corrientes de tus 4 dataframes emparejando por la columna 'voltage'
df_unido = df[['voltage', 'x']].rename(columns={'x': '5V'})
df_unido = df_unido.merge(df2[['voltage', 'x']].rename(columns={'x': '4V'}), on='voltage')
df_unido = df_unido.merge(df3[['voltage', 'x']].rename(columns={'x': '3V'}), on='voltage')
df_unido = df_unido.merge(df4[['voltage', 'x']].rename(columns={'x': '2V'}), on='voltage')

# Calculamos la diferencia entre el valor máximo y mínimo para cada voltaje
columnas_corriente = ['5V', '4V', '3V', '2V']
df_unido['dispersion'] = df_unido[columnas_corriente].max(axis=1) - df_unido[columnas_corriente].min(axis=1)

# Ubicamos la fila donde esa dispersión es la menor posible
punto_cruce = df_unido.loc[df_unido['dispersion'].idxmin()]

# Imprimimos los resultados con formato científico
print(f"Voltaje de corte:({punto_cruce['voltage']:.3f} ± {punto_cruce['voltage']*0.01:.3f}) V")
print("Corrientes en ese punto:")
print(f"5V: ({punto_cruce['5V']*1e12:.2f} ± {punto_cruce['5V']*1e12*0.01:.2f}) pA")
print(f"4V: ({punto_cruce['4V']*1e12:.2f} ± {punto_cruce['4V']*1e12*0.01:.2f}) pA")
print(f"3V: ({punto_cruce['3V']*1e12:.2f} ± {punto_cruce['3V']*1e12*0.01:.2f}) pA")
print(f"2V: ({punto_cruce['2V']*1e12:.2f} ± {punto_cruce['2V']*1e12*0.01:.2f}) pA")

# ahora vamos a tomar un valor representativo de ese voltaje. suponiendo que la
# distribución de voltajes en ese punto es gaussiana con una misma esperanza 
# para todos los puntos (pero no necesariamente igual varianza), podemos tomar 
# como mejor estimador al promedio ponderado o pesado. 


corrientes_cruce = np.array([punto_cruce['5V'], punto_cruce['4V'],  # pongo las 
                             punto_cruce['3V'], punto_cruce['2V']]) # corrientes en un array
errores_cruce = np.abs(corrientes_cruce * 0.01) # su incerteza

def promedio_pesado(valores, incertezas):
    x = np.array(valores)
    sigma = np.array(incertezas)
    pesos = 1 / (sigma ** 2)
    promedio = np.sum(x * pesos) / np.sum(pesos)
    incerteza_prom = np.sqrt(1 / np.sum(pesos))
    return promedio, incerteza_prom

I_media, err_I_media = promedio_pesado(corrientes_cruce, errores_cruce)
print(f"\nCorriente de corte representativa: ({I_media*1e12:.2f} ± {err_I_media*1e12:.2f}) pA")

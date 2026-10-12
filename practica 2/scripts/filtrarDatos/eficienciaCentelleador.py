import funciones as misf
import matplotlib.pyplot as plt
import pandas as pd

plt.style.use('estiloGraficos.mplstyle')

dfTest = misf.abrir_parquet("decaimientos.parquet", motor ="pyarrow")
misf.obtenerInfoDataframe(dfTest)
                            
#%%

umbral = -50.0
umbralSup = 100 
tiempo_trigger = 210.0
tiempo_minimo = 50.0

def hayEventoTriple(dataframe: pd.DataFrame) -> bool:
    
    mascara2 = dataframe["canal 2 [mV]"] < umbral
    mascara2Sup = dataframe["canal 2 [mV]"] > umbralSup
    mascara3 = dataframe["canal 3 [mV]"] < umbral
    mascara3Sup = dataframe["canal 3 [mV]"] > umbralSup
    mascara1Sup = dataframe["canal 1 [mV]"] > umbralSup

    if (not mascara2.any()) and (not mascara3.any()) :
        return False #descarta si no hay decaimiento
    if (mascara2Sup.any()) or (mascara3Sup.any()) or (mascara1Sup.any()) :
        return False #descarta si hay señal ruidosa
    
    tiempos_evento2 = dataframe.loc[mascara2, "tiempo [ns]"]
    tiempos_evento3 = dataframe.loc[mascara3, "tiempo [ns]"]
    dif2 = tiempos_evento2 - tiempo_trigger
    dif3 = tiempos_evento3 - tiempo_trigger
 
    return bool ( (dif2 > tiempo_minimo).any() and (dif3 > tiempo_minimo).any() )

def hayEventoDoble(dataframe: pd.DataFrame) -> bool:
    
    mascara2Sup = dataframe["canal 2 [mV]"] > umbralSup
    mascara3 = dataframe["canal 3 [mV]"] < umbral
    mascara3Sup = dataframe["canal 3 [mV]"] > umbralSup
    mascara1Sup = dataframe["canal 1 [mV]"] > umbralSup

    if not mascara3.any():
        return False #descarta si no hay decaimiento
    if (mascara2Sup.any()) or (mascara3Sup.any()) or (mascara1Sup.any()) :
        return False #descarta si hay señal ruidosa
    
    tiempos_evento3 = dataframe.loc[mascara3, "tiempo [ns]"]
    dif3 = tiempos_evento3 - tiempo_trigger

    return bool ( (dif3 > tiempo_minimo).any() )

#%%
"""
acá calcula la eficiencia del centelleador 2, que es la que usamos en la mayoría de mediciones
"""
eDobles, eTriples , eDescartados= 0, 0, 0 

# eficiencia de centelleador 2
decaimientosTotales = dfTest['#decaimiento'].unique()
print(f"\nCentelleador 2 ----------------------------------------\nDecaimientos totales: {len(decaimientosTotales)}")

for n in decaimientosTotales:
    nDecaimiento = dfTest[dfTest["#decaimiento"] == n]
    if hayEventoDoble(nDecaimiento):
        if hayEventoTriple(nDecaimiento):
            eTriples += 1
            continue
        else:
            eDobles += 1
    else:
        eDescartados += 1
            
try:
    eficiencia2 = (eTriples)/(eDobles + eTriples)
    print(f"Eventos dobles: {eDobles}\nEventos triples: {eTriples}\nEventos descartados: {eDescartados}\nEficiencia: {eficiencia2}")
except ZeroDivisionError:
    print("\nNo se puede dividir por cero.")
    
# %%

df1 = misf.abrir_parquet("decaimientosCentelleador1.parquet", motor ="pyarrow")
misf.obtenerInfoDataframe(df1)
"""
acá calcula la eficiencia del centelleador 1
"""
eDobles, eTriples , eDescartados= 0, 0, 0 

# eficiencia de centelleador 2
decaimientosTotales = df1['#decaimiento'].unique()
print(f"\nCentelleador 1 ----------------------------------------\nDecaimientos totales: {len(decaimientosTotales)}")

for n in decaimientosTotales:
    nDecaimiento = df1[df1["#decaimiento"] == n]
    if hayEventoDoble(nDecaimiento):
        if hayEventoTriple(nDecaimiento):
            eTriples += 1
            continue
        else:
            eDobles += 1
    else:
        eDescartados += 1
            
try:
    eficiencia2 = (eTriples)/(eDobles + eTriples)
    print(f"Eventos dobles: {eDobles}\nEventos triples: {eTriples}\nEventos descartados: {eDescartados}\nEficiencia: {eficiencia2}")
except ZeroDivisionError:
    print("\nNo se puede dividir por cero.")
    
# %%

df3 = misf.abrir_parquet("decaimientosCentelleador3.parquet", motor ="pyarrow")
misf.obtenerInfoDataframe(df3)
"""
acá calcula la eficiencia del centelleador 3
"""
eDobles, eTriples , eDescartados= 0, 0, 0 

# eficiencia de centelleador 2
decaimientosTotales = df3['#decaimiento'].unique()
print(f"\nCentelleador 3 ----------------------------------------\nDecaimientos totales: {len(decaimientosTotales)}")

for n in decaimientosTotales:
    nDecaimiento = df3[df3["#decaimiento"] == n]
    if hayEventoDoble(nDecaimiento):
        if hayEventoTriple(nDecaimiento):
            eTriples += 1
            continue
        else:
            eDobles += 1
    else:
        eDescartados += 1
            
try:
    eficiencia2 = (eTriples)/(eDobles + eTriples)
    print(f"Eventos dobles: {eDobles}\nEventos triples: {eTriples}\nEventos descartados: {eDescartados}\nEficiencia: {eficiencia2}")
except ZeroDivisionError:
    print("\nNo se puede dividir por cero.")
    
# %%
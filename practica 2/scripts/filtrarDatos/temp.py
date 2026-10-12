import funciones as misf
import matplotlib.pyplot as plt
import pandas as pd

plt.style.use('estiloGraficos.mplstyle')

df_completo = misf.abrir_parquet("datos_completos_eficiencia.parquet", motor="pyarrow")

# separar las mediciones creando una máscara (filtro) para cada orden
df123 = df_completo[df_completo['carpeta_origen'] == 'medicionEficienciaOrden123'].copy()
df132 = df_completo[df_completo['carpeta_origen'] == 'medicionEficienciaOrden132'].copy()
df312 = df_completo[df_completo['carpeta_origen'] == 'medicionEficienciaOrden312'].copy()

# resetear los índices para que cada dataframe arranque de 0
df123.reset_index(drop=True, inplace=True)
df132.reset_index(drop=True, inplace=True)
df312.reset_index(drop=True, inplace=True)

print(f"Filas en orden 123: {len(df123)}")
print(f"Filas en orden 132: {len(df132)}")
print(f"Filas en orden 312: {len(df312)}")

misf.obtenerInfoDataframe(df123)
misf.obtenerInfoDataframe(df132)
misf.obtenerInfoDataframe(df312)

#%%

umbral = -90.0
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
 
    return bool ( (dif2 > tiempo_minimo).any() or (dif3 > tiempo_minimo).any() )

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

eDobles, eTriples = 0,0 

# eficiencia de 2

decaimientosTotales = df123['#decaimiento'].unique()
print(f"Decaimientos totales: {len(decaimientosTotales)}")

for n in decaimientosTotales:
    nDecaimiento = df123[df123["#decaimiento"] == n]
    if hayEventoDoble(nDecaimiento):
        if hayEventoTriple(nDecaimiento):
            eTriples += 1
            continue
        else:
            eDobles += 1
            
try:
    eficiencia123 = (eTriples)/(eDobles + eTriples)
    print(f"\nCentelleador 2:\nEventos dobles: {eDobles}\nEventos triples: {eTriples}\nEficiencia: {eficiencia123}")
except ZeroDivisionError:
    print("\nNo se puede dividir por cero.")

import funciones as misf
import matplotlib.pyplot as plt
import pandas as pd
#%%
"""
redefino esta funcion de funciones.py para que no tenga que tener una columna decaimientos
"""

def obtenerInfoDataframe(df):
    total_filas = len(df)
    cant_muones = df["id_muon"].max()
    print("\n" + "=" * 40)
    print("RESUMEN DE DATOS CARGADOS")
    print("=" * 40)
    print(f"Total de filas: {total_filas}")
    print("\nColumnas presentes y tipos:")
    print(df.dtypes)
    print(f"cantidad de muones detectados: {cant_muones}")
 #%%
"""
obtengo data de los parquets de pasos de muones
"""

plt.style.use('estiloGraficos.mplstyle')

df1 = misf.abrir_parquet("muones_cent1.parquet", motor ="pyarrow")
obtenerInfoDataframe(df1)

df2 = misf.abrir_parquet("muones_cent2.parquet", motor ="pyarrow")
obtenerInfoDataframe(df2)

df3 = misf.abrir_parquet("muones_cent3.parquet", motor ="pyarrow")
obtenerInfoDataframe(df3)

#%%
def calcularEficiencia1(dataframe: pd.DataFrame, 
                       umbral: float = -119.0,) -> float:
    
    eDobles, eTriples, eOtros = 0, 0, 0
    cantMuones = dataframe["id_muon"].unique()
    
    # veo si hay eventos dobles o triples
    for i in cantMuones:
        df_muon = dataframe[dataframe["id_muon"] == i]
        # detecta si hay algun valor de la columna dada que cumple ser menor al trigger
        deteccionCanal1 = df_muon["canal 1 [mV]"] < umbral
        deteccionCanal2 = df_muon["canal 2 [mV]"] < umbral
        deteccionCanal3 = df_muon["canal 3 [mV]"] < umbral
        if ( deteccionCanal1.any() and deteccionCanal2.any() and deteccionCanal3.any() ) :
            eTriples = eTriples + 1
            continue
        if ( deteccionCanal2.any()) and (deteccionCanal3.any() ) :
            eDobles = eDobles + 1
            continue
        else:
            eOtros = eOtros + 1
        
    # calculo eficiencia
    try:
        eficiencia = (eTriples)/(eDobles + eTriples)
        print(f"\nMuones totales: {len(cantMuones)}\nEventos dobles: {eDobles}\nEventos triples: {eTriples}\nOtros / Sin coincidencia C2+C3: {eOtros}\nEficiencia: {eficiencia}\nThreshold:{umbral} mV")
        return eficiencia
    except ZeroDivisionError:
        print("\nNo se puede dividir por cero.")
        return 0
    
def calcularEficiencia2(dataframe: pd.DataFrame, 
                       umbral: float = -105.0,) -> float:
    
    eDobles, eTriples, eOtros = 0, 0, 0
    cantMuones = dataframe["id_muon"].unique()
    
    # veo si hay eventos dobles o triples
    for i in cantMuones:
        df_muon = dataframe[dataframe["id_muon"] == i]
        # detecta si hay algun valor de la columna dada que cumple ser menor al trigger
        deteccionCanal1 = df_muon["canal 1 [mV]"] < umbral
        deteccionCanal2 = df_muon["canal 2 [mV]"] < umbral
        deteccionCanal3 = df_muon["canal 3 [mV]"] < umbral
        if ( deteccionCanal1.any() and deteccionCanal2.any() and deteccionCanal3.any() ) :
            eTriples = eTriples + 1
            continue
        if ( deteccionCanal1.any()) and (deteccionCanal3.any() ) :
            eDobles = eDobles + 1
            continue
        else:
            eOtros = eOtros + 1
        
    # calculo eficiencia
    try:
        eficiencia = (eTriples)/(eDobles + eTriples)
        print(f"\nMuones totales: {len(cantMuones)}\nEventos dobles: {eDobles}\nEventos triples: {eTriples}\nOtros / Sin coincidencia C1+C3: {eOtros}\nEficiencia: {eficiencia}\nThreshold:{umbral} mV")
        return eficiencia
    except ZeroDivisionError:
        print("\nNo se puede dividir por cero.")
        return 0
    
def calcularEficiencia3(dataframe: pd.DataFrame, 
                       umbral: float = -80.0,) -> float:
    
    eDobles, eTriples, eOtros = 0, 0, 0
    cantMuones = dataframe["id_muon"].unique()
    
    # veo si hay eventos dobles o triples
    for i in cantMuones:
        df_muon = dataframe[dataframe["id_muon"] == i]
        # detecta si hay algun valor de la columna dada que cumple ser menor al trigger
        deteccionCanal1 = df_muon["canal 1 [mV]"] < umbral
        deteccionCanal2 = df_muon["canal 2 [mV]"] < umbral
        deteccionCanal3 = df_muon["canal 3 [mV]"] < umbral
        if ( deteccionCanal1.any() and deteccionCanal2.any() and deteccionCanal3.any() ) :
            eTriples = eTriples + 1
            continue
        if ( deteccionCanal1.any()) and (deteccionCanal2.any() ) :
            eDobles = eDobles + 1
            continue
        else:
            eOtros = eOtros + 1
        
    # calculo eficiencia
    try:
        eficiencia = (eTriples)/(eDobles + eTriples)
        print(f"\nMuones totales: {len(cantMuones)}\nEventos dobles: {eDobles}\nEventos triples: {eTriples}\nOtros / Sin coincidencia C1+C2: {eOtros}\nEficiencia: {eficiencia}\nThreshold:{umbral} mV")
        return eficiencia
    except ZeroDivisionError:
        print("\nNo se puede dividir por cero.")
        return 0
#%%
print("=" * 40)
print("\nCentelleador 1:")
efi_orden1 = calcularEficiencia1(df1)
print("=" * 40)
print("\nCentelleador 2:")
efi_orden2 = calcularEficiencia2(df2)
print("=" * 40)
print("\nCentelleador 3:")
efi_orden3 = calcularEficiencia3(df3)
print("=" * 40)
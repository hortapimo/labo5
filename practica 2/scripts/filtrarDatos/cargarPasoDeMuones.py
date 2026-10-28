from pathlib import Path
import pandas as pd
import funciones as misf

#%%
carpeta_datos = Path("/home/juan_cruz/Documentos/Mi_git/labo5/practica 2/scripts/filtrarDatos/medicionEficienciaOrden123")
archivos_txt = list(carpeta_datos.glob("*.txt"))
    
nMuon = 1
lista_dataframes = []
    
nArchivos=len(archivos_txt)
i=1
for archivo in archivos_txt:
    print(f"Procesando {archivo.name}, archivo {i} de {nArchivos}")
    i+=1
    dataframes = misf.cargarArchivo(archivo) 
    if dataframes: #Verifica que la lista no este vacia
        for df in dataframes:         
            df_filtrado = df.copy()
            df_filtrado["id_muon"] = nMuon
            lista_dataframes.append(df_filtrado)
            nMuon += 1
                    
if lista_dataframes:
    df_total = pd.concat(lista_dataframes, ignore_index=True)
    ruta_salida = carpeta_datos / "muones_cent2.parquet"
    df_total.to_parquet(ruta_salida, index=False)
    print(f"Procesados {nMuon - 1} muones. Guardado en: {ruta_salida.name}")
else:
        print("No se encontraron trazas que cumplan con la condición de paso de un muon.")

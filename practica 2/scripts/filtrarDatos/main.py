from pathlib import Path
import pandas as pd
import funciones as misf


carpeta_datos = Path("Datos4/")
archivos_txt = list(carpeta_datos.glob("*.txt"))

n_decaimiento = 1
lista_dataframes = []

nArchivos=len(archivos_txt)
i=1
for archivo in archivos_txt:
    print(f"Procesando {archivo.name}, archivo {i} de {nArchivos}")
    i+=1
    dataframes = misf.cargarArchivo(archivo) 
    for df in dataframes:
        if misf.hay_decaimiento(df):
            # .copy() previene warnings de SettingWithCopyWarning de pandas
            df_filtrado = df.copy()
            df_filtrado["#decaimiento"] = n_decaimiento
            lista_dataframes.append(df_filtrado)
            n_decaimiento += 1

if lista_dataframes:
    df_total = pd.concat(lista_dataframes, ignore_index=True)
    ruta_salida = carpeta_datos / "decaimientos.parquet"
    df_total.to_parquet(ruta_salida, index=False)
    print(f"Procesados {n_decaimiento - 1} decaimientos. Guardado en: {ruta_salida.name}")
else:
    print("No se encontraron trazas que cumplan con la condición de decaimiento.")

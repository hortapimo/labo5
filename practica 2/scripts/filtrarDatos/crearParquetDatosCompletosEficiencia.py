import pandas as pd
from pathlib import Path

def cargarArchivo_robusto(archivo: Path | str, puntos_por_bloque: int = 1024) -> pd.DataFrame:
    columnas = ["tiempo [ns]", "canal 1 [mV]", "canal 2 [mV]", "canal 3 [mV]"]
    dataframes = []
    num_decaimiento = 1

    with open(archivo, "r", encoding="utf-8", errors="replace") as f:
        while True:
            linea = f.readline()
            if not linea:
                break
            if linea.startswith("Event #"):
                f.readline() # Saltar la línea de los nombres de las columnas
                
                df_bloque = pd.read_csv(
                    f,
                    nrows=puntos_por_bloque,
                    sep=r"\s+",
                    header=None,
                    names=columnas,
                    engine="python"
                )
                
                df_bloque["#decaimiento"] = num_decaimiento
                dataframes.append(df_bloque)
                num_decaimiento += 1

    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        return pd.DataFrame(columns=columnas + ["#decaimiento"])

def procesar_y_guardar_parquet(directorio_base: str | Path, nombre_salida: str = "todas_las_mediciones.parquet"):
    ruta_base = Path(directorio_base)
    dataframes_totales = []
    
    # Busca recursivamente todos los .txt en las carpetas de mediciones
    archivos_txt = list(ruta_base.rglob("medicionEficiencia*/*.txt"))
    
    print(f"Se encontraron {len(archivos_txt)} archivos .txt para procesar.")
    
    for archivo in archivos_txt:
        print(f"Procesando: {archivo.name}...")
        df_archivo = cargarArchivo_robusto(archivo)
        
        # Agregamos columnas de origen para mantener trazabilidad
        df_archivo['carpeta_origen'] = archivo.parent.name
        df_archivo['archivo_origen'] = archivo.name
        
        dataframes_totales.append(df_archivo)
        
    if dataframes_totales:
        df_final = pd.concat(dataframes_totales, ignore_index=True)
        print("\n¡Lectura de .txt terminada! Guardando en archivo Parquet...")
        
        # Guardar todo el DataFrame combinado en un único archivo parquet
        ruta_salida = ruta_base / nombre_salida
        df_final.to_parquet(ruta_salida, engine="pyarrow")
        
        print(f"✅ Datos guardados exitosamente en: {ruta_salida}")
        return df_final
    else:
        print("No se encontraron datos para procesar.")
        return pd.DataFrame()

# --- Cómo usarlo ---
# Configurá la ruta donde tenés tus scripts y carpetas de datos
ruta_directorio = "/home/juan_cruz/Documentos/Mi_git/labo5/practica 2/scripts/filtrarDatos/"

# Ejecutá la función por única vez para procesar los txt y generar el parquet
df_completo = procesar_y_guardar_parquet(ruta_directorio, "datos_completos_eficiencia.parquet")

# %%
df_jeje = df_completo.head(100)
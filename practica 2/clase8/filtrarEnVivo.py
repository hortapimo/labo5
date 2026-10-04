import os
import time
import glob
from pathlib import Path
import pandas as pd
import funciones as misF

# Definir variables globales faltantes
CARPETA_DATOS = ""  
CARPETA_SALIDA = ""
PATRON_ARCHIVO = os.path.join(CARPETA_DATOS, "*.txt") # Ajustar extensión según corresponda

def obtener_archivo_mas_reciente():
    archivos = glob.glob(PATRON_ARCHIVO)
    if not archivos:
        return None
    return max(archivos, key=os.path.getmtime)

def esperar_archivo_listo(ruta_archivo, tiempo_espera=3):
    tamano_actual = -1
    while True:
        if os.path.exists(ruta_archivo):
            nuevo_tamano = os.path.getsize(ruta_archivo)
            
            if nuevo_tamano == tamano_actual and nuevo_tamano > 0:
                print("El archivo está listo para ser procesado.")
                return True
            
            tamano_actual = nuevo_tamano
            
        time.sleep(tiempo_espera)

# --- Bucle Principal ---
ultimo_archivo_procesado = None
ultimo_mtime = 0
n_decaimiento = 1  # Inicializar el contador

print(f"Monitoreando carpeta: {CARPETA_DATOS}...")

while True:
    archivo_actual_str = obtener_archivo_mas_reciente()
    
    if archivo_actual_str:
        mtime_actual = os.path.getmtime(archivo_actual_str)
        
        if archivo_actual_str != ultimo_archivo_procesado or mtime_actual > ultimo_mtime:
            # Convertimos a objeto Path para extraer fácilmente el nombre
            archivo_path = Path(archivo_actual_str) 
            lista_dataframes = []
            
            esperar_archivo_listo(archivo_actual_str)
            
            try:
                dataframes = misF.cargarArchivo(archivo_actual_str)
                print(f"Procesando {archivo_path.name}")
                
                if dataframes: 
                    for df in dataframes:
                        if misF.hay_decaimiento(df): 
                            df_filtrado = df.copy()
                            df_filtrado["#decaimiento"] = n_decaimiento
                            lista_dataframes.append(df_filtrado)
                            n_decaimiento += 1
                            
                    if lista_dataframes:
                        df_total = pd.concat(lista_dataframes, ignore_index=True)
                        
                        nombre_salida = f"{archivo_path.stem}_filtrado.parquet"
                        ruta_salida = Path(CARPETA_SALIDA) / nombre_salida
                        
                        df_total.to_parquet(ruta_salida, index=False)
                        print(f"Procesados {n_decaimiento - 1} decaimientos. Guardado en: {ruta_salida.name}")
                    else:
                        print("No se encontraron trazas que cumplan con la condición de decaimiento.")
                
                # Borramos el archivo original una vez procesado
                archivo_path.unlink()
                print(f"Archivo original eliminado: {archivo_path.name}")
                        
            except Exception as e:
                print(f"Error procesando el archivo: {e}")
             # Actualizamos las banderas para no volver a procesar lo mismo
            ultimo_archivo_procesado = archivo_actual_str
            ultimo_mtime = mtime_actual  # Usamos la variable que ya habíamos leído antes   

    # Fundamental para no saturar el procesador
    time.sleep(1)
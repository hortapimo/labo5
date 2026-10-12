import pandas as pd
from pathlib import Path

def cargarArchivo_continuo(archivo: Path | str, id_inicial: int, puntos_por_bloque: int = 1024) -> tuple[pd.DataFrame, int]:
    columnas = ["tiempo [ns]", "canal 1 [mV]", "canal 2 [mV]", "canal 3 [mV]"]
    dataframes = []
    num_decaimiento = id_inicial

    with open(archivo, "r", encoding="utf-8", errors="replace") as f:
        while True:
            linea = f.readline()
            if not linea:
                break
            if linea.startswith("Event #"):
                f.readline() # Saltear nombres de columnas
                
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
                
                # Incrementamos el contador para el próximo evento
                num_decaimiento += 1

    if dataframes:
        return pd.concat(dataframes, ignore_index=True), num_decaimiento
    else:
        return pd.DataFrame(columns=columnas + ["#decaimiento"]), num_decaimiento

def procesar_carpeta_acumulativa(ruta_carpeta: str | Path, nombre_salida: str):
    ruta_base = Path(ruta_carpeta)
    dataframes_totales = []
    
    # Buscamos los .txt y los ordenamos para que la lectura sea secuencial
    archivos_txt = sorted(list(ruta_base.glob("*.txt")))
    
    print(f"Se encontraron {len(archivos_txt)} archivos .txt en {ruta_base.name}")
    
    # Arrancamos el contador global en 1
    id_actual = 1 
    
    for archivo in archivos_txt:
        print(f"Procesando: {archivo.name} | Arrancando en evento: {id_actual}")
        
        # La función nos devuelve el df del archivo y el ID actualizado para el siguiente
        df_archivo, id_actual = cargarArchivo_continuo(archivo, id_inicial=id_actual)
        
        dataframes_totales.append(df_archivo)
        
    if dataframes_totales:
        df_final = pd.concat(dataframes_totales, ignore_index=True)
        
        # Guardar en parquet
        ruta_salida = ruta_base / nombre_salida
        df_final.to_parquet(ruta_salida, engine="pyarrow")
        
        print(f"\n¡Listo! Datos guardados en: {ruta_salida}")
        print(f"Total de decaimientos únicos acumulados: {df_final['#decaimiento'].nunique()}")
    else:
        print("No se encontraron datos.")

# --- Ejecución ---
# Cambiá esta ruta a la carpeta exacta donde tenés los txt del centelleador 3
ruta_directorio = "/home/juan_cruz/Documentos/Mi_git/labo5/practica 2/scripts/filtrarDatos/medicionEficienciaOrden312"

procesar_carpeta_acumulativa(ruta_directorio, "decaimientosCentelleador1.parquet")
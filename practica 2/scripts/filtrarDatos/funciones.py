from pathlib import Path
import pandas as pd

def cargarArchivo(archivo: Path | str, puntos_por_bloque: int = 1024) -> pd.DataFrame:
    columnas = ["tiempo [ns]", "canal 1 [mV]", "canal 2 [mV]", "canal 3 [mV]"]
    dataframes = []

    # Se usa la variable 'archivo' que viene por parámetro
    with open(archivo, 'r', encoding='utf-8') as f:
        while True:
            linea = f.readline()
            
            if not linea:
                break
                
            if linea.startswith("Event"):
                df_bloque = pd.read_csv(
                    f,
                    nrows=puntos_por_bloque,
                    sep=r"\s+",
                    header=None,
                    names=columnas,
                    engine="python"
                )
                dataframes.append(df_bloque)
            
    # Validación de seguridad por si el archivo estaba vacío o no tenía eventos
    if dataframes:
        print(f"Se cargaron {len(dataframes)} bloques en total.")
        return dataframes
    else:
        print(f"No se encontró ningún 'Evento' en el archivo {archivo}.")
        # Retorna un DataFrame vacío con las columnas para evitar errores más adelante
        return pd.DataFrame(columns=columnas)


def hay_decaimiento(dataframe: pd.DataFrame, umbral = -90.0, umbralSup=100, tiempo_trigger =210.0, tiempo_minimo=50.0) -> bool:

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

    return bool((dif2 > tiempo_minimo).any() or (dif3 > tiempo_minimo).any() )

def abrir_parquet(ruta_archivo: Path | str, motor: str = "auto") -> pd.DataFrame:
    """
    Carga un archivo Parquet. 
    Permite especificar el motor ('pyarrow', 'fastparquet' o 'auto').
    """
    ruta = Path(ruta_archivo)
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta.resolve()}")

    try:
        # Intenta primero con el motor por defecto o el especificado
        df = pd.read_parquet(ruta, engine=motor)
    except Exception as e:
        # Fallback a fastparquet si pyarrow falla por conflictos de versión
        if motor == "auto":
            print(f"Aviso: Falló el motor principal ({e}). Intentando con fastparquet...")
            df = pd.read_parquet(ruta, engine="fastparquet")
        else:
            raise e

    return df

def obtenerInfoDataframe(df):
    total_filas = len(df)
    decaimientos_unicos = df["#decaimiento"].nunique()
    print("\n" + "=" * 40)
    print("RESUMEN DE DATOS CARGADOS")
    print("=" * 40)
    print(f"Total de filas: {total_filas}")
    print(f"Total de eventos de decaimiento: {decaimientos_unicos}")
    print("\nColumnas presentes y tipos:")
    print(df.dtypes)
from pathlib import Path
import pandas as pd

def cargarArchivo(archivo: Path | str, num_bloques: int = 81, puntos_por_bloque: int = 1024) -> list[pd.DataFrame]:
    columnas = ["tiempo [ns]", "canal 1 [mV]", "canal 2 [mV]", "canal 3 [mV]"]
    dataframes = []

    with open(archivo, "r", encoding="utf-8", errors="replace") as f:
        # Saltear el header global inicial (primeras 4 líneas)
        for _ in range(4):
            f.readline()

        for i in range(num_bloques):
            df_bloque = pd.read_csv(
                f,
                nrows=puntos_por_bloque,
                sep=r"\s+",
                header=None,
                names=columnas,
                engine="python"
            )
            dataframes.append(df_bloque)

            # Consumir la línea en blanco y los 2 headers entre bloques
            if i < num_bloques - 1:
                for _ in range(3):
                    f.readline()

    return dataframes


def hay_decaimiento(dataframe: pd.DataFrame) -> bool:
    umbral = -90.0
    tiempo_trigger = 220.0
    tiempo_minimo = 50.0

    mascara = dataframe["canal 3 [mV]"] < umbral

    if not mascara.any():
        return False

    tiempos_evento = dataframe.loc[mascara, "tiempo [ns]"]
    dif = tiempos_evento - tiempo_trigger

    return bool((dif > tiempo_minimo).any())

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
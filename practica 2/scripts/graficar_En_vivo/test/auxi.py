import pandas as pd

def cargarArchivo(archivo, num_bloques=81, puntos_por_bloque=1024):
    columnas = ["tiempo [ns]", "canal 1 [mV]", "canal 2 [mV]", "canal 3 [mV]"]
    dataframes = []  # Lista local en memoria RAM

    with open(archivo, "r") as f:
        # Saltear el header global inicial (primeras 4 líneas)
        for _ in range(4):
            f.readline()

        for i in range(num_bloques):
            df_bloque = pd.read_csv(
                f,
                nrows=puntos_por_bloque,
                sep=r'\s+',
                header=None,
                names=columnas,
                engine='python'
            )
            dataframes.append(df_bloque)

            # Consumir la línea en blanco y los 2 headers entre bloques
            if i < num_bloques - 1:
                for _ in range(3):
                    f.readline()

    # Retornamos la lista de DataFrames vivos en RAM
    return dataframes

cargarArchivo("run_20260911_131544_idx0_selected.txt")
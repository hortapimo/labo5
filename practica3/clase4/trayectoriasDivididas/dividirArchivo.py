import os
import numpy as np
import pandas as pd


def dividir_csv_por_filas(
    archivo_entrada: str,
    n_partes: int = None,
    tamano_bloque: int = None,
    carpeta_salida: str = "tramos_csv",
    separador: str = ",",
    reajustar_origen: bool = False,
):
  """Divide un archivo CSV con múltiples columnas en sub-archivos CSV cortando

  las filas en intervalos de longitud N/n.

  Parámetros:
  -----------
  archivo_entrada : str
      Ruta al archivo original (.csv).
  n_partes : int, opcional
      Cantidad de partes (n) en las que se divide el total N de filas.
      El tamaño del intervalo será L = ceil(N / n).
  tamano_bloque : int, opcional
      Tamaño exacto del bloque de filas (L).
  carpeta_salida : str
      Directorio donde se guardarán los archivos resultantes.
  separador : str
      Delimitador del archivo CSV (por defecto ',' o ';' si viene de Excel en
      español).
  reajustar_origen : bool
      Si es True, resta a cada columna numérica su valor inicial en el bloque.
  """
  print(f"Cargando archivo CSV: {archivo_entrada}...")
  df = pd.read_csv(archivo_entrada, sep=separador)

  N = len(df)
  columnas = list(df.columns)
  print(f"Total de filas (N): {N}")
  print(f"Columnas detectadas ({len(columnas)}): {columnas}")

  # Determinar longitud de corte L = N / n
  if n_partes is not None:
    L = int(np.ceil(N / n_partes))
    print(
        f"División en n = {n_partes} partes -> Longitud del intervalo: L = {L}"
        " filas."
    )
  elif tamano_bloque is not None:
    L = int(tamano_bloque)
    n_partes = int(np.ceil(N / L))
    print(
        f"Intervalo fijado en L = {L} filas -> Total de partes resultantes:"
        f" {n_partes}."
    )
  else:
    raise ValueError("Debes especificar 'n_partes' o 'tamano_bloque'.")

  os.makedirs(carpeta_salida, exist_ok=True)
  nombre_base = os.path.splitext(os.path.basename(archivo_entrada))[0]

  archivos_generados = []

  for i in range(0, N, L):
    num_bloque = (i // L) + 1
    df_bloque = df.iloc[i : i + L].copy()

    # Si querés que cada sub-trayectoria empiece en el origen (0, 0)
    if reajustar_origen:
      cols_num = df_bloque.select_dtypes(include=[np.number]).columns
      df_bloque[cols_num] = df_bloque[cols_num] - df_bloque[cols_num].iloc[0]

    df_bloque.reset_index(drop=True, inplace=True)

    nombre_salida = f"{nombre_base}_parte_{num_bloque:03d}.csv"
    ruta_salida = os.path.join(carpeta_salida, nombre_salida)
    df_bloque.to_csv(ruta_salida, index=False, sep=separador)

    archivos_generados.append(ruta_salida)
    print(
        f"  [+] Generado: {nombre_salida} (filas {i} a"
        f" {min(i + L, N) - 1} | {len(df_bloque)} filas)"
    )

  print(
      f"\nProceso finalizado: se crearon {len(archivos_generados)} archivos en"
      f" '{carpeta_salida}/'."
  )
  return archivos_generados


# --- EJEMPLO DE USO ---
if __name__ == "__main__":
  # Modificá la ruta al archivo con tus datos:
  ARCHIVO_CSV = "trayectoria_particula9_video_sinLserGod1_1.avi.csv"

  dividir_csv_por_filas(
      archivo_entrada=ARCHIVO_CSV,
      n_partes=7,  # Divide en n=12 partes de longitud L = N / 12
      carpeta_salida="sub_trayectorias_7_archivo9",
      separador=",",  # Si tu CSV usa punto y coma como separador, cambialo a ';'
      reajustar_origen=False,  # Cambiá a True si querés restar (x0, y0) al inicio de cada tramo
  )
import numpy as np
from pathlib import Path
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

# %%

def tuki(archivo: Path):
    data = np.genfromtxt(archivo, skip_header=53, skip_footer=1, usecols=(0,1), delimiter=',')
    return data.T

def analizar_espectro(archivo_csv):
  l0, a0 = tuki(archivo_csv)
  l0 = np.array(l0)
  a0 = np.array(a0)

  peaks, _ = find_peaks(a0, prominence = 0.1)

  #amplitudes_picos = a0[peaks]
  #longitudes_picos = l0[peaks]

  # seleccionamos estrictamente el primer pico
  idx_pico = peaks[0]
  longitud_pico = l0[idx_pico]
  amplitud_pico = a0[idx_pico]

  # cálculo de incerteza

  dist_izq = abs(l0[idx_pico] - l0[idx_pico - 1])
  dist_der = abs(l0[idx_pico + 1] - l0[idx_pico])

  # menor distancia dividida por 2
  incerteza = min(dist_izq, dist_der) / 2.0

  print(f"Primer pico en: {longitud_pico:.2f} nm")
  print(f"Incerteza calculada: \u00b1{incerteza:.4f} nm")

  #

  # cálculo del ancho de banda

  mitad_intensidad = amplitud_pico / 2.0

  # Búsqueda hacia la izquierda
  idx_izq = idx_pico
  while idx_izq > 0 and a0[idx_izq] > mitad_intensidad:
      idx_izq -= 1

  # Búsqueda hacia la derecha
  idx_der = idx_pico
  while idx_der < len(a0) - 1 and a0[idx_der] > mitad_intensidad:
      idx_der += 1

  lambda_izq = l0[idx_izq]
  lambda_der = l0[idx_der]

  # Resta para el ancho de banda
  ancho_banda = lambda_der - lambda_izq

  print(f"Ancho de banda calculado: {ancho_banda:.2f} nm")

  # gráfico

  plt.rc("font", size=16)
  plt.figure(figsize=(10,6))

  # Ploteamos los datos base SIN label para que no ensucie la leyenda
  plt.errorbar(l0, a0, fmt=".", alpha=0.7, lw=3)

  # 1er Elemento de la leyenda: Las cruces de todos los picos detectados
  plt.plot(l0[peaks], a0[peaks], "rx", markersize=12, markeredgewidth=2, label="Picos de intensidad")

  # 2do Elemento de la leyenda: Los datos calculados
  # Armamos un texto con los dos valores para ponerlo en el label
  label_calculos = r"$\lambda$ = (" f"{longitud_pico:.1f} \u00b1 {incerteza:.1f}) nm \nAncho de Banda = {ancho_banda:.1f} nm"

  # Dibujamos la línea del ancho de banda y le asignamos el texto de los cálculos como label
  plt.hlines(y=mitad_intensidad, xmin=lambda_izq, xmax=lambda_der, color="green", linestyle="--", linewidth=2, label=label_calculos)

  # (Opcional) Marcamos los puntitos de corte en verde para que quede más visual
  plt.plot([lambda_izq, lambda_der], [a0[idx_izq], a0[idx_der]], "go")

  plt.ylabel("Amplitud [u.a.]")
  plt.xlabel(r"$\lambda$ [nm]")
  plt.xticks(fontsize=12)
  plt.yticks(fontsize=12)
  plt.xlim((420,730))

  # Mostramos la leyenda. Ajustá el fontsize si el texto queda muy grande
  plt.legend(fontsize=12, loc="upper right")
  plt.grid(which="major")
  plt.minorticks_on()
  plt.grid(which="minor", alpha=0.3)
  plt.show()


# %%
archivos = ["420nm3seg.csv", "430nm1500ms.csv", "450nm100ms.csv"]

for archivo in archivos:
    analizar_espectro(archivo)
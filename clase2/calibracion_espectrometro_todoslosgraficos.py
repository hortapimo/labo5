import numpy as np
from pathlib import Path
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import re 

# --- Cargar estilo de gráficos ---
#ruta_estilo = Path("/home/juan_cruz/Documentos/Mi_git/labo5/practica 1 - dia 1/estiloGraficos.mplstyle")
#plt.style.use(ruta_estilo)
# ---------------------------------    

plt.style.use('./estiloGraficos.mplstyle')
# %%

def tuki(archivo: Path):
    data = np.genfromtxt(archivo, skip_header=53, skip_footer=1, usecols=(0,1), delimiter=',')
    return data.T
    
def analizar_espectro(archivo_csv, carpeta_destino):
    l0, a0 = tuki(archivo_csv)
    l0 = np.array(l0)
    a0 = np.array(a0)
    
    # --- Extracción de la longitud de onda pedida ---
    coincidencia = re.match(r'^(\d+)', archivo_csv.name)
    if coincidencia:
        lambda_pedido = float(coincidencia.group(1))
    else:
        print(f"No se pudo extraer el lambda pedido de: {archivo_csv.name}")
        lambda_pedido = np.nan
  
    peaks, _ = find_peaks(a0, prominence = 0.1)

    # Obtenemos las amplitudes de todos los picos detectados
    amplitudes_picos = a0[peaks]

    # Buscamos qué pico tiene el valor máximo
    indice_maximo = np.argmax(amplitudes_picos)

    # Seleccionamos el índice correspondiente a ese pico máximo
    idx_pico = peaks[indice_maximo]
    
    longitud_pico = l0[idx_pico]
    amplitud_pico = a0[idx_pico]
    
    # Cálculo de incerteza
    dist_izq = abs(l0[idx_pico] - l0[idx_pico - 1])
    dist_der = abs(l0[idx_pico + 1] - l0[idx_pico])
    incerteza = min(dist_izq, dist_der) / 2.0
    
    # Cálculo del offset
    offset = longitud_pico - lambda_pedido

    print(f"Pico máximo en: {longitud_pico:.2f} nm")
    print(f"Incerteza calculada: \u00b1{incerteza:.4f} nm")
    print(f"Offset (Medido - Pedido): {offset:.2f} nm")

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
    ancho_banda = lambda_der - lambda_izq

    print(f"Ancho de banda calculado: {ancho_banda:.2f} nm")

    # --- Gráfico ---
    plt.figure(figsize=(10,6))

    # Ploteamos los datos base
    plt.errorbar(l0, a0, fmt=".", alpha=0.7, lw=3)

    # Cruz SOLAMENTE en el pico de mayor intensidad
    plt.plot(longitud_pico, amplitud_pico, "rx", markersize=12, markeredgewidth=2, label="Pico máximo")

    # Armamos un texto con TODOS los valores para ponerlo en el label (incluyendo el offset)
    label_calculos = (r"$\lambda_{medido}$ = " f"({longitud_pico:.1f} \u00b1 {incerteza:.1f}) nm\n"
                      f"Offset = {offset:.1f} nm\n"
                      f"Ancho de Banda = {ancho_banda:.1f} nm")

    # Línea del ancho de banda
    plt.hlines(y=mitad_intensidad, xmin=lambda_izq, xmax=lambda_der, color="green", linestyle="--", linewidth=2, label=label_calculos)
    plt.plot([lambda_izq, lambda_der], [a0[idx_izq], a0[idx_der]], "go")
    
    # --- Línea vertical para el Lambda pedido ---
    if not np.isnan(lambda_pedido):
        plt.axvline(x=lambda_pedido, color="orange", linestyle="-.", linewidth=2, label=r"$\lambda_{pedido}$ = " f"{lambda_pedido:.1f} nm")

    plt.ylabel("Amplitud [u.a.]")
    plt.xlabel(r"$\lambda$ [nm]")
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlim((420,730))

    plt.legend(fontsize=12, loc="best")
    plt.grid(which="major")
    plt.minorticks_on()
    plt.grid(which="minor", alpha=0.3)
    plt.tight_layout()
    
    # Guardado automático
    nombre_salida = carpeta_destino / f"espectro_{archivo_csv.stem}.png"
    plt.savefig(nombre_salida, dpi=300, bbox_inches="tight")
    plt.close()

# %%
carpeta_mediciones = Path("/home/juan_cruz/Documentos/Mi_git/labo5/clase2")
carpeta_destino = Path("/home/juan_cruz/Documentos/Mi_git/labo5/clase2")

archivos = sorted(carpeta_mediciones.glob("*.csv"))

if not archivos:
    print("No se encontraron archivos .csv en la carpeta.")

for archivo in archivos:
    print(f"\n--- Procesando: {archivo.name} ---")
    analizar_espectro(archivo, carpeta_destino)
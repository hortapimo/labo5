import numpy as np
from pathlib import Path
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import re

# --- Cargar estilo de gráficos ---
#ruta_estilo = Path("/home/juan_cruz/Documentos/Mi_git/labo5/practica 1 - dia 1/estiloGraficos.mplstyle")
#plt.style.use(ruta_estilo)
plt.style.use('./estiloGraficos.mplstyle')
# ---------------------------------  
# %%

def tuki(archivo: Path):
    data = np.genfromtxt(archivo, skip_header=53, skip_footer=1, usecols=(0,1), delimiter=',')
    return data.T
    
def analizar_espectro(archivo_csv):
    l0, a0 = tuki(archivo_csv)
    l0 = np.array(l0)
    a0 = np.array(a0)

    peaks, _ = find_peaks(a0, prominence=0.1)
    

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

    # Cálculo del ancho de banda
    mitad_intensidad = amplitud_pico / 2.0
    
    idx_izq = idx_pico
    while idx_izq > 0 and a0[idx_izq] > mitad_intensidad:
        idx_izq -= 1
        
    idx_der = idx_pico
    while idx_der < len(a0) - 1 and a0[idx_der] > mitad_intensidad:
        idx_der += 1
        
    lambda_izq = l0[idx_izq]
    lambda_der = l0[idx_der]
    ancho_banda = lambda_der - lambda_izq

    return longitud_pico, incerteza, ancho_banda

# %%

carpeta_mediciones = Path("/home/juan_cruz/Documentos/Mi_git/labo5/clase2")
# carpeta_mediciones = Path("F:/Juan/UBA/Materias/Física/Laboratorio 5/GitHub/labo5/clase2")
archivos = sorted(carpeta_mediciones.glob("*.csv"))

if not archivos:
    print("No se encontraron archivos .csv en la carpeta.")

lambdas_pedidos = []
offsets = []
incertezas_offsets = []
anchos_de_banda = [] # Lista para el segundo gráfico
lambdas_hallados = []

for archivo in archivos:
    coincidencia = re.match(r'^(\d+)', archivo.name)
    
    if coincidencia:
        lambda_pedido = float(coincidencia.group(1))
        
        # Recibimos los 3 parámetros de la función
        longitud_pico, incerteza, ancho_banda = analizar_espectro(archivo)
        
        offset = longitud_pico - lambda_pedido
        
        lambdas_pedidos.append(lambda_pedido)
        offsets.append(offset)
        incertezas_offsets.append(incerteza)
        anchos_de_banda.append(ancho_banda)
        lambdas_hallados.append(longitud_pico)
        
        print(f"Pedido: {lambda_pedido} nm | Offset: {offset:.2f} nm | Ancho de banda: {ancho_banda:.2f} nm")
lambdas_hallados = np.array(lambdas_hallados)
anchos_de_banda = np.array(anchos_de_banda)
print(lambdas_hallados)
print(anchos_de_banda)
# %% 1. Gráfico de Offset

carpeta_destino = Path("/home/juan_cruz/Documentos/Mi_git/labo5/clase2")

plt.figure(figsize=(10,6))
plt.errorbar(lambdas_pedidos, offsets, yerr=incertezas_offsets, fmt="o", color="blue", 
             markersize=8, capsize=5, label="Offset instrumental", lw=2)
plt.axhline(0, color='red', linestyle='--', alpha=0.6, label="Offset nulo (Ideal)")
plt.xlabel(r"$\lambda_{pedido}$ [nm]")
plt.ylabel(r"Offset ($\lambda_{medido} - \lambda_{pedido}$) [nm]")
plt.legend(loc="best")
plt.grid(which="major", alpha=0.8)
plt.grid(which="minor", alpha=0.3)
plt.minorticks_on()
plt.tight_layout()
plt.savefig(carpeta_destino / "grafico_offset.png", dpi=300, bbox_inches="tight")
plt.show()

# %% 2. Gráfico de Ancho de Banda
plt.figure(figsize=(10,6))
plt.plot(lambdas_pedidos, anchos_de_banda, "o-", color="purple", markersize=8, lw=2, label="Ancho de banda")
plt.xlabel(r"$\lambda_{pedido}$ [nm]")
plt.ylabel("Ancho de banda [nm]")
plt.legend(loc="best")
plt.grid(which="major", alpha=0.8)
plt.grid(which="minor", alpha=0.3)
plt.minorticks_on()
plt.tight_layout()
plt.savefig(carpeta_destino / "grafico_ancho_banda.png", dpi=300, bbox_inches="tight")
plt.show()

# (Interesante: el parámetro dpi=300 asegura que los gráficos se guarden con excelente resolución, 
# ideal para cuando tengas que armar el póster o informe del experimento, y bbox_inches="tight"
# evita que se corten los bordes).
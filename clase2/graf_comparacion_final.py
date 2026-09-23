import numpy as np
import re
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from pathlib import Path

# --- Cargar estilo de gráficos ---
plt.style.use('/home/juan_cruz/Documentos/Mi_git/labo5/clase2/estiloGraficos.mplstyle')
# ---------------------------------  

def tuki(archivo: Path):
    data = np.genfromtxt(archivo, skip_header=53, skip_footer=1, usecols=(0,1), delimiter=',')
    return data.T
    
def analizar_espectro(archivo_csv):
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
  
    peaks, _ = find_peaks(a0, prominence=0.1)

    # Obtenemos las amplitudes y el pico máximo
    amplitudes_picos = a0[peaks]
    indice_maximo = np.argmax(amplitudes_picos)
    idx_pico = peaks[indice_maximo]
    
    longitud_pico = l0[idx_pico]
    amplitud_pico = a0[idx_pico]
    
    # Cálculo de incerteza
    dist_izq = abs(l0[idx_pico] - l0[idx_pico - 1])
    dist_der = abs(l0[idx_pico + 1] - l0[idx_pico])
    incerteza = min(dist_izq, dist_der) / 2.0
    
    # Cálculo del offset
    offset = longitud_pico - lambda_pedido

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

    # Retornamos un diccionario con todo lo necesario tanto para los cálculos globales como para el plot individual
    return {
        'nombre': archivo_csv.stem,
        'l0': l0,
        'a0': a0,
        'lambda_pedido': lambda_pedido,
        'longitud_pico': longitud_pico,
        'amplitud_pico': amplitud_pico,
        'ancho_banda': ancho_banda,
        'offset': offset,
        'incerteza': incerteza,
        'lambda_izq': lambda_izq,
        'lambda_der': lambda_der,
        'idx_izq': idx_izq,
        'idx_der': idx_der,
        'mitad_intensidad': mitad_intensidad
    }

# %% PROCESAMIENTO DE ARCHIVOS

carpeta_mediciones = Path("/home/juan_cruz/Documentos/Mi_git/labo5/clase2")
carpeta_destino = carpeta_mediciones
archivos = sorted(carpeta_mediciones.glob("*.csv"))

if not archivos:
    print("No se encontraron archivos .csv en la carpeta.")

# Lista para guardar los resultados de todos los espectros
resultados_completos = []

lambdas_pedidos = []
offsets = []
anchos_de_banda = []

for archivo in archivos:
    print(f"--- Procesando: {archivo.name} ---")
    datos = analizar_espectro(archivo)
    resultados_completos.append(datos)
    
    # Llenamos las listas para el gráfico global
    if not np.isnan(datos['lambda_pedido']):
        lambdas_pedidos.append(datos['lambda_pedido'])
        offsets.append(datos['offset'])
        anchos_de_banda.append(datos['ancho_banda'])
        
        print(f"Pedido: {datos['lambda_pedido']} nm | Offset: {datos['offset']:.2f} nm | Ancho de banda: {datos['ancho_banda']:.2f} nm")

lambdas_pedidos = np.array(lambdas_pedidos)
offsets = np.array(offsets)
anchos_de_banda = np.array(anchos_de_banda)

# %% GRÁFICO COMBINADO (1 FILA, 2 COLUMNAS)

# Ajustar tamaño general para que entren los dos subplots cómodamente
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# ---------------------------------------------------------
# AX1: ESPECTRO INDIVIDUAL (Izquierda)
# Elegimos un espectro de ejemplo para mostrar. El índice 0 es el primer archivo.
# Podés cambiar este índice si preferís que el panel izquierdo muestre otro archivo.
indice_ejemplo = 8 
ej = resultados_completos[indice_ejemplo]

ax1.errorbar(ej['l0'], ej['a0'], fmt=".", alpha=0.7, lw=3)

label_grande = r"$\lambda_{medido}$ = " f"({ej['longitud_pico']:.0f} \u00b1 {30}) nm"
ax1.axvline(x=ej['longitud_pico'], color="red", linestyle="--", linewidth=2, label=label_grande)
    
if not np.isnan(ej['lambda_pedido']):
    ax1.axvline(x=ej['lambda_pedido'], color="orange", linestyle="-.", linewidth=2, label=r"$\lambda_{nominal}$ = " f"{ej['lambda_pedido']:.0f} nm")

ax1.hlines(y=ej['mitad_intensidad'], xmin=ej['lambda_izq'], xmax=ej['lambda_der'], color="green", linestyle="--", linewidth=2, label="Ancho de banda (incerteza)")
ax1.plot([ej['lambda_izq'], ej['lambda_der']], [ej['a0'][ej['idx_izq']], ej['a0'][ej['idx_der']]], "go")    

ax1.set_ylabel("Amplitud [u.a.]")
ax1.set_xlabel(r"$\lambda$ [nm]")
ax1.tick_params(axis='both', which='major', labelsize=18)
ax1.set_xlim((420, 730))
# ax1.set_title(f"Espectro de muestra: {ej['nombre']}", fontsize=18)
ax1.legend(fontsize=18, loc="best")
ax1.grid(which="major")
ax1.minorticks_on()
ax1.grid(which="minor", alpha=0.3)


# ---------------------------------------------------------
# AX2: GRÁFICO DE OFFSETS Y ERRORES (Derecha)

ax2.errorbar(lambdas_pedidos, offsets, yerr=anchos_de_banda, fmt="o", color="blue", 
             markersize=8, capsize=5, label="Desplazamiento instrumental", lw=2)
ax2.axhline(0, color='red', linestyle='--', alpha=0.6, label="Desplazamiento nulo (Ideal)")

ax2.set_xlabel(r"$\lambda_{nominal}$ [nm]", fontsize=18)
ax2.set_ylabel(r"Desplazamiento ($\lambda_{medido} - \lambda_{nominal}$) [nm]", fontsize=18)
# ax2.set_title("Corrimientos y error para todas las mediciones", fontsize=18)
ax2.tick_params(axis='both', which='major', labelsize=18)
ax2.legend(loc="best", fontsize=16)
ax2.grid(which="major", alpha=0.8)
ax2.minorticks_on()
ax2.grid(which="minor", alpha=0.3)

# ---------------------------------------------------------
# Ajustes finales y guardado
plt.tight_layout()
plt.savefig(carpeta_destino / "analisis_completo_espectrometro.png", dpi=300, bbox_inches="tight")
plt.show()
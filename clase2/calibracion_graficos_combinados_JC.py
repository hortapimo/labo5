import numpy as np
import re
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from pathlib import Path

# --- Cargar estilo de gráficos (descomentar si lo usas) ---
# plt.style.use('./Documentos/Mi_git/labo5/clase2/estiloGraficos.mplstyle')

def tuki(archivo: Path):
    data = np.genfromtxt(archivo, skip_header=53, skip_footer=1, usecols=(0,1), delimiter=',')
    return data.T

carpeta_mediciones = Path("/home/juan_cruz/Documentos/Mi_git/labo5/clase2")
carpeta_destino = Path("/home/juan_cruz/Documentos/Mi_git/labo5/clase2")

archivos = sorted(carpeta_mediciones.glob("*.csv"))

if not archivos:
    print("No se encontraron archivos .csv en la carpeta.")

# --- PASO 1: Procesar todos los archivos y guardar los datos ---
resultados = []
lambdas_pedidos = []
offsets = []
incertezas_offsets = []

for archivo in archivos:
    l0, a0 = tuki(archivo)
    l0 = np.array(l0)
    a0 = np.array(a0)
    
    coincidencia = re.match(r'^(\d+)', archivo.name)
    if coincidencia:
        lambda_pedido = float(coincidencia.group(1))
    else:
        lambda_pedido = np.nan

    peaks, _ = find_peaks(a0, prominence=0.1)
    amplitudes_picos = a0[peaks]
    indice_maximo = np.argmax(amplitudes_picos)
    idx_pico = peaks[indice_maximo]
    
    longitud_pico = l0[idx_pico]
    amplitud_pico = a0[idx_pico]
    
    dist_izq = abs(l0[idx_pico] - l0[idx_pico - 1])
    dist_der = abs(l0[idx_pico + 1] - l0[idx_pico])
    incerteza = min(dist_izq, dist_der) / 2.0
    offset = longitud_pico - lambda_pedido

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
    
    # IMPORTANTE: Guardamos también las variables necesarias para el ancho de banda
    resultados.append({
        'archivo': archivo,
        'l0': l0, 'a0': a0,
        'lambda_pedido': lambda_pedido,
        'longitud_pico': longitud_pico,
        'amplitud_pico': amplitud_pico,
        'offset': offset,
        'incerteza': incerteza,
        'ancho_banda': ancho_banda,
        'mitad_intensidad': mitad_intensidad,
        'lambda_izq': lambda_izq,
        'lambda_der': lambda_der,
        'idx_izq': idx_izq,
        'idx_der': idx_der
    })
    
    if not np.isnan(lambda_pedido):
        lambdas_pedidos.append(lambda_pedido)
        offsets.append(offset)
        incertezas_offsets.append(incerteza)

# --- PASO 2: Generar un gráfico combinado por cada archivo CSV ---
for res in resultados:
    archivo = res['archivo']
    print(f"Generando gráfico para: {archivo.name} ...")
    
    # Tamaño total 12x6 para que cada subplot sea de 6x6
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # ==========================================
    # SUBPLOT 1 (IZQUIERDA): Espectro Individual
    # ==========================================
    ax1.errorbar(res['l0'], res['a0'], fmt=".", alpha=0.7, lw=3)
    
    label_grande = r"$\lambda_{medido}$ = " f"({res['longitud_pico']:.2f} \u00b1 {res['ancho_banda']:.2f}) nm"
    ax1.axvline(x=res['longitud_pico'], color="red", linestyle="--", linewidth=2, label=label_grande)
    
    if not np.isnan(res['lambda_pedido']):
        ax1.axvline(x=res['lambda_pedido'], color="orange", linestyle="-.", linewidth=2, label=r"$\lambda_{pedido}$ = " f"{res['lambda_pedido']:.2f} nm")
                      
    # LÍNEA DEL ANCHO DE BANDA CORREGIDA (usando los datos de res[])
    ax1.hlines(y=res['mitad_intensidad'], xmin=res['lambda_izq'], xmax=res['lambda_der'], 
               color="green", linestyle="--", linewidth=2, label="Ancho de banda (incerteza)")
    ax1.plot([res['lambda_izq'], res['lambda_der']], 
             [res['a0'][res['idx_izq']], res['a0'][res['idx_der']]], "go")   

    # Aumento de labelsize y fontsize
    ax1.set_ylabel("Amplitud [u.a.]", fontsize=14)
    ax1.set_xlabel(r"$\lambda$ [nm]", fontsize=14)
    ax1.set_xlim((420,730))
    ax1.set_title(f"Espectro: {archivo.stem}", fontsize=16)
    ax1.tick_params(axis='both', which='major', labelsize=12)
    ax1.legend(loc="best", fontsize=12)
    ax1.grid(which="major")
    ax1.minorticks_on()
    ax1.grid(which="minor", alpha=0.3)

    # ==========================================
    # SUBPLOT 2 (DERECHA): Gráfico de Offset Global
    # ==========================================
    ax2.errorbar(lambdas_pedidos, offsets, yerr=incertezas_offsets, fmt="o", color="blue", 
                 markersize=8, capsize=5, label="Desplazamiento", lw=2)
    ax2.axhline(0, color='red', linestyle='--', alpha=0.6, label="Ideal")

    if not np.isnan(res['lambda_pedido']):
        ax2.plot(res['lambda_pedido'], res['offset'], 'ro', markersize=12, markerfacecolor='none', 
                 markeredgewidth=2, label='Medición actual')
    
    # Aumento de labelsize y fontsize
    ax2.set_xlabel(r"$\lambda_{pedido}$ [nm]", fontsize=14)
    ax2.set_ylabel(r"Desplazamiento ($\lambda_{med} - \lambda_{ped}$) [nm]", fontsize=14)
    ax2.set_title("Desplazamiento vs. $\lambda$ Pedido", fontsize=16)
    ax2.tick_params(axis='both', which='major', labelsize=12)
    ax2.legend(loc="best", fontsize=12)
    ax2.grid(which="major", alpha=0.8)
    ax2.minorticks_on()
    ax2.grid(which="minor", alpha=0.3)

    plt.tight_layout()
    nombre_salida = carpeta_destino / f"combinado_{archivo.stem}.png"
    plt.savefig(nombre_salida, dpi=300, bbox_inches="tight")
    plt.close()
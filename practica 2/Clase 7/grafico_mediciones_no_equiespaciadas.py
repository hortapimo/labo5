from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('estiloGraficos.mplstyle')

def cargarArchivo(archivo: Path | str) -> list[pd.DataFrame]:
    columnas = ["tiempo [ns]", "canal 1 [mV]", "canal 2 [mV]", "canal 3 [mV]"]
    dataframes = []
    datos_evento = []

    with open(archivo, "r", encoding="utf-8", errors="replace") as f:
        for linea in f:
            linea = linea.strip()

            # Omitir líneas vacías, comentarios iniciales o la fila de nombres de columnas
            if not linea or linea.startswith('#') or linea.startswith('t[ns]'):
                continue

            # Cada vez que aparece un nuevo evento, guardamos el bloque anterior
            if linea.startswith('Event'):
                if datos_evento:
                    # Convertir la lista de listas en un DataFrame
                    df = pd.DataFrame(datos_evento, columns=columnas)
                    dataframes.append(df)
                    datos_evento = []  # Reiniciar para el nuevo bloque
                continue

            # Procesar las líneas de datos numéricos
            try:
                valores = [float(x) for x in linea.split()]
                if len(valores) == 4:
                    datos_evento.append(valores)
            except ValueError:
                continue

        # Agregar el último DataFrame que quedó cargado al terminar el iterador
        if datos_evento:
            df = pd.DataFrame(datos_evento, columns=columnas)
            dataframes.append(df)

    return dataframes

# --- Resto de tu script de ejecución y ploteo ---

archivo7 = "run_20260925_132914_idx0_selected.txt"
archivo8 = "run_20260925_134117_idx0_selected.txt"
archivo9 = "run_20260925_134941_idx0_selected.txt"
dataframes = cargarArchivo(archivo9) 
num = 1

# Verificar que el índice exista antes de plotear
if num < len(dataframes):
    df = dataframes[num]

    # 3. Crear y configurar la figura
    fig, ax = plt.subplots(figsize=(9, 6))
    plt.title(label=f"Data Frame = {num}")
    
    # Graficar (heredando el tamaño de marcador y grosor del .mplstyle)
    ax.plot(df["tiempo [ns]"], df["canal 1 [mV]"], marker='o', markersize=2, linestyle='', color='#377eb8', label='Canal 1 (u1)')
    ax.plot(df["tiempo [ns]"], df["canal 2 [mV]"], marker='o', markersize=2, linestyle='', color='#e41a1c', label='Canal 2 (u2)')
    ax.plot(df["tiempo [ns]"], df["canal 3 [mV]"], marker='o', markersize=2, linestyle='', color='#4daf4a', label='Canal 3 (u3)')

    ax.set_xlabel('Tiempo [ns]')
    ax.set_ylabel('Voltaje [mV]')
    ax.legend(loc='lower right')
    fig.tight_layout()
    fig.savefig("MediciónOptimizadaDetecciónMuon3.png")
    plt.show()
else:
    print(f"El archivo solo contiene {len(dataframes)} bloques de datos.")
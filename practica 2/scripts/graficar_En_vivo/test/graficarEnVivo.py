import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('./estiloGraficos.mplstyle')

CARPETA_DATOS = ""  # Directorio a monitorear
CARPETA_SALIDA= "./figuras"
PATRON_ARCHIVO = os.path.join(CARPETA_DATOS, "*.txt")
#%%
def obtener_archivo_mas_reciente():
    archivos = glob.glob(PATRON_ARCHIVO)
    if not archivos:
        return None
    # Retorna el archivo con la fecha de modificación más reciente
    return max(archivos, key=os.path.getmtime)


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
#%%

# Configuración inicial del gráfico interactivo
plt.ion()
fig, ax = plt.subplots(figsize=(8, 5))

ultimo_archivo_procesado = None
ultimo_mtime = 0

print(f"Monitoreando carpeta: {CARPETA_DATOS}...")

while True:
    archivo_actual = obtener_archivo_mas_reciente()
    
    if archivo_actual:
        mtime_actual = os.path.getmtime(archivo_actual)
        
        if archivo_actual != ultimo_archivo_procesado or mtime_actual > ultimo_mtime:
            try:
                dataframes = cargarArchivo(archivo_actual)
                total_bloques = len(dataframes)
                nombre_base = os.path.splitext(os.path.basename(archivo_actual))[0]
                
                print(f"Procesando {total_bloques} bloques de: {archivo_actual}")
                
                # Iterar en 9 grupos de 9 subplots (9 figuras de 3x3)
                for fig_idx in range(9):
                    fig, axes = plt.subplots(3, 3, figsize=(15, 12), sharex=True)
                    axes_flat = axes.flatten()
                    
                    for sub_idx in range(9):
                        bloque_idx = fig_idx * 9 + sub_idx
                        ax = axes_flat[sub_idx]
                        
                        if bloque_idx < total_bloques:
                            df = dataframes[bloque_idx]
                            
                            # Graficar canales (plot con linewidth es mucho más rápido que scatter para 1024 pts)
                            ax.plot(df.iloc[:, 0], df.iloc[:, 1], label="ch1", color="tab:blue", alpha=0.8)
                            ax.plot(df.iloc[:, 0], df.iloc[:, 2], label="ch2", color="tab:orange", alpha=0.8)
                            ax.plot(df.iloc[:, 0], df.iloc[:, 3], label="ch3", color="tab:green", alpha=0.8)
                            
                            ax.set_title(f"Corrida {bloque_idx}", fontsize=9)
                            ax.grid(True, linestyle="--", alpha=0.6)
                            
                            # Mostrar leyenda solo en el primer subplot para no sobrecargar
                            if sub_idx == 0:
                                ax.legend(fontsize=7, loc="upper right")
                        else:
                            ax.axis("off")  # Ocultar subplots vacíos si faltan tandas
                    
                    fig.suptitle(f"{nombre_base} - Grupo {fig_idx + 1}/9 (Corridas {fig_idx*9} a {min((fig_idx+1)*9 - 1, total_bloques - 1)})", fontsize=12)
                    plt.tight_layout()
                    
                    # Guardar archivo PNG
                    ruta_guardado = os.path.join(CARPETA_SALIDA, f"{nombre_base}_grupo_{fig_idx + 1}.png")
                    fig.savefig(ruta_guardado, dpi=120)
                    plt.close(fig)  # Libera la memoria de la figura inmediatamente
                
                ultimo_archivo_procesado = archivo_actual
                ultimo_mtime = mtime_actual
                print(f"Listo: 9 figuras guardadas en '{CARPETA_SALIDA}'")
                
            except (pd.errors.EmptyDataError, PermissionError):
                pass

    plt.pause(1.0)
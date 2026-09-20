import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

def histograma_vida_media(carpeta_datos, archivo_estilo):
    # Cargar tu estilo de gráficos
    plt.style.use(archivo_estilo)
    
    umbral_muon = -100    # mV (Pico principal)
    umbral_electron = -100 # mV (Pico secundario del electrón)
    tiempo_minimo = 100   # ns (Separación mínima)
    tiempo_corte = 10.0   # ns (Ignora el artefacto inicial)
    
    archivos_txt = glob.glob(os.path.join(carpeta_datos, "*.txt"))
    if not archivos_txt:
        print("No se encontraron archivos .txt en la carpeta especificada.")
        return

    # Lista para almacenar exclusivamente los deltas de tiempo (súper liviano para la RAM)
    tiempos_decaimiento = []

    def leer_evento_limpio(archivo):
        datos = []
        nombre = None
        with open(archivo, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if linea.startswith("Event #"):
                    if nombre and datos:
                        yield nombre, pd.DataFrame(datos, columns=['t', 'u1', 'u2', 'u3'])
                    nombre = linea.split("ts=")[0].strip()
                    datos = []
                elif linea and not linea.startswith("t") and not linea.startswith("#"):
                    try:
                        valores = [float(x) for x in linea.split()]
                        if len(valores) == 4 and valores[0] > tiempo_corte:
                            datos.append(valores)
                    except ValueError:
                        pass
            
            if nombre and datos:
                yield nombre, pd.DataFrame(datos, columns=['t', 'u1', 'u2', 'u3'])

    print("Procesando archivos y calculando deltas de tiempo...")

    for archivo in archivos_txt:
        for nombre, df in leer_evento_limpio(archivo):
            df['v_min'] = df[['u1', 'u2', 'u3']].min(axis=1)
            df_picos = df[df['v_min'] < umbral_electron].copy()
            
            if df_picos.empty:
                continue
            
            df_picos['dif_tiempo'] = df_picos['t'].diff()
            df_picos['id_pulso'] = (df_picos['dif_tiempo'] > 50).cumsum()
            
            idx_minimos = df_picos.groupby('id_pulso')['v_min'].idxmin()
            minimos_pulsos = df_picos.loc[idx_minimos]
            
            if len(minimos_pulsos) < 2:
                continue
            
            # Verificar las condiciones físicas y extraer el delta de tiempo (dt)
            dt_evento = None
            tiempos = minimos_pulsos['t'].values
            voltajes = minimos_pulsos['v_min'].values
            
            for i in range(len(tiempos)):
                for j in range(i + 1, len(tiempos)):
                    dt = tiempos[j] - tiempos[i]
                    if dt >= tiempo_minimo:
                        if voltajes[i] < umbral_muon or voltajes[j] < umbral_muon:
                            dt_evento = dt
                            break
                if dt_evento is not None:
                    break
                    
            if dt_evento is not None:
                tiempos_decaimiento.append(dt_evento)

    print(f"Análisis finalizado. Se encontraron {len(tiempos_decaimiento)} eventos de decaimiento válidos.")

    # Generar un ÚNICO gráfico al final
    if tiempos_decaimiento:
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.hist(tiempos_decaimiento, bins=30, color='#377eb8', edgecolor='black', alpha=0.8)
        
        ax.set_title('Distribución de tiempos de decaimiento del muón')
        ax.set_xlabel(r'$\Delta t$ [ns]')
        ax.set_ylabel('Frecuencia (Cuentas)')
        
        # Guardar en disco y luego mostrar
        plt.savefig('histograma_muones.png', bbox_inches='tight')
        plt.show()

# Ejecutar script
histograma_vida_media("/home/juan_cruz/Descargas/Datos", "estiloGraficos.mplstyle")
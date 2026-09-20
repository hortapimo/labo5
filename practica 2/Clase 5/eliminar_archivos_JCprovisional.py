import os
import glob
import pandas as pd

def eliminar_archivos_sin_decaimientos(carpeta_datos):
    umbral_muon = -100    # mV (Pico principal)
    umbral_electron = -100 # mV (Pico secundario)
    tiempo_minimo = 100   # ns (Separación temporal)
    tiempo_corte = 10.0   # ns (Corte del glitch inicial)
    
    archivos_txt = glob.glob(os.path.join(carpeta_datos, "*.txt"))
    if not archivos_txt:
        print("No se encontraron archivos .txt en la carpeta especificada.")
        return

    # Generador para leer eficientemente sin saturar la RAM
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

    archivos_eliminados = 0
    archivos_conservados = 0

    print("Iniciando escaneo y limpieza de archivos...")

    for archivo in archivos_txt:
        tiene_decaimiento = False
        
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
            
            tiempos = minimos_pulsos['t'].values
            voltajes = minimos_pulsos['v_min'].values
            
            for i in range(len(tiempos)):
                for j in range(i + 1, len(tiempos)):
                    if tiempos[j] - tiempos[i] >= tiempo_minimo:
                        if voltajes[i] < umbral_muon or voltajes[j] < umbral_muon:
                            tiene_decaimiento = True
                            break
                if tiene_decaimiento:
                    break
            
            if tiene_decaimiento:
                # Freno rápido: si ya encontró un decaimiento, el archivo se salva y deja de leerlo
                break
        
        # Eliminar el archivo si recorrió todos sus eventos sin éxito
        if tiene_decaimiento:
            archivos_conservados += 1
            print(f"Conservado: {os.path.basename(archivo)}")
        else:
            os.remove(archivo)
            archivos_eliminados += 1
            print(f"ELIMINADO: {os.path.basename(archivo)}")

    print(f"\nLimpieza finalizada.")
    print(f"Archivos conservados (con decaimientos): {archivos_conservados}")
    print(f"Archivos eliminados (sin decaimientos): {archivos_eliminados}")

# Ejecutar el script apuntando a tu carpeta actual (reemplazar "." por tu ruta si es necesario)
eliminar_archivos_sin_decaimientos("/home/juan_cruz/Descargas/Datos")
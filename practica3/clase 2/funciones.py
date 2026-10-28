import cv2
import matplotlib.pyplot as plt
import trackpy as tp
import pandas as pd

def cargar_video(ruta_video):
    # Escala de calibración: micrómetros por píxel
    distancia_um = 0.1 * 1000
    distancia_px = 1049.9014
    escala = distancia_um / distancia_px  # µm/px

    # Leer el video directamente en memoria con OpenCV
    cap = cv2.VideoCapture(ruta_video)
    if not cap.isOpened():
        raise FileNotFoundError(f"No se pudo abrir el video en: {ruta_video}")

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # En OpenCV (BGR), el canal 1 corresponde al canal verde
        frames.append(frame[:, :, 1])
    cap.release()
    return frames,escala

def dibujarFrame(frames, nFrame, diam, minmass):
    # Localizar partículas y resetear el índice para que vayan de 0 a N en orden
    particulas = tp.locate(frames[nFrame], diameter=diam, minmass=minmass, invert=True).reset_index(drop=True)

    # Visualizar detección (un solo eje)
    fig, axes = plt.subplots(figsize=(8, 8))
    
    # Dibujar la imagen base y las partículas detectadas
    tp.annotate(particulas, frames[nFrame], ax=axes)
    axes.set_title(f'Frame {nFrame} (Partículas detectadas: {len(particulas)})')

    # Añadir etiquetas con el índice de cada partícula
    for i, row in particulas.iterrows():  # Como ya está reseteado, i y el índice coinciden
        axes.text(
            row['x'], row['y'] - (diam/2) - 2,  
            str(i),                            
            color='yellow',                    
            fontsize=9,
            weight='bold',
            ha='center', va='bottom'
        )

    plt.tight_layout()
    plt.show()

    return fig, axes, particulas

def rastrear_particula_roi(frames, x_inicial, y_inicial, n_inicio, diam, minmass, radio_caja=15):
    """
    Sigue una partícula específica cuadro por cuadro mediante una región de interés (ROI).
    Retorna un DataFrame con la trayectoria [frame, x, y].
    """
    trayectoria = []
    x_actual, y_actual = x_inicial, y_inicial

    for num_frame in range(n_inicio, len(frames)):
        frame = frames[num_frame]
        
        # Definir los límites de la caja asegurándonos de no salirnos de la imagen
        ymin = max(0, int(y_actual - radio_caja))
        ymax = min(frame.shape[0], int(y_actual + radio_caja))
        xmin = max(0, int(x_actual - radio_caja))
        xmax = min(frame.shape[1], int(x_actual + radio_caja))
        
        # Recortar la imagen en esa zona pequeña
        recorte = frame[ymin:ymax, xmin:xmax]
        
        # Localizar partículas SOLO dentro del recorte
        f_recorte = tp.locate(recorte, diameter=diam, minmass=minmass, invert=True)
        
        if len(f_recorte) > 0:
            # Seleccionar la partícula más brillante dentro de la caja
            mejor_punto = f_recorte.sort_values(by='mass', ascending=False).iloc[0]
            
            # Convertir coordenadas locales a coordenadas globales de la imagen
            x_actual = mejor_punto['x'] + xmin
            y_actual = mejor_punto['y'] + ymin
            
            trayectoria.append({'frame': num_frame, 'x': x_actual, 'y': y_actual})
        else:
            print(f"Advertencia: La partícula se perdió en el frame {num_frame}")
            break

    return pd.DataFrame(trayectoria)

def superponer_trayectoria_video(frames, t_individual, diam, frame_muestra=10):
    """
    Toma los frames y la trayectoria para superponerla y verificar visualmente 
    si la siguió correctamente en un fotograma dado (o puedes adaptarlo para graficar varios).
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Seleccionamos un frame donde queramos verificar (ej. el frame_muestra)
    # Buscamos si la partícula existe en ese frame dentro de nuestro DataFrame de trayectoria
    datos_frame = t_individual[t_individual['frame'] == frame_muestra]
    
    if not datos_frame.empty:
        x_pos = datos_frame['x'].values[0]
        y_pos = datos_frame['y'].values[0]
        
        # Mostramos la imagen de fondo de ese frame
        ax.imshow(frames[frame_muestra], cmap='gray')
        
        # Dibujamos un círculo rojo alrededor de la posición rastreada
        circulo = plt.Circle((x_pos, y_pos), diam, color='red', fill=False, linewidth=2)
        ax.add_patch(circulo)
        
        # Dibujamos toda la estela o camino que recorrió hasta ese frame
        estela = t_individual[t_individual['frame'] <= frame_muestra]
        ax.plot(estela['x'], estela['y'], color='yellow', linestyle='-', linewidth=1.5, label='Trayectoria')
        
        ax.set_title(f"Verificación - Frame {frame_muestra}")
        ax.legend()
    else:
        print(f"El frame {frame_muestra} no está registrado en la trayectoria.")

    plt.tight_layout()
    plt.show()
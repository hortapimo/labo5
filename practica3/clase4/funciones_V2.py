import cv2
import matplotlib.pyplot as plt
import trackpy as tp
import pandas as pd
import api as api

def obtener_escala():
    """Devuelve la escala en µm/px."""
    distancia_um = 0.1 * 1000
    distancia_px = 1049.9014
    return distancia_um / distancia_px
def preprocesar_frame(frame_gris, diam):
    """
    Limpia el ruido de alta frecuencia, corrige la iluminación no uniforme (viñeteo)
    y resalta partículas oscuras redondas dejándolas brillantes sobre fondo oscuro.
    """
    # 1. Suavizar el grano fino del sensor sin perder el borde de la partícula
    suavizado = cv2.GaussianBlur(frame_gris, (3, 3), 0)

    # 2. Definir un elemento estructurante elíptico un poco más grande que la partícula
    # Esto asegura que las partículas entren en el filtro pero las manchas grandes de fondo se ignoren
    tam_kernel = int(diam * 1.5)
    if tam_kernel % 2 == 0:
        tam_kernel += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (tam_kernel, tam_kernel))

    # 3. Transformación Black-Hat: extrae elementos oscuros más pequeños que el kernel
    # IMPORTANTE: El resultado ya queda invertido (partículas blancas, fondo negro)
    blackhat = cv2.morphologyEx(suavizado, cv2.MORPH_BLACKHAT, kernel)

    # 4. Normalizar el contraste entre 0 y 255 para estabilizar 'minmass'
    procesado = cv2.normalize(blackhat, None, 0, 255, cv2.NORM_MINMAX)

    return procesado
def obtener_frame(ruta_video, n_frame):
    """Extrae un único frame del video sin cargar el resto en memoria."""
    cap = cv2.VideoCapture(ruta_video)
    if not cap.isOpened():
        raise FileNotFoundError(f"No se pudo abrir el video en: {ruta_video}")
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, n_frame)
    ret, frame = cap.read()
    #frame=frame.max() - frame
    
    #frame = smo(frame,sigma=2, size=3)
    cap.release()
    
    if not ret:
        raise ValueError(f"No se pudo leer el frame {n_frame}.")
    return frame[:, :, 1]  # Canal verde

def dibujarFrame(ruta_video, nFrame, diam, minmass):
    frame = obtener_frame(ruta_video, nFrame)
    frame = preprocesar_frame(frame, diam)
   
    # smo=api.SMO(sigma=1, size=3,shape=(1024,1024))
    # frame = smo.bg_corrected(frame)
    
    particulas = tp.locate(frame, diameter=diam, minmass=minmass, invert=False).reset_index(drop=True)

    fig, axes = plt.subplots(figsize=(8, 8))
    tp.annotate(particulas, frame, ax=axes)
    axes.set_title(f'Frame {nFrame} (Partículas detectadas: {len(particulas)})')

    for i, row in particulas.iterrows():
        axes.text(
            row['x'], row['y'] - (diam / 2) - 2,
            str(i),
            color='yellow',
            fontsize=9,
            weight='bold',
            ha='center', va='bottom'
        )

    plt.tight_layout()
    plt.show()
    return fig, axes, particulas

def rastrear_particula_roi(ruta_video, x_inicial, y_inicial, diam, minmass, radio_caja=15, n_inicio=0):
    """
    Rastrea leyendo frame por frame directamente desde disco.
    Uso de memoria RAM constante: O(1).
    """
    cap = cv2.VideoCapture(ruta_video)
    if not cap.isOpened():
        raise FileNotFoundError(f"No se pudo abrir el video en: {ruta_video}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if n_inicio > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, n_inicio)

    trayectoria = []
    x_actual, y_actual = x_inicial, y_inicial
    num_frame = n_inicio

    while True:
        ret, frame_bgr = cap.read()
        if not ret:
            break

        frame = frame_bgr[:, :, 1]
        frame = preprocesar_frame(frame, diam)
        # Límites del ROI
        ymin = max(0, int(y_actual - radio_caja))
        ymax = min(frame.shape[0], int(y_actual + radio_caja))
        xmin = max(0, int(x_actual - radio_caja))
        xmax = min(frame.shape[1], int(x_actual + radio_caja))

        recorte = frame[ymin:ymax, xmin:xmax]
        f_recorte = tp.locate(recorte, diameter=diam, minmass=minmass, invert=False)

        if len(f_recorte) > 0:
            mejor_punto = f_recorte.sort_values(by='mass', ascending=False).iloc[0]
            x_actual = mejor_punto['x'] + xmin
            y_actual = mejor_punto['y'] + ymin
            trayectoria.append({'frame': num_frame, 'x': x_actual, 'y': y_actual})
        else:
            print(f"Advertencia: La partícula se perdió en el frame {num_frame}")
            break

        num_frame += 1

    cap.release()
    return pd.DataFrame(trayectoria)

def superponer_trayectoria_video(ruta_video, t_individual, diam, frame_muestra=10):
    datos_frame = t_individual[t_individual['frame'] == frame_muestra]
    frame_fin = len(t_individual)-1
    if datos_frame.empty:
        print(f"El frame {frame_muestra} no está registrado en la trayectoria.")
        return

    frame = obtener_frame(ruta_video, frame_muestra)
    frameFinal = obtener_frame(ruta_video,frame_fin)
    
    def dib(frame):
        fig, ax = plt.subplots(figsize=(8, 8))
        x_pos = datos_frame['x'].values[0]
        y_pos = datos_frame['y'].values[0]
    
        ax.imshow(frame, cmap='gray')
        circulo = plt.Circle((x_pos, y_pos), diam, color='red', fill=False, linewidth=2)
        ax.add_patch(circulo)
    
        #estela = t_individual[t_individual['frame'] <= frame_muestra]
        ax.plot(t_individual['x'], t_individual['y'], color='black', linestyle='-', linewidth=1.5, label='Trayectoria')
    
        ax.set_title(f"Verificación - Frame {frame_muestra}")
        ax.legend()
        plt.tight_layout()
        plt.show()
        
    dib(frame)
    return t_individual
    #dib(frameFinal)

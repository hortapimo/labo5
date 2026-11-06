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
def exportar_video_trayectoria(ruta_video_entrada, ruta_video_salida, t_individual, diam, fps=None):
    """
    Lee el video original desde disco y exporta un nuevo archivo de video (.mp4 o .avi)
    dibujando la posición actual de la partícula y la estela acumulada cuadro por cuadro.
    Uso de RAM constante O(1).
    """
    if t_individual.empty:
        print("Error: El DataFrame de trayectoria está vacío.")
        return

    cap = cv2.VideoCapture(ruta_video_entrada)
    if not cap.isOpened():
        raise FileNotFoundError(f"No se pudo abrir el video: {ruta_video_entrada}")

    # Obtener propiedades del video original
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if fps is None:
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or np.isnan(fps):
            fps = 30.0  # Valor por defecto si el .avi no reporta FPS

    # Configurar el escritor de video (mp4v para .mp4, o XVID para .avi)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(ruta_video_salida, fourcc, fps, (ancho, alto), isColor=True)

    # Ordenar trayectoria por frame para asegurar continuidad
    t_ord = t_individual.sort_values(by='frame').reset_index(drop=True)
    frame_inicio = int(t_ord['frame'].iloc[0])
    frame_fin = int(t_ord['frame'].iloc[-1])

    # Diccionario {num_frame: (x, y)} para búsqueda instantánea O(1)
    mapa_posiciones = {
        int(row['frame']): (float(row['x']), float(row['y'])) 
        for _, row in t_ord.iterrows()
    }

    # Posicionar la lectura en el primer frame de la trayectoria
    if frame_inicio > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_inicio)

    puntos_estela = []
    radio_circulo = max(1, int(round(diam / 2)))

    print(f"Generando video desde el frame {frame_inicio} hasta {frame_fin}...")

    for num_frame in range(frame_inicio, frame_fin + 1):
        ret, frame_bgr = cap.read()
        if not ret:
            break

        # Extraer el canal verde y pasarlo a BGR de 3 canales para poder dibujar en color sobre fondo gris
        canal_verde = frame_bgr[:, :, 1]
        frame_vis = cv2.cvtColor(canal_verde, cv2.COLOR_GRAY2BGR)

        if num_frame in mapa_posiciones:
            x_actual, y_actual = mapa_posiciones[num_frame]
            pt_actual = (int(round(x_actual)), int(round(y_actual)))
            puntos_estela.append(pt_actual)

            # 1. Dibujar la estela acumulada (color amarillo en BGR: (0, 255, 255) o negro: (0, 0, 0))
            if len(puntos_estela) > 1:
                pts_array = np.array(puntos_estela, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame_vis, [pts_array], isClosed=False, color=(0, 255, 255), thickness=2, lineType=cv2.LINE_AA)

            # 2. Marcar el punto inicial (verde)
            cv2.circle(frame_vis, puntos_estela[0], radius=3, color=(0, 255, 0), thickness=-1)

            # 3. Dibujar el círculo alrededor de la partícula actual (rojo en BGR: (0, 0, 255))
            cv2.circle(frame_vis, pt_actual, radius=radio_circulo, color=(0, 0, 255), thickness=2, lineType=cv2.LINE_AA)

        # 4. Agregar texto con el número de frame arriba a la izquierda
        cv2.putText(
            frame_vis, f"Frame: {num_frame}", (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA
        )

        # Guardar el fotograma procesado en el archivo de video
        out.write(frame_vis)

    cap.release()
    out.release()
    print(f"Video guardado exitosamente en: {ruta_video_salida}")
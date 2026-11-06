import cv2
import matplotlib.pyplot as plt
import trackpy as tp
import pandas as pd

def obtener_escala():
    """Devuelve la escala en µm/px."""
    distancia_um = 0.1 * 1000
    distancia_px = 1049.9014
    return distancia_um / distancia_px

def obtener_frame(ruta_video, n_frame):
    """Extrae un único frame del video sin cargar el resto en memoria."""
    cap = cv2.VideoCapture(ruta_video)
    if not cap.isOpened():
        raise FileNotFoundError(f"No se pudo abrir el video en: {ruta_video}")
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, n_frame)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError(f"No se pudo leer el frame {n_frame}.")
    return frame[:, :, 1]  # Canal verde

def dibujarFrame(ruta_video, nFrame, diam, minmass):
    frame = obtener_frame(ruta_video, nFrame)
    particulas = tp.locate(frame, diameter=diam, minmass=minmass, invert=True).reset_index(drop=True)

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

        # Límites del ROI
        ymin = max(0, int(y_actual - radio_caja))
        ymax = min(frame.shape[0], int(y_actual + radio_caja))
        xmin = max(0, int(x_actual - radio_caja))
        xmax = min(frame.shape[1], int(x_actual + radio_caja))

        recorte = frame[ymin:ymax, xmin:xmax]
        f_recorte = tp.locate(recorte, diameter=diam, minmass=minmass, invert=True)

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
    if datos_frame.empty:
        print(f"El frame {frame_muestra} no está registrado en la trayectoria.")
        return

    frame = obtener_frame(ruta_video, frame_muestra)

    fig, ax = plt.subplots(figsize=(8, 8))
    x_pos = datos_frame['x'].values[0]
    y_pos = datos_frame['y'].values[0]

    ax.imshow(frame, cmap='gray')
    circulo = plt.Circle((x_pos, y_pos), diam, color='red', fill=False, linewidth=2)
    ax.add_patch(circulo)

    estela = t_individual[t_individual['frame'] <= frame_muestra]
    ax.plot(estela['x'], estela['y'], color='yellow', linestyle='-', linewidth=1.5, label='Trayectoria')

    ax.set_title(f"Verificación - Frame {frame_muestra}")
    ax.legend()
    plt.tight_layout()
    plt.show()
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import trackpy as tp

#%% 1. CARGAR VIDEO Y CALIBRAR EN EL PRIMER FRAME
# Coloca la ruta local a tu archivo de video en tu PC
ruta_video = 'videoOtroGrupo.avi'

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

print(f"Video cargado exitosamente: {len(frames)} frames de {frames[0].shape[1]}x{frames[0].shape[0]} px.")

#%% 2. PRUEBA DE DETECCIÓN (Ajustar parámetros aquí con Shift + Enter)
d_micro = 3.01  # Diámetro estimado de detección en µm
diam = int(d_micro // escala)
if diam % 2 == 0:
    diam += 1  # trackpy exige un número entero impar de píxeles

minmass = 2000  # Brillantez mínima para descartar ruido de fondo
frame_prueba = 0

# Localizar partículas en un solo cuadro
f_prueba = tp.locate(frames[frame_prueba], diameter=diam, minmass=minmass, invert=True)

# Visualizar detección e histograma de masas
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
tp.annotate(f_prueba, frames[frame_prueba], ax=axes[0])
axes[0].set_title(f'Frame {frame_prueba} (Partículas detectadas: {len(f_prueba)})')

axes[1].hist(f_prueba['mass'], bins=20, edgecolor='black')
axes[1].axvline(minmass, color='red', linestyle='--', label=f'minmass = {minmass}')
axes[1].set_xlabel('Brillantez total (mass)')
axes[1].set_ylabel('Cantidad de partículas')
axes[1].set_title('Distribución de brillantez')
axes[1].legend()
plt.tight_layout()
plt.show()

# Verificar sesgo subpíxel (los histogramas deben verse lo más planos posible)
(f_prueba[['x', 'y']] % 1).hist()
plt.show()


#%% 3. PROCESAR TODO EL VIDEO Y VINCULAR TRAYECTORIAS
tp.quiet()  # Desactiva los mensajes de progreso por consola para acelerar el cálculo

# Detectar en todos los frames (puedes usar frames[:500] para probar con una fracción)
f_todas = tp.batch(frames[:30], diameter=diam, minmass=minmass, invert=True)

# Unir posiciones cuadro a cuadro para armar las trayectorias
t = tp.link(f_todas, search_range=diam // 2, memory=3)

# Filtrar trayectorias cortas (se conservan las que sobreviven al menos 50 frames)
t_final = tp.filter_stubs(t, threshold=10).reset_index(drop=True)
print(f"Partículas totales: {t['particle'].nunique()} | Tras filtrar: {t_final['particle'].nunique()}")

# Pasar posiciones y errores a micrómetros (µm)
t_final['x_um'] = t_final['x'] * escala
t_final['y_um'] = t_final['y'] * escala
t_final['ep_um'] = t_final['ep'] * escala

# Graficar las trayectorias en µm
plt.figure(figsize=(6, 6))
for pid, traj in t_final.groupby('particle'):
    plt.plot(traj['x_um'], traj['y_um'], marker='o', markersize=2, linewidth=1, label=f'p{pid}')

plt.xlabel('x (µm)')
plt.ylabel('y (µm)')
plt.title('Trayectorias identificadas')
plt.gca().invert_yaxis()
plt.grid(True, linestyle=':', alpha=0.6)
plt.show()

# Opcional: Guardar la tabla de posiciones en el mismo directorio del script
# t_final.to_csv('trayectorias_particulas.csv', index=False)
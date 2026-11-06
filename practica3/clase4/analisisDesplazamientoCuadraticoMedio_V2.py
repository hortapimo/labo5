import funciones_V2 as f
import matplotlib.pyplot as plt
import trackpy as tp

#%% Configuración
rutaVideo = "sinLserGod1_1.avi"
escala = f.obtener_escala()

# Parámetros de detección
d_micro = 3.01  # µm
diam = int(d_micro // escala)
if diam % 2 == 0:
    diam += 1

minmass = 1700
nframe = 0

#%% Visualización del frame 0 para elegir partícula
fig, ax, particulas = f.dibujarFrame(rutaVideo, nframe, diam, minmass)

#%% Selección de partícula
nParticula = 11
x_inicial = particulas.loc[nParticula, 'x']
y_inicial = particulas.loc[nParticula, 'y']
print(f"La partícula {nParticula} está en la posición: x = {x_inicial:.2f}, y = {y_inicial:.2f}")

# Rastrear (inicia en frame 0 de forma predeterminada)
trayectoria = f.rastrear_particula_roi(
    rutaVideo, x_inicial, y_inicial, diam, minmass, radio_caja=300, n_inicio=0
)

#%% Guardar trayectoria
trayectoria.to_csv(f'trayectoria_particula{nParticula}_video_{rutaVideo}.csv', index=False, encoding='utf-8')

#%% Superponer sobre el fotograma elegido
f.superponer_trayectoria_video(rutaVideo, trayectoria, diam, frame_muestra=0)
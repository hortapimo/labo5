import funciones_V2 as f
import matplotlib.pyplot as plt
import trackpy as tp

#%% Configuración
rutaVideo = "laser_atrapa_diluido_uno_en_seis_5.avi"
escala = f.obtener_escala()

d_micro = 3.01  # µm
diam = int(d_micro // escala)
if diam % 2 == 0:
    diam += 1
#%% Visualización del frame 0 para elegir partícula
minmass = 10000
nframe = 0
fig, ax, particulas = f.dibujarFrame(rutaVideo, nframe, diam, minmass)

#%% Selección de partícula
nParticula = 2
x_inicial = particulas.loc[nParticula, 'x']
y_inicial = particulas.loc[nParticula, 'y']
print(f"La partícula {nParticula} está en la posición: x = {x_inicial:.2f}, y = {y_inicial:.2f}")

# Rastrear (inicia en frame 0 de forma predeterminada)
trayectoria = f.rastrear_particula_roi(
    rutaVideo, x_inicial, y_inicial, diam, minmass, radio_caja=100, n_inicio=0
)

#%% Superponer sobre el fotograma elegido
aux =f.superponer_trayectoria_video(rutaVideo, trayectoria, diam, frame_muestra=0)
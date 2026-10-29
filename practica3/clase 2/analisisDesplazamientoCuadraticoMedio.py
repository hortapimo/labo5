import funciones as f
import matplotlib.pyplot as plt
import trackpy as tp

#%%    Cargar video
rutaVideo="muestra_mas_nueva_mas_diluido_laser_epico_mucha_traccion_2_2.avi"
frames, escala= f.cargar_video(rutaVideo)

#%%    figura de frame
d_micro = 3.01  # Diámetro estimado de detección en µm
diam = int(d_micro // escala)
if diam % 2 == 0:
    diam += 1  # trackpy exige un número entero impar de píxeles

minmass = 1700  # Brillantez mínima para descartar ruido de fondo
nframe = 0

fig,ax, particulas= f.dibujarFrame(frames, nframe,diam,minmass)

#%%    calcular desplazamiento medio de particula

nParticula = 21
x_inicial = particulas.loc[nParticula, 'x']
y_inicial = particulas.loc[nParticula, 'y']

print(f"La partícula {nParticula} está en la posición: x = {x_inicial:.2f}, y = {y_inicial:.2f}")

trayectoria = f.rastrear_particula_roi(frames, x_inicial, y_inicial, nParticula, diam, minmass, radio_caja=60)

#%% mostrar trayectoria superpuesta
f.superponer_trayectoria_video(frames, trayectoria, diam, frame_muestra=1500)
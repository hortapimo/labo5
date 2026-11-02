import funciones as f
import matplotlib.pyplot as plt
import trackpy as tp
import numpy as np

#%%    Cargar video
ruta_video = '/home/juan_cruz/Descargas/recorte.avi'
frames, escala= f.cargar_video(ruta_video)
#%%    figura de frame
d_micro = 3.0  # Diámetro estimado de detección en µm
diam = int(d_micro // escala)
if diam % 2 == 0:
    diam += 1  # trackpy exige un número entero impar de píxeles

minmass = 1700  # Brillantez mínima para descartar ruido de fondo
nframe = 0
fig,ax, particulas= f.dibujarFrame(frames, nframe,diam,minmass)
#%% Detectar en todo el video y vincular trayectorias
fps = 30.0
tp.quiet()

f_todas = tp.batch(frames, diameter=diam, minmass=minmass, invert=True)

# search_range en px: debe ser menor que la distancia típica entre partículas
t = tp.link(f_todas, search_range=diam, memory=3)
t_final = tp.filter_stubs(t, threshold=100).reset_index(drop=True)        # solo trayectorias largas
print(f"Partículas totales: {t['particle'].nunique()} | Tras filtrar: {t_final['particle'].nunique()}")

#%% Verificar trayectorias
plt.figure(figsize=(7, 7))
tp.plot_traj(t_final, mpp=escala)      # ejes en µm
plt.show()

#%% MSD individual y de ensamble
max_lag = 100   # en frames

imsd = tp.imsd(t_final, mpp=escala, fps=fps, max_lagtime=max_lag)   # columnas = partículas
emsd = tp.emsd(t_final, mpp=escala, fps=fps, max_lagtime=max_lag)   # promedio de ensamble

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(imsd.index, imsd.values, color='k', alpha=0.15)
ax.plot(emsd.index, emsd.values, 'o', color='tab:red', label=f'ensamble (N={imsd.shape[1]})')
ax.set(xscale='log', yscale='log', xlabel='τ (s)', ylabel=r'MSD (µm$^2$)')
ax.grid(True, which='both', linestyle=':', alpha=0.6)
ax.legend()
plt.tight_layout()
plt.show()

#%% Ajuste: MSD = 4 D τ^α  (2D)
tau = emsd.index.values
sel = tau <= tau.max() / 4                      # evitar lags largos, muy ruidosos
alpha, logK = np.polyfit(np.log(tau[sel]), np.log(emsd.values[sel]), 1)
D = np.exp(logK) / 4
print(f"α = {alpha:.2f}  |  D = {D:.3f} µm²/s^α")
#%%    calcular desplazamiento medio de particula
nParticula = 0
x_inicial = particulas.loc[nParticula, 'x']
y_inicial = particulas.loc[nParticula, 'y']

print(f"La partícula {nParticula} está en la posición: x = {x_inicial:.2f}, y = {y_inicial:.2f}")

trayectoria = f.rastrear_particula_roi(frames, x_inicial, y_inicial, nParticula, diam, minmass, radio_caja=60)

#%% mostrar trayectoria superpuesta
f.superponer_trayectoria_video(frames, trayectoria, diam, frame_muestra = 30)


"""
# %%    grafico MSD para una única partícula

fps = 30.0

MSD = np.square(trayectoria['x'] - x_inicial) + np.square(trayectoria['y'] - y_inicial)

plt.figure(figsize=(7,5))
plt.plot(MSD.index, MSD, 'o', color = 'tab:blue', label='MSD')
plt.xlabel('tiempo')
plt.ylabel('MSD')
plt.title('MSD')
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.show()

#%% MSD Claude
fps = 30.0
f_todas = tp.batch(frames, diameter=diam, minmass=minmass, invert=True)
t = tp.link(f_todas, search_range=diam // 2, memory=3)   # search_range en px
t_final = tp.filter_stubs(t, threshold=50).reset_index(drop=True)

imsd = tp.imsd(t_final, mpp=escala, fps=fps, max_lagtime=100)  # una columna por partícula
emsd = tp.emsd(t_final, mpp=escala, fps=fps, max_lagtime=100)  # promedio de ensamble

fig, ax = plt.subplots()
ax.plot(imsd.index, imsd.values, 'k-', alpha=0.2)
ax.plot(emsd.index, emsd, 'o', color='tab:red', label='ensamble')
ax.set(xscale='log', yscale='log', xlabel='τ (s)', ylabel=r'MSD (µm$^2$)')
ax.legend()
plt.grid(True, linestyle=':', alpha=1)
plt.tight_layout()
plt.show()
"""
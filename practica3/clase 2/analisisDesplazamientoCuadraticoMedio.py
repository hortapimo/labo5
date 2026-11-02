import funciones as f
import matplotlib.pyplot as plt
import trackpy as tp
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import chi2 as chi2_dist

#%%    Cargar video
ruta_video = 'recorte2.avi'
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
fps = 15.0

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

# %%

fps = 15.0
M = len(particulas)
msds = []

for nParticula in particulas.index:
    x_inicial = particulas.loc[nParticula, 'x']
    y_inicial = particulas.loc[nParticula, 'y']

    trayectoria = f.rastrear_particula_roi(frames, x_inicial, y_inicial, nframe,
                                            diam, minmass, radio_caja=100)
    
    if len(trayectoria) < 10:          # descartar si se perdió casi de inmediato
        continue

    x = trayectoria['x'].to_numpy() 
    y = trayectoria['y'].to_numpy()

    r2 = np.square(x - x[0]) + np.square(y - y[0])
    r2_medio = np.cumsum(r2[1:]) / np.arange(1, len(r2))      # ec. (30)
    msds.append(r2_medio)

L = min(len(m) for m in msds)
MSD = np.mean([m[:L] for m in msds], axis=0)                  # ec. (31)
tiempo = np.arange(1, L + 1) / fps
A = np.array([m[:L] for m in msds]) 
N = A.shape[0]
err = A.std(axis=0, ddof=1) / np.sqrt(N) 
print(f"\nPartículas usadas: {len(msds)} de {M} | puntos por curva: {L}")
print(f"\nMSD : {MSD}")    

#%% Ajuste MSD = A * t^n (ponderado)
def modelo(t, A_, n_):
    return A_ * t**n_

popt, pcov = curve_fit(modelo, tiempo, MSD, p0=[MSD[-1] / tiempo[-1], 1.0], 
                       sigma=err, absolute_sigma=True)
A_fit, n_fit = popt
dA, dn = np.sqrt(np.diag(pcov))

"""
residuos = (MSD - modelo(tiempo, *popt)) / err
chi2 = np.sum(residuos**2)
dof = len(tiempo) - len(popt)
chi2_red = chi2 / dof
p_valor = chi2_dist.sf(chi2, dof)
"""

print(f"A = {A_fit:.4f} ± {dA:.4f} | n = {n_fit:.3f} ± {dn:.3f}")

#%% 
fig, ax = plt.subplots(figsize=(7, 5))
ax.errorbar(tiempo, MSD, yerr=err, fmt='o', mfc='none', mec='tab:blue', ecolor='tab:blue',
            ms=4, elinewidth=1, capsize=2, label=f'Datos (N={N})')
ax.plot(tiempo, modelo(tiempo, *popt), '-', color='tab:red', lw=2.5,
        label=r'Ajuste')

texto = (rf'$A = {A_fit:.3f} \pm {dA:.3f}$' '\n'
         rf'$n = {n_fit:.3f} \pm {dn:.3f}$' '\n')

ax.text(0.97, 0.05, texto, transform=ax.transAxes, ha='right', va='bottom',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

ax.set_xlabel('Tiempo (s)')
ax.set_ylabel(r'$\langle r^2 \rangle$ (µm$^2$)')
ax.set_xlim(0, None); ax.set_ylim(0, None)
ax.grid(True, alpha=0.4)
ax.legend(loc='upper left')
plt.tight_layout()
plt.show()

#%% mostrar trayectoria superpuesta
f.superponer_trayectoria_video(frames, trayectoria, diam, frame_muestra = 30)


#%%
"""
fps = 15.0
nParticula = 1

# print(f"La partícula {nParticula} está en la posición: x = {x_inicial:.2f}, y = {y_inicial:.2f}")

trayectoria = f.rastrear_particula_roi(frames, x_inicial, y_inicial, nParticula, diam, minmass, radio_caja=60)

x = trayectoria['x'].to_numpy()
y = trayectoria['y'].to_numpy()
frames_idx = trayectoria['frame'].to_numpy()

r2 = np.square(x - x[0]) + np.square(y - y[0])

# Ec. (30): media acumulada, <r²>(t_n) = (1/n) * suma_{i=1..n} r²(t_i)
n = np.arange(1, len(r2))                     # n = 1, 2, ..., N-1
r2_medio = np.cumsum(r2[1:]) / n              # arreglo con el MSD para cada tiempo
t = (frames_idx[1:] - frames_idx[0]) / fps    # s

plt.figure(figsize=(7, 5))
plt.plot(t, r2_medio, 'o', mfc='none', ms=4)
plt.xlabel('Tiempo (s)')
plt.ylabel(r'$\langle r^2 \rangle$ (µm$^2$)')
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.show()
# %%
fps = 15.0 #Este es el caso de nuestro video
M = t_final['particle'].nunique()
MSD = 0
print(f"\nCantidad de particulas a analizar: {M}")
r2 = [] #Contiene los r2 de cada particula

for m in range(M):
    nParticula = m
    
    trayectoria = f.rastrear_particula_roi(frames, x_inicial, y_inicial, nParticula, diam, minmass, radio_caja=60)
    x = trayectoria['x'].to_numpy()
    y = trayectoria['y'].to_numpy()
    
    x_inicial = particulas.loc[nParticula, 'x']
    y_inicial = particulas.loc[nParticula, 'y']
    frames_idx = trayectoria['frame'].to_numpy()
    
    r2[m] = np.square(x - x[0]) + np.square(y - y[0])
    n = np.arange(1, len(r2))                     
    r2_medio = np.cumsum(r2[1:]) / n              # arreglo con el MSD para cada tiempo
    t = (frames_idx[1:] - frames_idx[0]) / fps
    MSD = MSD + r2_medio

print(f"\nMSD : {MSD}")    
"""

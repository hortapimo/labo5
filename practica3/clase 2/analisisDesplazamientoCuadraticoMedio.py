import funciones as f
import matplotlib.pyplot as plt
import trackpy as tp
import numpy as np

#%%    Cargar video
rutaVideo="/home/juan_cruz/Descargas/muestra_mas_nueva_mas_diluido_1.avi"
frames, escala= f.cargar_video(rutaVideo)

#%%    figura de frame
d_micro = 2.8  # Diámetro estimado de detección en µm
diam = int(d_micro // escala)
if diam % 2 == 0:
    diam += 1  # trackpy exige un número entero impar de píxeles

minmass = 1700  # Brillantez mínima para descartar ruido de fondo
nframe = 0

fig,ax, particulas= f.dibujarFrame(frames, nframe,diam,minmass)

#%%    calcular desplazamiento medio de particula

nParticula = 0
x_inicial = particulas.loc[nParticula, 'x']
y_inicial = particulas.loc[nParticula, 'y']

print(f"La partícula {nParticula} está en la posición: x = {x_inicial:.2f}, y = {y_inicial:.2f}")

trayectoria = f.rastrear_particula_roi(frames, x_inicial, y_inicial, nParticula, diam, minmass, radio_caja=60)

#%% mostrar trayectoria superpuesta
f.superponer_trayectoria_video(frames, trayectoria, diam, frame_muestra = 30)

# %%    MSD Para una única partícula

fps = 30.0

# %% 1. MSD PARA UNA SOLA PARTÍCULA ESPECÍFICA (trayectoria)

# Asegurar que el DataFrame de la trayectoria tenga identificador de partícula
trayectoria['particle'] = nParticula

# Definir tiempo de lag máximo (1/3 de la longitud de la trayectoria)
max_lag_indiv = max(1, len(trayectoria) // 3)

# Calcular IMSD de la partícula individual
imsd_indiv = tp.imsd(trayectoria, mpp=escala, fps=fps, max_lagtime=max_lag_indiv)

# Ajuste lineal 2D: MSD = 4 * D * tau + b
n_puntos = min(puntos_ajuste, len(imsd_indiv))
tau_indiv = imsd_indiv.index[:n_puntos].values
msd_indiv_vals = imsd_indiv[nParticula].iloc[:n_puntos].values

m_indiv, b_indiv = np.polyfit(tau_indiv, msd_indiv_vals, 1)
D_indiv = m_indiv / 4.0

print(f"=== Resultados Partícula {nParticula} ===")
print(f"Pendiente (m): {m_indiv:.4f} µm²/s")
print(f"Coeficiente de difusión (D): {D_indiv:.4f} µm²/s\n")

# Gráfico del MSD individual con su ajuste lineal
plt.figure(figsize=(7, 5))
plt.plot(imsd_indiv.index, imsd_indiv[nParticula], 'o', color='tab:blue', label='Datos medidos')
plt.plot(tau_indiv, m_indiv * tau_indiv + b_indiv, 'r--', linewidth=2, 
         label=f'Ajuste 2D ($D = {D_indiv:.3f}\\ \\mu\\mathrm{{m}}^2/\\mathrm{{s}}$)')
plt.xlabel(r'Tiempo de lag $\tau$ [s]')
plt.ylabel(r'MSD [$\mu\mathrm{m}^2$]')
plt.title(f'Desplazamiento Cuadrático Medio - Partícula {nParticula}')
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.show()


# %% 2. IMSD Y EMSD GLOBAL (ENSAMBLE COMPLETO t_final)

# Definir tiempo de lag máximo basado en la trayectoria más corta del conjunto
duracion_minima = t_final.groupby('particle')['frame'].count().min()
max_lag_global = max(1, duracion_minima // 3)

# 1. Obtener MSDs individuales y MSD promedio de ensamble
imsd_global = tp.imsd(t_final, mpp=escala, fps=fps, max_lagtime=max_lag_global)
emsd_global = tp.emsd(t_final, mpp=escala, fps=fps, max_lagtime=max_lag_global)

# 2. Visualización: Trayectorias individuales vs Promedio Ensamble
plt.figure(figsize=(8, 6))
plt.plot(imsd_global.index, imsd_global, color='gray', alpha=0.3, linewidth=1)
plt.plot([], [], color='gray', alpha=0.5, label='Partículas individuales')  # Para la leyenda
plt.plot(emsd_global.index, emsd_global, 'o-', color='crimson', linewidth=2.5, label='EMSD (Promedio Ensamble)')

plt.xlabel(r'Tiempo de lag $\tau$ [s]')
plt.ylabel(r'MSD [$\mu\mathrm{m}^2$]')
plt.title(f'MSD del Ensamble ({imsd_global.shape[1]} partículas)')
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.show()


# %% 3. AJUSTE LINEAL GLOBAL Y CÁLCULO DE D CON ERROR ESTÁNDAR (SEM)

n_puntos_global = min(puntos_ajuste, len(emsd_global))
tau_fit = emsd_global.index[:n_puntos_global].values
emsd_fit = emsd_global.iloc[:n_puntos_global].values

# Ajuste sobre la curva de ensamble
m_global, b_global = np.polyfit(tau_fit, emsd_fit, 1)
D_global = m_global / 4.0

# Cálculo de D para cada partícula para determinar la incertidumbre del experimento
D_individuales = []
for p_id in imsd_global.columns:
    imsd_p = imsd_global[p_id].iloc[:n_puntos_global].dropna()
    if len(imsd_p) >= 3:
        m_i, _ = np.polyfit(imsd_p.index.values, imsd_p.values, 1)
        D_individuales.append(m_i / 4.0)

D_std = np.std(D_individuales, ddof=1)
D_sem = D_std / np.sqrt(len(D_individuales))  # Error estándar de la media (SEM)

print("=" * 50)
print(f"Partículas analizadas: {len(D_individuales)}")
print(f"Pendiente global (m): {m_global:.4f} µm²/s")
print(f"Coeficiente de Difusión Global (D): {D_global:.4f} ± {D_sem:.4f} µm²/s")
print("=" * 50)

# Gráfico del EMSD con su ajuste lineal y barra de incertidumbre reportada
plt.figure(figsize=(7, 5))
plt.plot(emsd_global.index, emsd_global, 'o', color='crimson', label='EMSD medido')
plt.plot(tau_fit, m_global * tau_fit + b_global, 'k--', linewidth=2, 
         label=f'Ajuste 2D: $D = ({D_global:.3f} \\pm {D_sem:.3f})\\ \\mu\\mathrm{{m}}^2/\\mathrm{{s}}$')

plt.xlabel(r'Tiempo de lag $\tau$ [s]')
plt.ylabel(r'EMSD [$\mu\mathrm{m}^2$]')
plt.title('Ajuste de Difusión del Ensamble Global')
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.show()
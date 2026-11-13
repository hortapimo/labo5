import funciones_V2 as f
import matplotlib.pyplot as plt
import trackpy as tp

#%% Configuración
plt.style.use("estiloGraficos.mplstyle")
rutaVideo = "sinLserGod1_1.avi"
escala = f.obtener_escala()

# Parámetros de detección
d_micro = 4.01  # µm
diam = int(d_micro // escala)
if diam % 2 == 0:
    diam += 1



#%% Visualización del frame 0 para elegir partícula
minmass = 20000
nframe = 0
fig, ax, particulas = f.dibujarFrame(rutaVideo, nframe, diam, minmass)

fig.savefig("particulas_prueba_de_deteccion.png", dpi=300, bbox_inches="tight")

#%% Selección de partícula
nParticula = 17
x_inicial = particulas.loc[nParticula, 'x']
y_inicial = particulas.loc[nParticula, 'y']
print(f"La partícula {nParticula} está en la posición: x = {x_inicial:.2f}, y = {y_inicial:.2f}")

# Rastrear (inicia en frame 0 de forma predeterminada)
trayectoria = f.rastrear_particula_roi(
    rutaVideo, x_inicial, y_inicial, diam, minmass, radio_caja=70, n_inicio=0
)

#%% Guardar trayectoria
trayectoria.to_csv(f'trayectoria_particula{nParticula}_video_{rutaVideo}.csv', index=False, encoding='utf-8')

#%% Superponer sobre el fotograma elegido
aux =f.superponer_trayectoria_video(rutaVideo, trayectoria, diam, frame_muestra=0)
#%% hago figura prolija para el informe
minmass = 20000
nframe = 0
# Parámetros de detección
d_micro = 4.01  # µm
diam = int(d_micro // escala)
if diam % 2 == 0:
    diam += 1
frame = nframe
frame = f.obtener_frame("sinLserGod1_1.avi", nframe)
frame = f.preprocesar_frame(frame, diam)

particulas = tp.locate(frame, diameter=diam, minmass=minmass, invert=False).reset_index(drop=True)
fig, axes = plt.subplots(figsize=(8, 8))
tp.annotate(particulas, frame, ax=axes)
for i, row in particulas.iterrows():
    axes.text(
        row['x'], row['y'] - (diam / 2) - 2,
        str(i),
        color='yellow',
        fontsize=9,
        weight='bold',
        ha='center', va='bottom'
    )
axes.plot([], [], marker='o', color='none', markeredgecolor='red', markersize=10, label='Partículas detectadas')
axes.set_xlim(150,1250)
axes.set_ylim(0,1000)
axes.set_xlabel("x [px]")
axes.set_ylabel("y [px]")
axes.legend()
fig.tight_layout()
fig.savefig("DeteccionParticulasInforme")
plt.show()





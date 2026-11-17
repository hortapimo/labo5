import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
plt.style.use('estiloGraficos22.mplstyle')
# ==========================================
# PARÁMETROS DE LA SIMULACIÓN
# ==========================================
N_PARTICULAS = 50      # Número total de partículas
L = 200.0                # Tamaño de la caja cuadrada [-L/2, L/2]
RADIO = 1.2              # Radio de cada partícula (R)
DIST_COLISION = 2 * RADIO
D = 10                  # Coeficiente de difusión
DT = 1                 # Paso temporal (dt)
PASO_CLAVAR = 40         # Paso en el que se clava la primera partícula
PASOS_POR_FRAME = 3      # Pasos físicos por cada cuadro de animación
MAX_PASOS = 3000         # Límite de pasos de la simulación

# Escala del salto browniano: sqrt(2 * D * dt)
sigma = np.sqrt(2.0 * D * DT)

# ==========================================
# ESTADO INICIAL
# ==========================================
np.random.seed(42)
# Posiciones iniciales uniformes dentro de la caja
pos = np.random.uniform(-L / 2 + RADIO, L / 2 - RADIO, size=(N_PARTICULAS, 2))

# Estado: False = libre (móvil), True = clavada (en el cúmulo)
clavada = np.zeros(N_PARTICULAS, dtype=bool)
tiempo_pegado = np.full(N_PARTICULAS, np.nan)
semilla_idx = None

paso_actual = 0
historial_tiempo = []
historial_cumulo = []

# ==========================================
# CONFIGURACIÓN GRÁFICA
# ==========================================
fig, (ax_sim, ax_curva) = plt.subplots(1, 2, figsize=(11, 5))
#fig.suptitle("Simulación de Movimiento Browniano y Formación de Cúmulo (DLA)", fontsize=13, fontweight="bold")

# Panel 1: Cámara de partículas
ax_sim.set_xlim(-L / 2, L / 2)
ax_sim.set_ylim(-L / 2, L / 2)
ax_sim.set_aspect("equal")
ax_sim.set_title("Cámara")
ax_sim.set_xlabel("x [$\\mu$m] ")
ax_sim.set_ylabel("y [$\\mu$m]")

# Scatters de las partículas
scatter_libres = ax_sim.scatter([], [], s=35, c="steelblue", alpha=0.6)
scatter_cumulo = ax_sim.scatter([], [], s=45, c=[], cmap="plasma", vmin=PASO_CLAVAR, vmax=MAX_PASOS, zorder=3)
scatter_semilla = ax_sim.scatter([], [], s=65, c="crimson", edgecolors="black", zorder=4)

# Leyenda exclusiva con las 3 categorías y sus colores visibles desde el inicio
handles_leyenda = [
    Line2D([0], [0], marker="o", color="w", label="Libres", markerfacecolor="steelblue", alpha=0.7, markersize=7),
    Line2D([0], [0], marker="o", color="w", label="Cúmulo", markerfacecolor="darkorchid", markersize=8),
    Line2D([0], [0], marker="o", color="w", label="Semilla inicial", markerfacecolor="crimson", markeredgecolor="black", markersize=9),
]
ax_sim.legend(handles=handles_leyenda, loc="upper right", frameon=True)

# Panel 2: Evolución temporal del tamaño del cúmulo
ax_curva.set_xlim(0, MAX_PASOS)
ax_curva.set_ylim(0, N_PARTICULAS)
ax_curva.set_title("Crecimiento del cúmulo")
ax_curva.set_xlabel("t")
ax_curva.set_ylabel("Partículas en el cúmulo")
#ax_curva.axvline(PASO_CLAVAR, color="crimson", linestyle="--", alpha=0.6, label="Se clava la 1ª partícula")
linea_crecimiento, = ax_curva.plot([], [], color="darkorange", lw=2, label="Tamaño del cúmulo")
ax_curva.legend(loc="upper left")
ax_curva.grid(True, alpha=0.3)


# ==========================================
# DINÁMICA DE UN PASO TEMPORAL
# ==========================================
def avanzar_fisica():
    global paso_actual, semilla_idx

    paso_actual += 1

    # 1. Clavar la primera partícula en el paso elegido
    if paso_actual == PASO_CLAVAR and not np.any(clavada):
        dist_centro = np.linalg.norm(pos, axis=1)
        semilla_idx = np.argmin(dist_centro)
        clavada[semilla_idx] = True
        tiempo_pegado[semilla_idx] = paso_actual

    # 2. Mover únicamente las partículas libres
    idx_libres = np.where(~clavada)[0]
    if len(idx_libres) > 0:
        desplazamiento = sigma * np.random.randn(len(idx_libres), 2)
        pos[idx_libres] += desplazamiento

        # Condiciones de contorno reflectivas en los bordes de la caja
        limite = L / 2 - RADIO
        for dim in (0, 1):
            rebote_sup = pos[idx_libres, dim] > limite
            pos[idx_libres[rebote_sup], dim] = 2 * limite - pos[idx_libres[rebote_sup], dim]

            rebote_inf = pos[idx_libres, dim] < -limite
            pos[idx_libres[rebote_inf], dim] = -2 * limite - pos[idx_libres[rebote_inf], dim]

    # 3. Detección vectorizada de colisiones (Libres vs. Clavadas)
    if np.any(clavada) and len(idx_libres) > 0:
        idx_clavadas = np.where(clavada)[0]

        diff = pos[idx_libres, np.newaxis, :] - pos[np.newaxis, idx_clavadas, :]
        dist_sq = np.sum(diff ** 2, axis=2)

        chocaron_mask = np.any(dist_sq <= DIST_COLISION ** 2, axis=1)
        nuevas_pegadas = idx_libres[chocaron_mask]

        if len(nuevas_pegadas) > 0:
            clavada[nuevas_pegadas] = True
            tiempo_pegado[nuevas_pegadas] = paso_actual

    # 4. Guardar estadísticas
    historial_tiempo.append(paso_actual)
    historial_cumulo.append(int(np.sum(clavada)))


# ==========================================
# BUCLE DE ANIMACIÓN
# ==========================================
def actualizar_frame(frame):
    for _ in range(PASOS_POR_FRAME):
        if paso_actual < MAX_PASOS and not np.all(clavada):
            avanzar_fisica()

    # Actualizar posiciones de partículas libres
    pos_libres = pos[~clavada]
    if len(pos_libres) > 0:
        scatter_libres.set_offsets(pos_libres)
    else:
        scatter_libres.set_offsets(np.empty((0, 2)))

    # Actualizar partículas del cúmulo
    pos_cumulo = pos[clavada]
    if len(pos_cumulo) > 0:
        scatter_cumulo.set_offsets(pos_cumulo)
        scatter_cumulo.set_array(tiempo_pegado[clavada])

    # Destacar la semilla original
    if semilla_idx is not None:
        scatter_semilla.set_offsets(pos[semilla_idx].reshape(1, 2))

    # Actualizar curva temporal
    linea_crecimiento.set_data(historial_tiempo, historial_cumulo)

    return scatter_libres, scatter_cumulo, scatter_semilla, linea_crecimiento


ani = FuncAnimation(
    fig, actualizar_frame, frames=MAX_PASOS // PASOS_POR_FRAME,
    interval=20, blit=False, repeat=False
)

plt.tight_layout()
plt.show()
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import truncexpon#, norm # exponencial truncada, normal
from scipy.special import xlogy
#%%
N_datos = 2000
tau_real = 2196.981 # ns
l_real = 1 / tau_real # ns-1
min_m, max_m = 50, 1700 # ns, intervalo de truncado
b_estandarizado = (max_m - min_m) / tau_real # parámetro que toma la función que me
# genera los datos de la exponencial
rng = np.random.default_rng(42) # rng se define una sola vez por fuera para que
# las simulaciones sean distintas. le pongo un valor fijo para que puedan ser reproducibles
n_bins = 30 # vamos a trabajar con histogramas de 30 bins.

def logl_distribucion(n_medidos, bordes): # le paso los datos medidos por bin y los bordes de cada bin
    # SciPy nos pide la escala (1/lambda) y el b estandarizado para evaluar
    escala_real = 1 / l_real
    b_std_real = (max_m - min_m) / escala_real
    cdf_evaluada = truncexpon.cdf(bordes, b=b_std_real, loc=min_m, scale=escala_real)
    # es la CDF evaluada en los bordes, 31 en total.
    p_i = np.diff(cdf_evaluada) # uso la CDF y la resta sucesiva entre los bordes
    # de los bines para hallar la probabilidad p_i
    nu_i = N_datos * p_i # eventos esperados en cada bin
    return 2 * np.sum(nu_i - n_medidos + xlogy(n_medidos, n_medidos / nu_i)) # xlogy maneja n_i = 0 sin generar NaN

def simular_experimento():
    x_medido = truncexpon.rvs(b=b_estandarizado, loc=min_m, scale=tau_real,
                              size=N_datos, random_state=rng) # los datos de la simulación
    n_obs, bin_edges = np.histogram(x_medido, bins=n_bins, range=(min_m, max_m))
    logl_simulado = logl_distribucion(n_obs, bin_edges)
    return logl_simulado

rng = np.random.default_rng(42) # rng se define una sola vez por fuera para que
cant_simulaciones = 100000 # hacemos 10**5 simulaciones, tarda bastante poco en simular.
logl_obtenidos = []

for i in range(cant_simulaciones):
    logl_obtenido = simular_experimento() # simulamos
    logl_obtenidos.append(logl_obtenido) # guardamos los resultados
    if (i + 1) % 100 == 0:
        print(f"Simulaciones procesadas: {i + 1}")
#%%
plt.rc("font", size=16)
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(logl_obtenidos, bins=100, density=True, alpha=0.6, color="C1", label="Simulaciones")
#x = np.linspace(0, logl_obtenidos.max(), 400)
#ax.plot(x, chi2.pdf(x, df=n_bins - 1), color="C0", lw=2.5, label=r"$\chi^2$ (29 g.l.)")
#ax.axvline(logl_medido, color="k", ls="--", label=f"Medido (p = {p_valor:.2f})")
ax.set_xlabel(r"- 2 log(L) [u.a.]")
ax.set_ylabel(r"PDF [u.a.]")
ax.tick_params(axis='y', labelsize=12)
ax.minorticks_on()
ax.legend(fontsize=12)
fig.tight_layout()
fig.show()
#%% esto no lo use al final.
"""
N_datos = 2000 # tiene que ser igual al N total de tus datos medidos
tau_real = 2196.981 # ns
l_real = 1 / tau_real # ns-1
min_m, max_m = 50, 1700 # ns, intervalo de truncado
b_estandarizado = (max_m - min_m) / tau_real
n_bins = 30
bordes = np.linspace(min_m, max_m, n_bins + 1)
rng = np.random.default_rng(42) # una sola vez, por fuera
cant_simulaciones = 1000

def logl_distribucion(n_medidos, bordes):
    cdf_evaluada = truncexpon.cdf(bordes, b=b_estandarizado, loc=min_m, scale=tau_real)
    p_i = np.diff(cdf_evaluada)
    nu_i = N_datos * p_i # eventos esperados en cada bin
    # -2 log L respecto del modelo saturado (elimina la constante que depende de n_i)
    return 2 * np.sum(nu_i - n_medidos + xlogy(n_medidos, n_medidos / nu_i))

def simular_experimento():
    x_medido = truncexpon.rvs(b=b_estandarizado, loc=min_m, scale=tau_real,
                              size=N_datos, random_state=rng)
    n_obs, bin_edges = np.histogram(x_medido, bins=bordes)
    return logl_distribucion(n_obs, bin_edges)

# --- dato medido: n_medidos es el histograma de tus datos reales con los mismos bordes ---
#logl_medido = logl_distribucion(n_medidos, bordes) # en los valores verdaderos, NO en el MLE

# --- distribución de -2 log L bajo la hipótesis ---
logl_obtenidos = np.array([simular_experimento() for _ in range(cant_simulaciones)])

#p_valor = np.mean(logl_obtenidos >= logl_medido)
#err_p = np.sqrt(p_valor * (1 - p_valor) / cant_simulaciones)
#print(f"p-valor = {p_valor:.3f} ± {err_p:.3f}")

# --- gráfico ---
plt.rc("font", size=16)
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(logl_obtenidos, bins=30, density=True, alpha=0.8, color="C1", label="Simulaciones")
x = np.linspace(0, logl_obtenidos.max(), 400)
#ax.plot(x, chi2.pdf(x, df=n_bins - 1), color="C0", lw=2.5, label=r"$\chi^2$ (29 g.l.)")
#ax.axvline(logl_medido, color="k", ls="--", label=f"Medido (p = {p_valor:.2f})")
ax.set_xlabel(r"- 2 log(L) [u.a.]")
ax.set_ylabel(r"PDF [u.a.]")
ax.tick_params(axis='y', labelsize=12)
ax.minorticks_on()
ax.legend(fontsize=12)
fig.tight_layout()
fig.show()


"""



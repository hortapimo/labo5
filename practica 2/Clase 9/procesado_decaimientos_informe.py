import matplotlib.pyplot as plt
import numpy as np
#import pandas as pd
from scipy.signal import find_peaks
import funciones as misf
from scipy.stats import truncexpon # exponencial truncada
from scipy.optimize import minimize # algoritmo que realiza la minimización
from scipy.special import xlogy
from scipy.stats import rv_histogram
plt.style.use('estiloGraficos2hist.mplstyle')
#%%
def extraer_delta_t(df):
    df =df.reset_index(drop=True)
    indices_pico_canal_1, _ = find_peaks(-df["canal 1 [mV]"], prominence=1, distance=len(df["canal 1 [mV]"]/2))
    # Si el canal 1 no tuvo pico, no podemos calcular la resta
    if len(indices_pico_canal_1) == 0:
        return None, None

    indices_pico_canal_2, prop_2 = find_peaks(-df["canal 2 [mV]"][indices_pico_canal_1[0]+30:], prominence=1, height=-np.inf, distance=len(df["canal 2 [mV]"][indices_pico_canal_1[0]+30:]))
    indices_pico_canal_3, prop_3 = find_peaks(-df["canal 3 [mV]"][indices_pico_canal_1[0]+30:], prominence=1, height=-np.inf, distance=len(df["canal 2 [mV]"][indices_pico_canal_1[0]+30:]))
    t1=df["tiempo [ns]"][indices_pico_canal_1]
    h2 = prop_2["peak_heights"][0] if len(indices_pico_canal_2) > 0 else -np.inf
    h3 = prop_3["peak_heights"][0] if len(indices_pico_canal_3) > 0 else -np.inf
    if h2 == -np.inf and h3 == -np.inf: # Si ninguno de los dos canales secundarios registró un pico post-muón
        return None, None
    if h2 > h3:
        indices_pico_canal_2 = indices_pico_canal_2[0]+ indices_pico_canal_1[0] + 30
        delta_t_21 = (df["tiempo [ns]"][indices_pico_canal_2] - t1.iloc[0])
        delta_t_31 = None
    else:
        indices_pico_canal_3 =indices_pico_canal_3[0]+ indices_pico_canal_1[0] + 30
        delta_t_31 = (df["tiempo [ns]"][indices_pico_canal_3] - t1.iloc[0]) 
        delta_t_21 = None
    return delta_t_21, delta_t_31
#%%
nombre_archivo = "decaimientos.parquet"
df = misf.abrir_parquet(nombre_archivo)
misf.obtenerInfoDataframe(df)
resultados = []

for id_dec,dfaux in df.groupby("#decaimiento"):
    print("N° = ",id_dec)
    if len(dfaux["canal 1 [mV]"])==1024:
        delta_t_aux = extraer_delta_t(dfaux)
        if delta_t_aux[0] != None:
            resultados.append(delta_t_aux[0])
            print("Canal 2:", delta_t_aux[0])
        if delta_t_aux[1] != None:
            resultados.append(delta_t_aux[1])
            print("Canal 3:", delta_t_aux[1])
    print("----------------")

nombre_archivo_3 = "decaimientos3raSemana.parquet"
df = misf.abrir_parquet(nombre_archivo_3)
misf.obtenerInfoDataframe(df)

for id_dec,dfaux in df.groupby("#decaimiento"):
    print("N° = ",id_dec)
    if len(dfaux["canal 1 [mV]"])==1024:
        delta_t_aux = extraer_delta_t(dfaux)
        if delta_t_aux[0] != None:
            resultados.append(delta_t_aux[0])
            print("Canal 2:", delta_t_aux[0])
        if delta_t_aux[1] != None:
            resultados.append(delta_t_aux[1])
            print("Canal 3:", delta_t_aux[1])
    print("----------------")

nombre_archivo_4 = "decaimientos4taSemana.parquet"
df = misf.abrir_parquet(nombre_archivo_4)
misf.obtenerInfoDataframe(df)

for id_dec,dfaux in df.groupby("#decaimiento"):
    print("N° = ",id_dec)
    if len(dfaux["canal 1 [mV]"])==1024:
        delta_t_aux = extraer_delta_t(dfaux)
        if delta_t_aux[0] != None:
            resultados.append(delta_t_aux[0])
            print("Canal 2:", delta_t_aux[0])
        if delta_t_aux[1] != None:
            resultados.append(delta_t_aux[1])
            print("Canal 3:", delta_t_aux[1])
    print("----------------")
#%%
#min_m, max_m = 50, 1491 # ns, intervalo de truncado
#nbins = 30
#resultados = [x for x in resultados_2 if x >= 100]
#n_obs3, bin_edges3 = np.histogram(resultados, bins=nbins, range=(min_m, max_m)) 
#fig1, ax1 = plt.subplots(figsize = (8,6))
#ax1.hist(resultados, bins = bin_edges3, edgecolor='black', alpha=0.9, label="Datos")
#ax1.set_xlabel(r"$\Delta t$ [ns]")
#ax1.set_ylabel("Cuentas")
#ax1.legend()
#fig1.tight_layout()
#fig1.show()
#%%
periodo_muestreo = 1350
min_m, max_m = 50, 1491 # ns, intervalo de truncado
tau_real = 2196.981 # ns
l_real = 1 / tau_real # ns-1
nbins = 30

def nu_i_ajuste(params, bordes): # calculo los nu_i esperados por bin
    N_fit, lam_fit = params
    # SciPy nos pide la escala (1/lambda) y el b estandarizado para evaluar
    escala_fit = 1 / lam_fit
    b_std_fit = (max_m - min_m) / escala_fit
    cdf_evaluada = truncexpon.cdf(bordes, b=b_std_fit, loc=min_m, scale=escala_fit)
    # es la CDF evaluada en los bordes, 31 en total.
    p_i = np.diff(cdf_evaluada) # uso la CDF y la resta sucesiva entre los bordes
    # de los bines para hallar la probabilidad p_i
    nu_i = N_fit * p_i # eventos esperados en cada bin
    return nu_i

def nll_poisson(params, n_obs, bordes, f_modelo):# defino la verosimilitud de poisson bineada
    # Calculamos los nu_i teóricos pasándole los parámetros de la función a elegir
    nu_i = f_modelo(params, bordes)
    nu_i = np.maximum(nu_i, 1e-10)# con esto evito que durante la minimización se
    return 2 * np.sum(nu_i - n_obs + xlogy(n_obs, n_obs / nu_i)) # xlogy maneja n_i = 0 sin generar NaN

def hessiano_numerico(f, x0, rel_step=1e-3): # para las incertezas
    x0 = np.asarray(x0, dtype=float)
    n = len(x0)
    h = rel_step * np.abs(x0) # paso relativo a cada parámetro (N ~ 1e2, lam ~ 1e-4)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            ei = np.zeros(n); ei[i] = h[i]
            ej = np.zeros(n); ej[j] = h[j]
            H[i, j] = (f(x0 + ei + ej) - f(x0 + ei - ej)
                       - f(x0 - ei + ej) + f(x0 - ei - ej)) / (4 * h[i] * h[j])
    return H
#%%
x_medido = resultados # los decaimientos
guess = [len(resultados), l_real]
n_obs, bin_edges = np.histogram(x_medido, bins=nbins, range=(min_m, max_m))
# con esto obtengo los eventos de cada bin y los bordes de cada bin
params_fit = minimize(fun=nll_poisson, x0=guess,  # aplico la minimización
    args=(n_obs, bin_edges, nu_i_ajuste),
    bounds=([0.1, None],[0.0001, None]), # le pedimos que sea estrictamente positivo
    method='L-BFGS-B') # esto es un método de "descenso por gradiente". solo le especifico
    # con qué método realizar la minimización.
nu_i_fit = nu_i_ajuste(params_fit.x, bin_edges) # calculo los nu_i ajustados
N_fit, lam_fit = params_fit.x
m_cov_fit = params_fit.hess_inv.todense()

f_nll = lambda params: nll_poisson(params, n_obs, bin_edges, nu_i_ajuste)
H_s = hessiano_numerico(f_nll, [N_fit, lam_fit])
m_cov_s = 2 * np.linalg.inv(H_s) # nll_poisson es -2lnL, por eso la cov. es 2*H^-1
error_N, error_lam = np.sqrt(np.diag(m_cov_s))
tau_fit = 1 / lam_fit
error_tau = error_lam / (lam_fit**2)

x_fit = np.linspace(min_m, max_m, 500)
pdf_fit = truncexpon.pdf(x_fit, b = (max_m - min_m) / tau_fit, loc=min_m, scale=tau_fit)
anchos_bines = np.diff(bin_edges)
centros_bines = (bin_edges[:-1] + bin_edges[1:]) / 2
factor_escala = N_fit * anchos_bines[0]
errores_cuentas = np.sqrt(nu_i_fit) # usamos la var o esperanza (es lo mismo).
 
fig1, ax1 = plt.subplots(figsize = (8,6))
ax1.hist(x_medido, bins = bin_edges, edgecolor='black', alpha=0.9)
ax1.errorbar(centros_bines,n_obs, yerr=errores_cuentas, fmt='.', color='black', label="Datos")
ax1.plot(x_fit,pdf_fit * factor_escala,lw=3,alpha=0.8, label="Ajuste")
ax1.plot([],[], " ", label=r"$\hat{\tau}$ = "f"({tau_fit:.0f} ± {error_tau:.0f} ns)")
ax1.plot([],[], " ", label=r"$\hat{N^{fit}}$ = "f"{N_fit:.0f} ± {error_N:.0f}")
ax1.set_xlabel("$\Delta t$ [ns]")
ax1.set_ylabel("Cuentas")
ax1.legend()
fig1.tight_layout()
fig1.savefig("decaimientos_ajustados_todos.png")
fig1.show()
#%%
resultados_2 = resultados
resultados = [x for x in resultados_2 if x >= 100]
periodo_muestreo = 1350
min_m, max_m = 100, 1491 # ns, intervalo de truncado
tau_real = 2196.981 # ns
l_real = 1 / tau_real # ns-1
nbins = 30

def nu_i_ajuste(params, bordes): # calculo los nu_i esperados por bin
    N_fit, lam_fit = params
    # SciPy nos pide la escala (1/lambda) y el b estandarizado para evaluar
    escala_fit = 1 / lam_fit
    b_std_fit = (max_m - min_m) / escala_fit
    cdf_evaluada = truncexpon.cdf(bordes, b=b_std_fit, loc=min_m, scale=escala_fit)
    # es la CDF evaluada en los bordes, 31 en total.
    p_i = np.diff(cdf_evaluada) # uso la CDF y la resta sucesiva entre los bordes
    # de los bines para hallar la probabilidad p_i
    nu_i = N_fit * p_i # eventos esperados en cada bin
    return nu_i

x_medido = resultados # los decaimientos
guess = [len(resultados), l_real]
n_obs, bin_edges = np.histogram(x_medido, bins=nbins, range=(min_m, max_m))
# con esto obtengo los eventos de cada bin y los bordes de cada bin
params_fit = minimize(fun=nll_poisson, x0=guess,  # aplico la minimización
    args=(n_obs, bin_edges, nu_i_ajuste),
    bounds=([0.1, None],[0.0001, None]), # le pedimos que sea estrictamente positivo
    method='L-BFGS-B') # esto es un método de "descenso por gradiente". solo le especifico
    # con qué método realizar la minimización.
nu_i_fit = nu_i_ajuste(params_fit.x, bin_edges) # calculo los nu_i ajustados
N_fit, lam_fit = params_fit.x
m_cov_fit = params_fit.hess_inv.todense()

f_nll = lambda params: nll_poisson(params, n_obs, bin_edges, nu_i_ajuste)
H_s = hessiano_numerico(f_nll, [N_fit, lam_fit])
m_cov_s = 2 * np.linalg.inv(H_s) # nll_poisson es -2lnL, por eso la cov. es 2*H^-1
error_N, error_lam = np.sqrt(np.diag(m_cov_s))
tau_fit = 1 / lam_fit
error_tau = error_lam / (lam_fit**2)

print(r"$\hat{\tau}$ = "f"({tau_fit:.0f} ± {error_tau:.0f} ns)")
print(r"$\hat{N_{fit}}$ = "f"{N_fit:.0f} ± {error_N:.0f}")
x_fit = np.linspace(min_m, max_m, 500)
pdf_fit = truncexpon.pdf(x_fit, b = (max_m - min_m) / tau_fit, loc=min_m, scale=tau_fit)
anchos_bines = np.diff(bin_edges)
centros_bines = (bin_edges[:-1] + bin_edges[1:]) / 2
factor_escala = N_fit * anchos_bines[0]
errores_cuentas = np.sqrt(nu_i_fit) # usamos la var o esperanza (es lo mismo).
 
fig1, ax1 = plt.subplots(figsize = (8,6))
ax1.hist(x_medido, bins = bin_edges, edgecolor='black', alpha=0.9)
ax1.errorbar(centros_bines,n_obs, yerr=errores_cuentas, fmt='.', color='black', label="Datos")
ax1.plot(x_fit,pdf_fit * factor_escala,lw=3,alpha=0.8, label="Ajuste")
ax1.plot([],[], " ", label=r"$\hat{\tau}$ = (2000 ± 300) ns")
ax1.plot([],[], " ", label=r"$\hat{N_{fit}}$ = 1620 ± 40")
ax1.set_xlabel("$\Delta t$ [ns]")
ax1.set_ylabel("Cuentas")
ax1.set_xlim(50,1550)
ax1.set_ylim(0,90)
ax1.legend()
fig1.tight_layout()
fig1.savefig("decaimientos_ajustados_todos_recortados_informe.png")
fig1.show()
#%%
# ahora queremos testear la bondad del ajuste, para lo cual hacemos simulaciones.
N_datos = len(x_medido)
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

#%%
def simular_experimento():
    x_medido = truncexpon.rvs(b=b_estandarizado, loc=min_m, scale=tau_real,
                              size=N_datos, random_state=rng) # los datos de la simulación
    n_obs, bin_edges = np.histogram(x_medido, bins=n_bins, range=(min_m, max_m))
    logl_simulado = nll_poisson([N_datos,l_real], n_obs, bin_edges, nu_i_ajuste)
    return logl_simulado
rng = np.random.default_rng(42) # rng se define una sola vez por fuera para que
cant_simulaciones = 100000 # hacemos 10**5 simulaciones, tarda bastante poco en simular.
logl_obtenidos = []

for i in range(cant_simulaciones):
    logl_obtenido = simular_experimento() # simulamos
    logl_obtenidos.append(logl_obtenido) # guardamos los resultados
    if (i + 1) % 10000 == 0:
        print(f"Simulaciones procesadas: {i + 1}")
#%%
logl_medido = nll_poisson([N_fit,lam_fit], n_obs, bin_edges, nu_i_ajuste)
print(logl_medido)
h0_rv = rv_histogram(np.histogram(logl_obtenidos, bins="auto"))
beta = h0_rv.cdf(logl_medido)
p_val = 1 - beta
print(f"{beta:.2f}")
print(f"{p_val:.2f}")
#%%
logl_obtenidos1 = np.array(logl_obtenidos)
logl_recorte = logl_obtenidos1[logl_obtenidos1 > logl_medido]
plt.rc("font", size=16)
fig, ax = plt.subplots(figsize=(7, 6))
alturas, bins, _ = ax.hist(logl_obtenidos1, bins=100, histtype="step", density=True,
                           alpha=0.6, color="C1")
mascara = bins[1:] > logl_medido
ax.hist(bins[:-1][mascara], bins=bins, weights=alturas[mascara],
        alpha=0.6, color="C1", label="Distribución simulada")
ax.axvline(logl_medido, color="black", ls="--", label=r"$\mathscr{L}_{obs}$ = "f"{logl_medido:.0f}")
ax.plot([],[]," ", label=f"P valor = {p_val:.2f}")
ax.set_xlabel(r"$\mathscr{L}$ [u.a.]")
ax.set_ylabel(r"PDF [u.a.]")
ax.set_xlim(4,66)
ax.set_ylim(0,0.056)
ax.tick_params(axis='y', labelsize=12)
ax.minorticks_on()
ax.legend()#(fontsize=12)
ax.grid(False)
fig.tight_layout()
fig.savefig("pvalor_verosimilitud_todos_recortados_opcion1.png")
fig.show()
#%%
logl_obtenidos1 = np.array(logl_obtenidos)
plt.rc("font", size=16)
fig, ax = plt.subplots(figsize=(7, 6))
alturas, bins, _ = ax.hist(logl_obtenidos1, bins=100,density=True,
                           alpha=0.6, color="C1", label="Distribución simulada")
ax.axvline(logl_medido, color="black", ls="--", label=r"$\mathscr{L}_{obs}$ = "f"{logl_medido:.0f}")
ax.plot([],[]," ", label=f"P valor = {p_val:.2f}")
ax.set_xlabel(r"$\mathscr{L}$ [u.a.]")
ax.set_ylabel(r"PDF [u.a.]")
ax.set_xlim(4,66)
ax.set_ylim(0,0.056)
ax.tick_params(axis='y', labelsize=12)
ax.minorticks_on()
ax.legend()
ax.grid(False)
fig.tight_layout()
fig.savefig("pvalor_verosimilitud_todos_recortados_opcion2.png")
fig.show()
#%%
logl_obtenidos1 = np.array(logl_obtenidos)
logl_recorte = logl_obtenidos1[logl_obtenidos1 > logl_medido]
plt.rc("font", size=16)
fig, ax = plt.subplots(figsize=(7, 6))
alturas, bins, _ = ax.hist(logl_obtenidos1, bins=100,density=True,
                           alpha=0.6, color="C1", label="Distribución simulada")
pesos = np.ones_like(logl_recorte) / (len(logl_obtenidos1) * np.diff(bins)[0])
ax.hist(logl_recorte, bins=bins, weights=pesos,
        alpha=0.8, color="C1", hatch='//',label="Área integrada")
ax.axvline(logl_medido, color="black", ls="--", label=r"$\mathscr{L}_{obs}$ = "f"{logl_medido:.0f}")
ax.plot([],[]," ", label=f"P valor = {p_val:.2f}")
ax.set_xlabel(r"$\mathscr{L}$ [u.a.]")
ax.set_ylabel(r"PDF [u.a.]")
ax.set_xlim(4,66)
ax.set_ylim(0,0.056)
ax.tick_params(axis='y', labelsize=12)
ax.minorticks_on()
ax.legend()#(fontsize=12)
ax.grid(False)
fig.tight_layout()
fig.savefig("pvalor_verosimilitud_todos_recortados_opcion3_informe.png")
fig.show()

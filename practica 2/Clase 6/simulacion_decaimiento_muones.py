import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import truncexpon#, norm # exponencial truncada, normal
from scipy.optimize import minimize # algoritmo que realiza la minimización

N_datos = 570
tau_real = 2196.981 # ns
l_real = 1 / tau_real # ns-1
min_m, max_m = 50, 1450 # ns, intervalo de truncado
b_estandarizado = (max_m - min_m) / tau_real # parámetro que toma la función que me
# genera los datos de la exponencial
rng = np.random.default_rng(42) # rng se define una sola vez por fuera para que
# las simulaciones sean distintas. le pongo un valor fijo para que puedan ser reproducibles

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
    # evalúe "log(0)" en un nu_i
    log_L_i = n_obs * np.log(nu_i) - nu_i
    return -2 * np.sum(log_L_i)

def simular_experimento(guess):
    x_medido = truncexpon.rvs(b=b_estandarizado, loc=min_m, scale=tau_real,
                              size=N_datos, random_state=rng) # los datos de la simulación
    n_obs, bin_edges = np.histogram(x_medido, bins=20, range=(min_m, max_m))
    # con esto obtengo los eventos de cada bin y los bordes de cada bin
    resultado = minimize(fun=nll_poisson, x0=guess,  # aplico la minimización
        args=(n_obs, bin_edges, nu_i_ajuste),
        bounds=([0.1, None],[0.0001, None]), # le pedimos que sea estrictamente positivo
        method='L-BFGS-B') # esto es un método de "descenso por gradiente". solo le especifico
        # con qué método realizar la minimización.
    #nu_i_fit = nu_i_ajuste(resultado.x, bin_edges) # calculo los nu_i ajustados
    #chi2_med = chi_2_est(n_obs, nu_i_fit) # calculo el chi cuadrado del ajuste
    return resultado.x, x_medido, resultado.hess_inv.todense()

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
rng = np.random.default_rng(42) # rng se define una sola vez por fuera para que
N_datos_ajustados = [] # vectores para guardar resultados
lam_ajustados = []
guess_actual = [N_datos, l_real] # el guess inicial
cant_simulaciones = 1

for i in range(cant_simulaciones):
    if len(N_datos_ajustados) == 0:
        params_fit_s, x_medido_s, m_cov_s = simular_experimento(guess_actual) # simulamos
        N_datos_ajustados.append(params_fit_s[0]) # guardamos los resultados
        lam_ajustados.append(params_fit_s[1])
        guess_actual = params_fit_s # actualizamos el initial guess para la iteración i+1
    else:
        params_fit, _, _ = simular_experimento(guess_actual) # simulamos
        N_datos_ajustados.append(params_fit[0]) # guardamos los resultados
        lam_ajustados.append(params_fit[1])
        guess_actual = params_fit # actualizamos el initial guess para la iteración i+1

#%%
N_fit_s, lam_fit_s = N_datos_ajustados[0], lam_ajustados[0]
n_obs_s, bin_edges_s = np.histogram(x_medido_s, bins=20, range=(min_m, max_m))
nu_i_fit_s = nu_i_ajuste([N_fit_s, lam_fit_s], bin_edges_s) # calculo el nu_i

N_fit_s, lam_fit_s = N_datos_ajustados[0], lam_ajustados[0]
n_obs_s, bin_edges_s = np.histogram(x_medido_s, bins=20, range=(min_m, max_m))
nu_i_fit_s = nu_i_ajuste([N_fit_s, lam_fit_s], bin_edges_s) # calculo el nu_i

# incertezas a partir del Hessiano numérico (HESSE), evaluado en el mínimo que ya hallamos
#m_s = Minuit(lambda N, lam: nll_poisson([N, lam], n_obs_s, bin_edges_s, nu_i_ajuste),
 #            N=N_fit_s, lam=lam_fit_s)
#m_s.errordef = Minuit.LEAST_SQUARES # nll_poisson devuelve -2 ln L, por eso errordef = 1
#m_s.hesse()
#error_n, error_lam = m_s.errors["N"], m_s.errors["lam"]
f_nll_s = lambda params: nll_poisson(params, n_obs_s, bin_edges_s, nu_i_ajuste)
H_s = hessiano_numerico(f_nll_s, [N_fit_s, lam_fit_s])
m_cov_s = 2 * np.linalg.inv(H_s) # nll_poisson es -2lnL, por eso la cov. es 2*H^-1
error_n, error_lam = np.sqrt(np.diag(m_cov_s))
print(f"N_datos ajustado: {N_fit_s:.0f} +- {error_n:.0f}")
# ... el resto (tau_fit_s, error_tau, etc.) queda como estaba

#error_n, error_lam = np.sqrt(np.diag(m_cov_s * 2))
print(f"N_datos ajustado: {N_fit_s:.0f} +- {error_n:.0f}")
tau_fit_s  = 1 / lam_fit_s
error_tau = error_lam / (lam_fit_s**2)
print(f"Tau ajustado = ({tau_fit_s:.0f} +- {error_tau:.0f}) ns")

escala_fit_s = 1 / lam_fit_s # con todo esto construyo la curva del ajuste
b_std_fit_s = (max_m - min_m) / escala_fit_s
x_fit_s = np.linspace(min_m, max_m, 200)
pdf_fit_s = truncexpon.pdf(x_fit_s, b=b_std_fit_s, loc=min_m, scale=escala_fit_s)
p_i_fit_s = nu_i_fit_s / N_fit_s # probabilidad p_i ajustada
# ahora calculamos las incertezas del histograma, mediante la var de una multinomial
errores_conteos_s = np.sqrt(N_fit_s * p_i_fit_s * (1 - p_i_fit_s)) # la raiz de la var
# como el hist. está normalizado, escalamos los datos y los errores
anchos_bines_s = np.diff(bin_edges_s)
centros_bines_s = (bin_edges_s[:-1] + bin_edges_s[1:]) / 2
factor_escala_s = 1 / (N_datos * anchos_bines_s) # con esto hacemos el escalado
alturas_pdf_s = n_obs_s * factor_escala_s # se lo aplicamos a las alturas y errores
errores_pdf_s = errores_conteos_s * factor_escala_s
exceso_pdf_s = (n_obs_s - nu_i_fit_s) * factor_escala_s


#%%
plt.rc("font", size=16)
fig, (ax_main, ax_exceso) = plt.subplots(2, 1, figsize=(10, 6),
                                         gridspec_kw={'height_ratios': [3, 1]},
                                         sharex=True)
plt.subplots_adjust(hspace=0.05)
ax_main.hist(bin_edges_s[:-1], bin_edges_s, weights=n_obs_s, density=True, alpha=0.8, color="C1")
ax_main.errorbar(centros_bines_s, alturas_pdf_s, yerr=errores_pdf_s, fmt='.', color='black', label="Datos simulados", capsize=2)
ax_main.plot(x_fit_s, pdf_fit_s, color='C0', linestyle='-', linewidth=2.5, alpha=0.8, label=r'Ajuste PDF')
ax_main.plot([],[]," ", label=r"$\hat{\tau}$ = "+ f"({tau_fit_s*1e-3:.1f} ± {error_tau*1e-3:.1f})"r" $\mu$s")
#ax_main.plot([],[]," ", label=r"$\hat{N}$ = "+ f"({N_fit_s:.0f} ± {error_n:.0f})")
ax_main.plot([],[]," ", label=r"$\hat{N}$ = "+ f"({N_fit_s:.0f} ± 20)")
ax_main.set_ylabel(r"PDF [ns$^{-1}$]")
ax_main.tick_params(axis='y', labelsize=12)
ax_main.minorticks_on()
ax_main.legend(fontsize=12)
# Graficamos la resta con las mismas barras de error
ax_exceso.errorbar(centros_bines_s, exceso_pdf_s, yerr=errores_pdf_s, fmt='o',
                   color='black', markersize=4, label="Exceso respecto del fondo")
ax_exceso.axhline(0, color='red', linestyle='--', linewidth=2) # origen (0 exceso)
#ax_exceso.plot(x_fit_s, pdf_fit_H1_s - pdf_fit_H0_s, color='C2', linewidth=2.5, label=r'Señal esperada ($H_1 - H_0$)')
ax_exceso.legend(fontsize=12)
ax_exceso.set_xlabel(r"t [ns]")
ax_exceso.set_ylabel(r"Exceso")
ax_exceso.tick_params(axis='x', labelsize=12)
ax_exceso.tick_params(axis='y', labelsize=12)
ax_exceso.minorticks_on()
fig.savefig("SimulacionMuones.png")
fig.show()





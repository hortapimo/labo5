import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import scipy.odr as odr # salta una advertencia, ignorarla
from scipy.stats import chi2

plt.style.use('./estiloGraficos.mplstyle')

#%%
#[429., 439., 442., 449., 464., 479., 507., 518., 531., 547., 564., 575.,
# 587., 605., 618., 632., 642., 662., 677., 690., 707.]
#[16., 18., 14., 14., 18., 35., 24., 25., 27., 30., 31., 32., 35., 34., 35.,
# 36., 40., 41., 40., 43., 44.]
#%%
# método 1
# aca los potenciales desde 420 nm hasta 690 nm con paso de 30 nm (10 puntos)
l_onda_pedidos_m1 = np.array([420., 430., 435., 450., 465., 480., 495., 510., 525., 540., 555., 570.,
 585., 600., 615., 630., 645., 660., 675., 690., 705.]) # asi hay registro  # nm
l_onda_m1 = np.array([429., 449.,479., 518.,547., 575.,605.,632.,662., 690.]) # nm
e_l_onda_m1 = np.array([16., 14., 35., 25., 30., 32., 34.,  36., 41.,  43.]) # nm
 # uso como error al ancho de banda

potencial_corte_m1 = np.array([-0.94827586, -1.03448276, -0.84482759, -0.77586207, -0.67241379, -0.5862069,
 -0.55862069, -0.53103448, -0.6137931,  -0.6137931 ]) # V
error_potencial_m1 = np.array([0.04310345, 0.04310345, 0.03448276, 0.03448276, 0.02586207, 0.01724138,
 0.0137931,  0.0137931,  0.0137931,  0.0137931])

#%%
# método 2
l_onda_m2 = np.array([442, 547, 575, 618]) # nm
e_l_onda_m2 = np.array([14, 30, 32, 40]) # nm
 # uso como error al ancho de banda
potencial_corte_m2 = np.array([-1.034, -1.121, -0.69 , -0.862]) # V
error_potencial_m2 = np.array([0.01 , 0.011, 0.007, 0.009])
#%%
c_luz = 299792458 # m s-1
c_luz = c_luz*1e9 # nm s-1
carga_e = 1.602176634 *1e-19 # C
datos_ev0_m1 = carga_e * potencial_corte_m1 # lo paso así mas fácil
error_ev0_m1 = carga_e * error_potencial_m1

nu_m1 = c_luz / l_onda_m1 # s-1
e_nu_m1 = np.abs((c_luz/(l_onda_m1**2)) * e_l_onda_m1) # s-1
e_rel_ev0_m1 = np.mean(np.abs((error_ev0_m1/datos_ev0_m1) * 100))
e_rel_nu_m1 = np.mean(np.abs((e_nu_m1/nu_m1) * 100))
print(f"Error rel. ev0 método 1: {e_rel_ev0_m1:.2f} %")
print(f"Error rel. nu método 1: {e_rel_nu_m1:.2f} %")


datos_ev0_m2 = carga_e * potencial_corte_m2 # lo paso así mas fácil
error_ev0_m2 = carga_e * error_potencial_m2
nu_m2 = c_luz / l_onda_m2 # s-1
e_nu_m2 = np.abs((c_luz/(l_onda_m2**2)) * e_l_onda_m2) # s-1
e_rel_ev0_m2 = np.mean(np.abs((error_ev0_m2/datos_ev0_m2) * 100))
e_rel_nu_m2 = np.mean(np.abs((e_nu_m2/nu_m2) * 100))
print(f"Error rel. ev0 método 2: {e_rel_ev0_m2:.2f} %")
print(f"Error rel. nu método 2: {e_rel_nu_m2:.2f} %")

def lineal(x,a,b):
    return a*x + b

#%%
popt, pcov = curve_fit(lineal, datos_ev0_m1, nu_m1,sigma=e_nu_m1,
                       absolute_sigma=True, p0=[-1.5e33, 1e14],
                       maxfev=6000,xtol=1e-10,ftol=1e-10)
a_fit_m1, b_fit_m1 = popt
a_err_m1, b_err_m1 = np.sqrt(np.diag(pcov))

h_m1 = 1 / np.abs(a_fit_m1)
e_h_m1 = a_err_m1 / (a_fit_m1**2)
phi_m1 = b_fit_m1 * h_m1
e_phi_m1 = np.sqrt(((h_m1*b_err_m1)**2) + ((b_fit_m1*e_h_m1)**2))
print(f"h método 1: ({h_m1:.1e} +- {e_h_m1:.1e}) J s")
print(f"phi método 1: ({phi_m1:.1e} +- {e_phi_m1:.1e}) J")

popt, pcov = curve_fit(lineal, datos_ev0_m2, nu_m2,sigma=e_nu_m2,
                       absolute_sigma=True, p0=[-1.5e33, 1e14],
                       maxfev=6000,xtol=1e-10,ftol=1e-10)
a_fit_m2, b_fit_m2 = popt
a_err_m2, b_err_m2 = np.sqrt(np.diag(pcov))

h_m2 = 1 / np.abs(a_fit_m2)
e_h_m2 = a_err_m2 / (a_fit_m2**2)
phi_m2 = b_fit_m2 * h_m2
e_phi_m2 = np.sqrt(((h_m2*b_err_m2)**2) + ((b_fit_m2*e_h_m2)**2))
print(f"h método 2: ({h_m2:.1e} +- {e_h_m2:.1e}) J s")
print(f"phi método 2: ({phi_m2:.1e} +- {e_phi_m2:.1e}) J")

#%%
y_fit_m1 = lineal(datos_ev0_m1,a_fit_m1,b_fit_m1)
y_fit_m2 = lineal(datos_ev0_m2,a_fit_m2,b_fit_m2)
res_m1 = nu_m1 - y_fit_m1
res_m2 = nu_m2 - y_fit_m2

dof_m1 = len(nu_m1) - 2
# Chi-cuadrado: Suma de los residuos al cuadrado sobre la incerteza al cuadrado
chi_2red_m1 = np.sum((res_m1 / e_nu_m1)**2) / dof_m1
# El p-valor se calcula con la función de supervivencia (sf) de la distribución chi2
p_valor_m1 = chi2.sf(chi_2red_m1, dof_m1)

print(f"Chi-2 red. método 1: {chi_2red_m1:.2f}")
print(f"p-valor método 1: {p_valor_m1:.4e}")

# --- Método 2 ---
dof_m2 = len(nu_m2) - 2
chi_2red_m2 = np.sum((res_m2 / e_nu_m2)**2) / dof_m2
p_valor_m2 = chi2.sf(chi_2red_m2, dof_m2)

print(f"Chi-cuadrado método 2: {chi_2red_m2:.2f}")
print(f"p-valor método 2: {p_valor_m2:.4e}\n")

fig, (ax, ax_res) = plt.subplots(2, 1, figsize=(8,8), sharex=True, 
                                    gridspec_kw={'height_ratios': [3, 1]})
ax.errorbar(datos_ev0_m1,nu_m1, yerr=e_nu_m1, fmt="o", label="Datos método 1",color="C0")
ax.errorbar(datos_ev0_m2,nu_m2, yerr=e_nu_m2, fmt="o", label="Datos método 2",color="C1")
ax.plot(datos_ev0_m1, y_fit_m1, 
        label=r"$\chi_{\nu}^2$ = "f"{chi_2red_m1:.1f} | P = {p_valor_m1:.1e}", c="C0", alpha=0.8, lw=3)
ax.plot(datos_ev0_m2, y_fit_m2,
        label=r"$\chi_{\nu}^2$ = "f"{chi_2red_m2:.1f} | P = {p_valor_m2:.1e}", c="C1", alpha=0.8, lw=3)
ax.set_xlabel(r"e$V_0$ [J]")
ax.set_ylabel(r"$\nu$ [$s^{-1}$]")
ax.legend()
ax_res.errorbar(datos_ev0_m1, res_m1, yerr=e_nu_m1, fmt="o", color="C0")
ax_res.errorbar(datos_ev0_m2, res_m2, yerr=e_nu_m2, fmt="o", color="C1")
ax_res.axhline(0, color='black', linestyle='--', alpha=0.7)
ax_res.set_xlabel(r"e$V_0$ [J]")
ax_res.set_ylabel(r"Residuos [$s^{-1}$]")
fig.tight_layout()
fig.savefig("AjustePlanckDosCriteriosCuadradosMinimos.png")
fig.show()

#%%
def lineal_odr(B, x):
    return B[0]*x + B[1]
modelo = odr.Model(lineal_odr)
data_m1 = odr.RealData(nu_m1, datos_ev0_m1, sx=e_nu_m1, sy=error_ev0_m1)
# beta0: [pendiente (h), ordenada (-phi)]
odr_obj_m1 = odr.ODR(data_m1, modelo, beta0=[6.626e-34, -1e-19])
salida_m1 = odr_obj_m1.run()

a_odr_m1, b_odr_m1 = salida_m1.beta
a_err_odr_m1, b_err_odr_m1 = salida_m1.sd_beta

# Asignación directa de parámetros físicos
h_odr_m1 = a_odr_m1
e_h_odr_m1 = a_err_odr_m1
phi_odr_m1 = np.abs(b_odr_m1)
e_phi_odr_m1 = b_err_odr_m1

# --- ODR Método 2 ---
data_m2 = odr.RealData(nu_m2, datos_ev0_m2, sx=e_nu_m2, sy=error_ev0_m2)
odr_obj_m2 = odr.ODR(data_m2, modelo, beta0=[6.626e-34, -1e-19])
salida_m2 = odr_obj_m2.run()

a_odr_m2, b_odr_m2 = salida_m2.beta
a_err_odr_m2, b_err_odr_m2 = salida_m2.sd_beta

h_odr_m2 = a_odr_m2
e_h_odr_m2 = a_err_odr_m2
phi_odr_m2 = np.abs(b_odr_m2)
e_phi_odr_m2 = b_err_odr_m2

print("--- AJUSTE ODR (X: Frecuencias | Y: Energía) ---")
print(f"h ODR método 1: ({h_odr_m1:.2e} ± {e_h_odr_m1:.2e}) J s")
print(f"phi ODR método 1: ({phi_odr_m1:.2e} ± {e_phi_odr_m1:.2e}) J")
print(f"h ODR método 2: ({h_odr_m2:.2e} ± {e_h_odr_m2:.2e}) J s")
print(f"phi ODR método 2: ({phi_odr_m2:.2e} ± {e_phi_odr_m2:.2e}) J")

# Evaluamos las curvas de ajuste 
y_odr_m1 = lineal_odr(salida_m1.beta, nu_m1)
y_odr_m2 = lineal_odr(salida_m2.beta, nu_m2)

# --- Chi Cuadrado y P-valor ODR ---
dof_m1 = len(nu_m1) - 2
chi_2red_odr_m1 = salida_m1.res_var  # ODR entrega el chi-cuadrado reducido acá
p_valor_odr_m1 = chi2.sf(salida_m1.sum_square, dof_m1)  # sum_square es el chi-cuadrado total

dof_m2 = len(nu_m2) - 2
chi_2red_odr_m2 = salida_m2.res_var
p_valor_odr_m2 = chi2.sf(salida_m2.sum_square, dof_m2)

print(f"Chi-2 red. ODR método 1: {chi_2red_odr_m1:.2f}")
print(f"p-valor ODR método 1: {p_valor_odr_m1:.4e}")
print(f"Chi-2 red. ODR método 2: {chi_2red_odr_m2:.2f}")
print(f"p-valor ODR método 2: {p_valor_odr_m2:.4e}\n")

# --- Gráfico ODR (Un solo panel) ---
fig, ax = plt.subplots(figsize=(8,6))

# Panel Principal 
ax.errorbar(nu_m1, datos_ev0_m1, xerr=e_nu_m1, yerr=error_ev0_m1, fmt="o", label="Datos método 1", color="C0")
ax.errorbar(nu_m2, datos_ev0_m2, xerr=e_nu_m2, yerr=error_ev0_m2, fmt="o", label="Datos método 2", color="C1")

ax.plot(nu_m1, y_odr_m1, 
        label=r"$\chi_{\nu}^2$ = "f"{chi_2red_odr_m1:.1f} | P = {p_valor_odr_m1:.1e}", 
        c="C0", alpha=0.8, lw=3)
ax.plot(nu_m2, y_odr_m2, 
        label=r"$\chi_{\nu}^2$ = "f"{chi_2red_odr_m2:.1f} | P = {p_valor_odr_m2:.1e}", 
        c="C1", alpha=0.8, lw=3)

ax.set_xlabel(r"$\nu$ [$s^{-1}$]")
ax.set_ylabel(r"e$V_0$ [J]")
ax.legend()
ax.grid(which="major")
ax.grid(which="minor", alpha=0.3)
ax.minorticks_on()
fig.tight_layout()
fig.savefig("AjustePlanckDosCriteriosODR.png")
plt.show()








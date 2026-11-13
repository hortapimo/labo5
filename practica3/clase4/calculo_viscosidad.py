import numpy as np

# calculo viscosidad

k_b = 1.380649e-23
T, dT = 293.15, 1.0
R_h, dR = 1.5e-6, 5e-7
A, dA = 0.15e-12, 0.03e-12
D = A / 2

eta = k_b * T / (6 * np.pi * R_h * D)
rel = np.sqrt((dT/T)**2 + (dR/R_h)**2 + (dA/A)**2)
d_eta = eta * rel

print(f"eta = {eta:.3g} ± {d_eta:.2g} Pa·s  (error relativo {rel:.2f})")
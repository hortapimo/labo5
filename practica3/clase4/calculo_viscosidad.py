import numpy as np

# calculo viscosidad

A = 0.15e-12          # m²/s  (0.15 µm²/s)
D = A / 2 #ACLARAR ESTO, NO ES A / 4!!!!
k_b = 1.380649e-23
T = 293.15
R_h = 1.5e-6
aux_1 = (k_b * T)
aux_2 = (6 * np.pi * R_h * D)
etha = aux_1 / aux_2

print(f"{etha:.3g} Pa·s")   # ≈ 1.9e-3 Pa·s = 1.9 mPa·s
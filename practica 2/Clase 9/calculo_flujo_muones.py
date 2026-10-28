import numpy as np
l = 209
d1 = 4.5 # cm
d2 = d1 # cm
d_e = 0.2 # cm
A = d1**2 # cm**2
A_e = 2*d1*d_e # cm**2
print(f"A = ({A:.1f} +- {A_e:.1f}) cm^2")
dt = 15 # min
dt_e = 1 # min
eta_1 = eta_2 = eta_3 = 0.95
eta_e = 0.01
phi = (l)/((eta_1**3) * A * dt)
d_eta = (3*l)/((eta_1**4) * A * dt)
d_A = (l)/((eta_1**3) * (A**2) * dt)
d_dt = (l)/((eta_1**3) * A * (dt**2))
phi_e = np.sqrt(((d_eta*eta_e)**2) + ((d_A*A_e)**2) + ((d_dt*dt_e)**2))
print(f"phi = ({phi:.2f} +- {phi_e:.2f}) muones min^-1 cm^-2")







import numpy as np

tiempo = np.array([5.1,5.1,7,5]) # s
t_e = 0.2 # s
aceleración = 0.005 # mm s**-2
velocidad = aceleración * t_e # mm s**-1
dist_px = 0.094 * 1e3 # mm px**-1
d_px_e = 0.005 * 1e3 # mm px**-1
diametro = np.array([31,33,34,34]) * dist_px # mm








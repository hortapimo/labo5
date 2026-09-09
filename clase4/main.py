import numpy as np
from claseLockIn import SR830
from adquisicion import sweep_aux_voltage, save_dataset_csv
import matplotlib.pyplot as plt

#%% parametros
RESOURCE_LOCKIN = "GPIB0::8::INSTR"
OUTPUT_FILENAME = "barridoFinal_435nm_5V_colimado_Apertura5.txt"
VOLTAGES = np.linspace(-5, -0.5, 30)
SAMPLES_PER_POINT = 1
SETTLE_TIME = 2.5        # Segundos entre pasos de tensión
FIRST_SETTLE_TIME = 5.0    # Segundos en el punto inicial

#%% medimos
print(f"Conectando al Lock-In en {RESOURCE_LOCKIN}...")
with SR830(RESOURCE_LOCKIN) as lockin:
    print(f"Instrumento detectado: {lockin.idn()}")

    df_medicion = sweep_aux_voltage(
    lockin=lockin,
    voltages=VOLTAGES,
    aux_channel=1,
    samples_per_point=SAMPLES_PER_POINT,
    settle_time=SETTLE_TIME,
    first_point_settle_time=FIRST_SETTLE_TIME,
        )
    save_dataset_csv(df_medicion, OUTPUT_FILENAME)

#%% analisamos datos ..

fig,ax=plt.subplots()
ax.scatter(df_medicion['voltage'],df_medicion["x"])


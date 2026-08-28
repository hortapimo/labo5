import numpy as np
from claseLockIn import SR830
from adquisicion import sweep_aux_voltage, save_dataset


#%% parametros
RESOURCE_LOCKIN = "GPIB0::8::INSTR"
OUTPUT_FILENAME = "barrido_voltajes_-5_7_420nm.txt"
VOLTAGES = np.linspace(-5, 7, 34)
SAMPLES_PER_POINT = 10
SETTLE_TIME = 4.0          # Segundos entre pasos de tensión
FIRST_SETTLE_TIME = 7.0    # Segundos en el punto inicial

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
    save_dataset(df_medicion, OUTPUT_FILENAME)

#%% analisamos datos ..



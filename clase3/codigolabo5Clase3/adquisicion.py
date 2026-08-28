
import time
import numpy as np
import pandas as pd
from claseLockIn import SR830

def sweep_aux_voltage(
    lockin: SR830,
    voltages: np.ndarray,
    aux_channel: int = 1,
    samples_per_point: int = 10,
    settle_time: float = 4.0,
    first_point_settle_time: float = 7.0,
    sample_delay: float = 0.1,
    progress_bar: bool = True
) -> pd.DataFrame:
    """
    Realiza un barrido de voltaje sobre la salida auxiliar del Lock-in y adquiere muestras (X, Y).
    """
    records = []
    print(f"Iniciando barrido de {len(voltages)} puntos de tensión...")
    
    for idx, v in enumerate(voltages):
        lockin.set_aux_out(aux_channel, v)
        lockin.auto_scale()
        # Tiempo de estabilización (más largo en el primer punto si se desea)
        wait = first_point_settle_time if idx == 0 else settle_time
        time.sleep(wait)
        for _ in range(samples_per_point):
            time.sleep(sample_delay)
            x, y = lockin.get_measurement(is_xy=True)
            records.append({
                "voltage": v,
                "x": x,
                "y": y,
                "r": np.sqrt(x**2 + y**2)
            })
        if progress_bar:
            print(f"\rProgreso: [{idx + 1}/{len(voltages)}] V = {v:6.2f} V", end="", flush=True)
    print("\n¡Barrido completado!")
    return pd.DataFrame(records)


def save_dataset_csv(df: pd.DataFrame, filename: str):
    df.to_csv(filename, index=False)
    print(f"Datos guardados exitosamente en: {filename}")
"""
Driver para Amplificador Lock-In Stanford Research Systems SR830.
"""
import time
import pyvisa as visa
class SR830:
    """Clase para el control del Lock-In SR830 a través de PyVISA."""
    SCALE_VALUES = (
        2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9,
        1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6,
        1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1.0
    ) #en Volt
    TIME_CONSTANT_VALUES = (
        10e-6, 30e-6, 100e-6, 300e-6, 1e-3, 3e-3, 10e-3, 30e-3, 100e-3, 300e-3,
        1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1e3, 3e3, 10e3, 30e3
    )  # en Segundos
    def __init__(self, resource_name: str, rm: visa.ResourceManager = None):
        if rm is None:
            rm = visa.ResourceManager()
        self._inst = rm.open_resource(resource_name)
        self.lock_front_panel(True)
        time.sleep(0.5)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    def close(self):
        """Libera el panel frontal y cierra la conexión VISA."""
        try:
            self.lock_front_panel(False)
            self._inst.close()
        except Exception:
            pass
    def lock_front_panel(self, lock: bool = True):
        """Bloquea (True) o desbloquea (False) el panel frontal."""
        self._inst.write(f"LOCL {2 if lock else 0}")
    def idn(self) -> str:
        """Devuelve la identificación del instrumento."""
        return self._inst.query("*IDN?").strip()
    # --- Configuración ---
    def set_input_mode(self, mode: int):
        """Modo de entrada: 0=A, 1=A-B, 2=I(1M), 3=I(100M)."""
        self._inst.write(f"ISRC {mode}")
    def set_aux_out(self, aux_num: int = 1, voltage: float = 0.0):
        """Establece la tensión en una salida auxiliar (-10.5 V a 10.5 V)."""
        if not (-10.5 <= voltage <= 10.5):
            raise ValueError("El voltaje auxiliar debe estar entre -10.5V y 10.5V.")
        self._inst.write(f"AUXV {aux_num}, {voltage:.4f}")
    def set_reference(self, internal: bool, freq: float = 1000.0, voltage: float = 1.0):
        """Configura la referencia interna o externa."""
        if internal:
            self._inst.write("FMOD 1")
            self._inst.write(f"SLVL {voltage:f}")
            self._inst.write(f"FREQ {freq:f}")
        else:
            self._inst.write("FMOD 0")
    def get_scale_index(self) -> int:
        return int(self._inst.query_ascii_values("SENS ?")[0])
    def set_scale_index(self, scale_idx: int):
        scale_idx = max(0, min(scale_idx, len(self.SCALE_VALUES) - 1))
        self._inst.write(f"SENS {scale_idx}")
    def get_time_constant_index(self) -> int:
        return int(self._inst.query_ascii_values("OFLT ?")[0])
    def set_time_constant_index(self, tc_idx: int):
        tc_idx = max(0, min(tc_idx, len(self.TIME_CONSTANT_VALUES) - 1))
        self._inst.write(f"OFLT {tc_idx}")
    # --- Mediciones ---
    def get_measurement(self, is_xy: bool = True):
        """
        Retorna (X, Y) si is_xy=True, o (R, Theta) si is_xy=False.
        """
        if is_xy:
            return self._inst.query_ascii_values("SNAP? 1, 2", separator=",")
        else:
            return self._inst.query_ascii_values("SNAP? 3, 4", separator=",")
    def auto_scale(self, is_xy: bool = False, low_thresh: float = 0.1, high_thresh: float = 1.0, debug: bool = False):
        """Ajusta automáticamente la escala para evitar saturación o pérdida de resolución."""
        tc_idx = self.get_time_constant_index()
        wait_time = self.TIME_CONSTANT_VALUES[tc_idx] * 4
        scale_idx = self.get_scale_index()
        time.sleep(wait_time)
        val1, val2 = self.get_measurement(is_xy=is_xy)
        primary_val = abs(val1)
        while primary_val < self.SCALE_VALUES[scale_idx]*1e-6 * low_thresh and scale_idx > 0:#agreue el 1e-6 para pasar a amp
            scale_idx -= 1
            self.set_scale_index(scale_idx)
            time.sleep(wait_time)
            val1, val2 = self.get_measurement(is_xy=is_xy)
            primary_val = abs(val1)
        while primary_val > self.SCALE_VALUES[scale_idx] *1e-6 * high_thresh and scale_idx < len(self.SCALE_VALUES) - 1:
            scale_idx += 1
            self.set_scale_index(scale_idx)
            time.sleep(wait_time)
            val1, val2 = self.get_measurement(is_xy=is_xy)
            primary_val = abs(val1)
        if debug:
            print(f"[AutoScale] Escala fijada en {self.SCALE_VALUES[scale_idx]*1e-6} A (Val: {primary_val:g})")
        return val1, val2

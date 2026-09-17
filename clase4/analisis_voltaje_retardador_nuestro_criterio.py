import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.style.use('./estiloGraficos.mplstyle')

def tuki2(archivo):
    df = pd.read_csv(archivo, skiprows=1, sep=",")
    df.columns = ['l', 'I',"d", "k"]
    df['l'] = pd.to_numeric(df['l'], errors='coerce')
    df['I'] = pd.to_numeric(df['I'], errors='coerce')
    df['d'] = pd.to_numeric(df['d'], errors='coerce')
    df['k'] = pd.to_numeric(df['k'], errors='coerce')
    v = df["l"]
    ampl = df["I"]
    fase = df["d"]
    radio = df["k"]
    return v, ampl, fase, radio
#%%
datos = [("barridoFinal_435nm_2V.txt","barridoFinal_435nm_3V.txt",
          "barridoFinal_435nm_4V.txt","barridoFinal_435nm_5V.txt"),
         ("barridoFinal_540nm_2V.txt","barridoFinal_540nm_3V.txt",
          "barridoFinal_540nm_4V.txt","barridoFinal_540nm_5V.txt"),
         ("barrido_570nm_2V.txt","barrido_570nm_3V.txt",
          "barrido_570nm_4V.txt","barrido_570nm_5V.txt"),
         ("barridoFinal_615nm_2V.txt","barridoFinal_615nm_3V.txt",
          "barridoFinal_615nm_4V.txt","barridoFinal_615nm_5V.txt")]

#%%
potenciales_corte = []
errores_potenciales = []
for archivos in datos:
    arch_2v, arch_3v, arch_4v, arch_5v = archivos
    longitud_onda = arch_2v.split('_')[1]
    v2, i2, _, _ = tuki2(arch_2v)
    v3, i3, _, _ = tuki2(arch_3v)
    v4, i4, _, _ = tuki2(arch_4v)
    v5, i5, _, _ = tuki2(arch_5v)
    i2 = i2*1e12 # paso a pA
    i3 = i3*1e12
    i4 = i4*1e12
    i5 = i5*1e12
    e_v2 = np.abs(v2)*0.01
    e_v3 = np.abs(v3)*0.01
    e_v4 = np.abs(v4)*0.01
    e_v5 = np.abs(v5)*0.01
    e_i2 = np.abs(i2)*0.01
    e_i3 = np.abs(i3)*0.01
    e_i4 = np.abs(i4)*0.01
    e_i5 = np.abs(i5)*0.01
    # Armamos el DataFrame unificado
    df_unido = pd.DataFrame({'voltage': v5, '5V': i5})
    df_unido = df_unido.merge(pd.DataFrame({'voltage': v4, '4V': i4}), on='voltage')
    df_unido = df_unido.merge(pd.DataFrame({'voltage': v3, '3V': i3}), on='voltage')
    df_unido = df_unido.merge(pd.DataFrame({'voltage': v2, '2V': i2}), on='voltage')
    
    # Calculamos la dispersión y ubicamos el voltaje de convergencia
    columnas_corriente = ['5V', '4V', '3V', '2V']
    df_unido['dispersion'] = df_unido[columnas_corriente].max(axis=1) - df_unido[columnas_corriente].min(axis=1)
    
    punto_cruce = df_unido.loc[df_unido['dispersion'].idxmin()]
    
    # Asignamos el voltaje y su incerteza (1% sistemático)
    v_corte = punto_cruce['voltage']
    error_v_corte = np.abs(v_corte) * 0.01
    
    # Guardamos en las listas
    potenciales_corte.append(v_corte)
    errores_potenciales.append(error_v_corte)

    print(f"--- Análisis para {longitud_onda} ---")
    print(f"Voltaje de corte: ({v_corte:.3f} ± {error_v_corte:.3f}) V\n")

    fig, ax = plt.subplots(figsize=(8,6))
    ax.errorbar(v5, np.array(i5),xerr=e_v5, yerr=e_i5, fmt="o",label="5V", alpha=0.8)
    ax.errorbar(v4, np.array(i4),xerr=e_v4, yerr=e_i4, fmt="o",label="4V", alpha=0.8)
    ax.errorbar(v3, np.array(i3),xerr=e_v3, yerr=e_i3, fmt="o",label="3V", alpha=0.8)
    ax.errorbar(v2, np.array(i2),xerr=e_v2, yerr=e_i2, fmt="o",label="2V", alpha=0.8)
    ax.plot([],[], " ", label=r"$\lambda_{nom}$ = "f"{longitud_onda}")    
    # Trazamos la línea representativa
    ax.axvline(v_corte, color='red', linestyle='--', alpha=0.6, 
               label=r"$V_C$ = "f"({v_corte:.3f} ± {error_v_corte:.3f}) V")
    #ax.set_title(f"Fotocorriente vs Voltaje - {longitud_onda}")
    ax.set_xlabel("Voltaje [V]")
    ax.set_ylabel("Corriente [pA]")
    ax.legend()
    ax.grid(which="major")
    ax.grid(which="minor", alpha=0.3)
    ax.minorticks_on()
    fig.tight_layout()
    plt.show()

potenciales_corte = np.array(potenciales_corte)
errores_potenciales = np.array(errores_potenciales) 
#%%
print(np.array2string(potenciales_corte, precision=3, separator=', '))
print(np.array2string(errores_potenciales, precision=3, separator=', '))

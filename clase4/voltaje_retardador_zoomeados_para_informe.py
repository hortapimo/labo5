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
datos = [# ("barrido_420nm_5V.txt","420 nm", "CurvaLambda420nm.png"),
         #("barrido_420nm_5V_bien.txt","420 nm", "CurvaLambda420nm.png"),
         #("barrido_420nm_5V_bienralta.txt","420 nm", "CurvaLambda420nm.png"),
         ("barrido_420nm_5V_clase3.txt","420 nm", "CurvaLambda420nm.png")]

# grafico por separado
for (archivo, etiqueta, guardado) in datos:
    fig1, ax1 = plt.subplots(figsize=(8,6))
    ax1.set_title("A", fontsize=30)
    v, i, _, _= tuki2(archivo)
    
    # Convierto a numpy arrays para la búsqueda del mínimo
    v = np.array(v)
    i = np.array(i) * 1e12 # paso a unidades de pA
    
    error_sistematico_i = np.abs(i) * 0.01 
    error_sistematico_v = np.abs(v) * 0.01 
    
    # --- BÚSQUEDA DEL PUNTO MÁS CERCANO A CERO ---
    # Buscamos el mínimo del valor absoluto[cite: 2]
    indice_minimo = np.argmin(np.abs(i))
    v_min = v[indice_minimo]
    i_min = i[indice_minimo]
    
    # Incerteza como la mitad de la distancia espacial al punto siguiente[cite: 2]
    if indice_minimo < len(v) - 1:
        error_v_min = np.abs(v[indice_minimo + 1] - v_min) / 2
    else:
        error_v_min = np.abs(v_min - v[indice_minimo - 1]) / 2

    # Graficamos con capsize para visualizar las incertezas
    ax1.errorbar(v, i, xerr=error_sistematico_v, yerr=error_sistematico_i,
                 fmt="o", label=r"$\lambda_{nom}$ = "f"{etiqueta}", capsize=3, alpha=0.8)
                 
    # Línea vertical marcando el cruce en el gráfico principal
    ax1.axvline(v_min, color='red', linestyle='--', alpha=0.7, 
                label="Valor elegido")
    ax1.axhline(0, color='black', linestyle='--', alpha=0.7, 
                label="Origen")
    # --- INICIO DEL ZOOM ---
    # Posición del recuadro dentro de la figura: [posición_x, posición_y, ancho, alto]
    axins1 = ax1.inset_axes([0.1, 0.3, 0.6, 0.4]) 
    
    # Re-graficamos los datos dentro del recuadro sumando capsize
    axins1.errorbar(v, i, xerr=error_sistematico_v, yerr=error_sistematico_i, 
                    fmt="o", capsize=3, alpha=0.8)
                    
    # Trazamos la línea vertical también dentro del zoom
    axins1.axvline(v_min, color='red', linestyle='--', alpha=0.7)
    axins1.axhline(0, color='black', linestyle='--', alpha=0.7)

    # Límites de tu zona de interés para el zoom
    axins1.set_xlim(-2, -0.8) 
    axins1.set_ylim(-8, 8) 
    axins1.grid(which="both", alpha=0.3)
    axins1.minorticks_on()
    
    # Dibuja las líneas que conectan la zona original con el recuadro
    ax1.indicate_inset_zoom(axins1, edgecolor="black")
    # --- FIN DEL ZOOM ---
    
    ax1.set_xlabel(r"$V_0$ [V]")
    ax1.set_ylabel(r"$i_f$ [pA]")
    ax1.legend()
    fig1.tight_layout()
    fig1.savefig(guardado)
    plt.show()

#%%
datos = [ ("barrido_570nm_2V.txt","barrido_570nm_3V.txt",
          "barrido_570nm_4V.txt","barrido_570nm_5V.txt")]

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
    I_1 = 1.00
    I_2 = 0.74
    I_3 = 0.49
    I_4 = 0.21
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
    ax.set_title("B", fontsize=30)
    # Gráfico principal (sin capsize)
    ax.errorbar(v5, np.array(i5), xerr=e_v5, yerr=e_i5, fmt="o", label=r"$I_1$ = 1.00", alpha=0.8)
    ax.errorbar(v4, np.array(i4), xerr=e_v4, yerr=e_i4, fmt="o", label=r"$I_2$ = 0.74", alpha=0.8)
    ax.errorbar(v3, np.array(i3), xerr=e_v3, yerr=e_i3, fmt="o", label=r"$I_3$ = 0.49", alpha=0.8)
    ax.errorbar(v2, np.array(i2), xerr=e_v2, yerr=e_i2, fmt="o", label=r"$I_4$ = 0.21", alpha=0.8)
    ax.plot([], [], " ", label=r"$\lambda_{nom}$ = "f"{longitud_onda}")    
    
    # Trazamos la línea representativa (sin el valor numérico en el label)
    ax.axvline(v_corte, color='red', linestyle='--', alpha=0.6, label="Valor elegido")
               
    # --- INICIO DEL ZOOM ---
    # Posición del recuadro: arriba a la izquierda [x, y, ancho, alto]
    axins = ax.inset_axes([0.1,0.1, 0.5, 0.4])
    
    # Re-graficamos los datos dentro del zoom (sin capsize)
    axins.errorbar(v5, np.array(i5), xerr=e_v5, yerr=e_i5, fmt="o", alpha=0.8)
    axins.errorbar(v4, np.array(i4), xerr=e_v4, yerr=e_i4, fmt="o", alpha=0.8)
    axins.errorbar(v3, np.array(i3), xerr=e_v3, yerr=e_i3, fmt="o", alpha=0.8)
    axins.errorbar(v2, np.array(i2), xerr=e_v2, yerr=e_i2, fmt="o", alpha=0.8)
    axins.axvline(v_corte, color='red', linestyle='--', alpha=0.6)
    
    # Centrado alrededor del voltaje de corte
    axins.set_xlim(v_corte - 0.15, v_corte + 0.15)
    axins.set_ylim(-8,8) 
    axins.grid(which="both", alpha=0.3)
    axins.minorticks_on()
    
    # Conectores visuales del zoom
    ax.indicate_inset_zoom(axins, edgecolor="black")
    # --- FIN DEL ZOOM ---

    ax.set_xlabel(r"$V_0$ [V]")
    ax.set_ylabel(r"$i_f$ [pA]")
    ax.legend(loc="lower right") # Moví la leyenda para no pisar el zoom
    ax.grid(which="major")
    ax.grid(which="minor", alpha=0.3)
    ax.minorticks_on()
    fig.tight_layout()
    fig.savefig("570nmVariosVoltajesParaInforme.png")
    plt.show()

potenciales_corte = np.array(potenciales_corte)
errores_potenciales = np.array(errores_potenciales)


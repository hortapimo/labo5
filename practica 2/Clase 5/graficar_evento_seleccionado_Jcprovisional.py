import matplotlib.pyplot as plt

# --- Cargar estilo de gráficos ---
plt.style.use('/home/juan_cruz/Documentos/Mi_git/labo5/clase2/estiloGraficos.mplstyle')
# ---------------------------------  

#%%

def graficar_evento_seleccionado(nombre_archivo):

    t, u1, u2, u3 = [], [], [], []

    # 2. Procesar el archivo .txt
    with open(nombre_archivo, 'r') as f:
        for linea in f:
            linea = linea.strip()
            
            if linea.startswith("t[ns]") or linea == "":
                continue

            # Se eliminó la sangría extra para que esté al nivel del 'if'
            try:
                valores = linea.split()
                if len(valores) == 4:
                    t.append(float(valores[0]))
                    u1.append(float(valores[1]))
                    u2.append(float(valores[2]))
                    u3.append(float(valores[3]))
            except ValueError:
                pass
            
    # 3. Crear y configurar la figura
    fig, ax = plt.subplots(figsize=(9, 6))

    # Graficar (heredando el tamaño de marcador y grosor del .mplstyle)
    ax.plot(t, u1, marker='o', markersize = 2 , linestyle='', color='#377eb8', label='Canal 1 (u1)')
    ax.plot(t, u2, marker='o', markersize = 2, linestyle='', color='#e41a1c', label='Canal 2 (u2)')
    ax.plot(t, u3, marker='o', markersize = 2, linestyle='', color='#4daf4a', label='Canal 3 (u3)')

    ax.set_xlabel('Tiempo [ns]')
    ax.set_ylabel('Voltaje [mV]')

    ax.legend(loc='lower right')

    plt.show()

# Ejecutar el programa pasándole ambos archivos
graficar_evento_seleccionado("run_20260911_121022_idx0_selected.txt")
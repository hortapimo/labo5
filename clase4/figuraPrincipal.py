import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

plt.style.use('./estiloGraficos.mplstyle')

def load_archiv0(name):
    df = pd.read_csv(name, skiprows=1)
    df.columns = ['V', 'Ix','Iy','r']
    df['V'] = pd.to_numeric(df['V'], errors='coerce')
    return df

sinColimador=load_archiv0("barridoFinal_435nm_5V.txt")
apertura1=load_archiv0("barridoFinal_435nm_5V_colimado.txt")
apertura2=load_archiv0("barridoFinal_435nm_5V_colimado_Apertura2.txt")
apertura3=load_archiv0("barridoFinal_435nm_5V_colimado_Apertura3.txt")
apertura4=load_archiv0("barridoFinal_435nm_5V_colimado_Apertura5.txt")#Este quedo con n=5 por error, deberia decir 4
tapando=load_archiv0('barridoFinal_435nm_5V_tapando.txt')
#%%

def calcularFactor(curvaReferencia, curva2):
    """
    obj: la funcion debe entregar el parametro de prporiconalidad que mejor pega los puntos 
    de corriente negeativa de la curva 2 con lso de la curva de referencia.
    
    implementacion: Vpy primero con la forma mas sencilla que es simplemente tomar los
    ultimos n putnos dividirlos y hacer un promedio de ese factor de proporcionalidad
    """
    n=1
    aux=0
    for i in range(n):
        #si la curva de ref no es la de sin colimador poner -1
        aux +=curvaReferencia["Ix"].iloc[-i-6]/curva2["Ix"].iloc[-i-1]
        
    return aux/n

def calcularFactor2(curvaReferencia, curva2):
    """
    obj: la funcion debe entregar el parametro de prporiconalidad que mejor pega los puntos 
    de corriente negeativa de la curva 2 con lso de la curva de referencia.
    
    Voy a probar de otra forma. voy a minimizar la diferencia entre los ultimos n puntos de las curvas
    calculando este valor para distintos factores de proporcionalidad, haciendo e algoritmo del estilo de, eligiendo 
    como factores iniciales 1 y 20 por ejemplo. veamoosss
    """
    n=2
    fmin=1
    fmax=20
    #Esta el menos 5 y -6 si la de ref es la curva sin colimadoer, sino solo -1
    p_i=np.sum(abs(curvaReferencia.iloc[-n-5,-6]-curva2.iloc[-n:-1]*fmin))
    p_d=np.sum(abs(curvaReferencia.iloc[-n-5,-6]-curva2.iloc[-n:-1]*fmax))
    j=0
    jmax=10000
    p=1
    while((p>1e-15) and (j<jmax)):
        f=(fmin + fmax)/2
        p=np.sum(abs(curvaReferencia.iloc[-n-5:-6]-curva2.iloc[-n,-1]*f))
        if(abs(p-p_i)>abs(p-p_d)):
            fmin=f
            p_i=p
        else:
            fmax=f
            p_d=p
        j+=1
        if(j==jmax): print("frena por jmax")
    print(f"la j fue {j}")
    return f

def calcularFactor3(curvaReferencia, curva2, n=5, offset_ref=-6, col='Ix'):
    """
    Alinea por mínimos cuadrados una ventana de longitud n de curvaReferencia
    que termina en offset_ref con los últimos n puntos de curva2.
    """
    # Si le pasas un DataFrame completo, extrae la columna col ('Ix')
    ref = curvaReferencia[col] if isinstance(curvaReferencia, pd.DataFrame) else curvaReferencia
    c2 = curva2[col] if isinstance(curva2, pd.DataFrame) else curva2

    idx_fin = offset_ref + 1 if offset_ref != -1 else None
    idx_ini = offset_ref - n + 1
    
    # Asegura vectores 1D limpios de tipo float
    y_ref = np.asarray(ref.iloc[idx_ini : idx_fin], dtype=float).ravel()
    y2 = np.asarray(c2.iloc[-n:], dtype=float).ravel()

    if len(y_ref) != len(y2) or len(y_ref) == 0:
        raise ValueError(f"Tamaños incompatibles: len(y_ref)={len(y_ref)}, len(y2)={len(y2)}")

    den = np.dot(y2, y2)
    if den == 0:
        raise ValueError("curva2 contiene únicamente ceros en la ventana de ajuste seleccionada.")

    return np.dot(y_ref, y2) / den

def graficar(*tuplasXY,**karg):
    fig, ax = plt.subplots()
    
    for (x,y,label) in tuplasXY:
        ax.plot(x,y,label=label,marker='o')
    
    try:
        ax.set_xlabel(karg["xlabel"])
        ax.set_ylabel(karg["ylabel"])    
    except: pass  

 
    ax.legend()
#%%
#factorA4_A1=calcularFactor(apertura4, apertura1)
#La medcion con apertura 1 tiene una señal muy baja y es muy ruidosa, arruina el grafico, la voya sacr, por eso renombre todo
fmanual=0.7#ya e cualquier cosa
factor_A3=calcularFactor3(sinColimador, apertura4)
factor_A2=calcularFactor3(sinColimador, apertura3)
factor_A1=calcularFactor3(sinColimador, apertura2)

graficar((sinColimador["V"],sinColimador["Ix"],"Sin colimar"),
    (apertura4["V"],apertura4["Ix"]*factor_A3*fmanual,"apertura 3"),
         (apertura3["V"],apertura3["Ix"]*factor_A2*fmanual,"apertura 2"),
         (apertura2["V"],apertura2["Ix"]*factor_A1*fmanual,"apertura 1"),
         xlabel="voltaje [V]", ylabel="I [A]")

#%%
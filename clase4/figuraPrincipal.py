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
        aux +=curvaReferencia["Ix"].iloc[-i-6]/curva2["Ix"].iloc[-i-1]
        
    return aux/n

def calcularFactor2(curvaReferencia, curva2):
    """
    Voy a probar de otra forma. voy a minimizar la diferencia entre los ultimos n puntos de las curvas
    calculando este valor para distintos factores de proporcionalidad, haciendo e algoritmo del estilo de, eligiendo 
    como factores iniciales 1 y 20 por ejemplo. veamoosss
    """
    n=1
    fmin=1
    fmax=20
    
    p_i=np.sum(abs(curvaReferencia.iloc[-n,-1]-curva2.iloc[-n,-1]*fmin))
    p_d=np.sum(abs(curvaReferencia.iloc[-n,-1]-curva2.iloc[-n,-1]*fmax))
    j=0
    jmax=10000
    p=1
    while((p>1e-15) and (j<jmax)):
        f=(fmin + fmax)/2
        p=np.sum(abs(curvaReferencia.iloc[-n-5,-6]-curva2.iloc[-n,-1]*f))
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
factor_A3=calcularFactor(sinColimador, apertura4)
factor_A2=calcularFactor(sinColimador, apertura3)
factor_A1=calcularFactor(sinColimador, apertura2)

graficar((sinColimador["V"],sinColimador["Ix"],"Sin colimar"),
    (apertura4["V"],apertura4["Ix"]*factor_A3,"apertura 3"),
         (apertura3["V"],apertura3["Ix"]*factor_A2,"apertura 2"),
         (apertura2["V"],apertura2["Ix"]*factor_A1,"apertura 1"),
         xlabel="voltaje [V]", ylabel="I [A]")

#%%
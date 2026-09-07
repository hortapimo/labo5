import numpy as np
import matplotlib.pyplot as plt
import pandas as pd



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

#%% PAra ver el archivo
def graficar(*tuplasXY):
    fig, ax = plt.subplots()
    
    for (x,y,label) in tuplasXY:
        ax.scatter(x,y,label=label)
    ax.legend()
    
graficar((apertura3['V'],apertura3['r'],"sinColimador"))

#%%  
def dividirDatos(df):
    datosPositivos=[]
    datosNegativos=[]
    for I,V in zip(df['Ix'],df['V']):
        if I>0: 
            datosPositivos.append([V,I])
    
    for I,V in zip(df['Ix'],df['V']):
        if I<0: 
            datosNegativos.append([V,I])
            
    datosPositivos=np.array(datosPositivos)
    datosNegativos=np.array(datosNegativos)
    
    graficar((datosPositivos[:,0],datosPositivos[:,1],"datos positivos"),
             (datosNegativos[:,0],datosNegativos[:,1],"datos negativos"))
    
    return datosPositivos, datosNegativos
    
            
def calcularParametroEfectoFotInverso(df):
    """
    LA idea es intentar armar algun criterio para cuantificar el efct fotoelectrico inverso
    Lo que propongo es tomar la "integral" del lado posisitivo de corriente (corriente inversa) y dividirla por
    la integral de lado negativo (corriente directa en nuestra idea de efecto fotoelectrico)
     y ver si esta relacion cambia si cambiamos la apertura. Si cambia de forma que para la apertura mas grande 
     la relaicon es mas grande, esto es indicio de que la al tener mas apertura la luz esta tocando con el electrodo colector
     haciendo un efecto fotoelectrico inverso
    """
    #Divido los datos en dos
    corrientePositiva, corrienteNegativa = dividirDatos(df)
    
    a = np.trapezoid(corrientePositiva[:,0], corrientePositiva[:,1])
    
    b = np.trapezoid(corrienteNegativa[:,0], corrienteNegativa[:,1])
    """
    El problema de este nfoque es que los pntos en el cruce aveces  pasan y vuelven del cero
    """
    
    return corrientePositiva, corrienteNegativa, a/b

def calcularParametroEfectoFotInverso2(df):
    aux = 0
    for i in range(10): 
        aux += abs(df['Ix'].iloc[i]/df['Ix'].iloc[-1*i-1])
    
    return aux/10

    
#%% grafico con calcularParametroEfectoFotInverso
"""
graficar((apertura4['V'],apertura4['Ix'],"apertura4"))    
x,y,paramAp1 = calcularParametroEfectoFotInverso(apertura1)
x,y,paramAp2 = calcularParametroEfectoFotInverso(apertura2)
x,y,paramAp3 = calcularParametroEfectoFotInverso(apertura3)
x,y,paramAp4 = calcularParametroEfectoFotInverso(apertura4)
x,y,paramSinColima = calcularParametroEfectoFotInverso(sinColimador)


fig,ax = plt.subplots()
ax.scatter(["1","2","3","4", "sin colimador"],[paramAp1, paramAp2, paramAp3, paramAp4, paramSinColima])
"""
#%% grafico con calcularParametroEfectoFotInverso2

paramAp1 = calcularParametroEfectoFotInverso2(apertura1)
paramAp2 = calcularParametroEfectoFotInverso2(apertura2)
paramAp3 = calcularParametroEfectoFotInverso2(apertura3)
paramAp4 = calcularParametroEfectoFotInverso2(apertura4)
paramSinColima = calcularParametroEfectoFotInverso2(sinColimador)


fig,ax = plt.subplots()
ax.scatter(["1","2","3","4", "sin colimador"],[paramAp1, paramAp2, paramAp3, paramAp4, paramSinColima])


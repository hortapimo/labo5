import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft
import pyvisa as visa
import time
from scipy.signal import butter,lfilter
import pandas as pd
#%%
class SR830:
    '''Clase para el manejo amplificador Lockin SR830 usando PyVISA de interfaz'''

    scale_values = (2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9, 1e-6,
                    2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6, 1e-3,
                    2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1) # in V

    time_constant_values = (10e-6, 30e-6, 100e-6, 300e-6, 1e-3, 3e-3, 10e-3, 30e-3, 100e-3, 300e-3,
                    1e0, 3e0, 10e0, 30e0, 100e0, 300e0, 1e3, 3e3, 10e3, 30e3) # in s

    def __init__(self, resource):
        self._lockin = visa.ResourceManager().open_resource(resource)
        #print(self._lockin.query('*IDN?')) # habria que ver si es mejor no pedir IDN. Puede que trabe la comunicacion al ppio
        self._lockin.write("LOCL 2") #Bloquea el uso de teclas del Lockin
        time.sleep(1) # tal vez ayuda a evitar errores de comunicacion del pyvisa
        self.scale = self.get_scale()
        self.time_constant = self.get_time_constant()

    def __del__(self):
        self._lockin.write("LOCL 0") #Desbloquea el Lockin
        self._lockin.close()

    def set_modo(self, modo):
        '''Selecciona el modo de medición, A, A-B, I, I(10M)'''
        self._lockin.write("ISRC {0}".format(modo))

    def set_filtro(self, sen, tbase, slope):
        '''Setea el filtro de la instancia'''
        #Página 90 (5-4) del manual
        self._lockin.write("OFLS {0}".format(slope))
        self._lockin.write("OFLT {0}".format(tbase))
        self._lockin.write("SENS {0}".format(sen))
       
    def set_aux_out(self, auxOut, auxV):
        '''Setea la tensión de salida de al Aux Output indicado.
        Las tensiones posibles son entre -10.5 a 10.5'''
        self._lockin.write('AUXV {0}, {1}'.format(auxOut, auxV))
           
    def set_referencia(self,isIntern, freq, voltaje = 1):
        if isIntern:
            #Referencia interna
            #Configura la referencia si es así
            self._lockin.write("FMOD 1")
            self._lockin.write("SLVL {0:f}".format(voltaje))
            self._lockin.write("FREQ {0:f}".format(freq))
        else:
            #Referencia externa
            self._lockin.write("FMOD 0")
           
    def set_scale(self, scale_number):
        self.scale = min(scale_number,len(self.scale_values))
        self._lockin.write(f'SENS {self.scale}')
        return self.scale
   
    def get_scale(self):
        self.scale = int(self._lockin.query_ascii_values('SENS ?')[0])
        return self.scale

    def set_time_constant(self, time_constant_number):
        self._lockin.write(f'OFLT {time_constant_number}')
        self.time_constant = time_constant_number
        return self.time_constant
   
    def get_time_constant(self):
        return int(self._lockin.query_ascii_values('OFLT ?')[0])

    def set_display(self, isXY):
        if isXY:
            self._lockin.write("DDEF 1, 0") #Canal 1, x
            self._lockin.write('DDEF 2, 0') #Canal 2, y
        else:
            self._lockin.write("DDEF 1,1") #Canal 1, R
            self._lockin.write('DDEF 2,1') #Canal 2, T
   
    def get_display(self):
        '''Obtiene la medición que acusa el display.
        Es equivalente en resolución a la medición de los parámetros con SNAP?'''
        orden = "SNAP? 10, 11"
        return self._lockin.query_ascii_values(orden, separator=",")
       
    def get_medicion(self,isXY = True):
        '''Obtiene X,Y o R,Ang, dependiendo de isXY'''
        orden = "SNAP? "
        if isXY:
            self._lockin.write("DDEF 1,0") #Canal 1, XY
            orden += "1, 2" #SNAP? 1,2
        else:
            self._lockin.write("DDEF 1,1") #Canal 1, RTheta
            orden += "3, 4" #SNAP? 3, 4
        return self._lockin.query_ascii_values(orden, separator=",")

    def auto_scale(self):
        '''
            Utiliza medicion polar (r, angulo)          
            inf_threshold es el porcentaje minimo de la escala  para el cual el
            autoescalado empiza a efectuarse: intenta mantenerse sobre ese rango. valor float de 0 a 1
        '''
        debug = True
        sup_theshold = 1
        inf_threshold = 0.1        
        nespera = 5 # se recomienda esperar entre 3 y 5 veces el tiempo de medicion entre escalado y medicion        
        tespera = self.time_constant_values[self.time_constant] * nespera
        time.sleep(tespera)
        r,tita = self.get_medicion(isXY=False)

        while r < self.scale_values[self.scale] * inf_threshold and self.scale > 0:
            if debug:
                print('Valor por debajo de threshold, bajo escala (r=%g, oldscale=%g)'%(r,self.scale_values[self.scale]))
            self.scale -= 1
            self.set_scale(self.scale)
            time.sleep(tespera) # esperar N * el tiempo de integracion antes de medir
            r,tita = self.get_medicion(isXY=False)

        while r > self.scale_values[self.scale] * sup_theshold and self.scale < (len(self.scale_values)-1):
            if debug:
                print('Overloaded, subo escala (oldscale=%g)'%(self.scale_values[self.scale]))
            self.scale += 1
            self.set_scale(self.scale)
            time.sleep(tespera)
            r,tita = self.get_medicion(isXY=False)
       
        if debug:
            print('Listo (r=%g, scale=%g)'%(r, self.scale_values[self.scale]))

        return r, tita
#%%



rm = visa.ResourceManager()
config = {
      'lockin_addr': 'GPIB0::8::INSTR',
      'medicion_modo' : int,
      'display_modo' : str,
      'sens' : int,
      'slope' : int,
      't_int' : int,
      'ref_intern' : bool,
      'ref_freq' : int,
      'ref_v' : int,
      }
print(rm.list_resources())
lockin = SR830(config['lockin_addr'])
#plt.pause(10)
#%%



voltajes = np.linspace(-2,8,200)
corrientes = []

#lockin.set_scale(21)
#lockin.auto_scale()


lockin.set_aux_out(1, voltajes[0])
time.sleep(2)


for i in range(len(voltajes)):
    
    #if i==50:
       # lockin.set_scale(22)
        #plt.pause(5)
    lockin.set_aux_out(1, voltajes[i])
    time.sleep(0.1)
    plt.pause(0.2)
    
    corrientes.append(lockin.get_medicion(isXY = False))
    plt.plot(voltajes[i],corrientes[i][0],".",color="red")
    
    #plt.plot(voltajes[i],corrientes[i][1],".",color="blue")  
#%%
plt.figure()
plt.scatter(voltajes,np.asarray(corrientes)[:,0])
plt.show()


#%%

corrientes = np.asarray(corrientes)

# corrientes[:,0] -> R
# corrientes[:,1] -> theta

# ---------------------------------------
# GUARDAR TODO JUNTO
# ---------------------------------------

datos = np.column_stack((
    voltajes,
    corrientes[:,0],
    corrientes[:,1]
))


np.savetxt(
    r"C:\Users\publico\Desktop\grupo 2 mañana\barrido longitud de onda\600_3Vnm.txt",
    datos,
    delimiter=",",
    header="Voltaje,R,Theta",
    comments=""
)

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------
# CARGAR ARCHIVO
# ---------------------------------------------------

data = np.loadtxt(
    r"C:\Users\publico\Desktop\grupo 2 mañana\barrido longitud de onda\610nm.txt",
    delimiter=",",
    skiprows=1
)

# ---------------------------------------------------
# SEPARAR COLUMNAS
# ---------------------------------------------------

voltaje = data[:,0]

R = data[:,1]

theta = data[:,2]

# ---------------------------------------------------
# GRAFICAR R vs V
# ---------------------------------------------------

plt.figure()

plt.plot(voltaje, R, 'o-')

plt.xlabel("Voltaje (V)")

plt.ylabel("R")

plt.title("Barrido Lock-in")

plt.grid()

plt.show()

#%%

corrientes2 = []
lista_frecuencias = np.arange(420, 740, 10) # long de onda en nm
#%%
V_cte = 10

#lockin.set_scale(21)
#lockin.auto_scale()
#lockin.set_aux_out(1, V_cte)
#time.sleep(15)
#corrientes2.append(lockin.get_medicion(isXY = False))
#corrientes2[-1] = lockin.get_medicion(isXY = False)

# Blanco 420, 

#%%
plt.plot(lista_frecuencias, np.asarray(corrientes2)[:,0], ".")
plt.show()

#np.savetxt("corrientes_Blanco_Vcte.csv", corrientes2, delimiter = ",")
#np.savetxt("frecuencias_Blanco_Vcte.csv", lista_frecuencias, delimiter = ",")
#%%
import matplotlib.pyplot as plt
import scipy.optimize as opt
import numpy as np
import time
import os
import glob

class Lockin(object):
    '''Clase para el manejo amplificador Lockin SR830 usando PyVISA de interfaz'''
    
    def __init__(self,resource):
        self._lockin = visa.ResourceManager().open_resource(resource)
        self._lockin.query('*IDN?')
        self._lockin("LOCL 2") #Bloquea el uso de teclas del Lockin
        
    def __del__(self):
        self._lockin("LOCL 0") #Desbloquea el Lockin
        self._lockin.close()
        
    def setModo(self, modo):
        '''Selecciona el modo de medición, A, A-B, I, I(10M)'''
        self._lockin.write("ISRC {0}".format(modo))
        
    def setFiltro(self, sen, tbase, slope):
        '''Setea el filtro de la instancia'''
        #Página 90 (5-4) del manual
        self._lockin.write("OFLS {0}".format(slope))
        self._lockin.write("OFLT {0}".format(tbase)) 
        self._lockin.write("SENS {0}".format(sen)) 
        
    def setAuxOut(self, auxOut = 1, auxV = 0):
        '''Setea la tensión de salida de al Aux Output indicado.
        Las tensiones posibles son entre -10.5 a 10.5'''
        self._lockin.write('AUXV {0}, {1}'.format(auxOut, auxV))
            
    def setReferencia(self,isIntern, freq, vRef = 1):
        if isIntern:
            #Referencia interna
            #Configura la referencia si es así
            self._lockin.write("FMOD 1")
            self._lockin.write("SLVL {0:f}".format(voltaje))
            self._lockin.write("FREQ {0:f}".format(freq))
        else:
            #Referencia externa
            self._lockin.write("FMOD 0")
            
    def setDisplay(self, isXY):
        if isXY:
            self._lockin.write("DDEF 1, 0") #Canal 1, x
            self._lockin.write('DDEF 2, 0') #Canal 2, y
        else:
            self._lockin.write("DDEF 1,1") #Canal 1, R
            self._lockin.write('DDEF 2,1') #Canal 2, T
    
    def getDisplay(self):
        '''Obtiene la medición que acusa el display. 
        Es equivalente en resolución a la medición de los parámetros con SNAP?'''
        orden = "SNAP? 10, 11"
        return self._lockin.query_ascii_values(orden, separator=",")
        
    def getMedicion(self,isXY = True):
        '''Obtiene X,Y o R,Ang, dependiendo de isXY'''
        orden = "SNAP? "
        if isXY:
            self._lockin.write("DDEF 1,0") #Canal 1, XY
            orden += "1, 2" #SNAP? 1,2
        else:
            self._lockin.write("DDEF 1,1") #Canal 1, RTheta
            orden += "3, 4" #SNAP? 3, 4
        return self._lockin.query_ascii_values(orden, separator=",")
        
#Configuración. Se puede cambiar sobre la marcha
config = {
          'medicion_path' : r'PATH_MED',
          'espectro_path' :  r'PATH_ESPECTRO',
          'lockin_addr': 'GPIB0::1::INSTR',
          #Página 90 del manual del Lockin SR830
          'v_sens' : 24, 
          't_slope' : 3, #18dB/oct
          't_base' : 7, #Tiempo de integración 300ms
          'aux_out' : 1,
          'aux_v_min' : -3,
          'aux_v_max' : 0.5,
          'ref_intern' : False,
          'ref_freq' : 323, 
          'ref_v' : 3.5,
          'medicion_dt': 25, #Múltiplo del tiempo de integración
          'medicion_modo' : 2,
          'medicion_xy' : True,
          }

SR830(config['t_base'])

### Funciones de manejo de Lockin ###
def init(config):
    '''Inicialización del Lockin. Devuelve la instancia lista para usar.'''
    inst = Lockin(config['lockin_addr'])
    inst.setReferencia(isIntern = config['ref_intern'],
                       freq = config['ref_freq'], 
                        vRef = config['ref_v'])
    inst.setModo(config['medicion_modo'])
    #Bloquea el uso de teclas del Lockin
    inst.write("LOCL 2")
    #Setea filtro del lockin
    inst.setFiltro(config['v_sens'], config['t_base'], config['t_slope'])
    ## Setea tensión de referencia ## 
    
    #Configura el display.
    inst.setDisplay(config['medicion_xy'])
    inst.setAuxOut(config['aux_out'], config['v_min'])
    time.sleep(5) #Está 5s antes de seguir
    return inst


def adquireCorriente(config):
    '''
    Adquirir datos del lockin para la expriencia. Varía la tensión de salida
    del Aux 1 entre la tensión vOut_min y vOut_max, y mide corriente. Se puede
    setear el tiempo de integración, el tiempo entre medición y medición
    que corresponde a un múltiplo del tiempo de integración,
    la sensibilidad, la frecuencia de referencia y la tensión de referencia.
    '''
    fileName = config['medicion_path']
    vMin = config['aux_v_min']
    vMax = config['aux_v_max']
    #Calcula el tiempo para esperar
    tWait = 0
    if config['t_base'] % 2 == 0:
        tWait = 1 * 10**(config['t_base']/2-5)
    else:
        tWait = 3 * 10**(-(config['t_base']-1)/2)
    tWait *= config['medicion_dt']
    os.chdir()
    # Tensiones a medir
    # Con np.concatenate((a,b)) se puede hacer pasos variables
    tensiones = np.arange(vMin, vMax ,0.01) 
    # Configuración inicial
    lockin = init(config)
    # Iteración sobre las tensiones
    data = []
    for v in tensiones(vMin,vMax):     
        lockin.setAuxOut(auxOut = config['aux_out'], auxV = v)
        #Calcula la base de tiempo a partir de la tabla
        # Espera un múltiplo del tiempo de base
        time.sleep(tWait)
        #Medición
        med = lockin.getDisplay() #o lockin.getMedicion(config['medicion_xy'])
        med.insert(0,v) #Agrega la tensión de aux
        data.append(med)
    data = np.array(data) #Transformo en ndarray
    np.savetxt(fileName, data)
    #Herramienta de ploteo de verificación
    plt.plot(data[:,0],data[:,1],'bo-')
    plt.figure()
    plt.plot(data[:,0],data[:,2],'gd-')
    plt.show()
    
barrido = adquireCorriente(config)

#%%%




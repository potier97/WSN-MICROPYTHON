import machine
import time
import network
import dht
import rf24

# Configurar alarma por interrupción para levantar el dispositivo de deepSleep
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

#Desactivar el modo AP de las conecciones wifi
#Siempre esta activado, incluso si no se usa el modulo Network
nic = network.WLAN(network.AP_IF)
nic.active(False)

print("Iniciando......")
print("Nodo 01")

# Validar de donde se esta levantando - reset o deepSleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('Iniciando por  deepSleep')
else:
    print('Iniciando por hardReset')

#10 segundos => 10000 -- 1 segundo => 1000 -- 5 min => 1000 * 60 * 5
milliseconds = 1000
seconds = 30
sleepTime = milliseconds * seconds 

#Declarar el sensor DHT11 en el pin GPIO-4
sensor = dht.DHT11(machine.Pin(4))

#Direcciones de los modulos NRF24L01 
#La tupla corresponde de dos direcciones
#pipes[0] = la direccion del nodo Esclavo - escucha los datos y los envia a AWS 
#pipes[1] = la direccion del nodos Maestro - envia los datos al nodo esclavo
#La direccion pipes[1] debe cambiar cada vez que carga el script  a un nodo diferente
#La direccion de tipo bytes corresponde a un dato tipo LL que corresponde a 0xF0F0F0F0D2LL
#Note que la forma de escribirlo es de LSB a MSB para el tipo bytes -> b"\xd2\xf0\xf0\xf0\xf0"
#Por lo tanto la ultima direccion es la que deberia cambiar para cada nodo, en este caso corresponde al d2
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

#------------------DIRECCIONES NODOS--------------------
#pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
#-------------- DIR SLAVE  -----------  DIR MASTER --------

#NodoDir 1 d2  D2   NODO05 invernadero  -- 01 -- 21
#NodoDir 2 d4  D4   NODO05 airelibre    -- 02 -- 12
#NodoDir 3 d6  D6   NODO05 invernadero  -- 03 -- 23
#NodoDir 4 d8  D8   NODO05 airelibre    -- 04 -- 14
#NodoDir 5 db  DB   NODO05 Invernadero  -- 05 -- 25

#Validar errores presentados
errs = 0
while True:
  try:
    #Los datos debe ser tomado por lo menos cada 2 segundos
    time.sleep(2)
    #Preparar los datos para ser leidos
    sensor.measure()
    #Leer los datos del sensor de temperatura y humedad
    temp = sensor.temperature()
    hum = sensor.humidity()
    #Convertir el formato de los datos
    formatTemp = '{:4.2f}'.format(temp)
    formatHum = '{:4.2f}'.format(hum)

    #Visualizar los datos de los nodos
    #print('Temperature: {} C'.format(formatTemp))
    #print('Humidity: {} %'.format(formatHum))

    #Validador de recibido de datos
    state = False
    while not state:
        #Inicializar la comunicación con el slave, enviando:
        #Direccion del nodo
        #Temperatura
        #Humedad
        #Direccion del canal
        #Tuberia para hacer la comunicación 
        state = rf24.master(21,formatTemp,formatHum, pipes, 1)
    if state:
        #Mensaje cuando los datos son recibidos
        print("Se envio la informacion")
        #Activar la alarma para despertar en <SleepTime> ms 
	      rtc.alarm(rtc.ALARM0, sleepTime)
	      #Poner a dormir la ESP por <SleepTime> ms
	      machine.deepsleep()
  except:
    #Errores principalmente generado por la conexion del DHT11
    errs +=1
    print('Failed to read sensor.')
    #Reiniciar si sobrepasa los 4 errores
    if errs > 4:
      machine.reset()

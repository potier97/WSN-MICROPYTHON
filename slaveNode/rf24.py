import sys
import ustruct as struct
import utime
from machine import Pin, SPI
from nrf24l01 import NRF24L01
from micropython import const

#Driver principal del Micropython
#https://github.com/micropython/micropython


# Slave pause between receiving data and checking for further packets.
_RX_POLL_DELAY = const(15)
# Slave pauses an additional _SLAVE_SEND_DELAY ms after receiving data and before
# transmitting to allow the (remote) master time to get into receive mode. The
# master may be a slow device. Value tested with Pyboard, ESP32 and ESP8266.
_SLAVE_SEND_DELAY = const(10)


#Configuracion de los pines GPIO - cambiar de acuedo al modulo ESP que utulice o board
cfg = {"spi": 1, "miso": 12, "mosi": 13, "sck": 14, "csn": 15, "ce": 2}


#Metodo de configuración para el nodo Maestro que envia los datos y luego escucha
#id - identificadr del nodo
#temperatura = valor :4.2f
#humedad = valor :4.2f
#pipe - Tupla - Direcciones de la comunicacion (idSlave. idMaster)
#npipe - Tuberia para hacer la comunicación - Más 5 por canal


def master(id = 00, temperature=20.20, humidity=30.30, pipe=(b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0"), npipe=1):


    #Diccionario a enviar al nodo Slave - Gategay
    body={}
    body['S'] = str(id)
    body['T'] = str(temperature)
    body['H'] = str(humidity)
    bodyString = str(body)
    bodyString = bodyString.replace(" ", "")

    #Configuración de los pines para hacer la comunicación
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    #Configuracion del modulo nrf24l01 y su carga util
    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=32)


    #Configuracion del canal de configuración
    nrf.open_tx_pipe(pipe[0])
    nrf.open_rx_pipe(npipe, pipe[1])

    #Comenzar a escuchar
    nrf.start_listening()

    statusSuccess = 0
    confirmSuccess = 5
    
    while statusSuccess < confirmSuccess:

        #Parar de escuchar y comenzar a enviar
        nrf.stop_listening()
        #Enviar los datos a l
        try:
            nrf.send(struct.pack('32s', bodyString))
        except OSError:
            pass

	    #Comenzar a escuchar
        nrf.start_listening()

        # Timeout de 250ms - comienza a contar
        start_time = utime.ticks_ms()
        timeout = False

        # Timeout si se cumplen los 250ms
        while not nrf.any() and not timeout:
            if utime.ticks_diff(utime.ticks_ms(), start_time) > 250:
                timeout = True

        if timeout:
            print("No confirm")

        else:
            # Paquetes Recibidos
            buff = nrf.recv()
        #Res es el resultado devuelto    
	    (res,)  = struct.unpack("i", buff)
        #Termina de escuchar si la comunicación es 5 
  	    if res > 5:
	        statusSuccess = res
        
        # delay then loop
        utime.sleep_ms(250)
    return True



#Metodo del nodo esclavo o Gateway
#Sus parametros corresponden unicamente a:
#pipe - Tupla - Direcciones de la comunicacion (idSlave. idMaster)
#npipe - Tuberia para hacer la comunicación - Más 5 por canal
def slave(pipe, npipe):

    #Configuración de los pines para hacer la comunicación
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    #Configuracion del modulo nrf24l01 y su carga util
    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=32)


    #Configuracion del canal de configuración
    nrf.open_tx_pipe(pipe[1])
    nrf.open_rx_pipe(npipe, pipe[0])

    #Comenzar a escuchar
    nrf.start_listening()

    #Validadores del paquete
    statusPackage = False
    pack = False

    while not statusPackage:
        #Escuchar de cualquier parte
        if nrf.any():
            while nrf.any():
                buf = nrf.recv()
                (led_state,) = struct.unpack('32s', buf)
                utime.sleep_ms(_RX_POLL_DELAY)

            #Convertir los datos de bites a String
            package = led_state
            package = package.decode()
            iside = package.find("'S':'21'")
            #Arreglar el string si el payload no alcanzó
            package = package + "'}"

            #Validar si es un string el contenido
            if isinstance(package, str):
              pack = True
            #Give response master
            utime.sleep_ms(_SLAVE_SEND_DELAY)
            
            #Parar de escuchar y comenzar a enviar
            nrf.stop_listening()
            try:
                #Enviar un int igual a 20
                nrf.send(struct.pack("i", 20))

            except OSError:
                pass

            #Validar si el paquete contiene algo    
            if pack and len(package) > 0:
              statusPackage = True
            #Comenzar a escuchar
            nrf.start_listening()
    #Retornar el paquete recibido
    return package


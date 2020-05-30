import network

#Conexion a red Wifi en modo de STATION

#El modo AP siempre esta habilitado en micropython, aún si no se usa el modulo NETWORK
#Se deshabilita este modo que no se va a implementar
def netWorkConnect(SSID='ssid', PASSWORD='pass'):
  nic = network.WLAN(network.STA_IF)
  ap = network.WLAN(network.AP_IF)

  #Validar si ya esta conectado
  if not nic.isconnected():
    print('Conectando a la red...')
    #Activar el modo STATION
    nic.active(True)
    try:
      #Realiza la conexion con las credenciales puestas como argumento
      nic.connect(SSID, PASSWORD)
      while not nic.isconnected():
        #print(".", end="")
        a = 'conectando....'
    except:
      print('Imposible conectar')'
  #Desactivar el modo APLICATION    
  ap.active(False)
  #Imprime las configuraciones de la red -IP - MASK - MODEN - DNS
  print('network config:', nic.ifconfig())
  #Devuelve True si logra realizar la comunicción
  return True
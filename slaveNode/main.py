from umqtt.robust import MQTTClient
import machine
import time
import timeSynchronizer
import network
import wificonnect
import utime
import rf24
import ujson


#CON ESTE CODIGO SE PUEDE ENVIAR POR MQTT A AWS
#AWS IOT con MQTT valida el Tema  del que escliente 
#Si el topic corresponde a <topic_sub> se ejecuta un lambda de AWS que envia los datos a DynamoDB - NodeJS
#Si el topic corresponde a <topic_subdb> se ejecuta un lambda de AWS que envia los datos a Firebase - Firebase

#10 segundos => 10000 -- 1 segundo => 1000 -- 5 min => 1000 * 60 * 5
seconds = 1000
minutes = 5 * 60
sleepTime = seconds * minutes  

thingName="GREENHOUSE-GATEWAY"
awsHost = '<YOUR-AMAZON-HOST>'                               #EndPoint
awsPort = 8883                                               #Port No
keyPath = "/4f44f5eed4-private.key.der"                      # <Thing_Name>.pem.key
certPath = "/4f44f5eed4-certificate.cert.der"                # <Thing_Name>.pem.crt
topic_sub = '<YOUR-TOPIC-NAME>'
topic_subdb = '<YOUR-OTHER-TOPIC-NAME>'


#Abrir el certificado <CETIFICATE>.cert.der
with open(certPath, 'rb') as f:
  certData = f.read()

#Abrir la clave privada <KEY>.key.der
with open(keyPath, 'rb') as f:
  keyData = f.read()

#Validarores de recibo de paquetes
sendNode01 = False
sendNode02 = False
sendNode03 = False
sendNode04 = False
sendNode05 = False
sendFirebase = False


print("Iniciando......")

# Validar de donde se esta levantando - reset o deepSleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('Iniciando por  deepSleep')
else:
    print('Iniciando por hardReset')


#Conectar a tu red wifi
if wificonnect.netWorkConnect('<YOUR-SSID>','<YOUR-PASSWORD>'):
  print('Conectado')


# Configuración de real time clock RTC
rtc = machine.RTC()
#Configura interrupción para despertar del deep sleep
#Pin 16
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
#Imprime la Hora - Con una tupla de 6 items, configura el RTC
#print(rtc.datetime())


#Conexion a MQTT en AWS de IOT CORE
#Solo es necesario para los parametros SSL el certificado y la llave privada
try:
  client = MQTTClient(thingName, server=awsHost, port=awsPort, ssl=True, keepalive=10000, ssl_params={'key':keyData,'cert':certData,"server_side":False})
  client.connect()
except:
  print("imposible conectar")



#Tuplas de las direcciones de cada NRF24L01
#los bytes de la tupla [0] siempre sera la direccion del Nodo Esclavo - Recibe del Maestro y envia por MQTT
#los bites de la tupla [1] siempre sera la direccion del Nodo Maestro - Envia al esclavo
pipesa = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")  # -- NODO05  D2 -- d2
pipesb = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd4\xf0\xf0\xf0\xf0")  # -- NODO05  D4 -- d4
pipesc = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd6\xf0\xf0\xf0\xf0")  # -- NODO05  D6 -- d6
pipesd = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd8\xf0\xf0\xf0\xf0")  # -- NODO05  D8 -- d8
pipese = (b"\xe1\xf0\xf0\xf0\xf0", b"\xdb\xf0\xf0\xf0\xf0")  # -- NODO05  DB -- db
#------------   slave      -----------   master  ---------

#Diccionario para recibir el contenido de los sensores y nodo
body={}
send = False

while True:

  #Para ejecutar el reloj sin necesidad de apagarlo
  #currentMinute = int("{5:02d}".format(*rtc.datetime()))
  #if currentMinute%5==0:
  #  send = True

  if send:
    #Validar si el dato del NodoX ha sido recibida - mientras sea falsa - realiza la comunicación
    if not sendNode01:
      #Habilitar comunicación con el nodo de direccion pipesA[1] en la pipe 1
      packG = rf24.slave(pipesa,1)
      #Validar si el contenido del package corresponde al Nodo05
      isidA = packG.find("'S':'21'")
      if isidA > 0:
        sendNode01 = True
        #Agregar los datos de Nodo01 al Diccionario
        body['node01'] = str(packG)
        print(body)

    elif not sendNode02:
      #Habilitar comunicación con el nodo de direccion pipesB[1] en la pipe 2
      packB = rf24.slave(pipesb,2)
      #Validar si el contenido del package corresponde al Nodo02
      isidb = packB.find("'S':'12'")
      if isidb > 0:
        sendNode02 = True
        #Agregar los datos de Nodo02 al Diccionario
        body['node02'] = packB
        print(body)

    elif not sendNode03:
      #Habilitar comunicación con el nodo de direccion pipesC[1] en la pipe 3
      packC = rf24.slave(pipesc,3)
      #Validar si el contenido del package corresponde al Nodo03
      isidc = packC.find("'S':'23'")
      if isidc > 0:
        sendNode03 = True
        #Agregar los datos de Nodo03 al Diccionario
        body['node03'] = packC
        print(body)

    elif not sendNode04:
      #Habilitar comunicación con el nodo de direccion pipesD[1] en la pipe 4
      packD = rf24.slave(pipesd,4)
      #Validar si el contenido del package corresponde al Nodo04
      isidd = packD.find("'S':'14'")
      if isidd > 0:
        sendNode04 = True
        #Agregar los datos de Nodo04 al Diccionario
        body['node04'] = packD
        print(body)

    elif not sendNode05:
      #Habilitar comunicación con el nodo de direccion pipesE[1] en la pipe 0
      packE = rf24.slave(pipese,0)
      #Validar si el contenido del package corresponde al Nodo05
      iside = packE.find("'S':'25'")
      if iside > 0:
        sendNode05 = True
        #Agregar los datos de Nodo05 al Diccionario
        body['node05'] = packE
        print(body)

    elif not sendFirebase:

      print("Send to Firebase")
      jsonBody = ujson.dumps(body)
      #Envia los datos a AWS Lambda e insertarlos en  Firebase - RealTime
      client.publish(topic_subdb, jsonBody)
      sendFirebase = True
      time.sleep(1)
    else:
      print("All get package")
      #Envia los datos a AWS Lambda e insertarlos en  DynamoDB - No RealTime
      #jsonBody = ujson.dumps(body)
      #client.publish(topic_sub, jsonBody)
      del body
      body = {}
      send = False
      #Activar la alarma para despertar en <SleepTime> ms 
      rtc.alarm(rtc.ALARM0, sleepTime)
      print("Go to sleep....")
      # Poner a dormir la ESP por <SleepTime> ms
      machine.deepsleep()
  else:
    sendNode01 = False
    sendNode02 = False
    sendNode03 = False
    sendNode04 = False
    sendNode05 = False
    sendFirebase = False
    #Comentar si se esta ejecutando sin apagar y con el RTC para validar
    send = True
    time.sleep(1)

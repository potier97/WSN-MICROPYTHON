from umqtt.robust import MQTTClient
import machine
import time
import network
import urequests
import utime
import rf24
import ujson



#import os
#os.listdir()
#print(os.listdir())

clientId="piId",
thingName="GREENHOUSE-GATEWAY"
awsHost = 'a2ejpqeqsr9chb-ats.iot.us-east-1.amazonaws.com'   #EndPoint
awsPort = 8883                                               #Port No
#caPem = "/AmazonRootCA1.pem"                                  # Root_CA_Certificate_Name
#keyPath = "/4f44f5eed4-private.pem.key"                      # <Thing_Name>.pem.key
keyPath = "/4f44f5eed4-private.key.der"                      # <Thing_Name>.pem.key
#certPath = "/4f44f5eed4-certificate.pem.crt"                   # <Thing_Name>.pem.crt
certPath = "/4f44f5eed4-certificate.cert.der"                   # <Thing_Name>.pem.crt


with open(certPath, 'rb') as f:
  certData = f.read()
#print(certData)

with open(keyPath, 'rb') as f:
  keyData = f.read()
#print(keyData)

#mqtt_server = '192.168.1.50'
topic_sub = 'telemetry/data'
#messagge = 'holamundo'
#userId = 'greenhouse'
#passId = 'Telemetry20.'


url = "http://worldtimeapi.org/api/timezone/America/Bogota" 
#http://worldtimeapi.org/timezones
rtc = machine.RTC()


sendNode01 = False
sendNode02 = False
sendNode03 = False
sendNode04 = False
sendNode05 = False


def netWorkConnect(SSID, PASSWORD):
  nic  = network.WLAN(network.STA_IF)
  ap = network.WLAN(network.AP_IF)
  if not nic.isconnected():
    print('connecting to network...')
    nic.active(True)

    nic.connect(SSID, PASSWORD)
    while not nic.isconnected():
      #print(".", end="")
      pass
  ap.active(False)
  print('network config:', nic.ifconfig())
  return True

print("Iniciando......")

if netWorkConnect('YOUR_SSID','YOUR_PASSWORD'):
  #print('Connected')
  response = urequests.get(url)
  if response.status_code == 200:
    #print("JSON response:\n", response.text)
    parsed = response.json()

    datetime_str = str(parsed["datetime"])
    year = int(datetime_str[0:4])
    month = int(datetime_str[5:7])
    day = int(datetime_str[8:10])
    hour = int(datetime_str[11:13])
    minute = int(datetime_str[14:16])
    second = int(datetime_str[17:19])
    subsecond = int(round(int(datetime_str[20:26]) / 10000))
    #update internal RTC
    rtc.datetime((year, month, day, 0, hour, minute, second, subsecond))
    update_time = utime.ticks_ms()
    print("RTC updated\n")

  date_str = "Date: {1:02d}/{2:02d}/{0:4d}".format(*rtc.datetime())
  time_str = "Time: {4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime())
  print('Date: ' + date_str)
  print('Hour: ' + time_str)
  ##Connect to mqtt
  try:
    client = MQTTClient(thingName, server=awsHost, port=awsPort, ssl=True, keepalive=10000, ssl_params={'key':keyData,'cert':certData,"server_side":False})
    client.connect()
  except:
    pass
  print('Conctado a AWS')
  #client.publish(topic_sub, "{ 'testFuncional': 'true'  }")

#NodoDir 1 d2  D2   NODO05 invernadero  -- 01 -- 21
#NodoDir 2 d4  D4   NODO05 airelibre    -- 02 -- 12
#NodoDir 3 d6  D6   NODO05 invernadero  -- 03 -- 23
#NodoDir 4 d8  D8   NODO05 airelibre    -- 04 -- 14
#NodoDir 5 db  DB   NODO05 Invernadero  -- 05 -- 25
pipesa = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")  # -- NODO05  D2
pipesb = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd4\xf0\xf0\xf0\xf0")  # -- NODO05  D4
pipesc = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd6\xf0\xf0\xf0\xf0")  # -- NODO05  D6
pipesd = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd8\xf0\xf0\xf0\xf0")  # -- NODO05  D8
pipese = (b"\xe1\xf0\xf0\xf0\xf0", b"\xdb\xf0\xf0\xf0\xf0")  # -- NODO05  DB
#pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
#------------   slave      ---------------   master       ------------

body={}
errs = 0
send = False
algomas = True
while True:
    #try:
    #time.sleep(1)

    currentMinute = int("{5:02d}".format(*rtc.datetime()))
    if currentMinute%5==0:
      send = True

    if algomas:
      sendMqtt = True

    if sendMqtt:
      algomas = False

      if not sendNode01:
        try:  
          packG = rf24.slave(pipesa,1)
        except:
          pass
        isidA = packG.find("'S':'21'")
        if isidA > 0:
          sendNode01 = True
          body['node01'] = str(packG)
          print(body)

      elif not sendNode02:

        packB = rf24.slave(pipesb,2)
        isidb = packB.find("'S':'12'")
        if isidb > 0:
          sendNode02 = True
          body['node02'] = packB
          print(body)

      elif not sendNode03:

        packC = rf24.slave(pipesc,3)
        isidc = packC.find("'S':'23'")
        if isidc > 0:
          sendNode03 = True
          body['node03'] = packC
          print(body)

      elif not sendNode04:

        packD = rf24.slave(pipesd,4)
        isidd = packD.find("'S':'14'")
        if isidd > 0:
          sendNode04 = True
          body['node04'] = packD
          print(body)

      elif not sendNode05:

        packE = rf24.slave(pipese,0)
        iside = packE.find("'S':'25'")
        if iside > 0:
          sendNode05 = True
          body['node05'] = packE
          print(body)
          #sendNode01 = False

      else:
        print("All get package")
        try:
          jsonBody = ujson.dumps(body)
          #print(jsonBody)
          client.publish(topic_sub, jsonBody)
        except:
          pass
        del body
        body = {}
        sendMqtt = False
    else:
      algomas = True
      sendNode01 = False
      sendNode02 = False
      sendNode03 = False
      sendNode04 = False
      sendNode05 = False
      time.sleep(3)

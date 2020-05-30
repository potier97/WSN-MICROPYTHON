import machine
import urequests
import ujson

#Consume una api para calibrar el RTC la esp - mediante elu uso de una peticion request
#Para más informacipon del API: http://worldtimeapi.org

def calibrateRTC(getTimeApi='http://worldtimeapi.org/api/timezone/America/Bogota'):
  
  try:
    #Hacer request a <getTimeApi>
    response = urequests.get(getTimeApi)
  except:
    print('No se puede hacer la peticion')
  if response.status_code == 200:
    #Convierte los datos y los organiza en una tupla
    parsed = response.json()
    datetime_str = str(parsed["datetime"])
    year = int(datetime_str[0:4])
    month = int(datetime_str[5:7])
    day = int(datetime_str[8:10])
    hour = int(datetime_str[11:13])
    minute = int(datetime_str[14:16])
    second = int(datetime_str[17:19])
    subsecond = int(round(int(datetime_str[20:26]) / 10000))
    #Retorna la tupla de 8 datos, estos datos luego se pasan a RTC().datetime(<Tupla>)
    #rtc.datetime((year, month, day, 0, hour, minute, second, subsecond))
    return (year, month, day, 0, hour, minute, second, subsecond)
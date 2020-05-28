import machine
import time
import network
import dht
import rf24

# configure RTC.ALARM0 to be able to wake the device
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

nic = network.WLAN(network.AP_IF)
nic.active(False)

print("Iniciando......")
print("Nod 01")
#print("Estado del firmware: " + str(esp.check_fw()))

# check if the device woke from a deep sleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('woke from a deep sleep')
else:
    print('power on or hard reset')

sleepTime = 10000
#Starting DHT11 on gpio 4
sensor = dht.DHT11(machine.Pin(4))

pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
#NodoDir 1 d2  D2   NODO05 invernadero  -- 01 -- 21
#NodoDir 2 d4  D4   NODO05 airelibre    -- 02 -- 12
#NodoDir 3 d6  D6   NODO05 invernadero  -- 03 -- 23
#NodoDir 4 d8  D8   NODO05 airelibre    -- 04 -- 14
#NodoDir 5 db  DB   NODO05 Invernadero  -- 05 -- 25
#------------   slave      ---------------   master   -----

#nrf.open_tx_pipe(pipes[1])
#nrf.open_rx_pipe(1, pipes[0])


errs = 0
while True:
  try:
    time.sleep(2)
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    formatTemp = '{:4.2f}'.format(temp)
    formatHum = '{:4.2f}'.format(hum)
    #print('Temperature: {} C'.format(formatTemp))
    #print('Humidity: {} %'.format(formatHum))

    state = False
    while not state:
        state = rf24.master(21,formatTemp,formatHum, pipes, 1)
    if state:
        print("Se envio la informacion")
	rtc.alarm(rtc.ALARM0, sleepTime)
	# put the device to sleep
	machine.deepsleep()
  except:
    errs +=1
    print('Failed to read sensor.')
    if errs > 4:
      #pass
      machine.reset()

import sys
import ustruct as struct
import utime
from machine import Pin, SPI
from nrf24l01 import NRF24L01
from micropython import const
#import ujson as json



# Slave pause between receiving data and checking for further packets.
_RX_POLL_DELAY = const(15)
# Slave pauses an additional _SLAVE_SEND_DELAY ms after receiving data and before
# transmitting to allow the (remote) master time to get into receive mode. The
# master may be a slow device. Value tested with Pyboard, ESP32 and ESP8266.
_SLAVE_SEND_DELAY = const(10)


cfg = {"spi": 1, "miso": 12, "mosi": 13, "sck": 14, "csn": 15, "ce": 2}

# Addresses are in little-endian format. They correspond to big-endian
# 0xf0f0f0f0e1, 0xf0f0f0f0d2
#pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")


def master(id = 00, temperature=20.20, humidity=30.30, pipe=(b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0"), npipe=1):

    body={}
    body['S'] = str(id)
    body['T'] = str(temperature)
    body['H'] = str(humidity)
    bodyString = str(body)
    bodyString = bodyString.replace(" ", "")


    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=32)



    nrf.open_tx_pipe(pipe[0])
    nrf.open_rx_pipe(npipe, pipe[1])
    #nrf.open_tx_pipe(pipes[0])
    #nrf.open_rx_pipe(1, pipes[1])
    nrf.start_listening()


    #pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
    #nrf.open_tx_pipe(pipe[1])
    #nrf.open_rx_pipe(1, pipe[0])



    statusSuccess = 0
    confirmSuccess = 5
    #print("NRF24L01 master mode, enviando hasta que responda")

    while statusSuccess < confirmSuccess:
        nrf.stop_listening()
        #millis = utime.ticks_ms()
        #print("sending:", bodyString )
        try:
            #print("se esta enviando")
            #nrf.send("hola mundo")
            nrf.send(struct.pack('32s', bodyString))
        except OSError:
            pass

	# start listening again
        nrf.start_listening()

        # wait for response, with 250ms timeout
        start_time = utime.ticks_ms()
        timeout = False


        while not nrf.any() and not timeout:
            if utime.ticks_diff(utime.ticks_ms(), start_time) > 250:
                timeout = True

        if timeout:
            print("No confirm")

        else:
            # recv packet
            buff = nrf.recv()
	    (res,)  = struct.unpack("i", buff)
  	    if res > 5:
	        statusSuccess = res

        # delay then loop
        utime.sleep_ms(250)

    return True

def slave(pipe, npipe):
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=32)

    nrf.open_tx_pipe(pipe[1])
    nrf.open_rx_pipe(npipe, pipe[0])
    nrf.start_listening()
    #pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
    #nrf.open_tx_pipe(pipes[1])
    #nrf.open_rx_pipe(1, pipes[0])
    #print("NRF24L01 slave mode, waiting for packets...")
    statusPackage = False
    pack = False
    while not statusPackage:
        if nrf.any():
            while nrf.any():
                buf = nrf.recv()
                (led_state,) = struct.unpack('32s', buf)
                #print("received:",  led_state)
                utime.sleep_ms(_RX_POLL_DELAY)


            package = led_state
            package = package.decode('UTF-8')
            package = package + "}"
            package = str(package)
            #print(package)
            if isinstance(package, str):
              pack = True
              #print("str pack")
            #Give response master
            utime.sleep_ms(_SLAVE_SEND_DELAY)
            nrf.stop_listening()
            try:
                nrf.send(struct.pack("i", 20))
                nrf.send(struct.pack("i", 20))
                #print("sent response")
            except OSError:
                #print("Error enviando")
                pass
            #print("sent response")
            if pack and len(package) > 0:
              #pass
              #print('se recivio paquete')
              statusPackage = True
            nrf.start_listening()
    return package


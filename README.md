# WSN-MICROPYTHON

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Proyecto básico de red de nodos (WSN), utilizando el transceptor NRF24L01+ con el ESP8266 y el sensor de temperatura y humedad DHT11, usada para obtener datos en 5 nodos y enviar estos datos a un gateway que se conecta con AWS-IOT, ejecuta una regla del topic selesccionado, que posteriormente activa un script para enviar o insertar los datos a una base de datos, en este proyecto nos conectamos a dos bases de datos DynamoDB de AWS y Firebase, el envio a la base de datos depende del tema MQTT seleccionado, todo esto se ejecuta sobre Micropython, en este repositorio se enseña como configurar cada nodo, como funcinan los scripts, y como configurar AWS para poder replicado facil y rapidamente. Este proyecto se realiza utilizando una raspberry cargar el código y hacer pruebas sobre el proyecto.

Puede saber más sobre [Micropython](https://micropython.org/) en su pagina oficial.
También puede consultar la documentación  de [Micropython](https://docs.micropython.org/en/latest/index.html) para entender como trabaja.

A continuación se muestran el paso a paso para poder construir el proyecto: 

  - Configuración de Esp8266 con micropython
  - Cargar los scripts, certificados y llaves a la esp8266 usando una herramienta
  - Conexión de nodos
  - Cómo funciona el proyecto
  - Visualizar los datos en consola, utilizando minicom
  - Pruebas y resultados obtenidos


Para replicar este proyecto necesitará:
 - Esp8266
 - Nrf24l01
 - DHT11
 - OS Linux - En nuestro caso utilizamos una Raspberry Pi


## Configuración de Esp8266 con micropython

Para iniciar debe tener a mano una ESP8266, conectela a su computadora, en este caso utilizamos una raspberry para configurarlo. Utilizando la terminal instalamos las siguientes herramientas, python3 o python2, esptool (Herramienta que nos permite hacer el flash sobre la esp8266 y cargar el firmware), minicom (permite ver por comunicación serial lo que imprime nuestros nodos).

Entonces instalamos usando la terminal conectados desde Putty, primero actualizamos nuestra RPI

#### Actualizar sistema operativo 
```sh
$ sudo apt-get update
$ sudo apt-get upgrade -y
```

#### Instalamos Python:
```sh
$ sudo apt-get install python3 python
```
#### Instalamos PIP (Herramienta de python para descargar módulos):
```sh
$ sudo apt install python3-pip
$ sudo apt install python-pip
```
#### Instalamos esptool
```sh
$ sudo pip install esptool.
```
#### Instalar minicom
```sh
$ sudo apt-get install minicom.
```
#### Para iniciar minicom, simplemente se hace con:
```sh
$ minicom -s
```
### Descargar el Firmware para la esp8266
Lo descargamos de la pagina oficial de micropython si posee un esp8266 con 1024 Kb de flash necesitan la versióm estable, si posee un esp8266 con 512 Kb necesitan la daily de 512 Kb.

Enlace directo a la página: [Descargar el Firmware](https://micropython.org/download/esp8266/)
Para este caso utilizamos el Firware estable, 1M o más de flash: [esp8266-20191220-v1.12.bin](https://micropython.org/resources/firmware/esp8266-20191220-v1.12.bin), puede descargarlo directamente con este enlace.

### Carpeta del proyecto
Recuerde que estamos haciendo esto sobre la raspberry, por lo tanto copie este archivo en una carpeta para realizar el proyecto.
```sh
$ mkdir wsn
$ cd wsn
```

### Herramienta Micropython
El proyecto de [Micropythone](https://github.com/micropython/micropython) en GIT, posee distintas herramientas para facilitar el desarrollo de proyectos, en nuestro caso utilizaremos un script llamado  [pyboard.py](https://github.com/micropython/micropython/blob/master/tools/pyboard.py), descarguelo o copie y pegue el codigo en un script nuevo.
```sh
$ sudo nano pyboard.py
```
#### ¿Cómo funciona esta herramientas?
Su principal funcionalidad es descrita en el proyecto: 

> "Este módulo proporciona la clase Pyboard, utilizada para comunicarse con y
> controlar un dispositivo MicroPython a través de un canal de comunicación. Tanto real
> se admiten placas y dispositivos emulados (por ejemplo, que se ejecutan en QEMU).
> Se admiten varios canales de comunicación, incluido un serial
> conexión, conexión de red estilo telnet, proceso externo conexión."

Puede revisar cómo trabaja esta herramienta en [Micropython](https://docs.micropython.org/en/latest/reference/pyboard.py.html) revise su documentación o puede ver desde la consola ejecutando:

```sh
$ python ./pyboard.py --help
```
O con python 3
```sh
$ python3 ./pyboard.py --help
```
#### Comandos básicos de pyboard.py
Cargar un script en la esp8266 llamado main.py (Script que siempre se ejecutara cuando cargue el firmware en la esp8266)
```sh
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp main.py:
```
 - --device /dev/ttyUSB0
 - Dispositivo conectado a la raspberry

Para saber en donde estan conectados los dispositivos, puede ejecutar lo siguiente:
```sh
$ ls /dev/ttyUSB*
```
Esto listara todos los dispositivos conectados. teniendo en cuenta que el dispositivo esta conectado por USB

 - -f cp 
 - Mediante -f podemos ejecutar comandos básicos de sheelm tales como cp, mkdir, rm, mv
 - main.py :main.py
 - El primer argumento hace referencia al directorio de la raspberry, mientras que el segundo, seguido de ":" hace referencia a los archivos ubicados en la esp8266 

### Implementar  el Firmware
Utilizando la herramienta esptool se carga el firmware a la esp8266, teniendo el archivo esp8266-20191220-v1.12.bin en la carpeta wsn.

Primero borramos la flash de la esp8266, ejecutando:
```sh
$ esptool.py --port /dev/ttyUSB0 erase_flash
```
Cargamos el firmware a la esp8266
```sh
$ esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash --flash_size=detect 0 esp8266-20191220-v1.12.bin
```
-  --port /dev/ttyUSB0 
-  Hace referencia al puerto donde esta conectado
-  --baud 115200
-  Velocidad de comunicación
-  --flash_size=detect 0
-  Poscición de donde va a estar escrito el firmware en la flash
-  esp8266-20191220-v1.12.bin
-  Firmware a cargar en la esp8266

Ahora ya puede cargar nuevos Scripts en la esp8266 haciendo uso de la herramienta pyboard, por ejemplo, encendiendo y apagando un led.
```py
import machine
import time
led = machine.Pin(2, machine.Pin.OUT)
while True:
  led.high()
  time.sleep(1)
  led.low()
  time.sleep(1)
```
El módulo machine, es uno de los más importantes ya que hace uso directamente del hardware como lo son los pines. Algo a tener en cuenta es que en micropython la identación solo debe ser de 2 espacios.

Si queremos ver un ejemplo usando la terminal de minicom, con un script como:
```py
import time
while True:
  print("Hola Mundo")
  time.sleep(1)
```
Pero antes, es necesario cargar los scripts en  la board, como:
```sh
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp main.py :main.py
```
Luego hacemos reset RST sobre el pin de la esp8266 para iniciar a ejecutar el script, ahora, si tenemos minicom en ttyUSB0, ejecutamos:
```sh
$ minicom -D /dev/ttyUSB0
```

Para poder salir de la terminal, solamente preciona:
CTRL + A
Luego, presiona:
q
con esto saldra un aviso si desea salir de minicom, selecciona YES, y luego Enter.

## Cargar los scripts, certificados y llaves a la esp8266 usando una herramienta
Tenemos (5) nodos Maestro, que cumplen la funcion de enviar datos obtenidos de los sensores de humedad y temperatura del sensor DHT11 al nodo esclavo o Gateway por medio del tranceptor NRF24L01, luego  de ser recibidos, el Gateway envia los datos a AWS IOT. Pero, ¿Que scripts son necesarios para eso?

#### Nodo Maestro

- [main.py](https://github.com/potier97/WSN-MICROPYTHON/blob/master/masterNode/main.py) 
- [nrf24l01.py](https://github.com/potier97/WSN-MICROPYTHON/blob/master/masterNode/nrf24l01.py) 
- [rf24.py](https://github.com/potier97/WSN-MICROPYTHON/blob/master/masterNode/rf24.py) 

Ahora cargamos los scripts en los (5) nodos, teniendo los scripts en una subcarpeta del directorio del proyecto, ya que algunos de los scripts del nodos esclavo se llaman igual, y tambien copiamos el script de pyboard.py:

```sh
$ mkdir nodeMaster
$ cd nodeMaster
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp main.py :main.py
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp nrf24l01.py :nrf24l01.py
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp rf24.py :rf24.py
```

#### Nodo Esclavo
- [main.py](https://github.com/potier97/WSN-MICROPYTHON/blob/master/slaveNode/main.py) 
- [nrf24l01.py](https://github.com/potier97/WSN-MICROPYTHON/blob/master/slaveNode/nrf24l01.py) 
- [rf24.py](https://github.com/potier97/WSN-MICROPYTHON/blob/master/slaveNode/rf24.py) 
- [wificonnect.py](https://github.com/potier97/WSN-MICROPYTHON/blob/master/slaveNode/wificonnect.py) 
- [timeSynchronizer.py ](https://github.com/potier97/WSN-MICROPYTHON/blob/master/slaveNode/timeSynchronizer.py) 
- [4f44f5eed4-certificate.cert.der](https://github.com/potier97/WSN-MICROPYTHON/blob/master/slaveNode/4f44f5eed4-certificate.cert.der) 
- [4f44f5eed4-private.key.der](https://github.com/potier97/WSN-MICROPYTHON/blob/master/slaveNode/4f44f5eed4-private.key.der) 
Luego cargamos los scripts del nodo Esclavo , al igual en otra sub carpeta del directorio del proyecto, ya que algunos de los scripts del nodos maestro se llaman igual, y tambien copiamos el script de pyboard.py:

```sh
$ mkdir nodeSlave
$ cd nodeSlave
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp main.py :main.py
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp nrf24l01.py :nrf24l01.py
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp rf24.py :rf24.py
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp wificonnect.py :wificonnect.py
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp timeSynchronizer.py :timeSynchronizer.py
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp 4f44f5eed4-certificate.cert.der :4f44f5eed4-certificate.cert.der
$ python ./pyboard.py --device /dev/ttyUSB0 -f cp 4f44f5eed4-private.key.der :4f44f5eed4-private.key.der
```

## Conexión de nodos

#### Nodo Maestro
Utilizando una Esp8266, un transceptor nrf24l01 y un sensor DHT11 se contruye el nodo Maestro, Siga el diagrama de conexión:
![nodeMaster](diagram/nodeMaster.png)


| Esp8266 | Nrf24l01 |
| ------ | ------ |
| Gnd | Gnd - Pin 1 |
| Vcc | Vcc - Pin 2 |
| D4 - GPIO 2  | CE - Pin 3 |
| D8 - GPIO 15 | CS - Pin 4 |
| D5 - GPIO 14 | SCK - Pin 5 |
| D7 - GPIO 13 | MOSI - Pin 6 |
| D6 - GPIO 14 | Miso - Pin 7 |

| Esp8266 | Dht11 |
| ------ | ------ |
| Gnd | Gnd - Pin 4 |
| Vcc | Vcc - Pin 1 |
| D2 - GPIO  | Data - Pin 2 |


El pin GPIO 16 o D0, Debe ir conectado al pin RST, esto con el fin de poder tener la funcionalidad de DeepSleep.


#### Nodo Esclavo
Utilizando una Esp8266 y un transceptor nrf24l01 se contruye el nodo Esclavo, Siga el diagrama de conexión:

![nodeSlave](diagram/nodeSlaver.png)

| Esp8266 | Nrf24l01 |
| ------ | ------ |
| Gnd | Gnd - Pin 1 |
| Vcc | Vcc - Pin 2 |
| D4 - GPIO 2  | CE - Pin 3 |
| D8 - GPIO 15 | CS - Pin 4 |
| D5 - GPIO 14 | SCK - Pin 5 |
| D7 - GPIO 13 | MOSI - Pin 6 |
| D6 - GPIO 14 | Miso - Pin 7 |

El pin GPIO 16 o D0, Debe ir conectado al pin RST, esto con el fin de poder tener la funcionalidad de DeepSleep.

## Cómo funciona el proyecto
Los nodos maestro se organizan de la siguiente manera, simulando que estan desplegados en campo, aunque todos los nodos se conectan al mismo Gateway:
| Nodo | Direccion | Zona |
| ------ | ------ | ------ |
| Nodo 00 | 0xF0F0F0F0E1 | Gateway |
| Nodo 01 | 0xF0F0F0F0D2 | invernadero |
| Nodo 02 | 0xF0F0F0F0D4 | airelibre |
| Nodo 03 | 0xF0F0F0F0D6 | invernadero |
| Nodo 04 | 0xF0F0F0F0D8 | airelibre |
| Nodo 05 | 0xF0F0F0F0DB | invernadero |



El siguiente diagrama de flujo muestra como es el proceso de obtencion de datos por el nodo esclavo:
![diagramSlave](diagram/DiagramaSlave.png)
El siguiente diagrama de flujo muestra como es el proceso de envio de datos por los nodos maestro:
![diagramMaster](diagram/DiagramaMaster.png)
El siguiente diagrama muestra la solución IOT utilizando AWS con Lambda, DynamoDB e IoT firebase y Firebase con su base de datos en tiempo real.
![architecture](diagram/arquitectura.png)


## Visualizar los datos en consola, utilizando minicom
Usando minicom. se puede ver como se capturan los datos y luego se envian, nuevamente iniciamos minicom, pero antes hay que tener en cuenta que el nodo Esclavo o Gateway necesita un certificado y llave privada para poder hacer la conexion a AWS MQTT, entonces, cuando se registra, se descargan los certificados y llaves para su validación, cuando se hace la conexión con MQTT a AWS esta se demora por los menos 1 minuto, debido a que utiliza certificados y llave clave que deben ser de tipo .der, estos se convierten ya que la esp8266 los puede leer solo en ese formato utilizando micropython,  para transformarlos utilice el módulo SSL, y ejecute los siguientes comandos.

```sh
$ sudo apt-get install openssl
$ openssl x509 -in <NAME-CERT-FILE>.cert.pem -out <NAME-CERT-FILE>.cert.der -outform DER 
$ openssl rsa -in <NAME-PRIVATE-KEY-FILE>.key.pem -out <NAME-PRIVATE-KEY-FILE>.key.der -outform DER
```
Para mas información del registro de Things en aws, revise el siguiente enlace: [Connect ESP 8266 to AWS MQTT using Miropython](https://awsiot.wordpress.com/2019/01/10/connect-8266-to-aws-mqtt-using-miropython/) 


Ahora, para ver el comportamiento del nodo en la consola, ejecutar nuevamente:

```sh
$ minicom -D /dev/ttyUSB0
```
Obteniendo los siguientes resultados.
![minicom](diagram/minicom.PNG)

Y en la base de datos Firebase se insertan
![firebase](diagram/firebaseData.PNG)

## Pruebas y resultados obtenidos
La siguiente imagen corresponde a la red de sensores desarrollada y probada
 
![physicalNodes](diagram/node.jpeg)

Por último hacemos un video para mostrar las pruebas desu funcionamiento de la red y subida a la base de datos. 
[![Watch the video](data:image/jpeg;base64,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)](https://youtu.be/MvrBQI6z2Rs)

[![Watch the video](https://i9.ytimg.com/vi/u97SmdQfPmQ/mq2.jpg?sqp=CIjTyfYF&rs=AOn4CLDobSrhSrVcpUK-tt71t9ul8RqV6A)](https://youtu.be/u97SmdQfPmQ)


License
----
MIT

import base64
import array
import StringIO
import RPi.GPIO as GPIO
import time
from picamera import PiCamera
from time import sleep
from PIL import Image
from io import BytesIO
from google.cloud import vision
from google.cloud.vision import types

#HackMTY 2018, parte del programa que despliega los arreglos prederminados
#para poder hacer la conexion con el hardware y se puedan imprimir


# IO Ports
pins=[22,7,16,13,18,15]

# Sometimes GPIO they are being used
GPIO.cleanup()

GPIO.setmode(GPIO.BOARD)

GPIO.setup (pins[0], GPIO.OUT)
GPIO.setup (pins[1], GPIO.OUT)
GPIO.setup (pins[2], GPIO.OUT)
GPIO.setup (pins[3], GPIO.OUT)
GPIO.setup (pins[4], GPIO.OUT)
GPIO.setup (pins[5], GPIO.OUT)

m1 = GPIO.PWM(pins[0],50)
m2 = GPIO.PWM(pins[1],50)
m3 = GPIO.PWM(pins[2],50)
m4 = GPIO.PWM(pins[3],50)
m5 = GPIO.PWM(pins[4],50)
m6 = GPIO.PWM(pins[5],50)

motorsArray = [m1,m2,m3,m4,m5,m6]

# Braile reference as arrays of 6 dots positions

braille={"a":[1,0,0,0,0,0],"b":[1,0,1,0,0,0],"c":[1,1,0,0,0,0],"d":[1,1,0,1,0,0],"e":[1,0,0,1,0,0],"f":[1,1,1,0,0,0],"g":[1,1,1,1,0,0],"h":[1,0,1,1,0,0],"i":[0,1,1,0,0,0],"j":[0,1,1,1,0,0],"k":[1,0,0,0,1,0],"l":[1,0,1,0,1,0],"m":[1,1,0,0,1,0],"n":[1,1,0,1,1,0],"o":[1,0,0,1,1,0],"p":[1,1,1,0,1,0],"q":[1,1,1,1,1,0],"r":[1,0,1,1,1,0],"s":[0,1,1,0,1,0],"t":[0,1,1,1,1,0],"u":[1,0,0,0,1,1],"v":[1,0,1,0,1,1],"w":[0,1,1,1,0,1],"x":[1,1,0,0,1,1],"y":[1,1,0,1,1,1],"z":[1,0,0,1,1,1],".":[0,0,1,1,0,1],",":[0,0,1,0,0,0],";":[0,0,1,0,1,0],":":[0,0,1,1,0,0],"/":[0,1,0,0,1,0],"?":[0,0,1,0,1,1],"!":[0,0,1,1,1,0],"'":[0,0,1,0,1,1],"(":[0,0,1,1,1,1]}


# This sets motors position based on character a hash map
def setLetter(letterin):
        try:
            fila = 0
            columna = 0
            while fila < 3:
                columna = 0
                while columna < 2:
                        print("Value for motor {}  is  {}".format(fila*2+columna,braille[letterin][fila*2+columna]))
                        
                        if(braille[letterin][fila*2+columna]):
                                if(columna==0):
                                        print("Set to 10")
                                        motorsArray[fila*2+columna].start(10)
                                else:
                                        print("Set to 2")
                                        motorsArray[fila*2+columna].start(2)
                        else:
                                if(columna==0):
                                        print("Set to 2")
                                        motorsArray[fila*2+columna].start(2)
                                else:
                                        print("Set to 10")
                                        motorsArray[fila*2+columna].start(10)

                        sleep(1)
                        #motorsArray[fila*2+columna].stop()
                        columna += 1
                fila += 1
        except:
            print("")




camera = PiCamera()

camera.resolution = (1024,768)
camera.rotation = 180
camera.start_preview()
sleep(0.5)

# This method takes image and send it to Google WS
def sendToGoogleAndProcess(content):
	client = vision.ImageAnnotatorClient()
	response = client.annotate_image({'image': {'content': content}, 'features': [{'type': vision.enums.Feature.Type.TEXT_DETECTION}],})
	print(response.full_text_annotation.text)
	for letter in response.full_text_annotation.text:
            print(letter)
            setLetter(str(letter).lower())
            

#Process image and send
output = StringIO.StringIO()

# Keep on recognizing image and process it
while True:
	sleep(0.3)
	stream = BytesIO()
	camera.capture(stream, format='jpeg')
	# "Rewind" the stream to the beginning so we can read its content
	stream.seek(0)
	sendToGoogleAndProcess(stream.getvalue())
        sleep(2)

camera.stop_preview()


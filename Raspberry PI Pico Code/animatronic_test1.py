#
# initial test code using both cores of a Pico W. Core 0 is running a sensor thread for the KY-008 laser 
# via a DaFuRui 5V Relay board. The relay connects to pin14 on the Pico. When i break the beam between the 
# ky-008 and sensor it trips the relay which activates the p14 on Pico. Then the core1 kicks off and turns 
# on each of the four SB Components Pico Relay Board (a really cool board!!!) 
# in series with a sleep between each relay to let the animatronic play.
#
from machine import Pin, lightsleep
import _thread
import time, utime

relay1 = Pin(18, Pin.OUT)
relay2 = Pin(19, Pin.OUT)
relay3 = Pin(20, Pin.OUT)
relay4 = Pin(21, Pin.OUT)

# thread syncronization 
runAnimatronic=False

# sensor Pin
sensorPin = Pin(14,Pin.IN, Pin.PULL_UP)

def allOn():
    #relay1.value(1)
    relay2.value(1)
    relay3.value(1)
    relay4.value(1)
    

    
def allOff():
    #relay1.value(0)
    relay2.value(0)
    relay3.value(0)
    relay4.value(0)


def sensorThread():
    global runAnimatronic
    global sensorPin
    c=0
    while True:
        print("count=",c," p14=",sensorPin.value())
        lightsleep(50)
        c = c + 1
        if sensorPin.value() == 0:
            print("turn on LED")
            relay1.value(1)
            runAnimatronic=True
            print("waiting for animatronics to run")
            while runAnimatronic == True:
                pass
        else:
            print("turn off LED")
            relay1.value(0)
            

        
def animatronicThread():
    global runAnimatronic
    while True:
        print("run animatronics")


        while runAnimatronic == False:
            pass


        print("Animatronic #1 - led")
        #relay1.toggle()
        #utime.sleep(5)
        #allOff()
        
        print("Animatronic #2 - empty")
        relay2.toggle()
        utime.sleep(5)
        allOff()
        
        print("Animatronic #3 - skull")
        relay3.toggle()
        utime.sleep(10)
        allOff()
        
        print("Animatronic #4 - girl")
        relay4.toggle()
        utime.sleep(20)
        allOff()    
    
        runAnimatronic=False

allOff()
sensorPin.value(0)
animatronic = _thread.start_new_thread(animatronicThread,())
print("Start Sensor Thread")
sensorThread()
allOff()

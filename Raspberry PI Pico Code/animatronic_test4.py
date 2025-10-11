#
# initial test code using both cores of a Pico W. Core 1 is running a sensor thread for the KY-008 laser 
# via a DaFuRui 5V Relay board. The relay connects to pin14 on the Pico. When I break the beam between the 
# ky-008 and sensor it trips the relay which activates the p14 on Pico. Then the core_1 kicks off and turns 
# on each of the four SB Components Pico Relay Board (a really cool board!!!) 
# in series with a sleep between each relay to let the animatronic play.
#
from machine import Pin, lightsleep, PWM
import _thread
import time, utime

relay1 = Pin(18, Pin.OUT)
relay2 = Pin(19, Pin.OUT)
relay3 = Pin(20, Pin.OUT)
relay4 = Pin(21, Pin.OUT)

# Initialize pins for LEDs
red = PWM(Pin(6), freq=1000)  #  red LED
yellow = PWM(Pin(7), freq=1000)  #  yellow LED
green = PWM(Pin(8), freq=1000)  # green LED

# thread syncronization 
runAnimatronic=False

#enabel debugging
debug=True
debug2=False

# sensor Pin
sensorPin = Pin(14,Pin.IN, Pin.PULL_UP)



# Function to set the brightness of an LED (0-100%)
def set_brightness(led, brightness):
    if brightness < 0 or brightness > 100:
        raise ValueError("Brightness should be between 0 and 100")
    led.duty_u16(int(brightness / 100 * 65535))


    

def allOn():
    relay1.value(1)
    relay2.value(1)
    relay3.value(1)
    relay4.value(1)
    

    
def allOff():
    relay1.value(0)
    relay2.value(0)
    relay3.value(0)
    relay4.value(0)


def sensorThread():
    global runAnimatronic
    global sensorPin
    c=0
    set_brightness(green, 100)
    set_brightness(red, 0)

    while True:
        #utime.sleep(20) #remove before use
        if debug2: print("count=",c," sesnor/pin_14=",sensorPin.value())
        lightsleep(50)
        c = c + 1
        #trip=0
        #if trip == 0:
        if sensorPin.value() == 0:
            #print("turn on LED")
            #relay1.value(1)
            if debug: print("Waiting for animatronics to run")
            runAnimatronic=True
            while runAnimatronic == True:
                pass
            set_brightness(green, 100)
        else:
            #if debug: print("Turn off LED")
            #relay1.value(0)
            pass
        
def animatronicThread():
    global runAnimatronic
    while True:


        while runAnimatronic == False:
            pass

        if debug: print("Run Animatronics")

        if debug: print("Animatronic #1 - empty")
        relay1.toggle()
        utime.sleep(4)
        set_brightness(red, 100)
        set_brightness(green, 0)
        allOff()
        
        if debug: print("Animatronic #2 - girl")
        relay2.toggle()
        utime.sleep(10)
        allOff()
        
        if debug: print("Animatronic #3 - empty")
        relay3.toggle()
        utime.sleep(4)
        allOff()
        
        if debug: print("Animatronic #4 - skull")
        relay4.toggle()
        utime.sleep(10)
        
        allOff()    
        set_brightness(red, 0)
        runAnimatronic=False

if debug: print("Initializing System, please wait...")
set_brightness(green, 100)
set_brightness(yellow, 100)
set_brightness(red, 100)
utime.sleep(2)
set_brightness(green, 0)
set_brightness(red, 0)
allOff()
allOn()
utime.sleep(2)
allOff()
sensorPin.value(0)
runAnimatronic=False
set_brightness(yellow, 0)
utime.sleep(20)

if debug: print("Start Animatronic Thread")
animatronic = _thread.start_new_thread(animatronicThread,())
if debug: print("Start Sensor Thread")
sensorThread()

allOff()

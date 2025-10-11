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

#configure controller/animatronics pairing
animatronicsCfg = [['empty_c1s1',2, 'girl',10,'empty_c1s3',1,'skull',10],
                    ['empty_c2s1]',1, 'empty_c2s2',1,'empty_c2s3',1,'empty_c2s4',1],
                    ['empty_c3s1]',1, 'empty_c2s2',1,'empty_c3s3',1,'empty_c3s4',1],
                    ['empty_c4s1]',1, 'empty_c2s2',1,'empty_c4s3',1,'empty_c4s4',1],
                    ['empty_c5s1]',1, 'empty_c2s2',1,'empty_c5s3',1,'empty_c5s4',1],
                    ['empty_c6s1]',1, 'empty_c2s2',1,'empty_c6s3',1,'empty_c6s4',1]]
controllerNumber=1
animatronicsInitialDelay=20

# initialize pins for relays (animatronics)
relay1 = Pin(18, Pin.OUT)
relay2 = Pin(19, Pin.OUT)
relay3 = Pin(20, Pin.OUT)
relay4 = Pin(21, Pin.OUT)

# Initialize pins for LEDs
red = PWM(Pin(6), freq=1000)  #  red LED
yellow = PWM(Pin(7), freq=1000)  #  yellow LED
green = PWM(Pin(8), freq=1000)  # green LED

# sensor Pin
sensorPin = Pin(14,Pin.IN, Pin.PULL_UP)

# initialize pins for dip switch
dipSwitchPin1 = Pin(10, Pin.IN,Pin.PULL_UP)
dipSwitchPin2 = Pin(11, Pin.IN,Pin.PULL_UP)
dipSwitchPin3 = Pin(12, Pin.IN,Pin.PULL_UP)
dipSwitchPin4 = Pin(13, Pin.IN,Pin.PULL_UP)

# thread syncronization 
runAnimatronic=False

#enabel debugging
debug=True
debug2=True


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

        if debug: print("Animatronic #1 - ",animatronicsCfg[controllerNumber-1][0],"/",animatronicsCfg[controllerNumber-1][1])
        relay1.toggle()
        utime.sleep(animatronicsCfg[controllerNumber-1][1])
        set_brightness(red, 100)
        set_brightness(green, 0)
        allOff()
        
        if debug: print("Animatronic #2 - ",animatronicsCfg[controllerNumber-1][2],"/",animatronicsCfg[controllerNumber-1][3])
        relay2.toggle()
        utime.sleep(animatronicsCfg[controllerNumber-1][3])
        allOff()
        
        if debug: print("Animatronic #3 - ",animatronicsCfg[controllerNumber-1][4],"/",animatronicsCfg[controllerNumber-1][5])
        relay3.toggle()
        utime.sleep(animatronicsCfg[controllerNumber-1][5])
        allOff()
        
        if debug: print("Animatronic #4 - ",animatronicsCfg[controllerNumber-1][6],"/",animatronicsCfg[controllerNumber-1][7])
        relay4.toggle()
        utime.sleep(animatronicsCfg[controllerNumber-1][7])
        
        allOff()    
        set_brightness(red, 0)
        if debug: print("Animatronics Run Done")
        runAnimatronic=False


if debug: print("Initializing System, please wait...")
if debug: print("Controller Number=",controllerNumber)
if debug: print("Animatronics Configured=",animatronicsCfg[controllerNumber-1])
set_brightness(green, 100)
set_brightness(yellow, 100)
set_brightness(red, 100)
utime.sleep(2)
set_brightness(green, 0)
set_brightness(red, 0)
if debug: print("All Animatronics will activate to verify function")
allOff()
allOn()
utime.sleep(2)
allOff()
sensorPin.value(0)
runAnimatronic=False
utime.sleep(animatronicsInitialDelay)
set_brightness(yellow, 0)

set_brightness(green, 100)
if debug: print("Start Animatronic Thread")
animatronic = _thread.start_new_thread(animatronicThread,())
if debug: print("Start Sensor Thread")
if debug: print("Controller is now live!")
sensorThread()

allOff()

#
# Halloween Animatronic Automation System
# This code is using both cores of a Pico or Pico W. Core 1 is running a sensor thread for the KY-008 laser
# detector via a DaFuRui 5V Relay board. The relay connects to pin14 on the Pico. When someone breaks the
# beam between the ky-008 laser and detector it trips the relay which activates the p14 on Pico.
# Then the core_1 kicks off and turns on each of the four SB Components Pico Relay Board (a really cool board!!!) 
# in series with a sleep between each relay to let the animatronic play.
#
# This code also controller an stop light LED board do show status of the controller during boot (yellow),
# green when waiting for someone to trip the laster and then red once the animatronics start running. 
#
# it supports 6 controllers by configuring the animatronics in the animatronicCfg List
#
# plan it select which controller id via dipswitch but find a way to mount that on a case is problematic.
#
#
codeRev="2"
codeDate="11 Oct 2025"

from machine import Pin, lightsleep, PWM
import _thread
import time, utime

# configure controller/animatronics pairing
# 
#  this is design for our maze which have 6 raspberry pico controllers. 
#
# cxr1 is controller #, relay #
animatronicsCfg = [['girl',4, 'skull',4,'pumpkin',4,'empty_c1r4',4],
                    ['empty_c2r1]',1, 'empty_c2r2',1,'empty_c2r3',1,'empty_c2r4',1],
                    ['empty_c3r1]',1, 'empty_c2r2',1,'empty_c3r3',1,'empty_c3r4',1],
                    ['empty_c4r1]',1, 'empty_c2r2',1,'empty_c4r3',1,'empty_c4r4',1],
                    ['empty_c5r1]',1, 'empty_c2r2',1,'empty_c5r3',1,'empty_c5r4',1],
                    ['empty_c6r1]',1, 'empty_c2r2',1,'empty_c6r3',1,'empty_c6r4',1]]

# change this to reflect which controller above in the list this instance is supporting
controllerNumber=1

#
# longest time period of the 4 animatronics. this is used during boot up to make sure
# all animatronics would and are in steady state before transitioning into sensor mode
#
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

#
# initialize pins for dip switch - currently not used
#
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
        if sensorPin.value() == 1:
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
        #
        # at the end of animatronic #1 turn light to red
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
if debug: print("Code Rev: ",codeRev," Code Date: ",codeDate)
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

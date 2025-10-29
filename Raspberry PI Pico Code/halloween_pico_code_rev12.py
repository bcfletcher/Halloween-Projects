#
# Halloween Animatronic Automation System
# This code is using both cores of a Pico or Pico W. Core 0 is running a sensor thread for the KY-008 laser
# detector via a DaFuRui 5V Relay board. The relay connects to pin14 on the Pico. When someone breaks the
# beam between the ky-008 laser and detector it trips the relay which activates the p14 on Pico.
# Then the core 1 kicks off and turns on each of the four relays on the SB Components Pico Relay Board (a really cool board!!!) 
# in series with a sleep between each relay to let the animatronic play.
#
# This code also controls an LED stoplight board do show status of the controller during boot (yellow),
# green when waiting for someone to trip the laser and then red once the animatronics start running. 
#
# it supports 7 controllers by configuring the animatronics in the ControllerIDs, ControllerRelayCorrections,
# and animatronicsCfg Lists. the code gets the controller id from the pico and uses that to determine the
# controller 
#
#
codeRev="12"
codeDate="28 Oct 2025"

from machine import Pin, lightsleep, PWM
import _thread
import time, utime

#enable debugging
debug=False
debug2=False

# configure controller/animatronics pairing
# 
#  this is design for our maze which has 7 raspberry pico controllers. 
#
# c#r# is controller #, relay #
#
# this is the list of controllers and the relay correction value 
ControllerIDs=["E661A4D4176D6D29",
               "E6616408438D882B",
               "E6611C08CB419822",
               "E661410403206530",
               "E661385283543132",
               "E6614104034B2730",
               "E66358986366412B"]

# this is controller relay sesnor correction value. some relays get high/low value wrong or the jumper doesn't work
# value is 0 or 1
ControllerRelayCorrections=[1,1,0,1,0,1,1]
# Default controller values
controllerNumber=1 
controllerRelayCorrection=0

animatronicsCfg = [['A/Scary Boy',6, 'B/Scary Girl',5,'C/Clown',5,'D/Ghost',5,"sleep time",5],
                    ['E/Crawing Zombie',4, 'DD/Ratman',7,'EE/Leatherface',8,'empty_c2s3',1,"sleep time",1],
                    ['FF/Jump Scare Pumpkin',15,'Skeleton Barrel',5, 'empty_c3s3',0,'empty_c3s4',0,"sleep time",10],
                    ['Pumpkin Guy',4, 'Witch',4,'I/Barry',6,'Werewolf 1 & 2',4,"sleep time",3],
                    ['Ghoul',5, 'Bottomless Zombie',5,'Dog House',5,'Headless Skull Guy',5,"sleep time",5],
                    ['empty_c6s1',6, 'empty_c6s2',6,'empty_c6s3',6,'empty_c6s4',6,"sleep time",5],
                    ['empty_c7s1',5, 'empty_c7s2',5,'empty_c7s3',5,'empty_c7s4',5,"sleep time",5]]

#
# longest time period of the 4 animatronics. this is used during boot up to make sure
# all animatronics would and are in steady state before transitioning into sensor mode
#      
animatronicsInitialDelay=15

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

# mode pin - if connected then controller will run if sensor not found
#
# if jumper from pin10 to pin11 in place animatronics will run only if laser signal is received
# if jumper from pin10 to pin11 removed anitmatronics will run if laser signal not received (default/fail safe mode)
#modePinIn=Pin(11,Pin.IN, Pin.PULL_DOWN)
#modePinIn.value(0)
#modePinOut=Pin(10,Pin.OUT, Pin.PULL_UP)
#modePinOut.value(1)

#
# initialize pins for dip switch - currently not used
#
#dipSwitchPin1 = Pin(10, Pin.IN,Pin.PULL_UP)
#dipSwitchPin2 = Pin(11, Pin.IN,Pin.PULL_UP)
#dipSwitchPin3 = Pin(12, Pin.IN,Pin.PULL_UP)
#dipSwitchPin4 = Pin(13, Pin.IN,Pin.PULL_UP)

# thread syncronization global variable
runAnimatronic=False

# more globals
controllerNumber=1 #default
controllerRelayCorrection=0 #default

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

#
# get's the PICO ID so the code can switch automatically based on the controller.
#
# from https://forums.raspberrypi.com/viewtopic.php?t=349189
#
def getPicoID():
    id = ""
    for b in machine.unique_id():
      id += "{:02X}".format(b)
    return(id)

def sensorThread():
    global controllerNumber
    global controllerRelayCorrection
    global ControllerIDs
    global ControllerRelayCorrections
    global animatronicsCfg
    global runAnimatronic
    global sensorPin
    global animatronicsInitialDelay

    c=0
    set_brightness(green, 100)
    set_brightness(red, 0)

    while True:
        if debug2: print("count=",c," sensor/pin_14=",sensorPin.value())
        lightsleep(50)
        c = c + 1
        if sensorPin.value() == controllerRelayCorrection:
            if debug: print("Waiting for animatronics to run, sensor value=",sensorPin.value())
            runAnimatronic=True
            while runAnimatronic == True:
                pass
            set_brightness(green, 100)
            if debug: print("Waiting for sensor detection, sensor value=",sensorPin.value())
        else:
            pass
        
def animatronicThread():
    global controllerNumber
    global controllerRelayCorrection
    global ControllerIDs
    global ControllerRelayCorrections
    global animatronicsCfg
    global runAnimatronic
    global sensorPin
    global animatronicsInitialDelay

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

        # extra time to make sure all animatronics are done so they can restart correctly
        if debug: print("Sleep Time - ",animatronicsCfg[controllerNumber-1][8],"/",animatronicsCfg[controllerNumber-1][9])
        utime.sleep(animatronicsCfg[controllerNumber-1][9])

        allOff()    
        set_brightness(red, 0)
        if debug: print("Animatronics Run Done")
        runAnimatronic=False





#
# main code
# 
def main():
    global controllerNumber
    global controllerRelayCorrection
    global ControllerIDs
    global ControllerRelayCorrections
    global animatronicsCfg
    global runAnimatronic
    global sensorPin
    global animatronicsInitialDelay
    
    
    
    if debug: print("Initializing System, please wait...")
    if debug: print("Code Rev: ",codeRev," Code Date: ",codeDate)
    if debug: print("Pico's Unique ID=",getPicoID())
    if debug: print("Number of known controllers=",len(ControllerIDs))

    # change this to reflect which controller above in the list that this instance is supporting
    try: 
        controllerNumber=ControllerIDs.index(getPicoID())+1
    except:
        print("Unknown Controller, defaulting to 1")
        controllerNumber=1

    try:
        controllerRelayCorrection=ControllerRelayCorrections[controllerNumber-1]
    except:
        print("Unknown Controller, defaulting to relay value of 0")
        controllerRelayCorrection=0
        
    if debug: print("Controller Number=",controllerNumber, " Relay Correction=",controllerRelayCorrection)
    if debug: print("Animatronics Configured=",animatronicsCfg[controllerNumber-1])
    if debug: print("Sensor Pin Current Value=",sensorPin.value())

    set_brightness(green, 100)
    set_brightness(yellow, 100)
    set_brightness(red, 100)
    utime.sleep(2)
    set_brightness(green, 0)
    set_brightness(red, 0)
    if debug: print("All Animatronics will activate to verify connection and function")
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
                                                                                 
#
# run main()
#
main()

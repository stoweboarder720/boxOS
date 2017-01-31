##########################################################################
############################### Initialize ###############################
##########################################################################

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
from time import sleep
import os
from shutdown import shutdown
from attemptAccess import attemptAccess
from LogSuccessAttempt import logAccessAttempt
from LogSuccessAttempt import logAccessCompletion
from neopixel import *
from ledanimations import *
import threading
from threading import Thread
MIFAREReader = MFRC522.MFRC522()			# Create an object of class MFRC522

continue_reading = True

# LED strip configuration:
LED_COUNT      = 5                                      # Number of LED pixels.
LED_PIN        = 18                                     # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000                                 # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5                                      # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255                                    # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False                                  # True to invert the signal (when using NPN transistor level shift)
red            = Color(  0, 255,   0)
green          = Color(255,   0,   0)
yellow         = Color(255, 255,   0)
blue           = Color(  0,   0, 255)
orange         = Color( 30, 255,   0)
pink           = Color(  0, 255, 127)
nocolor        = Color(  0,   0,   0)

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Intialize the library (must be called once before other functions).
strip.begin()


## GPIO pin assignments and initializations
os.system('gpio mode 0 out')                            # Interlock
os.system('gpio mode 25 out')				# Solid State Relay
os.system('gpio mode 23 out')                           # Buzzer
os.system('gpio mode 24 down')                          # Button
os.system('gpio write 25 0')                            # Turn off power to SSR
os.system('gpio write 0 1')                             # Open interlock

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

##########################################################################
########################### Embedded Functions ###########################
##########################################################################

def alertAuth():
    '''Flashes blue LED when a user is not authorized
        and returns to waiting for an ID
    '''
    colorFlash(strip, red)
    return
	
def poweron(readid, makerid, cnx, interlock):
    '''Activates the relay when a maker has been authorized
       and continues to ensure the MakerID has not been
       removed from the scanner. If it has, this function
       calls the shutdown protocol.
    '''
    while True:
        if interlock == 1:
            os.system('gpio write 25 1')	                # Energize the relay
        else:
            os.system('gpio write 0 0')                         # Close the interlock
        CardPresent = 1				                # Card is present at scanner			
        miss = 0					        # Set consecutive missed reads to 0

        while CardPresent:         
            stillthere = 0				        # Assume card is not present
            while ~stillthere:
			
                # Scan for cards    
                (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)                
                # Get the UID of the card
                (status,uid) = MIFAREReader.MFRC522_Anticoll() 
				
                # If we have the UID, generate unsigned integer
                if status == MIFAREReader.MI_OK:	        # If we read a UID
                    finalUID = 0
                    for i in range(4):
                        finalUID = finalUID + (uid[i] << (8 * (3 - i)))
                    currentid = finalUID

                else:					        # If we did not read a UID
                    miss += 1				        # Increment consecutive misses
                    currentid = 0				# Clear previously read ID
                                    
                if currentid == makerid:			# If the ID read == authorized ID
                    stillthere = 1			        # The ID is still at the scanner
                    colorSet(strip, green)
                    miss = 0
                
                elif currentid == readid:
                    stillthere = 1
                    colorSet(strip, orange)
                    miss = 0
                
                elif miss > 5:				        # If we miss 5 or more consecutive reads
                    return power_down(makerid, cnx, interlock)	# Assume ID removed; begin shutdown

def setBuzzer(onOff):
    if onOff:
        # Set on
        os.system("gpio write 23 1")
    else:
        # Set off
        os.system("gpio write 23 0")

import subprocess 
                                
def power_down(makerid, cnx, interlock):
    '''
    Begin powering down resource once a MakerId has
    been removed. If the MakerID is returned, abort
    the power down procedure and return power to the 
	resource.
    '''
    miss = 0						# Clear consecutive misses
    readid = 0						# Clear read ID number
    while miss < 15:					# While we have fewer than 5 consecutive misses
	p = subprocess.Popen(['gpio read 24'], stdout=subprocess.PIPE,shell=True)
	(buttonPress, errors) = p.communicate()
	print("button press", buttonPress)
        if (buttonPress == "1\n"):
	    print('read button press')
	    miss = 15

        colorSet(strip, yellow)                         # Set LEDs to yellow
        setBuzzer(True)
        sleep(0.25)                                     # Wait
        colorSet(strip, nocolor)                        # turn off LEDs
        setBuzzer(False)

	p = subprocess.Popen(['gpio read 24'], stdout=subprocess.PIPE,shell=True)
	(buttonPress, errors) = p.communicate()
	print("button press", buttonPress)
        if (buttonPress == "1\n"):
	    print('read button press')
	    miss = 15

        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()
               
        # If we have the UID, generate unsigned integer
        if status == MIFAREReader.MI_OK:		# If we read a UID
            finalUID = 0
	    for i in range(4):
	    	finalUID = finalUID + (uid[i] << (8 * (3 - i)))
            readid = finalUID

        else:						# If we did not read a UID
            readid = 0 
                 
        if readid == makerid or isAdminCard(cnx, readid):	# If the ID was returned to the reader
            return poweron(readid, makerid, cnx, interlock)	# Abort shutdown and return power

        elif readid == 0:
            miss += 1
        
        elif readid != makerid:
            miss += 1
            colorSet(strip, nocolor)
            colorSet(strip, pink)
            sleep(0.25)
            colorSet(strip, nocolor)
	    
    if interlock == 1:                
        os.system('gpio write 25 0')		        # Once we have more than 5 misses, remove power
    else:
        os.system('gpio write 0 1')
    return				                # Return to waiting for an ID
    
def isAdminCard(cnx, uid):
	query = ('SELECT cardId FROM ms_adminCards WHERE cardId=' + str(uid))
	adminExists = False
	cursor = cnx.cursor()
	cursor.execute(query)
	for (cardId) in cursor:
		adminExists = True
	return adminExists
###########################################################################
########################### Check for RFID chip ###########################
###########################################################################

def wait_for_maker(cnx, resourceType, needsTraining, rid, interlock):
    miss = 0                                            # Clear miss counter
    count = 0                                           # Clear read count
    readid = 0                                          # Clear read ID value
    lastid = 0                                          # Clear stored ID value
    makerid = 0                                         # Clear stored ID value
    standby = 0
    global sleepMode
    sleepMode = False
    colorWipe(strip, blue, 5)
    colorWipe(strip, orange, 10)
    colorWipe(strip, red, 15)
    while continue_reading:
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)            
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        if miss < 50:
            colorSet(strip, red)                        # Set LEDs to red
        elif miss == 50:
            sleepMode = True
            sleepThread = Thread(target = sleepDisplay, args=(strip, 20, 1))
            sleepThread.daemon = True
            sleepThread.start()
        
        # If we have the UID, generate unsigned integer
        if status == MIFAREReader.MI_OK:		# If we read an ID
            sleepMode = False
            miss = 0					# Clear consecutive misses
	    finalUID = 0
	    for i in range(4):
	    	finalUID = finalUID + (uid[i] << (8 * (3 - i)))
            readid = finalUID
        
        # Check if we have read ID before
            if lastid == 0:				# If we have no stored ID
                miss = 0				# Clear consecutive misses
                lastid = readid				# Store read ID value 
                count = 1				# Increment the read count
            elif lastid == readid:		        # If we have read the ID previously
                count += 1				# Increment the read count
                miss = 0				# Clear misses
            else:				        # If we read an ID that is not the stored ID
                lastid = 0				# Clear stored ID
                count = 0      				# Clear the read count
        else:						# If we did not read an ID
            miss += 1					# Increment the miss counter
            
	
        if count >= 3:					# If we read the same ID 3 times consecutively
            makerid = lastid				# Make this ID the MakerID
            colorSet(strip, blue)                       # Set LEDs to blue
            print(makerid)		
        # Check if maker is authorized
            isAuthorized = attemptAccess(cnx, makerid, resourceType, needsTraining, rid)
            if isAuthorized==1:			# If MakerID is authorized by Dan's block
                logAccessAttempt(cnx, makerid, rid, True)
                poweron(readid, makerid, cnx, interlock)		# Deliver power to the resource
                logAccessCompletion(cnx, makerid, rid)
                makerid = 0
                readid = 0
                lastid = 0
                miss = 0
                count = 0
                colorSet(strip, red)
            elif isAuthorized == 2:
                makerid = 0
                readid = 0
                lastid = 0
                miss = 0
                count = 0
                shutdown()
            else:					# If not authorized
                logAccessAttempt(cnx, makerid, rid, False)
                alertAuth()			        # Alert maker/admin
                makerid = 0
                readid = 0
                lastid = 0
                miss = 0
                count = 0
                colorSet(strip, red)
            
        elif miss > 2:				        # If we miss more than 2 consecutive reads
            lastid = 0					# Clear previously read ID
            makerid = 0					# Clear MakerID
            
def sleepDisplay(strip, wait_ms=10, iterations=1):
        while sleepMode:
            for j in range(256*iterations):
                if sleepMode:
                    for i in range(strip.numPixels()):
                            strip.setPixelColor(i, wheel(((i * 256 / strip.numPixels()) + j) & 255))
                    strip.show()
                    time.sleep(wait_ms/1000.0)
                


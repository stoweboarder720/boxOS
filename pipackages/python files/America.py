from mysql.connector import (connection)
from sshtunnel import SSHTunnelForwarder
from findRID import findRID
from getResourceProfile import getResourceProfile
from main import *
import RPi.GPIO as GPIO
import MFRC522
import signal
import time
from time import sleep
import os

GPIO.cleanup()
GPIO.setwarnings(False)

cnx = connection.MySQLConnection(user='MakerSpace', password='hieR7oo8eib0',\
        host='db.eg.bucknell.edu', database='MakerSpace',port=3306)
    
macAddress = open('/sys/class/net/eth0/address').read()
macAddress=str(macAddress)                              ##Data type to string
macAddress=macAddress[:-1]                              ##Deletes space at end
macAddress = macAddress.replace(":","")
macAddress="0x"+macAddress
print macAddress

rid = findRID(cnx, macAddress)[0]                       ##Retrieve RID from MySQL
cnx.commit()

continue_reading = True

Lis = getResourceProfile(cnx, rid)
while Lis == None:
    cnx.commit()
    Lis = getResourceProfile(cnx, rid)
    sleep(1)

resourceType = Lis[0]
needsTraining= Lis[1]
switchMode = Lis[2]

if switchMode == 0:
    interlock = 1
    print "SSR Mode"
else:
    interlock = 0
    print "Interlock Mode"


signal.signal(signal.SIGINT, end_read)			# Hook the SIGINT
MIFAREReader = MFRC522.MFRC522()			# Create an object of class MFRC522

wait_for_maker(cnx, resourceType, needsTraining, rid, interlock)

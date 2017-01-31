from pprint import pprint
from addMacAddress import addMacAddress
import time

def findRID(cnx, macAddress):
    #Query MySQL for RID by sending MAC Address
    query = ('SELECT rid FROM ms_macAddresses WHERE macAddress = "' + macAddress + '"')
    cursor = cnx.cursor()
    cursor.execute(query)
    numResults = 0
    numRIDs = 0
    for (rid) in cursor:
        numResults = numResults + 1
        if rid != (None, ):
            numRIDs = numRIDs + 1

    if numResults == 0:
            print("TEST FIND RID: This resource has not yet been discovered")
            addMacAddress(cnx, macAddress)  
            numResults = 1                          #MAC added but unintiated
    while (numResults == 1 and numRIDs == 0):                  
        query = ('SELECT rid FROM ms_macAddresses WHERE macAddress = "' + macAddress + '"')
        cursor = cnx.cursor()
	cnx.commit()
        cursor.execute(query)
        numResults = 0
        numRIDs = 0
        for (rid) in cursor:
            numResults = numResults + 1
            if rid != (None, ):
                numRIDs = numRIDs + 1 
        print("TEST FIND RID: There is one resource with this MAC address but it is uninitiated")
        time.sleep(10)
    print("TEST FIND RID: There is one resource with this MAC address and it has an RID")
    a = rid
    cursor.close()
    return rid

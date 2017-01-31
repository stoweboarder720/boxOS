from pprint import pprint

def addMacAddress(cnx, macAddress):
    print("Adding MAC address " + macAddress + " to database without an RID")
    cursor = cnx.cursor()
    query = ('INSERT INTO ms_macAddresses (macAddress, timeDiscovered, rid) VALUES ("' + macAddress + '", CURRENT_TIMESTAMP, NULL)')
    print (query)
    cursor.execute(query)
    cnx.commit()

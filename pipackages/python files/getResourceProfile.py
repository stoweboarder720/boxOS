
def getResourceProfile(cnx, rid):
    query = ('SELECT type, needsTraining, switchMode FROM ms_resources WHERE rid=' + str(rid))
    cursor = cnx.cursor()
    cursor.execute(query)
    
    print("TEST FIND RESOURCE PROFILE: RID " + str(rid))
    for (type, needsTraining, switchMode) in cursor:
        print("    RID: " + str(rid) + " has the following attributes \n"   + \
                "    type: "+ type + "\n"                                       + \
                "    needsTraining: " + str(bool(needsTraining)) + "\n" + \
                "    switchMode: " + str(switchMode))
        return (type, needsTraining, switchMode)
    return None
##    if str(bool(needsTraining)) != 'True':
##      mockTurnOnGreen()
##        #DetectUID()                ##Function that is in while loop till detection
##    else:
##        ID=DetectUID2()                ## Will return UID
##        Authorizaton = attemptAccess(cnx, ID, type)
##        print (Authorizaton)
##        if Authorizaton == True:
##            print 'approved UID for this Resource'
##            mockTurnOnGreen()
##        elif Authorizaton == False:
##            print 'Not approved UID for this Resource'
##            mockTurnOnRed()
##        else:
##            print 'Something went wrong, check RFID'

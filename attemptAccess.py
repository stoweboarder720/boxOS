def attemptAccess(cnx, attemptedUid, resourceType, needsTraining, rid):

    query = ('SELECT uid FROM ms_authorized WHERE resourceType="' + resourceType + '"')
    cursor = cnx.cursor()
    cursor.execute(query)
##    print("TEST ACCESS ATTEMPT") 
    isAuthorized = 0
    for (uid) in cursor:
        uid=uid[0]
        if uid == attemptedUid:
            isAuthorized = 1

#include case for checking if UID is in database
    if not needsTraining:
        query1 = ('SELECT uid FROM ms_users WHERE uid = "' + str(attemptedUid) + '"')
        cursor1 = cnx.cursor()
        cursor1.execute(query1)
        for (uid) in cursor1:
            uid = uid[0]
            if uid == attemptedUid:
                isAuthorized = 1
#check if shutdown card
    if isAuthorized == 0:
        query2 = ('SELECT cardId FROM ms_shutdownCards WHERE cardId = "' + str(attemptedUid) + '"')
        cursor2 = cnx.cursor()
        cursor2.execute(query2)
        for (cardId) in cursor:
            cardId = cardId[0]
            if cardId == attemptedUid:
                isAuthorized = 2
                cnx.commit()
                return isAuthorized
    else:    
        cnx.commit()
        return isAuthorized

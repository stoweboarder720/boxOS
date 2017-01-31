
def attemptAccess(cnx, attemptedUid, resourceType, needsTraining, rid):

    query = ('SELECT uid FROM ms_authorized WHERE resourceType="' + resourceType + '"')
    cursor = cnx.cursor()
    cursor.execute(query)
##    print("TEST ACCESS ATTEMPT") 
    isAuthorized = False
    for (uid) in cursor:
        uid=uid[0]
        if uid == attemptedUid:
            isAuthorized = True

#include case for checking if UID is in database
    if not needsTraining:
        query1 = ('SELECT uid FROM ms_users WHERE uid = "' + str(attemptedUid) + '"')
        cursor1 = cnx.cursor()
        cursor1.execute(query1)
        for (uid) in cursor1:
            uid = uid[0]
            if uid == attemptedUid:
                isAuthorized = True
    cnx.commit()
    return isAuthorized

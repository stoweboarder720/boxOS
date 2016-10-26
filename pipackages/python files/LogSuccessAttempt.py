def logAccessAttempt(cnx, uid, rid, wasSuccessful):
    print("    Add a log entry for attempted access")
    query = ('INSERT INTO ms_log (uid, rid, accessTime, wasSuccessful)' + \
             'VALUES (' + str(uid) + ', ' + str(rid) + ', ' + 'CURRENT_TIMESTAMP, ' + \
             str(wasSuccessful) + ')')
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit()

def logAccessCompletion(cnx, uid, rid):
    query = ('SELECT accessTime FROM ms_log WHERE uid=' + str(uid) + \
             ' AND rid=' + str(rid) + ' ORDER BY accessTime')
    print(query)
    cursor = cnx.cursor()
    cursor.execute(query)
    for (accessTime) in cursor:
        mostRecentAccess = accessTime

    query = ('UPDATE ms_log SET finishTime=CURRENT_TIMESTAMP WHERE uid=' + \
             str(uid) + ' AND rid=' + str(rid) + ' AND accessTime="' + 
             str(mostRecentAccess[0]) + '"')
    print(query)
    cursor.execute(query)
    cnx.commit()

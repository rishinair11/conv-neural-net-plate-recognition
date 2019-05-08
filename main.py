import Start
import PIL
import mysql.connector
from mysql.connector import Error
try:
    connection = mysql.connector.connect(host='localhost',
                                         database='trafficvc',
                                         user='root',
                                         password='')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL database... MySQL Server version on ", db_Info)

        # Get the row with case id = 0  TABLE : cases
        cursor = connection.cursor()
        query = ("SELECT caseid, reporterid, proof, licenseplatepic FROM cases "
                 "WHERE aadharid=0")
        cursor.execute(query)

        image_list = []
        for (caseid, reporterid, proof, licenseplatepic) in cursor:
            print("Case id : ", caseid)
            print("Reporter id : ", reporterid)
            image_list.append([caseid, licenseplatepic])

        # Get neural network prediction
        for image in image_list:
            # preprocess image
            with open('{}.jpg'.format(image[0]), 'wb') as file:
                file.write(image[1])
            platenumber = Start.recognize('{}.jpg'.format(image[0]))

        platenumber = 'CHIGGA 47'
        platetuple = (platenumber,)

        # Get the row with vehicle number to get offender's id TABLE : vehicleregistration
        cursor2 = connection.cursor()
        query2 = ("SELECT id FROM vehicleregistration "
                  "WHERE licenseplateno = %s")

        cursor2.execute(query2, (platetuple))
        for (id) in cursor2:
            print("Case id : ", id)
            criminalid = id[0]

        # print(case_id)
        # print(criminalid)

        # Update the offender's id TABLE : cases
        cursor3 = connection.cursor()
        query3 = """ UPDATE cases
                   SET aadharid = %s
                   WHERE caseid = %s """
        cursor3.execute(query3, (criminalid, case_id))


except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    # closing database connection.
    if(connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

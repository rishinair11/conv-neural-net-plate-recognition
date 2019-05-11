import Start
import os
import PIL
import time
import mysql.connector
from mysql.connector import Error
try:
    connection = mysql.connector.connect(host='localhost',
                                         database='trafficvc',
                                         user='root',
                                         password='password')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        while True:
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

            if image_list != []:
                platenumber = None
                for image in image_list:
                    # preprocess image
                    path = '{}.jpg'.format(image[0])
                    with open(path, 'wb') as file:
                        file.write(image[1])

                    # neural network returns licenceplate number
                    platenumber = Start.recognize(path)
                    print(platenumber)

                    # polling frequency for NN
                    time(1)

                    # delete image to save storage
                    os.remove(path)
                    if platenumber == None:
                        continue

                    platetuple = (platenumber,)

                    # Get the row with vehicle number to get offender's id TABLE : vehicleregistration
                    cursor2 = connection.cursor()
                    query2 = ("SELECT id FROM vehicleregistration "
                              "WHERE licenseplateno = %s")
                    cursor2.execute(query2, (platetuple))

                    criminalCount = 0
                    for (id) in cursor2:
                        criminalCount += 1
                        criminalid = id[0]
                        print("Criminal id : ", criminalid)

                    if criminalCount >= 1:
                        # Update the offender's id TABLE : cases
                        cursor3 = connection.cursor()
                        query3 = """ UPDATE cases
                                SET aadharid = %s
                                WHERE caseid = %s """
                        cursor3.execute(query3, (criminalid, image[0]))
            time.sleep(5)

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    # closing database connection.
    if(connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

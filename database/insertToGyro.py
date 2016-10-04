from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from datetime import datetime
 
def insert_GyroPoints(timestamp, roll, pitch, yaw, sessNum, deviceNum):
    query = "INSERT INTO GyroPoints" \
            "(timestamp, roll, pitch, yaw, sessNum, deviceNum) " \
            "VALUES(%s,%s, %s, %s, %s, %s)"
    args = (timestamp, roll, pitch, yaw, sessNum, deviceNum)
 
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
 
        cursor = conn.cursor()
        cursor.execute(query, args)
        # This is causing problem, I dont know why
        # if cursor.lastrowid:
        #     print('last insert id', cursor.lastrowid)
        # else:
        #     print('last insert id not found')
 
        conn.commit()
    except Error as error:
        print(error)
 
    finally:
        cursor.close()
        conn.close()

def insert_AccessPoints(timestamp, x, y, z, sessNum, deviceNum):
    query = "INSERT INTO AccessPoints" \
            "(timestamp, x, y, z, sessNum, deviceNum) " \
            "VALUES(%s,%s, %s, %s, %s, %s)"
    args = (timestamp, x, y, z, sessNum, deviceNum)
 
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
 
        cursor = conn.cursor()
        cursor.execute(query, args)
        # This is causing problem, I dont know why
        # if cursor.lastrowid:
        #     print('last insert id', cursor.lastrowid)
        # else:
        #     print('last insert id not found')
 
        conn.commit()
    except Error as error:
        print(error)
 
    finally:
        cursor.close()
        conn.close()


def main():
    # now = datetime.now().date()
    # now = datetime(2009, 5, 5)
    # str_now = now.date().isoformat()
    # insert_GyroPoints(now, 1.0, 1.0, 1.0, 'hear2', 2)
    
 
if __name__ == '__main__':
    main()

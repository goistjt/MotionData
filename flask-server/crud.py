from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from datetime import datetime
import hashlib
 
def create_session(description, starting_time):
#     m = hashlib.sha1()
#     records_id = desription + starting_time;
#     records_id = records_id.encode('utf-8')
#     m.update(records_id)
#     records_id = m.hexdigest()
    query = "INSERT INTO Session" \
            "(description, timestamp) " \
            "VALUES(%s, %s)"
    args = (description, timestamp)
    return insert(query, args, True) 

def insert_GyroPoints(records_id, timestamp, roll, pitch, yaw):
    query = "INSERT INTO GyroPoints" \
            "(records_id, timestamp, roll, pitch, yaw) " \
            "VALUES(%s,%s, %s, %s, %s)"
    args = (records_id, timestamp, roll, pitch, yaw)
    insert(query, args)

def insert_AccessPoints(records_id, timestamp, x, y, z):
    query = "INSERT INTO AccessPoints" \
            "(records_id, timestamp, surge, sway, heave) " \
            "VALUES(%s,%s, %s, %s, %s)"
    args = (records_id, timestamp, x, y, z)
    insert(query, args)

def readSession(name):
    #name has to be surrouded by ''
    #EX: 'Test'
    query = "SELECT * FROM Session WHERE name = %s"
    args = [name]
    return readOne(query, args)

def getSessionName(description, starting_time):
    query = "SELECT * FROM Session WHERE description = %s AND starting_time = %s"
    args = [description, starting_time]
    return readOne(query, args)

def readDataPoints(table, records_id, timestamp) :
    query = "SELECT * FROM table WHERE records_id = %s AND timestamp = %s"
    args = [records_id, timestamp]
    return readOne(query, args)

def readOne(query, args=[]):
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, args)
 
        data = cursor.fetchone()
        
    except Error as error:
        print(error)
 
    finally:
        cursor.close()
        conn.close()
        return data

def readAll(query, args=[]):
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, args)
 
        data = cursor.fetchall()
        
    except Error as error:
        print(error)
 
    finally:
        cursor.close()
        conn.close()
        return data


def delete_data(query, args=[]):
    execute_transaction_query(query, args=[])

def insert(query, args=[]):
    execute_transaction_query(query, args=[])

def insert(query, args=[], uniqueId = False):
     db_config = read_db_config()
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, args)
        lastId = cursor.lastrowid
        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')
        conn.commit()
    except Error as error:
        print(error)
 
    finally:
        cursor.close()
        conn.close()
        return lastId


def execute_transaction_query(query, args=[]):
    db_config = read_db_config()
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, args) 
        conn.commit()
    except Error as error:
        print(error)
 
    finally:
        cursor.close()
        conn.close()

# def main():
# if __name__ == '__main__':
#     main()

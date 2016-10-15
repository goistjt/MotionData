
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from datetime import datetime
import hashlib
 
def create_session(description, starting_time):
    query = "INSERT INTO Session" \
            "( description, starting_time) " \
            "VALUES( %s, %s)"
    args = ( description, starting_time)
    return insert(query, args)

def create_record(session_id, device_id):
    records_id = sha1(str(session_id)+device_id)
    query = "INSERT INTO Records" \
            "(records_id, session_name, decice_id)" \
            "VALUES(%s, %s, %s)"
    args = [records_id, session_id, device_id]
    return insert(query, args)
            
def sha1(input):
    m = hashlib.sha1()
    m.update(input.encode('utf-8'))
    return m.hexdigest()

def insert_GyroPoints(records_id, timestamp, roll, pitch, yaw):
    query = "INSERT INTO GyroPoints" \
            "(records_id, timestamp, roll, pitch, yaw) " \
            "VALUES(%s,%s, %s, %s, %s)"
    args = (records_id, timestamp, roll, pitch, yaw)
    return insert(query, args)

def insert_AccessPoints(records_id, timestamp, x, y, z):
    query = "INSERT INTO AccessPoints" \
            "(records_id, timestamp, surge, sway, heave) " \
            "VALUES(%s,%s, %s, %s, %s)"
    args = (records_id, timestamp, x, y, z)
    return insert(query, args)

def readSession(id):
    #id has to be surrouded by ''
    #EX: 'Test'
    query = "SELECT * FROM Session WHERE id = %s"
    args = [id]
    return readOne(query, args)

def getSessionId(description, starting_time):
    query = "SELECT * FROM Session WHERE description = %s AND starting_time = %s"
    args = [description, starting_time]
    return readOne(query, args)

def readDataPoints(table, records_id, timestamp) :
    query = "SELECT * FROM "+table+" WHERE records_id = %s AND timestamp = %s"
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
    execute_transaction_query(query, args)

def insert(query, args=[]):
    db_config = read_db_config()
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, args)
        lastId = cursor.lastrowid
        if lastId:
            print('last insert id', lastId)
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
        
def reset_session_autoIndex():
    selec_col = "SELECT MAX( `id` ) FROM `Session` ";
    numOfRow = readOne(selec_col)
    #if there is no rows in the table, reset the auto index to 0
    if numOfRow[0] is None:
        numOfRow = [1]
    else:
        numOfRow[0] = numOfRow[0]+1
    query = "ALTER TABLE Session AUTO_INCREMENT = %s"
    execute_transaction_query(query, numOfRow)

def getConnection():
    db_config = read_db_config()
    return MySQLConnection(**db_config)


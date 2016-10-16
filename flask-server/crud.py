
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import hashlib
 
def create_session(description, starting_time):
    query = "INSERT INTO Session" \
            "( description, starting_time) " \
            "VALUES( %s, %s)"
    args = ( description, starting_time)
    return insert(query, args)

def create_record(session_id, device_id):
    record_id = sha1(str(session_id)+device_id)
    query = "INSERT INTO Records" \
            "(id, session_id, device_id)" \
            "VALUES(%s, %s, %s)"
    args = [record_id, session_id, device_id]
    insert(query, args)
    return record_id
            
def sha1(input):
    m = hashlib.sha1()
    m.update(input.encode('utf-8'))
    return m.hexdigest()

def insert_GyroPoints(record_id, timestamp, roll, pitch, yaw):
    query = "INSERT INTO GyroPoints" \
            "(record_id, timestamp, roll, pitch, yaw) " \
            "VALUES(%s,%s, %s, %s, %s)"
    args = (record_id, timestamp, roll, pitch, yaw)
    return insert(query, args)

def insert_AccessPoints(record_id, timestamp, x, y, z):
    query = "INSERT INTO AccessPoints" \
            "(record_id, timestamp, surge, sway, heave) " \
            "VALUES(%s,%s, %s, %s, %s)"
    args = (record_id, timestamp, x, y, z)
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

def readDataPoints(table, record_id, timestamp) :
    query = "SELECT * FROM "+table+" WHERE record_id = %s AND timestamp = %s"
    args = [record_id, timestamp]
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
        numOfRow = [numOfRow[0]+1]
    query = "ALTER TABLE Session AUTO_INCREMENT = %s"
    execute_transaction_query(query, numOfRow)

def getConnection():
    db_config = read_db_config()
    return MySQLConnection(**db_config)

def delete_entire_session(session_id):
#     query = "DELETE FROM Session WHERE id = %s"
#     delete_data(query, [lastid])
#     reset_session_autoIndex()
#     query = ""
    #test
    pass
    



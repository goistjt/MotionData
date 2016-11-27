import hashlib
from pymysql import Error, connect

from database.python_mysql_dbconfig import read_db_config


def create_session(description, starting_time):
    query = "INSERT INTO Session" \
            "( description, starting_time) " \
            "VALUES( %s, %s)"
    args = (description, starting_time)
    return insert(query, args)


def create_record(session_id, device_id):
    record_id = sha1(str(session_id) + device_id)
    query = "INSERT INTO Records" \
            "(id, session_id, device_id)" \
            "VALUES(%s, %s, %s)"
    args = [record_id, session_id, device_id]
    insert(query, args)
    return record_id


def sha1(sha_input):
    m = hashlib.sha1()
    m.update(sha_input.encode('utf-8'))
    return m.hexdigest()


def insert_gyro_points(record_id, timestamp, roll, pitch, yaw):
    query = "INSERT INTO GyroPoints" \
            "(record_id, timestamp, roll, pitch, yaw) " \
            "VALUES(%s,%s, %s, %s, %s)"
    args = (record_id, timestamp, roll, pitch, yaw)
    return insert(query, args)


def insert_access_points(record_id, timestamp, x, y, z):
    query = "INSERT INTO AccessPoints" \
            "(record_id, timestamp, surge, sway, heave) " \
            "VALUES(%s,%s, %s, %s, %s)"
    args = (record_id, timestamp, x, y, z)
    return insert(query, args)


def read_session(sess_id):
    # id has to be surrouded by ''
    # EX: 'Test'
    query = "SELECT * FROM Session WHERE id = %s"
    args = [sess_id]
    return read_one(query, args)


def get_session_id(description, starting_time):
    query = "SELECT * FROM Session WHERE description = %s AND starting_time = %s"
    args = [description, starting_time]
    return read_one(query, args)


def read_data_points(table, record_id, timestamp):
    query = "SELECT * FROM " + table + " WHERE record_id = %s AND timestamp = %s"
    args = [record_id, timestamp]
    return read_one(query, args)


def read_one(query, args=[]):
    try:
        db_config = read_db_config()
        conn = connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, args)
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        return data
    except Error as error:
        print(error)


def read_all(query, args=[]):
    try:
        db_config = read_db_config()
        conn = connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, args)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Error as error:
        print(error)


def delete_data(query, args=[]):
    execute_transaction_query(query, args)


def insert(query, args=[]):
    db_config = read_db_config()
    try:
        conn = connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, args)
        last_id = cursor.lastrowid
        if last_id:
            print('last insert id', last_id)
        else:
            print('last insert id not found')
        conn.commit()
        cursor.close()
        conn.close()
        return last_id
    except Error as error:
        print(error)


def execute_transaction_query(query, args=[]):
    db_config = read_db_config()
    try:
        conn = connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as error:
        print(error)


def reset_session_auto_index():
    select_col = "SELECT MAX( `id` ) FROM `Session` ";
    num_of_row = read_one(select_col)
    # if there is no rows in the table, reset the auto index to 0
    if num_of_row[0] is None:
        num_of_row = [1]
    else:
        num_of_row = [num_of_row[0] + 1]
    query = "ALTER TABLE Session AUTO_INCREMENT = %s"
    execute_transaction_query(query, num_of_row)


def get_connection():
    db_config = read_db_config()
    return connect(**db_config)


def delete_entire_session(session_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        #select all records links to the sesson id
        all_records_query= "SELECT id FROM Records WHERE Records.session_id = %s"
        cursor.execute(all_records_query, [session_id])
        
        all_records = cursor.fetchall()
        for record in all_records:
            #delete all the access points and gyro points
            cursor.execute("DELETE FROM AccessPoints WHERE record_id = %s", [record])
            #remove the record
            cursor.execute("DELETE FROM GyroPoints WHERE record_id = %s", [record])
            
            cursor.execute("DELETE FROM Records WHERE id = %s", [record])
        #remove the session
        query = "DELETE FROM Session WHERE id = %s"
        cursor.execute(query, [session_id])    
        conn.commit()
        cursor.close()
        conn.close()
    except Error as error:
        print(error)
    #     query = "DELETE FROM Session WHERE id = %s"
    #     delete_data(query, [lastid])
    #     reset_session_autoIndex()
    #     query = ""
    # test
    finally:
        reset_session_auto_index()

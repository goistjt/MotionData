import hashlib
from pymysql import Error, connect

from database.python_mysql_dbconfig import read_db_config

'''
Created on Nov 4, 2016
@author: yangr
'''


class Crud(object):
    """
    This class handles the crud operation of the six-dof database
    """

    def __init__(self):
        """
        Constructor
        """
        self.conn = self.get_connection()

    # ********* connections ********#
    def start(self):
        self.conn = self.get_connection()

    def close(self):
        self.conn.close()

    def get_connection(self):
        db_config = read_db_config()
        return connect(**db_config)

    # ********* session ********#
    """
    returns session id
    EX: 1
    """
    def create_session(self, description, starting_time):
        args = (description, starting_time)
        return self.call_procedure('add_session', args, fetchall=False)[0]

    def read_session(self, sess_id):
        # id has to be surrouded by ''
        # EX: 'Test'
        query = "SELECT * FROM Session WHERE id = %s"
        args = [sess_id]
        return self.read_one(query, args)

    def get_all_sessions(self):
        query = "SELECT * FROM Session"
        return self.read_all(query)
    
    def get_sessions_not_related_to_device(self, device_id):
        args = [device_id]
        return self.call_procedure('get_sessions_not_related_to_device', args)

    def get_all_records_from_session(self, session_id):
        args = [session_id]
        return self.call_procedure('get_all_records_from_session', args)
    
    def get_record(self, record_id):
        args = [record_id]
        return self.call_procedure('select_record', args)
        
    def get_session_id(self, description, starting_time):
        args = [description, starting_time]
        return self.call_procedure("get_session_id", args, fetchall=False)

    def reset_session_auto_index(self):
        self.call_procedure('reset_session_auto_index')

    # ********* record ********#
    def create_record(self, session_id, device_id):
        record_id = self.sha1(str(session_id) + device_id)
        args = [record_id, session_id, device_id]
        self.call_procedure('create_record', args)
        return record_id

    def get_record_data(self, record_id):
        args = [record_id]
        access_points = self.call_procedure('select_gyro', args)
        gyro_points = self.call_procedure('select_accel', args)
        return access_points, gyro_points

    def sha1(self, sha_input):
        m = hashlib.sha1()
        m.update(sha_input.encode('utf-8'))
        return m.hexdigest()

    # ********* device ******** #
    def create_device_entry(self, device_id, device_name):
        args = (device_id, device_name)
        return self.call_procedure('create_device_entry', args)

    def update_device_entry(self, device_id, device_name):
        args = (device_id, device_name)
        return self.call_procedure('update_device_entry', args)

    def get_device_name(self, device_id):
        args = [device_id]
        name = self.call_procedure('get_device_name', args)
        if len(name) == 0:
            return name
        else:
            return name[0]

    # ********* gyro_points ********#
    '''
        This function is here for easier testing purpose
    '''
    def insert_gyro_points(self, record_id, timestamp, roll, pitch, yaw):
        query = "INSERT INTO GyroPoints" \
                "(record_id, timestamp, roll, pitch, yaw) " \
                "VALUES(%s,%s, %s, %s, %s)"
        args = (record_id, timestamp, roll, pitch, yaw)
        return self.insert(query, args)

    def bulk_insert_gyro_points(self, data_path, local=False):
        args = ["GyroPoints", '(record_id, timestamp, roll, pitch, yaw)']
        self.load_csv_data(local, data_path, args)

    def select_gyro(self, record_id):
        args = [record_id]
        return self.call_procedure('select_gyro', args)

    # ********* accel_points ********#
    '''
        This function is here for easier testing purpose
    '''
    def insert_accel_points(self, record_id, timestamp, x, y, z):
        query = "INSERT INTO AccelPoints " \
                "(record_id, timestamp, surge, sway, heave) " \
                "VALUES(%s,%s, %s, %s, %s)"
        args = (record_id, timestamp, x, y, z)
        return self.insert(query, args)

    def select_accel(self, record_id):
        args = [record_id]
        return self.call_procedure('select_accel', args)

    # Local means insert outside of server,
    def bulk_insert_accel_points(self, data_path, local=False):
        args = ["AccelPoints", '(record_id, timestamp, surge, sway, heave)']
        self.load_csv_data(local, data_path, args)

    # ********* integration ********#
    def delete_entire_session(self, session_id):
        args = [session_id]
        self.call_procedure('delete_session', args)
        self.reset_session_auto_index()

    # ********* read ********#
    def read_data_points(self, table, record_id, timestamp):
        query = "SELECT * FROM " + table + " WHERE record_id = %s AND timestamp = %s"
        args = [record_id, timestamp]
        return self.read_one(query, args)

    def read_one(self, query, args=[]):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, args)
            data = cursor.fetchone()
            cursor.close()
            return data
        except Error as error:
            print(error)

    def read_all(self, query, args=[]):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, args)
            data = cursor.fetchall()
            cursor.close()
            return data
        except Error as error:
            print(error)

    # ********* delete ********#
    def delete_data(self, query, args=[]):
        self.execute_transaction_query(query, args)

    # ********* insert ********#
    def insert(self, query, args=[], multi_row=False):
        try:
            cursor = self.conn.cursor()
            if multi_row:
                print(query)
                cursor.executemany(query, args)
            else:
                cursor.execute(query, args)
            last_id = cursor.lastrowid
            self.conn.commit()
            cursor.close()
            return last_id
        except Error as error:
            print(error)
    
    '''
        load csv data to mysql database
    '''
    def load_csv_data(self, local, path, args):
        if local:
            lo = 'LOCAL'
        else:
            lo = ''
        query = "LOAD DATA " + lo + " INFILE '" + path + "' INTO " \
                "TABLE " + args[0] + " FIELDS TERMINATED BY ',' LINES " \
                "TERMINATED BY '\r\n' IGNORE 1 LINES " + args[1] + ";"
        self.execute_transaction_query(query, [])

    # ********* generic query ********#
    def call_procedure(self, proc_name, args=[], fetchall=True):
        cursor = self.conn.cursor()
        cursor.callproc(proc_name, args)
        if fetchall:
            result = cursor.fetchall()
        else:
            result = cursor.fetchone()
        cursor.close()
        return result
    
    def execute_transaction_query(self, query, args=[]):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, args)
            self.conn.commit()
            cursor.close()
        except Error as error:
            print(error)

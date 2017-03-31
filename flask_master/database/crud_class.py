import hashlib
from pymysql import Error, connect
import platform

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
        What comes in: Nothing
        What goes out: Nothing
        Side effects:
        Description: Creates a connection with the database
        """
        self.conn = self.get_connection()

    # ********* connections ********#

    def close(self):
        """
        What comes in:
        What goes out:
        Side effects:
        Description:  Close the connection with the datbase
        """
        self.conn.close()

    def get_connection(self):
        """
        What comes in:  Nothing
        What goes out:  Returns a connection to the database
        Side effects:   None
        Description: Reads the configuration files of the database, includes username, password, address and port etc.
        """
        db_config = read_db_config()
        return connect(**db_config)

    # ********* session ********#

    def create_session(self, description, starting_time):
        """
        What comes in:  Description of the session, the starting time of the session
        What goes out:  The integer session id created in the database
        Side effects:   None
        Description: Creates a session
        """
        args = (description, starting_time)
        return self.call_procedure('add_session', args, fetchall=False)[0]

    def read_session(self, sess_id):
        """
        What comes in:  The id of the session
        What goes out:  The session id, description and starting time
        Side effects:   None
        Description: returns the session row correspondent to the session id from the database
        """
        query = "SELECT * FROM Session WHERE id = %s"
        args = [sess_id]
        return self.read_one(query, args)

    def get_all_sessions(self):
        """
        What comes in:  Nothing
        What goes out:  All the sessions in the database
        Side effects:   None
        Description: Returns all the sessions and their description and starting time
        """
        query = "SELECT * FROM Session"
        return self.read_all(query)
    
    def get_sessions_not_related_to_device(self, device_id):
        """
        What comes in:  device id
        What goes out:  All the sessions in the database that the provided
                        device is not a part of
        Side effects:   None
        Description: Returns all the sessions, descriptions, and starting times
                        that don't have any records from the indicated device
        """
        args = [device_id]
        return self.call_procedure('get_sessions_not_related_to_device', args)

    def get_all_records_from_session(self, session_id):
        """
        What comes in:  Nothing
        What goes out:  All the sessions in the database
        Side effects:   None
        Description: Returns all the sessions and their description and starting time
        """
        args = [session_id]
        return self.call_procedure('get_all_records_from_session', args)
    
    def get_all_data_from_session(self, session_id):
        """
        What comes in:  Session_id
        What goes out:  A pair contains the accel points and gyro points
        Side effects:   None
        Description: The accel points from different records are added together sorted by timestamp, same for gyro points.
        """
        return (self.get_all_accel_points_from_session(session_id), self.get_all_gyro_points_from_session(session_id))

    def get_record(self, record_id):
        args = [record_id]
        """
        What comes in:  Record_id
        What goes out: All the information for a record
        Side effects:   None
        Description: Returns the Session id and device id of a record
        """
        args = (record_id)
        return self.call_procedure('select_record', args)
        
    def get_session_id(self, description, starting_time):
        """
        What comes in:  description, starting_time
        What goes out: The session id
        Side effects:   None
        Description: Returns the Session id base on the given starting time and description
        """
        args = [description, starting_time]
        return self.call_procedure("get_session_id", args, fetchall=False)

    def reset_session_auto_index(self):
        """
        What comes in:  Nothing
        What goes out: Nothing
        Side effects: Reset the auto index in the session table
        Description: When a session is removed, in order to reuse the session id, the auto index is set to the highest current index in the session + 1
        """
        self.call_procedure('reset_session_auto_index')

    # ********* record ********#
    def create_record(self, session_id, device_id):
        """
        What comes in:  session id, and device id
        What goes out: record id
        Side effects:
        Description: Creates a record id(sha1) base on the session_id and device_id
        """
        record_id = self.sha1(str(session_id) + device_id)
        args = [record_id, session_id, device_id]
        self.call_procedure('create_record', args)
        return record_id

    def get_record_data(self, record_id):
        """
        What comes in:  record id
        What goes out: accel and gyro points from a record in a pair
        Side effects: None
        Description: Select the accel and gyro points from a record, and return them in two sperate lists
        """
        args = [record_id]
        access_points = self.call_procedure('select_gyro', args)
        gyro_points = self.call_procedure('select_accel', args)
        return access_points, gyro_points

    def sha1(self, sha_input):
        """
        What comes in:  a string
        What goes out: 128 character sha
        Side effects: None
        Description: Hash the input and return a 128 character hashkey
        """
        m = hashlib.sha1()
        m.update(sha_input.encode('utf-8'))
        return m.hexdigest()

    # ********* device ******** #
    def create_device_entry(self, device_id, device_name):
        """
        What comes in:  The device id and user-defined device name
        What goes out:  None
        Side effects:   None
        Description: Creates a new entry in the DeviceNames table with the provided
                        device name and id
        """
        args = (device_id, device_name)
        return self.call_procedure('create_device_entry', args)

    def update_device_entry(self, device_id, device_name):
        """
        What comes in:  The device id and user-defined device name
        What goes out:  None
        Side effects:   None
        Description: Updates the device name of the entry in the DeviceNames
                    table that has the given id
        """
        args = (device_id, device_name)
        return self.call_procedure('update_device_entry', args)

    def get_device_name(self, device_id):
        """
        What comes in:  The device id
        What goes out:  The name of the device with the given id
        Side effects:   None
        Description: Returns the device name of the device with the specified id
        """
        args = [device_id]
        name = self.call_procedure('get_device_name', args)
        if len(name) == 0:
            return name
        else:
            return name[0]

    def delete_device_entry(self, device_id):
        """
        What comes in:  The device id
        What goes out:  None
        Side effects:   None
        Description: Deletes the entry in the DeviceNames table corresponding
                        to the provided device id
        """
        args = [device_id]
        return self.call_procedure('delete_device_entry', args)

    # ********* gyro_points ********#

    def insert_gyro_points(self, record_id, timestamp, roll, pitch, yaw):
        """
        What comes in:  record_id, timestamp, roll, pitch, yaw
        What goes out: row id
        Side effects: None
        Description:  This function is here for easier testing purpose, in general, you should use bulk insert
        """
        query = "INSERT INTO GyroPoints" \
                "(record_id, timestamp, roll, pitch, yaw) " \
                "VALUES(%s,%s, %s, %s, %s)"
        args = (record_id, timestamp, roll, pitch, yaw)
        return self.insert(query, args)

    def get_all_gyro_points_from_session(self, session_id):
        """
        What comes in:  session id
        What goes out: all the gyro points within this session, despite the record id, sorted by time
        Side effects: None
        Description:
        """
        return self.call_procedure('select_all_gyro_from_session', [session_id])

    def bulk_insert_gyro_points(self, data_path, local=False):
        """
        What comes in:  path of the files,  if the file is on the server or a remote machine
        What goes out: Nothing
        Side effects: None
        Description: This allows inserting gyropoints to a record from a csv file, if insert from the server local = false, if insert from a remote client, then local = True
        """
        args = ["GyroPoints", '(record_id, timestamp, roll, pitch, yaw)']
        self.load_csv_data(local, data_path, args)

    def select_gyro(self, record_id):
        """
        What comes in:  record_id
        What goes out: Return the gyro points of one record
        Side effects: None
        Description:
        """
        args = [record_id]
        return self.call_procedure('select_gyro', args)

    # ********* accel_points ********#

    def insert_accel_points(self, record_id, timestamp, x, y, z):
        """
        What comes in:  record_id, timestamp, x, y, z
        What goes out: row id
        Side effects: None
        Description:  This function is here for easier testing purpose, in general, you should use bulk insert
        """
        query = "INSERT INTO AccelPoints " \
                "(record_id, timestamp, surge, sway, heave) " \
                "VALUES(%s,%s, %s, %s, %s)"
        args = (record_id, timestamp, x, y, z)
        return self.insert(query, args)

    def get_all_accel_points_from_session(self, session_id):
        """
        What comes in:  session id
        What goes out: all the accel points within this session, despite the record id, sorted by time
        Side effects: None
        Description:
        """
        return self.call_procedure('select_all_accel_from_session', [session_id])

    def select_accel(self, record_id):
        """
        What comes in:  record_id
        What goes out: Return the accel points of one record
        Side effects: None
        Description:
        """
        args = [record_id]
        return self.call_procedure('select_accel', args)

    # Local means insert outside of server,
    def bulk_insert_accel_points(self, data_path, local=False):
        """
        What comes in:  path of the files,  if the file is on the server or a remote machine
        What goes out: Nothing
        Side effects: None
        Description: This allows inserting accel points to a record from a csv file, if insert from the server local = false, if insert from a remote client, then local = True
        """
        args = ["AccelPoints", '(record_id, timestamp, surge, sway, heave)']
        self.load_csv_data(local, data_path, args)

    # ********* integration ********#
    def delete_entire_session(self, session_id):
        """
        What comes in:  session id
        What goes out: Nothing
        Side effects: The auto index in the session table is reseted.
        Description:
        """
        args = [session_id]
        self.call_procedure('delete_session', args)
        self.reset_session_auto_index()

    # ********* read ********#
    def read_data_points(self, table, record_id, timestamp):
        """
        What comes in:  table name, record_id, timestamp
        What goes out: One row of accel or gyro data
        Side effects:
        Description: Return one row from accel or gyro table based on the record id and timestamp
        """
        query = "SELECT * FROM " + table + " WHERE record_id = %s AND timestamp = %s"
        args = [record_id, timestamp]
        return self.read_one(query, args)

    def read_one(self, query, args=[]):
        """
        What comes in:  MySql query, arguments
        What goes out: One row from the query result
        Side effects:
        Description: Read and return the first row from the result
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, args)
            data = cursor.fetchone()
            cursor.close()
            return data
        except Error as error:
            print(error)

    def read_all(self, query, args=[]):
        """
        What comes in:  MySql query, arguments
        What goes out: The result of the query
        Side effects:
        Description: Read and return the entire result
        """
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
        """
        What comes in:  MySql query, arguments
        What goes out: Nothing
        Side effects: Remove elements that is a foreign key may cascade the entire database
        Description:
        """
        self.execute_transaction_query(query, args)

    # ********* insert ********#
    def insert(self, query, args=[], multi_row=False):
        """
        What comes in:  MySql query, arguments, If the insert is single row or multiple row
        What goes out: last inserted id
        Side effects: Multiple row might not have last inserted id
        Description:
        """
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

    def load_csv_data(self, local, path, args):
        """
        What comes in: If the location of the file is remote or local on the server, path to the file, args contains table name, column names
        What goes out: last inserted id
        Side effects:
        Description:  load csv data to mysql database
        """
        if local:
            lo = 'LOCAL'
        else:
            lo = ''

        system_name = platform.system()

        line_endings = '\r\n'
        if system_name == 'Linux':
            line_endings = '\n'

        query = "LOAD DATA " + lo + " INFILE '" + path + "' INTO " \
                "TABLE " + args[0] + " FIELDS TERMINATED BY ',' LINES " \
                "TERMINATED BY '" + line_endings + "' IGNORE 1 LINES " + args[1] + ";"
        self.execute_transaction_query(query, [])

    # ********* generic query ********#
    def call_procedure(self, proc_name, args=[], fetchall=True):
        """
        What comes in: Procedure name, the arguments for that procedure, return all result or just one row
        What goes out: Result of the query
        Side effects:
        Description:  Generic procedure call
        """
        try:
            cursor = self.conn.cursor()
            cursor.callproc(proc_name, args)
            if fetchall:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()
            cursor.close()
            return result
        except Error as error:
            print(error)
    
    def execute_transaction_query(self, query, args=[]):
        """
        What comes in: Procedure name, the arguments for that procedure
        What goes out: Result of the query
        Side effects:
        Description:  Generic transaction call
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, args)
            self.conn.commit()
            cursor.close()
        except Error as error:
            print(error)

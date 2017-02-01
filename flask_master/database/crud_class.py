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
    def create_session(self, description, starting_time):
        query = "INSERT INTO Session" \
                "( description, starting_time) " \
                "VALUES( %s, %s)"
        args = (description, starting_time)
        return self.insert(query, args)

    def read_session(self, sess_id):
        # id has to be surrouded by ''
        # EX: 'Test'
        query = "SELECT * FROM Session WHERE id = %s"
        args = [sess_id]
        return self.read_one(query, args)

    def get_all_sessions(self):
        query = "SELECT * FROM Session"
        return self.read_all(query)

    def get_sessions(self, device_id):
        query = "SELECT * FROM Session WHERE id in (SELECT session_id FROM Records WHERE device_id != %s)"
        args = [device_id]
        return self.read_all(query, args)

    def get_all_records_from_session(self, session_id):
        query = "SELECT Records.id, Records.session_id, Records.device_id FROM Records where session_id = %s"
        args = [session_id]
        return self.read_all(query, args)
    
    def get_all_data_from_session(self, session_id):
        return (self.get_all_accel_points_from_session(session_id), self.get_all_gyro_points_from_session(session_id))

    def get_session_id(self, description, starting_time):
        query = "SELECT * FROM Session WHERE description = %s AND starting_time = %s"
        args = [description, starting_time]
        return self.read_one(query, args)

    def reset_session_auto_index(self):
        select_col = "SELECT MAX( `id` ) FROM `Session` ";
        num_of_row = self.read_one(select_col)
        # if there is no rows in the table, reset the auto index to 0
        if num_of_row[0] is None:
            num_of_row = [1]
        else:
            num_of_row = [num_of_row[0] + 1]
        query = "ALTER TABLE Session AUTO_INCREMENT = %s"
        self.execute_transaction_query(query, num_of_row)

    # ********* record ********#
    def create_record(self, session_id, device_id):
        record_id = self.sha1(str(session_id) + device_id)
        query = "INSERT INTO Records" \
                "(id, session_id, device_id)" \
                "VALUES(%s, %s, %s)"
        args = [record_id, session_id, device_id]
        self.insert(query, args)
        return record_id

    def get_record_data(self, record_id):
        query_accel = "SELECT * FROM AccelPoints where record_id = %s"
        query_gyro = "SELECT * FROM GyroPoints where record_id = %s"
        args = [record_id]
        access_points = self.read_all(query_accel, args)
        gyro_points = self.read_all(query_gyro, args)
        return access_points, gyro_points

    def sha1(self, sha_input):
        m = hashlib.sha1()
        m.update(sha_input.encode('utf-8'))
        return m.hexdigest()

    # ********* gyro_points ********#
    def insert_gyro_points(self, record_id, timestamp, roll, pitch, yaw):
        query = "INSERT INTO GyroPoints" \
                "(record_id, timestamp, roll, pitch, yaw) " \
                "VALUES(%s,%s, %s, %s, %s)"
        args = (record_id, timestamp, roll, pitch, yaw)
        return self.insert(query, args)

    def insert_many_gyro_points(self, data):
        query = "INSERT INTO GyroPoints" \
                "(record_id, timestamp, roll, pitch, yaw) " \
                "VALUES(%s,%s, %s, %s, %s)"
        args = data
        return self.insert(query, args, multiRow=True)

    def bulk_insert_gyro_points(self, data_path, local=False):
        if local:
            lo = 'LOCAL'
        else:
            lo = ''
        args = ["GyroPoints", '(record_id, timestamp, roll, pitch, yaw)']
        self.load_csv_data(lo, data_path, args)

    def select_gyro(self, record_id):
        query = "SELECT GyroPoints.timestamp, GyroPoints.roll, GyroPoints.pitch, GyroPoints.yaw" \
                " FROM GyroPoints WHERE GyroPoints.record_id = %s ORDER BY GyroPoints.timestamp ASC"
        args = [record_id]
        return self.read_all(query, args)
    
    def get_all_gyro_points_from_session(self, session_id):
        cursor = self.conn.cursor()
        cursor.callproc('select_all_gyro_from_session',(session_id))
        return cursor.fetchall()

    # ********* accel_points ********#
    def insert_accel_points(self, record_id, timestamp, x, y, z):
        query = "INSERT INTO AccelPoints " \
                "(record_id, timestamp, surge, sway, heave) " \
                "VALUES(%s,%s, %s, %s, %s)"
        args = (record_id, timestamp, x, y, z)
        return self.insert(query, args)

    def select_accel(self, record_id):
        query = "SELECT AccelPoints.timestamp, AccelPoints.surge, AccelPoints.sway, AccelPoints.heave" \
                " FROM AccelPoints WHERE AccelPoints.record_id = %s ORDER BY AccelPoints.timestamp ASC"
        args = [record_id]
        return self.read_all(query, args)

    # Local means insert outside of server,
    def bulk_insert_accel_points(self, data_path, local=False):
        if local:
            lo = 'LOCAL'
        else:
            lo = ''
        args = ["AccelPoints", '(record_id, timestamp, surge, sway, heave)']
        self.load_csv_data(lo, data_path, args)
    
    def get_all_accel_points_from_session(self, session_id):
        cursor = self.conn.cursor()
        cursor.callproc('select_all_accel_from_session',(session_id))
        return cursor.fetchall()

    # ********* integration ********#
    def delete_entire_session(self, session_id):
        try:
            cursor = self.conn.cursor()
            # select all records links to the sesson id
            all_records_query = "SELECT id FROM Records WHERE Records.session_id = %s"
            cursor.execute(all_records_query, [session_id])

            all_records = cursor.fetchall()
            for record in all_records:
                # delete all the accel points and gyro points
                cursor.execute("DELETE FROM AccelPoints WHERE record_id = %s", [record])
                # remove the record
                cursor.execute("DELETE FROM GyroPoints WHERE record_id = %s", [record])

                cursor.execute("DELETE FROM Records WHERE id = %s", [record])
            # remove the session
            query = "DELETE FROM Session WHERE id = %s"
            cursor.execute(query, [session_id])
            self.conn.commit()
            cursor.close()
        except Error as error:
            print(error)
        # query = "DELETE FROM Session WHERE id = %s"
        #     delete_data(query, [lastid])
        #     reset_session_autoIndex()
        #     query = ""
        # test
        finally:
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
            # if last_id:
            #     print('last insert id', last_id)
            # else:
            #     print('last insert id not found')
            self.conn.commit()
            cursor.close()
            return last_id
        except Error as error:
            print(error)

    def load_csv_data(self, local, path, args):
        #         path has to be surrounded by single quotation mark '
        #         "LOAD DATA LOCAL INFILE" \
        #                 "'testdata.csv'"  \
        #                 "INTO TABLE Session FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n'"\
        #                 "(description, starting_time) SET ID = NULL;"
        query = "LOAD DATA " + local + " INFILE '" + path + "' INTO " \
                                                            "TABLE " + args[0] + " FIELDS TERMINATED BY ',' LINES " \
                                                                                 "TERMINATED BY '\r\n' IGNORE 1 LINES " + \
                args[1] + ";"
        self.execute_transaction_query(query, [])

    # ********* generic query ********#
    def execute_transaction_query(self, query, args=[]):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, args)
            self.conn.commit()
            cursor.close()
        except Error as error:
            print(error)

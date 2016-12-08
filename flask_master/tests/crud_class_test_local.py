import datetime
import unittest

from flask_server import server
from database import crud_class


class CrudTest(unittest.TestCase):
    def setUp(self):
        app = server.app
        app.config['TESTING'] = True
        t = datetime.datetime.now()
        starting_time = (t - datetime.datetime(1970, 1, 1)).total_seconds()
        self.crud = crud_class.Crud()
        self.starting_time = round(starting_time,5)
        self.app = app.test_client()

    def tearDown(self):
        self.crud.close()

    def test_create_and_read_session(self):
        description = "test"
        lastid = self.crud.create_session(description, self.starting_time)
        data = self.crud.read_session(lastid)
        self.assertEqual(description, data[1])
        self.assertEqual(self.starting_time, data[2])
        query = "DELETE FROM Session WHERE id = %s"
        self.crud.delete_data(query, [lastid])
        self.crud.reset_session_auto_index()
 
    def test_create_record(self):
        session_id = -1
        device_id = "-1"
        lastid = self.crud.create_record(session_id, device_id)
        self.assertEqual(lastid, self.crud.sha1(str(session_id) + device_id))
        query = "DELETE FROM Records WHERE id = %s"
        args = [lastid]
        self.crud.delete_data(query, args)
 
    def test_get_sessionId(self):
        description = "test"
        lastid = self.crud.create_session(description, self.starting_time)
        self.assertEqual(lastid, self.crud.get_session_id(description, self.starting_time)[0])
        query = "DELETE FROM Session WHERE id = %s"
        self.crud.delete_data(query, [lastid])
        self.crud.reset_session_auto_index()

    def test_insert_GyroPoints_and_readDataPoints(self):
        record_id = 'test'
        roll, pitch, yaw = 1.0, 1.0, 1.0;
        last_id = self.crud.insert_gyro_points(record_id, self.starting_time, roll, pitch, yaw)
        data = self.crud.read_data_points("GyroPoints", record_id, self.starting_time)
        self.assertEqual(data, (record_id, self.starting_time, roll, pitch, yaw))
        query = "DELETE FROM GyroPoints WHERE record_id = %s AND timestamp = %s"
        self.crud.delete_data(query, [record_id, self.starting_time])

    def test_insert_AccelPoints_and_readDataPoints(self):
        record_id = 'test'
        x, y, z = 1.0, 1.0, 1.0;
        last_id = self.crud.insert_accel_points(record_id, self.starting_time, x, y, z)
        data = self.crud.read_data_points("AccelPoints", record_id, self.starting_time)
        self.assertEqual(data, (record_id, self.starting_time, x, y, z))
        query = "DELETE FROM AccelPoints WHERE record_id = %s AND timestamp = %s"
        self.crud.delete_data(query, [record_id, self.starting_time])
 
    def test_readAll(self):
        description = "test"
        lastid = self.crud.create_session(description, self.starting_time)
        lastid1 = self.crud.create_session(description, self.starting_time + 1)
        lastid2 = self.crud.create_session(description, self.starting_time + 2)
        data = self.crud.read_all("SELECT * FROM Session")
        self.assertGreaterEqual(len(data), 3)
        query = "DELETE FROM Session WHERE id = %s"
        self.crud.delete_data(query, [lastid])
        self.crud.delete_data(query, [lastid1])
        self.crud.delete_data(query, [lastid2])
        self.crud.reset_session_auto_index()
 
    def test_reset_autoIndex(self):
        description = "test"
        query = "DELETE FROM Session WHERE id = %s"
 
        lastid = self.crud.create_session(description, self.starting_time)
        self.crud.delete_data(query, [lastid])
        self.crud.reset_session_auto_index()
 
        lastid1 = self.crud.create_session(description, self.starting_time + 1)
        self.assertEqual(lastid, lastid1)
 
        self.crud.delete_data(query, [lastid1])
        self.crud.reset_session_auto_index()
        
    


if __name__ == '__main__':
    unittest.main()

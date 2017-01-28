import datetime
import unittest

import flask_server as server
import pandas as pd


class CrudTest(unittest.TestCase):
    def setUp(self):
        app = server.app
        self.crud = server.crud
        app.config['TESTING'] = True
        t = datetime.datetime.now()
        starting_time = (t - datetime.datetime(1970, 1, 1)).total_seconds()
        self.starting_time = round(starting_time, 5)
        self.description = "test"
        self.app = app.test_client()

    def tearDown(self):
        server.t.cancel()

    def test_create_and_read_session(self):
        last_id = self.crud.create_session(self.description, self.starting_time)
        data = self.crud.read_session(last_id)
        self.assertEqual(self.description, data[1])
        self.assertEqual(self.starting_time, data[2])
        self.crud.delete_entire_session(last_id)
        self.crud.reset_session_auto_index()

    def test_create_record(self):
        device_id = "-1"
        session_id = self.crud.create_session(self.description, self.starting_time)
        last_id = self.crud.create_record(session_id, device_id)
        self.assertEqual(last_id, self.crud.sha1(str(session_id) + device_id))
        self.crud.delete_entire_session(session_id)

    def test_get_session_id(self):
        last_id = self.crud.create_session(self.description, self.starting_time)
        self.assertEqual(last_id, self.crud.get_session_id(self.description, self.starting_time)[0])
        self.crud.delete_entire_session(last_id)
        self.crud.reset_session_auto_index()

    def test_insert_gyro_points_and_read_data_points(self):
        device_id = 'test'
        sess_id = self.crud.create_session(self.description, self.starting_time)
        record_id = self.crud.create_record(sess_id, device_id)
        roll, pitch, yaw = 1.0, 1.0, 1.0
        self.crud.insert_gyro_points(record_id, self.starting_time, roll, pitch, yaw)
        data = self.crud.read_data_points("GyroPoints", record_id, self.starting_time)
        self.assertEqual(data, (record_id, self.starting_time, roll, pitch, yaw))
        self.crud.delete_entire_session(sess_id)

    def test_insert_accel_points_and_read_data_points(self):
        device_id = 'test'
        x, y, z = 1.0, 1.0, 1.0
        sess_id = self.crud.create_session(self.description, self.starting_time)
        record_id = self.crud.create_record(sess_id, device_id)
        self.crud.insert_accel_points(record_id, self.starting_time, x, y, z)
        data = self.crud.read_data_points("AccelPoints", record_id, self.starting_time)
        self.assertEqual(data, (record_id, self.starting_time, x, y, z))
        self.crud.delete_entire_session(sess_id)

    def test_read_all(self):
        last_id = self.crud.create_session(self.description, self.starting_time)
        last_id1 = self.crud.create_session(self.description, self.starting_time + 1)
        last_id2 = self.crud.create_session(self.description, self.starting_time + 2)
        data = self.crud.read_all("SELECT * FROM Session")
        self.assertGreaterEqual(len(data), 3)
        self.crud.delete_entire_session(last_id)
        self.crud.delete_entire_session(last_id1)
        self.crud.delete_entire_session(last_id2)
        self.crud.reset_session_auto_index()

    def test_reset_auto_index(self):
        last_id = self.crud.create_session(self.description, self.starting_time)
        self.crud.delete_entire_session(last_id)
        self.crud.reset_session_auto_index()
        last_id_1 = self.crud.create_session(self.description, self.starting_time + 1)
        self.assertEqual(last_id, last_id_1)
        self.crud.delete_entire_session(last_id_1)
        self.crud.reset_session_auto_index()


if __name__ == '__main__':
    unittest.main()

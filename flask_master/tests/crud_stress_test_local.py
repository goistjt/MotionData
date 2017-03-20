import datetime
import unittest
import pandas as pd
import os
import time

import flask_server as server


def get_now():
    t = datetime.datetime.now()
    return (t - datetime.datetime(1970, 1, 1)).total_seconds()


class CrudTest(unittest.TestCase):
    def setUp(self):
        app = server.app
        server.POOL_TIME = 10
        app.config['TESTING'] = True
        t = datetime.datetime.now()
        starting_time = (t - datetime.datetime(1970, 1, 1)).total_seconds()
        self.crud = server.crud
        self.starting_time = round(starting_time, 5)
        self.app = app.test_client()
        self.session_id = None
        self.device_id = None

    def tearDown(self):
        time.sleep(30)
        self.crud.delete_entire_session(self.session_id)
        self.crud.delete_device_entry(self.device_id)
        server.t.cancel()

    def test_load_infile(self):
        starting_time = get_now()

        description = "test_data_output"
        test_data = -1
        self.session_id = self.crud.create_session(description, starting_time)
        self.device_id = "-1"
        device_name = "crud_stress_test"
        self.crud.create_device_entry(self.device_id, device_name)
        record_id = self.crud.create_record(self.session_id, self.device_id)

        gyro_points = []
        access_points = []

        for i in range(100000):
            gyro_points.append((record_id, starting_time + i, test_data, test_data, test_data))
            access_points.append((record_id, starting_time + i, test_data, test_data, test_data))

        accel = pd.DataFrame(gyro_points)
        gyro = pd.DataFrame(access_points)
        #         pathAccel = '/home/csse/MotionData/tmp/accel.csv'
        #         pathGyro = '/home/csse/MotionData/tmp/gyro.csv'
        path_accel = 'accel.csv'
        path_gyro = 'gyro.csv'

        # make sure the columns matches with the sql db
        accel.to_csv(path_accel, index=False)
        gyro.to_csv(path_gyro, index=False)

        self.crud.bulk_insert_gyro_points(path_gyro, True)
        self.crud.bulk_insert_accel_points(path_accel, True)
        os.remove(path_accel)
        os.remove(path_gyro)


if __name__ == '__main__':
    unittest.main()

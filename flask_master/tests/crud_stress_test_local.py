import datetime
import unittest
import pandas as pd
import os

from flask_server import server
from database import crud_class


def get_now():
    t = datetime.datetime.now()
    return (t - datetime.datetime(1970, 1, 1)).total_seconds()


class CrudTest(unittest.TestCase):
    def setUp(self):
        app = server.app
        app.config['TESTING'] = True
        t = datetime.datetime.now()
        starting_time = (t - datetime.datetime(1970, 1, 1)).total_seconds()
        self.crud = crud_class.Crud()
        self.starting_time = round(starting_time, 5)
        self.app = app.test_client()

    def tearDown(self):
        self.crud.close()

    def test_load_infile(self):
        crud = self.crud
        starting_time = get_now()

        description = "test_data_output"
        test_data = -1
        session_id = crud.create_session(description, starting_time)
        device_id = "-1"
        record_id = crud.create_record(session_id, device_id)

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

        crud.bulk_insert_gyro_points(path_gyro, True)
        crud.bulk_insert_accel_points(path_accel, True)

        os.remove(path_accel)
        os.remove(path_gyro)

        crud.delete_entire_session(session_id)


if __name__ == '__main__':
    unittest.main()

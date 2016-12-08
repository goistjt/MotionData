"""
Created on Oct 15, 2016

@author: yangr
"""
import datetime
import unittest

from database import crud_class


def get_now():
    t = datetime.datetime.now()
    return (t - datetime.datetime(1970, 1, 1)).total_seconds()


class Test(unittest.TestCase):
    def setUp(self):
        self.crud = crud_class.Crud()
        pass

    def tearDown(self):
        pass

    def test_Data_Output(self):
        description = "test_data_output"
        starting_time = get_now()
        test_data = 1
        session_id = self.crud.create_session(description, starting_time)
        device_id = "-1"
        record_id = self.crud.create_record(session_id, device_id)
        self.crud.insert_gyro_points(record_id, starting_time, test_data, test_data, test_data)
        self.crud.insert_accel_points(record_id, starting_time, test_data, test_data, test_data)
        # csv = da.download_record(record_id)
        # print(csv)
        self.crud.delete_entire_session(session_id)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

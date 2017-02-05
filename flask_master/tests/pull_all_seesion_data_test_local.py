import datetime
import unittest
import numpy as np

import flask_server as server


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

#     def test_pull_accel_data(self):
#         data = np.array(self.crud.get_all_accel_points_from_session('6'))
#         self.assertEqual(3023, data.shape[0])
#     
#     def test_pull_gyro_data(self):
#         data = np.array(self.crud.get_all_gyro_points_from_session('6'))
#         self.assertEqual(3018, data.shape[0])


if __name__ == '__main__':
    unittest.main()

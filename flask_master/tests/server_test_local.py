import base64
import gzip
import json
import time
import unittest

import flask_server as fs


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        app = fs.app
        fs.local = True
        fs.POOL_TIME = 5
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.session = None

    def tearDown(self):
        time.sleep(30)
        delete_data = {"sess_id": self.session}
        response = self.app.delete('/deleteSession', data=json.dumps(delete_data), content_type='application/json')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)
        fs.t.cancel()

    def test_get_record_data_raw(self):
        pass

    def test_get_record_data_analyzed(self):
        pass

    def test_create_delete_session(self):
        create_data = {"device_id": "oqewiruo_t1",
                       "device_name": "test_device",
                       "gyroModels": [{"time_val": 123876098234, "roll_val": 1, "pitch_val": 1, "yaw_val": 1}],
                       "accelModels": [{"time_val": 123876098234, "x_val": 1, "y_val": 1, "z_val": 1}],
                       "sess_desc": "This is a description that I'm typing for no reason whatsoever",
                       "begin": 123876098234}
        zlibbed = gzip.compress(bytes(json.dumps(create_data), 'utf-8'))
        b64d = base64.b64encode(zlibbed)

        response = self.app.post('/createSession', data=b64d, content_type='application/json')
        resp_json = json.loads(response.data.decode("utf-8"))
        session_id = resp_json['session_id']
        self.assertIsNotNone(resp_json)

        self.session = session_id

        # delete_data = {"sess_id": session_id}
        # response = self.app.delete('/deleteSession', data=json.dumps(delete_data), content_type='application/json')
        # resp_json = json.loads(response.data.decode("utf-8"))
        # self.assertIsNotNone(resp_json)

    def test_create_add_delete_session(self):
        create_data = {"device_id": "oqewiruo_t1",
                       "device_name": "test_device_1",
                       "gyroModels": [{"time_val": 123876098234, "roll_val": 1, "pitch_val": 1, "yaw_val": 1}],
                       "accelModels": [{"time_val": 123876098234, "x_val": 1, "y_val": 1, "z_val": 1}],
                       "sess_desc": "This is a description that I'm typing for no reason whatsoever",
                       "begin": 123876098234}
        response = self.app.post('/createSession',
                                 data=base64.b64encode(gzip.compress(bytes(json.dumps(create_data), 'utf-8'))),
                                 content_type='application/json')
        resp_json = json.loads(response.data.decode("utf-8"))
        session_id = resp_json['session_id']
        self.assertIsNotNone(resp_json)

        add_data = {"sess_id": session_id,
                    "device_id": "oqewiruo_t2",
                    "device_name": "test_device_2",
                    "gyroModels": [{"time_val": 123876098235, "roll_val": 2, "pitch_val": 2, "yaw_val": 2}],
                    "accelModels": [{"time_val": 123876098235, "x_val": 2, "y_val": 2, "z_val": 2}],
                    "sess_desc": "This is a description that I'm typing for no reason whatsoever too"}
        response = self.app.post('/addToSession',
                                 data=base64.b64encode(gzip.compress(bytes(json.dumps(add_data), 'utf-8'))),
                                 content_type='application/json')
        resp_json = json.loads(response.data.decode("utf-8"))
        session_id = resp_json['session_id']
        self.assertIsNotNone(resp_json)

        self.session = session_id
        # delete_data = {"sess_id": session_id}
        # response = self.app.delete('/deleteSession', data=json.dumps(delete_data), content_type='application/json')
        # resp_json = json.loads(response.data.decode("utf-8"))
        # self.assertIsNotNone(resp_json)

    def test_get_sessions(self):
        response = self.app.get('/getSessions/12345')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)


if __name__ == '__main__':
    unittest.main()

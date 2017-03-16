import base64
import gzip
import json
import time
import unittest
import hashlib
import numpy as np
import pandas as pd

import flask_server as fs


class FlaskTestCase(unittest.TestCase):
    """
        This test class handles integration testing of the server
    """
    @classmethod
    def setUpClass(cls):
        """
            Set all relative settings to the appropriate testing values
        """
        app = fs.app
        fs.local = True
        fs.POOL_TIME = 5
        app.config['TESTING'] = True
        cls.app = app.test_client()
        cls.session = None

    @classmethod
    def tearDownClass(cls):
        """
            Cancels the background database upload thread so the test doesn't hang
        """
        fs.t.cancel()

    def tearDown(self):
        """
            Deletes the created session from the database, if applicable
        """
        if self.session:
            time.sleep(30)
            delete_data = {"sess_id": self.session}
            response = self.app.delete('/deleteSession', data=json.dumps(delete_data), content_type='application/json')
            resp_json = json.loads(response.data.decode("utf-8"))
            self.assertIsNotNone(resp_json)
            self.session = None

    def test_get_record_data_raw(self):
        """
            Tests the getRecordRaw server call
            Creates a session and gets the raw record data from that session
            Verifies that the response data is the same as what was used to create the session
            Sets the self.session variable so that the session can be deleted in tearDown
        """
        device_id = "oqewiruo_t1"
        create_data = {"device_id": device_id,
                       "device_name": "test_device",
                       "gyroModels": [{"time_val": 123876098234, "roll_val": 1, "pitch_val": 1, "yaw_val": 1}],
                       "accelModels": [{"time_val": 123876098234, "x_val": 1, "y_val": 1, "z_val": 1}],
                       "sess_desc": "This is a description that I'm typing for no reason whatsoever",
                       "begin": 123876098234}
        zlibbed = gzip.compress(bytes(json.dumps(create_data), 'utf-8'))
        b64d = base64.b64encode(zlibbed)

        response = self.app.post('/createSession', data=b64d, content_type='application/json')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)
        self.session = resp_json['session_id']

        sha_input = str(self.session) + device_id
        m = hashlib.sha1()
        m.update(sha_input.encode('utf-8'))
        record_id = m.hexdigest()

        time.sleep(60)
        response = self.app.get('/getRecordRaw/' + record_id)
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)

        zero = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        df = pd.DataFrame(np.array([zero, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], zero]))
        data = df.to_csv(index=False, header=False, sep=" ", float_format="%.6f")
        self.assertEquals(resp_json['data'], data)

    def test_get_record_data_analyzed(self):
        """
            Tests the getRecordAnalyzed server call
            Creates a session and gets the analyzed record data from that session
            Verifies that the response data is appropriate for what was used to create the session
            Sets the self.session variable so that the session can be deleted in tearDown
        """
        device_id = "oqewiruo_t1"
        create_data = {"device_id": device_id,
                       "device_name": "test_device",
                       "gyroModels": [{"time_val": 123876098234, "roll_val": 1, "pitch_val": 1, "yaw_val": 1},
                                      {"time_val": 123876098274, "roll_val": 1, "pitch_val": 1, "yaw_val": 1}],
                       "accelModels": [{"time_val": 123876098234, "x_val": 1, "y_val": 1, "z_val": 1},
                                       {"time_val": 123876098274, "x_val": 1, "y_val": 1, "z_val": 1}],
                       "sess_desc": "This is a description that I'm typing for no reason whatsoever",
                       "begin": 123876098234}
        zlibbed = gzip.compress(bytes(json.dumps(create_data), 'utf-8'))
        b64d = base64.b64encode(zlibbed)

        response = self.app.post('/createSession', data=b64d, content_type='application/json')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)
        self.session = resp_json['session_id']

        sha_input = str(self.session) + device_id
        m = hashlib.sha1()
        m.update(sha_input.encode('utf-8'))
        record_id = m.hexdigest()

        time.sleep(60)
        response = self.app.get('/getRecordAnalyzed/' + record_id)
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)

        data = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.000267, 0.000267, 0.000267, 0.000267, 0.000267, 0.000267],
                [0.001867, 0.001867, 0.001867, 0.001867, 0.001867, 0.001867],
                [0.004800, 0.004800, 0.004800, 0.004800, 0.004800, 0.004800],
                [0.007163, 0.007215, 0.007215, 0.000000, 0.000000, 0.000000],
                [0.005327, 0.005706, 0.005706, 0.000000, 0.000000, 0.000000],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
        df = pd.DataFrame(np.array(data))
        data = df.to_csv(index=False, header=False, sep=" ", float_format="%.6f")
        self.assertEquals(resp_json['data'], data)

    def test_get_session_data_raw(self):
        """
            Tests the getSessionRaw server call
            Creates a session and gets the raw session data
            Verifies that the response data is the same as what was used to create the session
            Sets the self.session variable so that the session can be deleted in tearDown
        """
        device_id = "oqewiruo_t1"
        create_data = {"device_id": device_id,
                       "device_name": "test_device",
                       "gyroModels": [{"time_val": 123876098234, "roll_val": 1, "pitch_val": 1, "yaw_val": 1}],
                       "accelModels": [{"time_val": 123876098234, "x_val": 1, "y_val": 1, "z_val": 1}],
                       "sess_desc": "This is a description that I'm typing for no reason whatsoever",
                       "begin": 123876098234}
        zlibbed = gzip.compress(bytes(json.dumps(create_data), 'utf-8'))
        b64d = base64.b64encode(zlibbed)

        response = self.app.post('/createSession', data=b64d, content_type='application/json')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)
        self.session = resp_json['session_id']

        time.sleep(60)
        response = self.app.get('/getSessionRaw/' + str(self.session))
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)

        zero = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        df = pd.DataFrame(np.array([zero, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], zero]))
        data = df.to_csv(index=False, header=False, sep=" ", float_format="%.6f")
        self.assertEquals(resp_json['data'], data)

    @unittest.skip("skipping")
    def test_get_session_data_analyzed(self):
        """
            Tests the getSessionAnalyzed server call
            Creates a session and gets the analyzed data from that session
            Verifies that the response data is appropriate for what was used to create the session
            Sets the self.session variable so that the session can be deleted in tearDown
        """
        device_id = "oqewiruo_t1"
        create_data = {"device_id": device_id,
                       "device_name": "test_device",
                       "gyroModels": [{"time_val": 123876098234, "roll_val": 1, "pitch_val": 1, "yaw_val": 1}],
                       "accelModels": [{"time_val": 123876098234, "x_val": 1, "y_val": 1, "z_val": 1}],
                       "sess_desc": "This is a description that I'm typing for no reason whatsoever",
                       "begin": 123876098234}
        zlibbed = gzip.compress(bytes(json.dumps(create_data), 'utf-8'))
        b64d = base64.b64encode(zlibbed)

        response = self.app.post('/createSession', data=b64d, content_type='application/json')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)
        self.session = resp_json['session_id']

        time.sleep(45)
        response = self.app.get('/getSessionAnalyzed/' + str(self.session))
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)

        zero = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        df = pd.DataFrame(np.array([zero, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], zero]))
        data = df.to_csv(index=False, header=False, sep=" ", float_format="%.6f")
        self.assertEquals(resp_json['data'], data)

    def test_create_delete_session(self):
        """
            Tests the createSession server call
            Verifies that the response and session ID are returned
            Sets the self.session variable so that the session can be deleted in tearDown
        """
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
        self.assertIsNotNone(resp_json)
        self.session = resp_json['session_id']
        self.assertIsNotNone(self.session)

    def test_create_add_delete_session(self):
        """
            Tests the createSession and addToSession server calls
            Verifies that the two returned session IDs match
            Sets the self.session variable so that the session can be deleted in tearDown
        """
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
        self.session = resp_json['session_id']
        self.assertIsNotNone(resp_json)

        add_data = {"sess_id": self.session,
                    "device_id": "oqewiruo_t2",
                    "device_name": "test_device_2",
                    "gyroModels": [{"time_val": 123876098235, "roll_val": 2, "pitch_val": 2, "yaw_val": 2}],
                    "accelModels": [{"time_val": 123876098235, "x_val": 2, "y_val": 2, "z_val": 2}],
                    "sess_desc": "This is a description that I'm typing for no reason whatsoever too"}
        response = self.app.post('/addToSession',
                                 data=base64.b64encode(gzip.compress(bytes(json.dumps(add_data), 'utf-8'))),
                                 content_type='application/json')
        resp_json = json.loads(response.data.decode("utf-8"))
        session_id2 = resp_json['session_id']
        self.assertEquals(self.session, session_id2)
        self.assertIsNotNone(resp_json)

    def test_get_sessions(self):
        """
            Tests the getSessions server call
            Verifies that data is returned
                {sessions: ()} is returned if the db is empty
                                or nothing matches the query
        """
        response = self.app.get('/getSessions/12345')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)


if __name__ == '__main__':
    unittest.main()

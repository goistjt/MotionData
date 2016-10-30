import json
import unittest
import run_server


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        app = run_server.app
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_hello_world(self):
        response = self.app.get('/hello-world')
        self.assertEqual(b'Hello World!', response.data)

    def test_echo(self):
        test_input = {'usernames': ['test_username']}
        response = self.app.get('/echo?usernames=test_username')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertEqual(test_input, resp_json)

    def test_gyro(self):
        response = self.app.get('/gyro')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)

    def test_session(self):
        pass

    def test_get_record(self):
        pass

    def test_create_delete_session(self):
        create_data = {"device_id": "oqewiruo",
                       "gyroModels": [{"time_val": 123876098234, "roll_val": 1, "pitch_val": 1, "yaw_val": 1}],
                       "accelModels": [{"time_val": 123876098234, "x_val": 1, "y_val": 1, "z_val": 1}],
                       "sess_desc": "This is a description that I'm typing for no reason whatsoever",
                       "begin": 123876098234}
        response = self.app.post('/createSession', data=json.dumps(create_data), content_type='application/json')
        resp_json = json.loads(response.data.decode("utf-8"))
        session_id = resp_json['session_id']
        self.assertIsNotNone(resp_json)

        delete_data = {"sess_id": session_id}
        response = self.app.delete('/deleteSession', data=json.dumps(delete_data), content_type='application/json')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)


if __name__ == '__main__':
    unittest.main()

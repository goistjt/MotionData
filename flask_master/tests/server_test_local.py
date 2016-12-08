import json
import unittest
import run_server as rs


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        app = rs.app
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

    def test_db_select_access(self):
        response = self.app.get('/gyro')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertIsNotNone(resp_json)


if __name__ == '__main__':
    unittest.main()

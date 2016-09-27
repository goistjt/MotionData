import unittest
import FlaskServer
import json


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        app = FlaskServer.app
        self.db = FlaskServer.db
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_hello_world(self):
        response = self.app.get('/hello-world')
        self.assertEquals(b'Hello World!', response.data)

    def test_echo(self):
        test_input = {'usernames': ['test_username']}
        response = self.app.get('/echo?usernames=test_username')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertEquals(test_input, resp_json)

    def test_db_select_access(self):
        test_input = {'row': '((\'2016\', \'1\', \'1\', \'1\', b\'hear\', \'1\'),)'}
        response = self.app.get('/gyro')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertEquals(test_input, resp_json)


if __name__ == '__main__':
    unittest.main()

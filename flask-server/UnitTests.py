import unittest
import FlaskServer
import json


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        app = FlaskServer.app
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_hello_world(self):
        response = self.app.get('/')
        assert b'Hello World!' in response.data

    def test_echo(self):
        test_input = {'usernames': ['brownba1']}
        response = self.app.get('/echo?usernames=brownba1')
        resp_json = json.loads(response.data.decode("utf-8"))
        print(resp_json)
        self.assertEquals(test_input, resp_json)

if __name__ == '__main__':
    unittest.main()

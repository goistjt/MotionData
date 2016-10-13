import unittest
import FlaskServer
import json
import crud
import datetime


class crud_test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hello_world(self):
        response = self.app.get('/hello-world')
        self.assertEqual(b'Hello World!', response.data)

    def test_insert(self):
        description = "test"
        starting_time = datetime.datetime.now()
        lastid = crud.create_session(description,starting_time)
        data = crud.readSession(lastid)
        print(data)
        query = "DELETE ROW FROM Session WHERE id = %s"
        crud.delet_data(query, lastid)


    def test_echo(self):
        test_input = {'usernames': ['test_username']}
        response = self.app.get('/echo?usernames=test_username')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertEqual(test_input, resp_json)

    def test_db_select_access(self):
        test_input = {'row': '()'}
        response = self.app.get('/gyro')
        resp_json = json.loads(response.data.decode("utf-8"))
        self.assertEqual(test_input, resp_json)


if __name__ == '__main__':
    unittest.main()

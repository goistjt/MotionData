import unittest
import FlaskServer
import json
import crud
import datetime
from flask import Flask, jsonify


class crud_test(unittest.TestCase):
    def setUp(self):
        app = FlaskServer.app
        app.config['TESTING'] = True
        t = datetime.datetime.now()
        starting_time = (t-datetime.datetime(1970,1,1)).total_seconds()
        self.starting_time = starting_time
        self.app = app.test_client()

    def tearDown(self):
        pass
        
    def test_create_session(self):
        description = "test"
        lastid = crud.create_session(description, self.starting_time)
        data = crud.readSession(lastid)
        self.assertEqual(description, data[1])
        self.assertEqual(self.starting_time, data[2])
        query = "DELETE FROM Session WHERE id = %s"
        crud.delete_data(query, [lastid])
        crud.reset_session_autoIndex()
    
    def test_get_sessionId(self):
        description = "test"
        lastid = crud.create_session(description, self.starting_time)
        self.assertEqual(lastid, crud.getSessionId(description, self.starting_time)[0])
        query = "DELETE FROM Session WHERE id = %s"
        crud.delete_data(query, [lastid])
        crud.reset_session_autoIndex()
    
    def test_insert_GyroPoints(self):
        record_id = 'test'
        roll, pitch, yaw = 1.0, 1.0, 1.0;
        last_id = crud.insert_GyroPoints(record_id, self.starting_time, roll, pitch, yaw)
        data = crud.readDataPoints("GyroPoints", record_id, self.starting_time)
        self.assertEqual(data, (record_id, self.starting_time, roll, pitch, yaw))
        query = "DELETE FROM GyroPoints WHERE records_id = %s AND timestamp = %s"
        crud.delete_data(query, [record_id, self.starting_time])
      
    def test_insert_AccessPoints(self):
        record_id = 'test'
        x, y, z = 1.0, 1.0, 1.0;
        last_id = crud.insert_AccessPoints(record_id, self.starting_time, x, y, z)
        data = crud.readDataPoints("AccessPoints", record_id, self.starting_time)
        self.assertEqual(data, (record_id, self.starting_time, x, y, z))
        query = "DELETE FROM AccessPoints WHERE records_id = %s AND timestamp = %s"
        crud.delete_data(query, [record_id, self.starting_time])        
  
  
    def test_readAll(self):
        description = "test"
        lastid = crud.create_session(description, self.starting_time)
        lastid1 = crud.create_session(description, self.starting_time+1)
        lastid2 = crud.create_session(description, self.starting_time+2)
        data = crud.readAll("SELECT * FROM Session")
        self.assertGreaterEqual(len(data),3)
        query = "DELETE FROM Session WHERE id = %s"
        crud.delete_data(query, [lastid])
        crud.delete_data(query, [lastid1])
        crud.delete_data(query, [lastid2])
        crud.reset_session_autoIndex()
        
    def test_reset_autoIndex(self):
        description = "test"
        query = "DELETE FROM Session WHERE id = %s"
        
        lastid = crud.create_session(description, self.starting_time)
        crud.delete_data(query, [lastid])
        crud.reset_session_autoIndex()
        
        lastid1 = crud.create_session(description, self.starting_time+1)
        self.assertEqual(lastid, lastid1)
        
        crud.delete_data(query, [lastid1])
        crud.reset_session_autoIndex()

if __name__ == '__main__':
    unittest.main()

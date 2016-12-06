import datetime
import unittest
import pandas as pd
import os

from flask_server import server
from database import crud_class

def get_now():
    t = datetime.datetime.now()
    return (t - datetime.datetime(1970, 1, 1)).total_seconds()

class CrudTest(unittest.TestCase):
    def setUp(self):
        app = server.app
        app.config['TESTING'] = True
        t = datetime.datetime.now()
        starting_time = (t - datetime.datetime(1970, 1, 1)).total_seconds()
        self.crud = crud_class.Crud()
        self.starting_time = round(starting_time,5)
        self.app = app.test_client()

    def tearDown(self):
        self.crud.close()
 
    def test_load_infile(self):
        crud = self.crud
        starting_time = get_now()
         
        description = "test_data_output"
        test_data = -1
        session_id = crud.create_session(description, starting_time)
        device_id = "-1"
        record_id = crud.create_record(session_id, device_id)
         
        gyroPoints = []
        accessPoints = []
         
        for i in range(100000):
            gyroPoints.append((record_id, starting_time+i, test_data, test_data, test_data))
            accessPoints.append((record_id, starting_time+i, test_data, test_data, test_data))
             
        accel = pd.DataFrame(gyroPoints)
        gyro = pd.DataFrame(accessPoints)
#         pathAccel = '/home/csse/MotionData/tmp/accel.csv'
#         pathGyro = '/home/csse/MotionData/tmp/gyro.csv'
        pathAccel = 'accel.csv'
        pathGyro = 'gyro.csv'
        
    #make sure the columns matches with the sql db
        accel.to_csv(pathAccel, index=False)
        gyro.to_csv(pathGyro, index= False)
 
        crud.bulk_insert_gyro_points(pathGyro, True)
        crud.bulk_insert_accel_points(pathAccel, True)
 
        os.remove(pathAccel)
        os.remove(pathGyro)
        
        crud.delete_entire_session(session_id)
        
    
    
    


if __name__ == '__main__':
    unittest.main()

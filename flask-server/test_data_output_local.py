'''
Created on Oct 15, 2016

@author: yangr
'''
import unittest
import crud
import data_analysis as da
import datetime

def getNow():
        t = datetime.datetime.now()
        return (t-datetime.datetime(1970,1,1)).total_seconds()
    
class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_Data_Output(self):
#         crud.reset_session_autoIndex()
#         description = "test_data_output"
        starting_time = getNow()
        test_data = 1
#         session_id = crud.create_session(description, starting_time)
#         record_id = crud.create_record(session_id, "data_out_test_device_id")
        record_id = '2c2b3609c6a7eefb232d816dd0222f42ee3eaa5b'
        crud.insert_GyroPoints(record_id, starting_time, test_data, test_data, test_data)
        crud.insert_AccessPoints(record_id, starting_time, test_data, test_data, test_data)
#         print()
        csv = da.download_record(record_id)
        print(csv)
#         print(da.select_record('2c2b3609c6a7eefb232d816dd0222f42ee3eaa5b'))
        
        
        
        
        
        
    
        

     

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
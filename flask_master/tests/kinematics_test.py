'''
Created on Oct 29, 2016

@author: steve
'''
import unittest
import data_analysis.data_analysis as da
import numpy as np
import decimal as dc

class TestKinematics(unittest.TestCase):

    def setUp(self):
        dc.getcontext().prec = 4
        self.MAX_EPSILON = 0.000001

    def tearDown(self):
        self.kin_keep = None
        
    def test_points_normalizer_same(self):
        points = [[0.0, 0.0, 0.0, 0.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5], [4.0, 0.0, 0.0, 0.0]]
        points_exp = [[0.0, 0.0, 0.0, 0.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5], [4.0, 0.0, 0.0, 0.0]]
        points = da.process_accelerations(0.0, 4.0, 1.0, points)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))
        
    def test_points_normalizer_beginning_off(self):
        points = [[0.2, 0.4, 100.2, 32.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5], [4.0, 0.0, 0.0, 0.0]]
        points_exp = [[0.0, 0.0, 0.0, 0.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5], [4.0, 0.0, 0.0, 0.0]]
        points = da.process_accelerations(0.0, 4.0, 1.0, points)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))
        
    def test_points_normalizer_end_off(self):
        points = [[0.2, 0.4, 100.2, 32.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5], [3.9, 22.0, 0.42, 42.0]]
        points_exp = [[0.0, 0.0, 0.0, 0.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5], [4.0, 0.0, 0.0, 0.0]]
        points = da.process_accelerations(0.0, 4.0, 1.0, points)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))
        
    def test_points_simple_shift(self):
        points = [[0.1, 0.0, 0.0, 0.0], [0.8, 2.0, 1.0, 8.0], [1.2, 1.2, 1.2, 1.2], [1.5, 2.0, 8.0, 9.0], [2.3, 43.0, 42.1, 42.0]]
        points_exp = [[0.0, 0.0, 0.0, 0.0], [1.1, 1.1, 1.1, 1.1], [2.2, 0.0, 0.0, 0.0]]
        points = da.process_accelerations(0.0, 2.2, 1.1, points)
        print(points)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))
        
    def test_points_normalizer_both(self):
        points = [[2.0, 1.0, 1.0, 1.0]]
        points_exp = [[0.0, 0.0, 0.0, 0.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5], [4.0, 0.0, 0.0, 0.0]]
        points = da.process_accelerations(0.0, 4.0, 1.0, points)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))
        
    def test_complex_shift(self):
        points = [[0.4, 0.0, 0.0, 0.0], [0.6, 1.0, 2.0, 3.0], [0.9, 4.0, 5.0, 6.0], [0.7, 1.0, 1.0, 1.0], [0.9, 8.0, 2.0, 3.0], [1.3, 0.0, 1.0, 2.0], [2.9, 2.32, 2.32, 2.32], [3.0, 8.0, 2.0, 3.0], [3.5, 1.0, 4.0, 9.2]]
        points_exp = [[0.5, 0.0, 0.0, 0.0], [1.5, 1.0, 1.0, 1.0], [2.5, 2.0, 2.0, 2.0], [3.5, 0.0, 0.0, 0.0]]
        points = da.process_accelerations(0.5, 3.5, 1.0, points)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))
    
    """
    def test_points_large_set(self):
        points = [[0, 0, 0, 0]]
        for x in range(2000):
            points.append([x * 0.000001, x, x, x])
        start = time.time()
        z = da.process_accelerations(0.2, 50000, 0.5, points)
        end = time.time()
    """
    
    def test_typical_session_cleaning(self):
        accel_list = [[0, 0, 0, 0], [1, 0.002, 0.003, 0.004], [2, 0.003, 0.004, 0.005], [3, 0.002, 0.004, 0.006]]
        gyro_list = [[0, 0, 0, 0], [1, 2, 3, 1], [2, 1, 4, 4], [3, 2, 2, 2]]
        start_time = 0
        end_time = 3
        result = da.clean_session(start_time, end_time, accel_list, gyro_list)
        print(result)
    
if __name__ == "__main__":
    unittest.main()
'''
Created on Oct 29, 2016

@author: steve
'''
import unittest
import data_analysis.data_analysis as da
import numpy as np
import decimal as dc
import data_analysis.kinematics_keeper as kk
import data_analysis.max_collection_factories as mcf

class TestKinematics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestKinematics, cls).setUpClass()
        dc.getcontext().prec = 6
        cls.MAX_EPSILON = 0.000001
        cls.max_coll_fact = mcf.MaxCollectionFactory()
        
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.kin_keep = kk.KinematicsKeeper(0, self.max_coll_fact.createMaxCollection(self.max_coll_fact.SURGE))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.kin_keep = None
        
    @classmethod
    def tearDownClass(cls):
        super(TestKinematics, cls).tearDownClass()
        cls.max_coll_fact = None
        
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
    
    def test_kk_determine_next_acceleration_by_pos(self):
        time_diff = dc.Decimal(0.0001)
        new_pos = dc.Decimal(1.0)
        actual = self.kin_keep._determine_next_acceleration_by_pos(time_diff, new_pos)
        expected = dc.Decimal(600000000)
        self.assertEqual(expected, actual)
    
    def test_kk_determine_next_acceleration_by_pos_nontrivial(self):
        self.kin_keep._curr_pos = dc.Decimal(1.0)
        self.kin_keep._curr_accel = dc.Decimal(-0.0023)
        self.kin_keep._curr_vel = dc.Decimal(-0.124)
        time_diff = dc.Decimal(0.0001)
        new_pos = dc.Decimal(2.0)
        actual = self.kin_keep._determine_next_acceleration_by_pos(time_diff, new_pos)
        expected = dc.Decimal(600006000) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)
        
    def test_kk_determine_next_acceleration_by_vel(self):
        time_diff = dc.Decimal(0.0001)
        new_vel = dc.Decimal(0.1)
        actual = self.kin_keep._determine_next_acceleration_by_vel(time_diff, new_vel)
        expected = dc.Decimal(2000)
        self.assertEqual(expected, actual)
        
    def test_kk_determine_next_acceleration_by_vel_nontrivial(self):
        self.kin_keep._curr_pos = dc.Decimal(1.0)
        self.kin_keep._curr_accel = dc.Decimal(-0.0023)
        self.kin_keep._curr_vel = dc.Decimal(-0.124)
        time_diff = dc.Decimal(0.0001)
        new_pos = dc.Decimal(2.0)
        actual = self.kin_keep._determine_next_acceleration_by_vel(time_diff, new_pos)
        expected = dc.Decimal(42480.0023) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)
        
    def test_kk_determine_next_position(self):
        time_diff = dc.Decimal(0.0001)
        new_accel = dc.Decimal(1)
        actual = self.kin_keep._determine_next_position(time_diff, new_accel)
        expected = dc.Decimal(0.00000000166667) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)
        
    def test_kk_determine_next_position_nontrivial(self):
        self.kin_keep._curr_pos = dc.Decimal(1.0)
        self.kin_keep._curr_accel = dc.Decimal(-0.0023)
        self.kin_keep._curr_vel = dc.Decimal(-0.124)
        time_diff = dc.Decimal(0.0001)
        new_pos = dc.Decimal(2.0)
        actual = self.kin_keep._determine_next_position(time_diff, new_pos)
        expected = dc.Decimal(0.9999876016) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)
        
    def test_kk_determine_next_velocity(self):
        time_diff = dc.Decimal(0.0001)
        new_accel = dc.Decimal(1)
        actual = self.kin_keep._determine_next_velocity(time_diff, new_accel)
        expected = dc.Decimal(0.00005) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)
        
    def test_kk_determine_next_velocity_nontrivial(self):
        self.kin_keep._curr_pos = dc.Decimal(1.0)
        self.kin_keep._curr_accel = dc.Decimal(-0.0023)
        self.kin_keep._curr_vel = dc.Decimal(-0.124)
        time_diff = dc.Decimal(0.0001)
        new_vel = dc.Decimal(2.0)
        actual = self.kin_keep._determine_next_velocity(time_diff, new_vel)
        expected = dc.Decimal(-0.123900) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)
    
if __name__ == "__main__":
    unittest.main()
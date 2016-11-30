'''
Created on Oct 29, 2016

@author: steve
'''
import unittest
from data_analysis import kinematics_keeper as kk
import data_analysis.data_analysis as da
import numpy as np
import decimal as dc
import time


class TestKinematics(unittest.TestCase):

    def setUp(self):
        dc.getcontext().prec = 4
        self.kin_keep = kk.KinematicsKeeper(0, None)
        self.MAX_EPSILON = 0.000001

    def tearDown(self):
        self.kin_keep = None
     
    def test_point_normalizer_perfect_input(self):
        points = np.array([[0.0, 1.0, 2.0, 3.0], [1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0], [3.0, 4.0, 5.0, 6.0]])
        points_exp = np.array([[0.0, 1.0, 2.0, 3.0], [1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0], [3.0, 0.0, 0.0, 0.0]])
        points = da.process_accelerations(0.0, 3.0, 1.0, points)
        print(points)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))
        
    def test_points_normalizer_beginning(self):
        points = np.array([[0.5, 0.5, 0.5, 0.5], [1.0, 1.0, 1.0, 1.0], [2.0, 2.0, 2.0, 2.0]])
        points_exp = np.array([[0.0, 0.0, 0.0, 0.0]])
        for x in range(20):
            points_exp = np.append(points_exp, np.array([[0.1 + (x * 0.1), 0.1 + (x * 0.1), 0.1 + (x * 0.1), 0.1 + (x * 0.1)]]), axis=0)
        points = da.process_accelerations(0.0, 2.0, 0.1, points)
        print(points)
        self.assertTrue(np.allclose(points_exp, points, self.MAX_EPSILON))
                
    def test_points_normalizer_ending(self):
        points = np.array([[0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0], [2.5, 2.5, 2.5, 2.5]])
        points_exp = np.array([[0.0, 0.0, 0.0, 0.0]])
        for x in range(25):
            points_exp = np.append(points_exp, np.array([[0.1 + (x * 0.1), 0.1 + (x * 0.1), 0.1 + (x * 0.1), 0.1 + (x * 0.1)]]), axis=0)
        for y in range(5):
            points_exp = np.append(points_exp, np.array([[2.6 + (y * 0.1), 2.0 - (y * 0.5), 2.0 - (y * 0.5), 2.0 - (y * 0.5)]]), axis=0)
        points = da.process_accelerations(0.0, 3.0, 0.1, points)
        print(points)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))
        
    def test_points_normalizer_both(self):
        points = np.array([[0.3, 0.3, 0.3, 0.3], [1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]])
        print(da.process_accelerations(0.0, 2.1, .5, points))
        
    def test_points_normalizer_everything(self):
        points = np.array([[0.3, 1.0, 2.0, 3.0], [1.4, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0], [3.4, 4.0, 5.1, 7.3]])
        print(da.process_accelerations(0.4, 2.0, 1.0, points))
     
    def test_points_under_everything(self):
        points = np.array([[0.3, 1.0, 2.0, 3.0], [0.999, 2.0, 3.0, 4.0], [1.999, 3.0, 4.0, 5.0], [3.4, 4.0, 5.1, 7.3]])
        print(da.process_accelerations(0.0, 2.0, 0.5, points))
         
    def test_points_large_set(self):
        points = np.array([[0, 0, 0, 0]])
        for x in range(20000):
            points = np.append(points, [[x * 0.1, x, x, x]], axis=0)
        start = time.time()
        res = da.process_accelerations(0.2, 20000, 0.5, points)
        end = time.time()
        print(end - start)
    
    """
    def test_kinetics_keeper_init(self):
        self.kin_keep = kk.KinematicsKeeper(200, None)
        self.assertEqual(self.kin_keep.get_excursion(), 0)
        self.assertEqual(self.kin_keep.get_velocity(), 0)
        self.assertEqual(self.kin_keep.get_acceleration(), 0)
        self.assertEqual(self.kin_keep.get_time(), 200)
        
    def test_next_position_no_time_change(self):
        new_time = self.kin_keep.get_time() + 0.0
        new_accel = 12.0
        self.kin_keep._curr_pos = 3.0
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_position() - 3.0)
        self.assertTrue(ans_diff < self.MAX_EPSILON);
        
    def test_next_position_one_time_unit(self):
        new_time = 1.0
        new_accel = 1.0
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_position() - (1/6))
        self.assertTrue(ans_diff < self.MAX_EPSILON)
    
    def test_next_position_negative_time_unit(self):
        new_time = -1.0
        new_accel = 1.0
        prev_pos = self.kin_keep.get_position()
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_position() - prev_pos)
        self.assertTrue(ans_diff < self.MAX_EPSILON)
        
    def test_next_position_negative_accel_unit(self):
        new_time = 1.0
        new_accel = -1.0
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_position() - (-1/6))
        self.assertTrue(ans_diff < self.MAX_EPSILON)
        
    def test_next_position_nonone_nonzero_both(self):
        new_time = 3.0
        new_accel = 12.0
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_position() - 54.0)
        self.assertTrue(ans_diff < self.MAX_EPSILON)
        
    def test_next_position_nonone_nonzero_full_equation(self):
        new_time = 256.0
        new_accel = 12.0
        self.kin_keep._curr_accel = 4.0
        self.kin_keep._curr_time = 42.0
        self.kin_keep._curr_pos = 7.0
        self.kin_keep._curr_vel = 10.0
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_position() - 13160864.333333)
        self.assertTrue(ans_diff < self.MAX_EPSILON)
        
    def test_next_velocity_no_time_change(self):
        new_time = 0
        new_accel = 12
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_velocity() - 0)
        self.assertTrue(ans_diff < self.MAX_EPSILON)
        
    def test_next_velocity_one_time_unit(self):
        new_time = 1
        new_accel = 1
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_velocity() - (1/2))
        self.assertTrue(ans_diff < self.MAX_EPSILON)
        
    def test_next_velocity_negative_time_unit(self):
        new_time = -1
        new_accel = 1
        prev_vel = self.kin_keep.get_velocity()
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_velocity() - prev_vel)
        self.assertTrue(ans_diff < self.MAX_EPSILON)
        
    def test_next_velocity_nonone_nonzero_full_equation(self):
        new_time = 256.0
        new_accel = 12.0
        self.kin_keep._curr_accel = 4.0
        self.kin_keep._curr_time = 42.0
        self.kin_keep._curr_pos = 7.0
        self.kin_keep._curr_vel = 10.0
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_velocity() - 184050)
        self.assertTrue(ans_diff < self.MAX_EPSILON)
        
    def test_next_excursion_no_time_change(self):
        new_time = 0
        new_accel = 12
        self.kin_keep._curr_pos = 8.0
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_velocity() - 0)
        self.assertTrue(ans_diff < self.MAX_EPSILON)
        
    def test_next_excursion_one_time_unit(self):
        new_time = 1
        new_accel = 1
        self.kin_keep._curr_pos = 6.0
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_velocity() - (1/2))
        self.assertTrue(ans_diff < self.MAX_EPSILON)
        
    def test_next_excursion_negative_time_unit(self):
        new_time = -1
        new_accel = 1
        self.kin_keep._curr_pos = 12
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_excursion() - 0)
        self.assertTrue(ans_diff < self.MAX_EPSILON)
        
    def test_next_excursion_nonone_nonzero_full_equation(self):
        new_time = 256.0
        new_accel = 12.0
        self.kin_keep._curr_accel = 4.0
        self.kin_keep._curr_time = 42.0
        self.kin_keep._curr_pos = 7.0
        self.kin_keep._curr_vel = 10.0
        self.kin_keep.generate_next_state(new_time, new_accel)
        ans_diff = abs(self.kin_keep.get_excursion() - (13160864.333333 - 7.0))
        self.assertTrue(ans_diff < self.MAX_EPSILON)

    def test_get_excursions_default(self):
        start_time = 0
        keeper_one = kk.KinematicsKeeper(0)
        keeper_one.generate_next_state(2, 1)
        exc_one_one = keeper_one.get_excursion()
        keeper_one.generate_next_state(4, 2)
        exc_one_two = keeper_one.get_excursion()
        keeper_two = kk.KinematicsKeeper(0)
        keeper_two.generate_next_state(2, 2)
        exc_two_one = keeper_two.get_excursion()
        keeper_two.generate_next_state(4, 4)
        exc_two_two = keeper_two.get_excursion()
        keeper_three = kk.KinematicsKeeper(0)
        keeper_three.generate_next_state(2, 1)
        exc_three_one = keeper_three.get_excursion()
        keeper_three.generate_next_state(4, 3)
        exc_three_two = keeper_three.get_excursion()
        accel_points = [[2, 1, 1, 1], [4, 2, 2, 3]]
        gyro_points = [[2, 2, 2, 2], [4, 4, 4, 4], [6, 10, 2, 10]]
        excursion_set = da.get_excursions(start_time, accel_points, gyro_points)
        exc_set_expected = [[0, 0, 0, 0, 0, 0], [exc_one_one, exc_one_one, exc_three_one, exc_two_one, exc_two_one, exc_two_one], [exc_one_two, exc_one_two, exc_three_two, exc_two_two, exc_two_two, exc_two_two]]
        for k in range(len(exc_set_expected)):
            for j in range(len(exc_set_expected[k])):
                ans_diff = abs(exc_set_expected[k][j] - excursion_set[k][j])
                self.assertTrue(ans_diff < self.MAX_EPSILON)
    """
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
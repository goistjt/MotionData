'''
Created on Oct 29, 2016

@author: steve
'''
import unittest
from flask_master.data_analysis import kinematics_keeper as kk


class TestKinematics(unittest.TestCase):
    
    MAX_EPSILON = 0.000001

    def setUp(self):
        self.kin_keep = kk.KinematicsKeeper(0)

    def tearDown(self):
        self.kin_keep = None

    def test_kinetics_keeper_init(self):
        self.kin_keep = kk.KinematicsKeeper(200)
        self.assertEqual(self.kin_keep.get_excursion(), 0)
        self.assertEqual(self.kin_keep.get_velocity(), 0)
        self.assertEqual(self.kin_keep.get_acceleration(), 0)
        self.assertEqual(self.kin_keep.get_time(), 200)
        
    def test_next_excursion_no_time_change(self):
        new_time = 0
        new_accel = 12
        self.kin_keep.generate_next_state(new_time, new_accel)
        self.assertTrue(self.kin_keep.get_excursion() - 0 < self.MAX_EPSILON);
        
    def test_next_excursion_one_time_unit(self):
        new_time = 1
        new_accel = 1
        self.kin_keep.generate_next_state(new_time, new_accel)
        self.assertTrue(self.kin_keep.get_excursion() - (1/6) < self.MAX_EPSILON)
    
    def test_next_excursion_negative_time_unit(self):
        new_time = -1
        new_accel = 1
        prev_exc = self.kin_keep.get_excursion()
        self.kin_keep.generate_next_state(new_time, new_accel)
        self.assertTrue(self.kin_keep.get_excursion() - prev_exc < self.MAX_EPSILON)
        
    def test_next_excursion_negative_accel_unit(self):
        new_time = 1
        new_accel = -1
        self.kin_keep.generate_next_state(new_time, new_accel)
        self.assertTrue(self.kin_keep.get_excursion() - (-1/6) < self.MAX_EPSILON)
        
    def test_next_excursion_nonone_nonzero_both(self):
        new_time = 3
        new_accel = 12
        self.kin_keep.generate_next_state(new_time, new_accel)
        self.assertTrue(self.kin_keep.get_excursion() - 54 < self.MAX_EPSILON)
        
    def test_next_excursion_nonone_nonzero_full_equation(self):
        new_time = 256.0
        new_accel = 12.0
        self.kin_keep._curr_accel = 4.0
        self.kin_keep._curr_time = 42.0
        self.kin_keep._curr_exc = 7.0
        self.kin_keep._curr_vel = 10.0
        self.kin_keep.generate_next_state(new_time, new_accel)
        self.assertTrue(self.kin_keep.get_excursion() - 13160864.333333 < self.MAX_EPSILON)
        
    def test_next_velocity_no_time_change(self):
        new_time = 0
        new_accel = 12
        self.kin_keep.generate_next_state(new_time, new_accel)
        self.assertTrue(self.kin_keep.get_velocity() - 0 < self.MAX_EPSILON)
        
    def test_next_velocity_one_time_unit(self):
        new_time = 1
        new_accel = 1
        self.kin_keep.generate_next_state(new_time, new_accel)
        self.assertTrue(self.kin_keep.get_velocity() - (1/2) < self.MAX_EPSILON)
        
    def test_next_velocity_negative_time_unit(self):
        new_time = -1
        new_accel = 1
        prev_vel = self.kin_keep.get_velocity()
        self.kin_keep.generate_next_state(new_time, new_accel)
        self.assertTrue(self.kin_keep.get_velocity() - prev_vel < self.MAX_EPSILON)
        
    def test_next_velocity_nonone_nonzero_full_equation(self):
        new_time = 256.0
        new_accel = 12.0
        self.kin_keep._curr_accel = 4.0
        self.kin_keep._curr_time = 42.0
        self.kin_keep._curr_exc = 7.0
        self.kin_keep._curr_vel = 10.0
        self.kin_keep.generate_next_state(new_time, new_accel)
        self.assertTrue(self.kin_keep.get_velocity() - 184050 < self.MAX_EPSILON)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
"""
Created on Oct 29, 2016

@author: steve
"""

import unittest
import flask_server
import data_analysis.data_analysis as da
import numpy as np
import decimal as dc
import data_analysis.kinematics_keeper as kk
import data_analysis.max_collection_factories as mcf


class TestKinematics(unittest.TestCase):

    def setUp(self):
        self.kin_keep = kk.KinematicsKeeper(self.max_coll_fact.create_max_collection(self.max_coll_fact.SURGE), 1.0)

    def tearDown(self):
        self.kin_keep = None

    @classmethod
    def setUpClass(cls):
        flask_server.app.testing = True
        dc.getcontext().prec = 6
        cls.MAX_EPSILON = 0.000001
        cls.max_coll_fact = mcf.MaxCollectionFactory()


    @classmethod
    def tearDownClass(cls):
        cls.max_coll_fact = None

    def test_points_normalizer_same(self):
        points = [[0.0, 0.0, 0.0, 0.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5],
                  [4.0, 0.0, 0.0, 0.0]]
        points_exp = [[0.0, 0.0, 0.0, 0.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5],
                      [4.0, 0.0, 0.0, 0.0]]
        points, end_time = da.process_accelerations(0.0, 4.0, points, 1.0)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))

    def test_points_normalizer_beginning_off(self):
        points = [[0.2, 0.4, 100.2, 32.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5],
                  [4.0, 0.0, 0.0, 0.0]]
        points_exp = [[0.0, 0.0, 0.0, 0.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5],
                      [4.0, 0.0, 0.0, 0.0]]
        points, end_time = da.process_accelerations(0.0, 4.0, points, 1.0)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))

    def test_points_normalizer_end_off(self):
        points = [[0.2, 0.4, 100.2, 32.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5],
                  [3.9, 22.0, 0.42, 42.0]]
        points_exp = [[0.0, 0.0, 0.0, 0.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5],
                      [4.0, 0.0, 0.0, 0.0]]
        points, end_time = da.process_accelerations(0.0, 4.0, points, 1.0)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))

    def test_points_simple_shift(self):
        points = [[0.1, 0.0, 0.0, 0.0], [0.8, 2.0, 1.0, 8.0], [1.2, 1.2, 1.2, 1.2], [1.5, 2.0, 8.0, 9.0],
                  [2.3, 43.0, 42.1, 42.0]]
        points_exp = [[0.0, 0.0, 0.0, 0.0], [1.1, 1.1, 1.1, 1.1], [2.2, 0.0, 0.0, 0.0]]
        points, end_time = da.process_accelerations(0.0, 2.2, points, 1.1)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))

    def test_points_normalizer_both(self):
        points = [[2.0, 1.0, 1.0, 1.0]]
        points_exp = [[0.0, 0.0, 0.0, 0.0], [1.0, 0.5, 0.5, 0.5], [2.0, 1.0, 1.0, 1.0], [3.0, 0.5, 0.5, 0.5],
                      [4.0, 0.0, 0.0, 0.0]]
        points, end_time = da.process_accelerations(0.0, 4.0, points, 1.0)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))

    def test_complex_shift(self):
        points = [[0.4, 0.0, 0.0, 0.0], [0.6, 1.0, 2.0, 3.0], [0.9, 4.0, 5.0, 6.0], [0.7, 1.0, 1.0, 1.0],
                  [0.9, 8.0, 2.0, 3.0], [1.3, 0.0, 1.0, 2.0], [2.9, 2.32, 2.32, 2.32], [3.0, 8.0, 2.0, 3.0],
                  [3.5, 1.0, 4.0, 9.2]]
        points_exp = [[0.5, 0.0, 0.0, 0.0], [1.5, 1.0, 1.0, 1.0], [2.5, 2.0, 2.0, 2.0], [3.5, 0.0, 0.0, 0.0]]
        points, end_time = da.process_accelerations(0.5, 3.5, points, 1.0)
        self.assertTrue(np.allclose(points_exp, points, atol=self.MAX_EPSILON))

    def test_kk_determine_next_acceleration_by_pos(self):
        dc.getcontext().prec = 6
        self.kin_keep.set_interval(0.0001)
        new_pos = dc.Decimal(1.0)
        actual = self.kin_keep._determine_next_acceleration_by_pos(new_pos)
        expected = dc.Decimal(100000000000000) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)

    def test_kk_determine_next_acceleration_by_pos_nontrivial(self):
        dc.getcontext().prec = 6
        self.kin_keep._curr_pos = dc.Decimal(1.0)
        self.kin_keep._curr_accel = dc.Decimal(-0.0023)
        self.kin_keep._curr_vel = dc.Decimal(-0.124)
        self.kin_keep.set_interval(0.0001)
        new_pos = dc.Decimal(2.0)
        actual = self.kin_keep._determine_next_acceleration_by_pos(new_pos)
        expected = dc.Decimal(100000000000000) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)

    def test_kk_determine_next_acceleration_by_vel(self):
        dc.getcontext().prec = 6
        self.kin_keep.set_interval(0.0001)
        new_vel = dc.Decimal(0.1)
        actual = self.kin_keep._determine_next_acceleration_by_vel(new_vel)
        expected = dc.Decimal(1000000) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)

    def test_kk_determine_next_acceleration_by_vel_nontrivial(self):
        dc.getcontext().prec = 6
        self.kin_keep.set_interval(0.0001)
        self.kin_keep._curr_pos = dc.Decimal(1.0)
        self.kin_keep._curr_accel = dc.Decimal(-0.0023)
        self.kin_keep._curr_vel = dc.Decimal(-0.124)
        new_pos = dc.Decimal(2.0)
        actual = self.kin_keep._determine_next_acceleration_by_vel(new_pos)
        expected = dc.Decimal(21240000) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)

    def test_kk_determine_next_position(self):
        dc.getcontext().prec = 6
        self.kin_keep.set_interval(0.0001)
        new_accel = dc.Decimal(1)
        actual = self.kin_keep._determine_next_position(new_accel)
        expected = dc.Decimal(0.000000000000000000000166667) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)

    def test_kk_determine_next_position_nontrivial(self):
        dc.getcontext().prec = 6
        self.kin_keep.set_interval(0.0001)
        self.kin_keep._curr_pos = dc.Decimal(1.0)
        self.kin_keep._curr_accel = dc.Decimal(-0.0023)
        self.kin_keep._curr_vel = dc.Decimal(-0.124)
        new_pos = dc.Decimal(2.0)
        actual = self.kin_keep._determine_next_position(new_pos)
        expected = dc.Decimal(1.00000) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)

    def test_kk_determine_next_velocity(self):
        dc.getcontext().prec = 6
        self.kin_keep.set_interval(0.0001)
        new_accel = dc.Decimal(1)
        actual = self.kin_keep._determine_next_velocity(new_accel) * dc.Decimal(1.0)
        expected = dc.Decimal(0.000000000000005) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)

    def test_kk_determine_next_velocity_nontrivial(self):
        dc.getcontext().prec = 6
        self.kin_keep.set_interval(0.0001)
        self.kin_keep._curr_pos = dc.Decimal(1.0)
        self.kin_keep._curr_accel = dc.Decimal(-0.0023)
        self.kin_keep._curr_vel = dc.Decimal(-0.124)
        new_vel = dc.Decimal(2.0)
        actual = self.kin_keep._determine_next_velocity(new_vel) * dc.Decimal(1.0)
        expected = dc.Decimal(-0.1239999) * dc.Decimal(1.0)
        self.assertEqual(expected, actual)

    def test_kk_determine_next_state_velocity(self):
        dc.getcontext().prec = 6
        self.kin_keep.set_interval(40)
        new_vel = dc.Decimal(2.0)
        self.kin_keep.generate_next_state(new_vel, kk.KinematicsKeeper.VELOCITY)
        actual_pos = self.kin_keep.get_position()
        actual_vel = self.kin_keep.get_velocity()
        actual_accel = self.kin_keep.get_acceleration()
        expected_accel = 50.0
        expected_vel = 2.0
        expected_pos = 0.0
        self.assertEqual(expected_accel, actual_accel)
        self.assertEqual(expected_vel, actual_vel)
        self.assertEqual(expected_pos, actual_pos)

    def test_kk_determine_next_state_position(self):
        dc.getcontext().prec = 6
        self.kin_keep.set_interval(40)
        new_vel = dc.Decimal(0.00015)
        self.kin_keep.generate_next_state(new_vel, kk.KinematicsKeeper.POSITION)
        actual_pos = self.kin_keep.get_position()
        actual_vel = self.kin_keep.get_velocity()
        actual_accel = self.kin_keep.get_acceleration()
        expected_accel = 0.09375
        expected_vel = 0.000075
        expected_pos = 0.00015
        self.assertEqual(expected_accel, actual_accel)
        self.assertEqual(float(expected_vel), actual_vel)
        self.assertEqual(float(expected_pos), actual_pos)

    def test_process_return_to_zero_trivial(self):
        max_fact = mcf.MaxCollectionFactory()
        modified_heave_collection = max_fact.create_max_collection(max_fact.HEAVE)
        modified_heave_collection._max_accel = 0.408

        surge_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)
        sway_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)
        heave_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)

        roll_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)
        pitch_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)
        yaw_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)

        keeps_accel = [surge_k, sway_k, heave_k]
        keeps_gyro = [roll_k, pitch_k, yaw_k]

        session = []

        result = da.process_return_to_zero(keeps_accel, keeps_gyro, session)

        self.assertTrue(np.allclose(result, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], atol=self.MAX_EPSILON))

    def test_process_return_to_nontrivial(self):
        max_fact = mcf.MaxCollectionFactory()
        modified_heave_collection = max_fact.create_max_collection(max_fact.HEAVE)

        surge_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)
        surge_k._curr_pos = dc.Decimal(0.261) * dc.Decimal(1.0)
        sway_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)
        sway_k._curr_pos = dc.Decimal(0.261) * dc.Decimal(1.0)
        heave_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)
        heave_k._curr_pos = dc.Decimal(0.261) * dc.Decimal(1.0)

        roll_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)
        roll_k._curr_pos = dc.Decimal(0.261) * dc.Decimal(1.0)
        pitch_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)
        pitch_k._curr_pos = dc.Decimal(0.261) * dc.Decimal(1.0)
        yaw_k = kk.KinematicsKeeper(modified_heave_collection, 1.0)
        yaw_k._curr_pos = dc.Decimal(0.261) * dc.Decimal(1.0)

        keeps_accel = [surge_k, sway_k, heave_k]
        keeps_gyro = [roll_k, pitch_k, yaw_k]

        session = []

        result = da.process_return_to_zero(keeps_accel, keeps_gyro, session)

        actual = result[len(result) - 1]

        self.assertTrue(np.allclose(actual, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 0.0000001))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
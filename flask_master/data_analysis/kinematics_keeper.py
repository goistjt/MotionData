"""
Created on Oct 29, 2016

@author: steve
"""

import decimal as dc


class KinematicsKeeper(object):

    def __init__(self, max_collection):
        self.interval = dc.Decimal(40)
        self.zero = dc.Decimal(0.0)
        self.one = dc.Decimal(1.0)
        self._curr_pos = dc.Decimal(0.0)
        self._curr_vel = dc.Decimal(0.0)
        self._curr_accel = dc.Decimal(0.0)
        self._max_collection = max_collection

    def generate_next_state(self, new_accel):

        dc.getcontext().prec = 6

        new_accel = dc.Decimal(new_accel) * self.one

        # Must convert time difference to milliseconds
        time_diff = self.interval * self.one / dc.Decimal(1000) * self.one

        # Acceleration
        if self._max_collection.get_max_accel() < dc.Decimal(abs(new_accel)):

            if new_accel == dc.Decimal(0.0):
                new_accel = self._max_collection.get_max_accel()

            else:
                new_accel = (new_accel / dc.Decimal(abs(new_accel))) * self._max_collection.get_max_accel()

        # Acceleration Onset
        if self._max_collection.get_max_accel_diff() < dc.Decimal(abs(new_accel - self._curr_accel) / time_diff):

            if new_accel == dc.Decimal(0.0):
                new_accel = (self._max_collection.get_max_accel_diff() * time_diff) + self._curr_accel

            else:
                new_accel = ((new_accel / dc.Decimal(abs(new_accel))) * (
                    self._max_collection.get_max_accel_diff() * time_diff)) + self._curr_accel

        new_vel = self._determine_next_velocity(time_diff, new_accel)

        # Velocity (positive and negative)
        if self._max_collection.get_max_vel() < dc.Decimal(abs(new_vel)):

            if new_vel == dc.Decimal(0.0):
                new_vel = self._max_collection.get_max_vel()

            else:
                new_vel = (new_vel / dc.Decimal(abs(new_vel))) * self._max_collection.get_max_vel()

            new_accel = dc.Decimal(0.0)
            # new_accel = self._determine_next_acceleration_by_vel(time_diff, new_vel)

        new_pos = self._determine_next_position(time_diff, new_accel)

        # Excursion (negative)
        if self._max_collection.get_max_neg_exc() > dc.Decimal(new_pos):

            new_pos = self._max_collection.get_max_neg_exc()
            # new_accel = self._determine_next_acceleration_by_pos(time_diff, new_pos)
            # new_vel = self._determine_next_velocity(time_diff, new_accel)

        # Excursion (positive)
        if self._max_collection.get_max_pos_exc() < dc.Decimal(new_pos):

            new_pos = self._max_collection.get_max_pos_exc()
            # new_accel = self._determine_next_acceleration_by_pos(time_diff, new_pos)
            # new_vel = self._determine_next_velocity(time_diff, new_accel)

        self._curr_vel = new_vel
        self._curr_accel = new_accel
        self._curr_pos = new_pos

    def check_max_accel(self, new_accel):
        # Acceleration
        if self._max_collection.get_max_accel() < dc.Decimal(abs(new_accel)):

            if new_accel == dc.Decimal(0.0):
                new_accel = self._max_collection.get_max_accel()

            else:
                new_accel = (new_accel / dc.Decimal(abs(new_accel))) * self._max_collection.get_max_accel()
        return new_accel

    def get_velocity(self):
        return float(self._curr_vel)

    def get_acceleration(self):
        return float(self._curr_accel)

    def get_position(self):
        return float(self._curr_pos)

    def set_position(self, new_pos):
        self._curr_pos = dc.Decimal(new_pos) * self.one

    def get_max_acceleration(self):
        return self._max_collection.get_max_accel()

    def _determine_next_acceleration_by_pos(self, time_diff, new_pos):
        return ((dc.Decimal(-6) * (self._curr_pos + (self._curr_vel * time_diff) + (
            dc.Decimal(1 / 2) * (self._curr_accel * (time_diff ** dc.Decimal(2)))) - new_pos)) / (
                    time_diff ** dc.Decimal(2))) + self._curr_accel

    def _determine_next_acceleration_by_vel(self, time_diff, new_vel):
        return ((dc.Decimal(-2) * (self._curr_vel + (self._curr_accel * time_diff) - new_vel)) / (
            time_diff)) + self._curr_accel

    def _determine_next_position(self, time_diff, new_accel):
        return self._curr_pos + (self._curr_vel * time_diff) + (
            dc.Decimal(1 / 2) * self._curr_accel * (time_diff ** dc.Decimal(2))) + (
                   dc.Decimal(1 / 6) * ((new_accel - self._curr_accel) * (time_diff ** dc.Decimal(2))))

    def _determine_next_velocity(self, time_diff, new_accel):
        return self._curr_vel + self._curr_accel * time_diff + dc.Decimal(1 / 2) * (
            (new_accel - self._curr_accel) * time_diff)

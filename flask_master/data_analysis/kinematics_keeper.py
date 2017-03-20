"""
Created on Oct 29, 2016

@author: steve
"""

import decimal as dc


class KinematicsKeeper(object):

    VELOCITY = 'VELOCITY'
    ACCELERATION = 'ACCELERATION'

    def __init__(self, max_collection):
        self.zero = dc.Decimal(0.0)
        self.one = dc.Decimal(1.0)
        self.interval = dc.Decimal(40)
        self.interval = (self.interval * self.one) / (dc.Decimal(1000) * self.one)
        self._curr_pos = dc.Decimal(0.0)
        self._curr_vel = dc.Decimal(0.0)
        self._curr_accel = dc.Decimal(0.0)
        self._max_collection = max_collection

    def generate_next_state(self, new_val, starting_val_type):

        dc.getcontext().prec = 6

        new_val = dc.Decimal(new_val) * self.one

        new_accel = new_val

        if starting_val_type == self.VELOCITY:
            new_accel = self._determine_next_acceleration_by_vel(new_val)

        elif starting_val_type == self.ACCELERATION:
            new_accel = self._determine_next_acceleration_by_pos(new_val)

        new_accel = self.check_max_accel(new_accel)

        new_accel = self.check_accel_onset(new_accel)

        new_vel = self._determine_next_velocity(new_accel)

        new_vel = self.check_max_velocity(new_vel)

        new_pos = self._determine_next_position(new_accel)

        new_pos = self.check_max_neg_position(new_pos)

        new_pos = self.check_max_pos_position(new_pos)

        self._curr_vel = new_vel
        self._curr_accel = new_accel
        self._curr_pos = new_pos

    def check_max_accel(self, new_accel):

        if self._max_collection.get_max_accel() < dc.Decimal(abs(new_accel)):

            if new_accel == dc.Decimal(0.0):
                new_accel = self._max_collection.get_max_accel()

            else:
                new_accel = (new_accel / dc.Decimal(abs(new_accel))) * self._max_collection.get_max_accel()

        return new_accel

    def check_accel_onset(self, new_accel):

        if self._max_collection.get_max_accel_diff() < dc.Decimal(abs(new_accel - self._curr_accel) / self.interval):

            if new_accel == dc.Decimal(0.0):
                new_accel = (self._max_collection.get_max_accel_diff() * self.interval) + self._curr_accel

            else:
                new_accel = ((new_accel / dc.Decimal(abs(new_accel))) * (
                    self._max_collection.get_max_accel_diff() * self.interval)) + self._curr_accel

        return new_accel

    def check_max_velocity(self, new_vel):

        if self._max_collection.get_max_vel() < dc.Decimal(abs(new_vel)):

            if new_vel == dc.Decimal(0.0):
                new_vel = self._max_collection.get_max_vel()

            else:
                new_vel = (new_vel / dc.Decimal(abs(new_vel))) * self._max_collection.get_max_vel()

        return new_vel

    def check_max_neg_position(self, new_pos):

        if self._max_collection.get_max_neg_exc() > dc.Decimal(new_pos):
            new_pos = self._max_collection.get_max_neg_exc()

        return new_pos

    def check_max_pos_position(self, new_pos):

        if self._max_collection.get_max_pos_exc() < dc.Decimal(new_pos):
            new_pos = self._max_collection.get_max_pos_exc()

        return new_pos

    def get_velocity(self):

        return float(self._curr_vel)

    def get_acceleration(self):

        return float(self._curr_accel)

    def get_position(self):

        return float(self._curr_pos)

    def set_position(self, new_pos):

        self._curr_pos = dc.Decimal(new_pos) * self.one

    def set_interval(self, interval):

        self.interval = (dc.Decimal(interval) * self.one) / (dc.Decimal(1000) * self.one)

    def get_max_acceleration(self):

        return float(self._max_collection.get_max_accel())

    def _determine_next_acceleration_by_pos(self, new_pos):

        return ((dc.Decimal(-6) * (self._curr_pos + (self._curr_vel * self.interval) + (
            dc.Decimal(1 / 2) * (self._curr_accel * (self.interval ** dc.Decimal(2)))) - new_pos)) / (
                    self.interval ** dc.Decimal(2))) + self._curr_accel

    def _determine_next_acceleration_by_vel(self, new_vel):

        return ((dc.Decimal(-2) * (self._curr_vel + (self._curr_accel * self.interval) - new_vel)) / (
            self.interval)) + self._curr_accel

    def _determine_next_position(self, new_accel):

        return self._curr_pos + (self._curr_vel * self.interval) + (
            dc.Decimal(1 / 2) * self._curr_accel * (self.interval ** dc.Decimal(2))) + (
                   dc.Decimal(1 / 6) * ((new_accel - self._curr_accel) * (self.interval ** dc.Decimal(2))))

    def _determine_next_velocity(self, new_accel):

        return self._curr_vel + self._curr_accel * self.interval + dc.Decimal(1 / 2) * (
            (new_accel - self._curr_accel) * self.interval)

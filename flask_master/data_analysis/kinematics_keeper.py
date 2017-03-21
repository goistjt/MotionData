"""
Created on Oct 29, 2016

@author: steve
"""

import decimal as dc

"""
This class represents the state of a particular degree of motion and composes what is needed to determine the next
valid motions based upon input and specified constraints.
"""


class KinematicsKeeper(object):
    # For usage in determining what a "new acceleration" is defined as in generating state
    VELOCITY = 'VELOCITY'
    ACCELERATION = 'ACCELERATION'

    def __init__(self, max_collection, buffer_factor):
        self.zero = dc.Decimal(0.0)
        self.one = dc.Decimal(1.0)
        self.max_buffer_factor = dc.Decimal(buffer_factor) * self.one
        self.interval = dc.Decimal(40)
        self.interval = (self.interval * self.one) / (dc.Decimal(1000) * self.one)
        self._curr_pos = dc.Decimal(0.0)
        self._curr_vel = dc.Decimal(0.0)
        self._curr_accel = dc.Decimal(0.0)
        self._max_collection = max_collection

    """
    Adjusts the values of position, velocity, and acceleration for each interval of this degree of motion.
    The user can then query for these values at a particular moment in time.
    """

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

    """
    Determines if the maximum acceleration was reached.
    """

    def check_max_accel(self, new_accel):

        definitive_max = self._max_collection.get_max_accel() * self.max_buffer_factor
        if definitive_max < dc.Decimal(abs(new_accel)):

            if new_accel == dc.Decimal(0.0):
                new_accel = definitive_max

            else:
                new_accel = (new_accel / dc.Decimal(abs(new_accel))) * definitive_max

        return new_accel

    """
    Determines if the maximum change in acceleration has been reached.
    """

    def check_accel_onset(self, new_accel):

        definitive_max = self._max_collection.get_max_accel_diff() * self.max_buffer_factor
        if definitive_max < dc.Decimal(abs(new_accel - self._curr_accel) / self.interval):

            if new_accel == dc.Decimal(0.0):
                new_accel = (definitive_max * self.interval) + self._curr_accel

            else:
                new_accel = ((new_accel / dc.Decimal(abs(new_accel))) * (
                    definitive_max * self.interval)) + self._curr_accel

        return new_accel

    """
    Determines if the maximum velocity has been reached.
    """

    def check_max_velocity(self, new_vel):

        definitive_max = self._max_collection.get_max_vel() * self.max_buffer_factor
        if definitive_max < dc.Decimal(abs(new_vel)):

            if new_vel == dc.Decimal(0.0):
                new_vel = definitive_max

            else:
                new_vel = (new_vel / dc.Decimal(abs(new_vel))) * definitive_max

        return new_vel

    """
    Determines if the maximum negative position has been reached.
    """

    def check_max_neg_position(self, new_pos):

        definitive_max = self._max_collection.get_max_neg_exc() * self.max_buffer_factor
        if definitive_max > dc.Decimal(new_pos):
            new_pos = definitive_max

        return new_pos

    """
    Determines if the maximum positive position has been reached.
    """

    def check_max_pos_position(self, new_pos):

        definitive_max = self._max_collection.get_max_pos_exc() * self.max_buffer_factor
        if definitive_max < dc.Decimal(new_pos):
            new_pos = definitive_max

        return new_pos

    """
    Getter for current velocity.
    """

    def get_velocity(self):

        return float(self._curr_vel)

    """
    Getter for current acceleration.
    """

    def get_acceleration(self):

        return float(self._curr_accel)

    """
    Getter for current position.
    """

    def get_position(self):

        return float(self._curr_pos)

    """
    Sets the current position. Used in some niche situations like returning to zero position.
    """

    def set_position(self, new_pos):

        self._curr_pos = dc.Decimal(new_pos) * self.one

    """
    Sets the interval of time motion occurs in.
    """

    def set_interval(self, interval):

        self.interval = (dc.Decimal(interval) * self.one) / (dc.Decimal(1000) * self.one)

    """
    Gets the maximum acceleration that this keeper was set to allow.
    """

    def get_max_acceleration(self):

        return float(self._max_collection.get_max_accel())

    """
    Determines the next accleration based upon existing values and a new position.
    """

    def _determine_next_acceleration_by_pos(self, new_pos):

        return ((dc.Decimal(-6) * (self._curr_pos + (self._curr_vel * self.interval) + (
            dc.Decimal(1 / 2) * (self._curr_accel * (self.interval ** dc.Decimal(2)))) - new_pos)) / (
                    self.interval ** dc.Decimal(2))) + self._curr_accel

    """
    Determines the next acceleration based upon existing values and a new velocity.
    """

    def _determine_next_acceleration_by_vel(self, new_vel):

        return ((dc.Decimal(-2) * (self._curr_vel + (self._curr_accel * self.interval) - new_vel)) / (
            self.interval)) + self._curr_accel

    """
    Determines the next position based upon existing values and a new acceleration.
    """

    def _determine_next_position(self, new_accel):

        return self._curr_pos + (self._curr_vel * self.interval) + (
            dc.Decimal(1 / 2) * self._curr_accel * (self.interval ** dc.Decimal(2))) + (
                   dc.Decimal(1 / 6) * ((new_accel - self._curr_accel) * (self.interval ** dc.Decimal(2))))

    """
    Determines the next velocity based upon existing values and a new acceleration.
    """

    def _determine_next_velocity(self, new_accel):

        return self._curr_vel + self._curr_accel * self.interval + dc.Decimal(1 / 2) * (
            (new_accel - self._curr_accel) * self.interval)

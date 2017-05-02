"""
Created on Oct 29, 2016

@author: steve
"""

import decimal as dc


class KinematicsKeeper(object):
    """
    This class represents the state of a particular degree of motion and composes what is needed to determine the next
    valid motions based upon input and specified constraints.
    """
    # For usage in determining what a "new acceleration" is defined as in generating state
    VELOCITY = 'VELOCITY'
    ACCELERATION = 'ACCELERATION'
    POSITION = 'POSITION'

    def __init__(self, max_collection, buffer_factor):
        self.zero = dc.Decimal(0.0)
        self.one = dc.Decimal(1.0)
        self.max_buffer_factor = dc.Decimal(buffer_factor) * self.one
        self._interval = dc.Decimal(40)
        self._interval = (self._interval * self.one) / (dc.Decimal(1000) * self.one)
        self._curr_pos = dc.Decimal(0.0)
        self._curr_vel = dc.Decimal(0.0)
        self._curr_accel = dc.Decimal(0.0)
        self._max_collection = max_collection

    def generate_next_state(self, new_val, starting_val_type):
        """
        Adjusts the values of position, velocity, and acceleration for each interval of this degree of motion.
        The user can then query for these values at a particular moment in time.
        :param: new_val - an input value, either acceleration, velocity, or position from the previous to generate from
        :param: starting_val_type - acceleration, velocity, or position based on the constants included in this class
        :returns: None
        """
        dc.getcontext().prec = 6
        new_val = dc.Decimal(new_val) * self.one

        if starting_val_type == self.VELOCITY:
            new_accel = self._determine_next_acceleration_by_vel(new_val)
        elif starting_val_type == self.POSITION:
            new_accel = self._determine_next_acceleration_by_pos(new_val)
        else:
            new_accel = new_val

        bool_res = True

        bool_res = bool_res and self.check_max_accel(new_accel)

        bool_res = bool_res and self.check_accel_onset(new_accel)

        new_vel = self._determine_next_velocity(new_accel)

        bool_res and self.check_max_velocity(new_vel)

        new_pos = self._determine_next_position(new_accel)

        bool_res = bool_res and self.check_max_neg_position(new_pos)

        bool_res = bool_res and self.check_max_pos_position(new_pos)

        if bool_res:
            self._curr_pos = new_pos

        self._curr_vel = new_vel

        self._curr_accel = new_accel

    def check_max_accel(self, new_accel):
        """
        Determines if the maximum acceleration was reached.
        :param: new_accel - the acceleration to check against the maximum allowed
        :returns: the acceleration deemed appropriate after checks have been made
        """
        definitive_max = self._max_collection.get_max_accel() * dc.Decimal(self.max_buffer_factor)
        if dc.Decimal(abs(new_accel)) > abs(definitive_max):
            return False
        return True

    def check_accel_onset(self, new_accel):
        """
        Determines if the maximum change in acceleration has been reached.
        :param: new_accel - the acceleration to check against (with the current acceleration) the maximum allowed change
                            in acceleration
        :returns: the acceleration deemed appropriate after checks have been made
        """
        definitive_max = self._max_collection.get_max_accel_diff() * dc.Decimal(self.max_buffer_factor)
        if definitive_max < dc.Decimal(abs(new_accel - self._curr_accel)):
            return False
        return True

    def check_max_velocity(self, new_vel):
        """
        Determines if the maximum velocity has been reached.
        :param: new_vel - the velocity to check against the maximum allowed
        :returns: the appropriate velocity
        """
        definitive_max = self._max_collection.get_max_vel() * self.max_buffer_factor
        if definitive_max < dc.Decimal(abs(new_vel)):
            return False
        return True

    def check_max_neg_position(self, new_pos):
        """
        Determines if the maximum negative position has been reached.
        :param: new_pos - the position to check against the maximum allowed in the negative direction
        :returns: the appropriate position
        """
        definitive_max = self._max_collection.get_max_neg_exc() * self.max_buffer_factor
        if definitive_max > new_pos:
            return False
        return True

    def check_max_pos_position(self, new_pos):
        """
        Determines if the maximum positive position has been reached.
        :param: new_pos - the position to check against the maximum allowed in the positive direction
        :returns: the appropriate position
        """
        definitive_max = self._max_collection.get_max_pos_exc() * self.max_buffer_factor
        if definitive_max < new_pos:
            return False
        return True

    def get_velocity(self):
        return float(self._curr_vel)

    def get_acceleration(self):
        return float(self._curr_accel)

    def get_position(self):
        return float(self._curr_pos)

    def set_position(self, new_pos):
        """
        Sets the current position. Used in some niche situations like returning to zero position.
        """
        self._curr_pos = dc.Decimal(new_pos) * self.one

    def set_interval(self, interval):
        self._interval = (dc.Decimal(interval) * self.one) / (dc.Decimal(1000) * self.one)

    def get_max_acceleration(self):
        """
        Gets the maximum acceleration that this keeper was set to allow.
        """
        return float(self._max_collection.get_max_accel())

    def _determine_next_acceleration_by_pos(self, new_pos):
        """
        Determines the next accleration based upon existing values and a new position.
        :param: new_pos - the new position to determine the next acceleration from
        :returns: the appropriate new acceleration for further calculations to use
        """

        return (
                   (((dc.Decimal(
                       new_pos) * self.one) - self._curr_pos) / self._interval) - self._curr_vel) / self._interval

    def _determine_next_acceleration_by_vel(self, new_vel):
        """
        Determines the next acceleration based upon existing values and a new velocity.
        :param: new_vel - the velocity to determine the new acceleration from
        :returns: the appropriate new acceleration for further calculations to use
        """
        return ((dc.Decimal(new_vel) * self.one) - self._curr_vel) / self._interval

    def _determine_next_position(self, new_accel):
        """
        Determines the next position based upon existing values and a new acceleration.
        :param: new_accel - the next accel value to generate state from
        :returns: the position of the next state
        """
        return self._curr_pos + (self._curr_vel * self._interval) + (
            dc.Decimal(1 / 2) * self._curr_accel * (self._interval ** dc.Decimal(2))) + (
                   dc.Decimal(1 / 6) * ((new_accel - self._curr_accel) * (self._interval ** dc.Decimal(3))))

    def _determine_next_velocity(self, new_accel):
        """
        Determines the next velocity based upon existing values and a new acceleration.
        :param: new_accel - the next accel to generate state from
        :returns: the velocity of the next state
        """
        return self._curr_vel + self._curr_accel * self._interval + dc.Decimal(1 / 2) * (
            (new_accel - self._curr_accel) * (self._interval ** dc.Decimal(2)))

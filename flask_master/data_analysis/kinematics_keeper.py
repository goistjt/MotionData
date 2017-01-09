'''
Created on Oct 29, 2016

@author: steve
'''

import decimal as dc

ZERO = dc.Decimal(0.0)
ONE = dc.Decimal(1.0)

class KinematicsKeeper(object):

    def __init__(self, starting_time, max_collection):
        self._curr_time = dc.Decimal(starting_time) * ONE
        self._start_time = dc.Decimal(starting_time) * ONE
        self._curr_pos = dc.Decimal(0.0)
        self._curr_vel = dc.Decimal(0.0)
        self._curr_accel = dc.Decimal(0.0)
        self._max_collection = max_collection
        """
        self._roll_back = False
        self._since_roll_back = 0
        self._accumulation_exc = 0
        """
        
    def needs_roll_back(self):
        return self._roll_back
    
    """
    def roll_back_average(self):
        return self._accumulation_exc / self._since_roll_back
    """
    
    def generate_next_state(self, new_time, new_accel):
        
        dc.getcontext().prec = 6
        # self._roll_back = False
        
        new_time = dc.Decimal(new_time) * ONE
        
        new_accel = dc.Decimal(new_accel) * ONE
        
        if(new_time == self._start_time):
            self._curr_accel = dc.Decimal(0.0)
            self._curr_pos = dc.Decimal(0.0)
            self._curr_vel = dc.Decimal(0.0)
            return
        
        #Must convert time difference to milliseconds
        time_diff = (new_time - self._curr_time) / dc.Decimal(1000)
        
        #Acceleration
        if(self._max_collection.get_max_accel() < dc.Decimal(abs(new_accel))):
            # self._roll_back = True
            new_accel = (new_accel / dc.Decimal(abs(new_accel))) * self._max_collection.get_max_accel()
            
        #Acceleration Onset
        if(self._max_collection.get_max_accel_diff() < dc.Decimal(abs(new_accel - self._curr_accel))):
            # self._roll_back = True
            new_accel = (new_accel / dc.Decimal(abs(new_accel))) * ((self._max_collection.get_max_accel_diff() * time_diff) + self._curr_accel)
        
        new_vel = self._determine_next_velocity(time_diff, new_accel)
        
        #Velocity (positive and negative)
        if(self._max_collection.get_max_vel() < dc.Decimal(abs(new_vel))):
            # self._roll_back = True
            new_vel = (new_vel / dc.Decimal(abs(new_vel))) * self._max_collection.get_max_vel()
            new_accel = self._determine_next_acceleration(time_diff, new_vel)
        
        new_pos = self._determine_next_position(time_diff, new_accel)
        
        #Excursion (negative)
        if(self._max_collection.get_max_neg_exc() > dc.Decimal(new_pos)):
            # self._roll_back = True
            new_pos = self._max_collection.get_max_neg_exc()
            new_accel = self._determine_next_acceleration_by_pos(time_diff, new_pos)
            new_vel = self._determine_next_velocity(time_diff, new_accel)
        
        #Excursion (positive)
        if(self._max_collection.get_max_pos_exc() < dc.Decimal(new_pos)):
            # self._roll_back = True
            new_pos = self._max_collection.get_max_pos_exc()
            new_accel = self._determine_next_acceleration_by_pos(time_diff, new_pos)
            new_vel = self._determine_next_velocity(time_diff, new_accel)
        
        self._curr_vel = new_vel
        self._curr_accel = new_accel
        self._curr_time = new_time
        self._curr_pos = new_pos
        
        
    
    def get_velocity(self):
        return float(self._curr_vel)
    
    def get_acceleration(self):
        return float(self._curr_accel)
    
    def get_position(self):
        return float(self._curr_pos)
    
    def get_time(self):
        return float(self._curr_time)
    
    
    
    def _determine_next_acceleration_by_pos(self, time_diff, new_pos):
        return ((dc.Decimal(-6) * (self._curr_pos + (self._curr_vel * time_diff) + (dc.Decimal(1 / 2) * (self._curr_accel * (time_diff ** dc.Decimal(2)))) - new_pos)) / (time_diff ** dc.Decimal(2))) + self._curr_accel
    
    def _determine_next_acceleration_by_vel(self, time_diff, new_vel):
        return ((dc.Decimal(-2) * (self._curr_vel + (self._curr_accel * time_diff) - new_vel)) / (time_diff)) + self._curr_accel
    
    def _determine_next_position(self, time_diff, new_accel):
        return self._curr_pos + (self._curr_vel * time_diff) + (dc.Decimal(1 / 2) * self._curr_accel * (time_diff ** dc.Decimal(2))) + (dc.Decimal(1/6) * ((new_accel - self._curr_accel) * (time_diff ** dc.Decimal(2))))
    
    def _determine_next_velocity(self, time_diff, new_accel):
        return self._curr_vel + self._curr_accel * time_diff + dc.Decimal(1 / 2) * ((new_accel - self._curr_accel) * (time_diff))
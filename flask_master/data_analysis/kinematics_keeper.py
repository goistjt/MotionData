'''
Created on Oct 29, 2016

@author: steve
'''

class KinematicsKeeper(object):

    def __init__(self, starting_time):
        self._curr_time = starting_time
        self._curr_exc = 0
        self._curr_vel = 0
        self._curr_accel = 0
        
    def generate_next_state(self, new_time, new_accel):
        new_vel = self.determine_next_velocity(new_time, new_accel)
        new_exc = self.determine_next_excursion(new_time, new_accel)
        self._curr_exc = new_exc
        self._curr_vel = new_vel
        self._curr_accel = new_accel
        self._curr_time = new_time
    
    def get_excursion(self):
        return self._curr_exc
    
    def get_velocity(self):
        return self._curr_vel
    
    def get_acceleration(self):
        return self._curr_accel
    
    def get_time(self):
        return self._curr_time
    
    def determine_next_excursion(self, new_time, new_accel):
        if(new_time < 0):
            return self._curr_exc
        time_diff = new_time - self._curr_time
        return self._curr_exc + self._curr_vel * time_diff + (1/2) * self._curr_accel * (time_diff ** 2) + (1/6) * (new_accel - self._curr_accel) * (time_diff ** 3)
    
    def determine_next_velocity(self, new_time, new_accel):
        if(new_time < 0):
            return self._curr_exc
        time_diff = new_time - self._curr_time
        return self._curr_vel + self._curr_accel * time_diff + (1/2) * (new_accel - self._curr_accel) * (time_diff ** 2)
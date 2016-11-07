'''
Created on Oct 29, 2016

@author: steve
'''

class KinematicsKeeper(object):

    def __init__(self, starting_time, max_collection):
        self._curr_time = starting_time
        self._curr_pos = 0
        self._curr_vel = 0
        self._curr_accel = 0
        self._curr_exc = 0
        self._max_collection = max_collection
    
    def generate_next_state(self, new_time, new_accel):
        #Time is before the current (back-tracking)
        if(new_time < self._curr_time):
            return
        #Acceleration
        if(self.max_collection.get_max_accel() < abs(new_accel)):
            new_accel = (new_accel / new_accel) * self.max_collection.get_max_accel()
        #Acceleration Onset
        if(self.max_collection.get_max_accel_diff() < abs((new_accel - self._curr_accel) / (new_time - self._curr_time))):
            new_accel = (new_accel / new_accel) * ((self.max_collection.get_max_accel_diff() * (new_time - self._curr_time) + self._curr_accel))
        new_vel = self.determine_next_velocity(new_time, new_accel)
        #Velocity (positive and negative)
        if(self.max_collection.get_max_vel() < abs(new_vel)):
            new_vel = (new_vel / new_vel) * self.max_collection.get_max_vel()
            new_accel = self.determine_next_acceleration(new_time, new_vel)
        new_pos = self.determine_next_position(new_time, new_accel)
        potential_exc = new_pos - self._curr_pos
        #Excursion (negative)
        if(self.max_collection.get_max_neg_exc() > potential_exc):
            new_pos = self._curr_pos - self.max_collection.get_max_neg_exc()
            new_accel = self.determine_next_acceleration_by_pos(new_time, new_pos)
            new_vel = self.determine_next_velocity(new_time, new_accel)
        #Excursion (positive)
        if(self.max_collection.get_max_pos_exc() < potential_exc):
            new_pos = self.curr_pos + self.max_collection.get_max_pos_exc()
            new_accel = self.determine_next_acceleration_by_pos(new_time, new_pos)
            new_vel = self.determine_next_velocity(new_time, new_accel)
        self._curr_exc = potential_exc
        self._curr_vel = new_vel
        self._curr_accel = new_accel
        self._curr_time = new_time
        self._curr_pos = new_pos
    
    def get_excursion(self):
        return self._curr_exc
    
    def get_velocity(self):
        return self._curr_vel
    
    def get_acceleration(self):
        return self._curr_accel
    
    def get_position(self):
        return self._curr_pos
    
    def get_time(self):
        return self._curr_time
    
    def determine_next_acceleration_by_pos(self, new_time, new_pos):
        time_diff = new_time - self._curr_time
        return ((6 * (new_pos - self._curr_pos - (self._curr_vel * time_diff) - ((1 / 2) * (self._curr_accel * (time_diff ** 2))))) / (time_diff ** 2)) + self._curr_accel
    
    def determine_next_acceleration_by_vel(self, new_time, new_vel):
        time_diff = new_time - self._curr_time
        return ((2 * (new_vel - self._curr_vel - (self._curr_accel * time_diff)))/(time_diff ** 2)) + self._curr_accel
    
    def determine_next_position(self, new_time, new_accel):
        time_diff = new_time - self._curr_time
        return self._curr_pos + self._curr_vel * time_diff + (1/2) * self._curr_accel * (time_diff ** 2) + (1/6) * ((new_accel - self._curr_accel) / time_diff) * (time_diff ** 3)
    
    def determine_next_velocity(self, new_time, new_accel):
        time_diff = new_time - self._curr_time
        return self._curr_vel + self._curr_accel * time_diff + (1/2) * ((new_accel - self._curr_accel) / time_diff) * (time_diff ** 2)
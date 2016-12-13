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
        self._roll_back = False
        self._begin_roll_back = 0
        self._end_roll_back = 0
        self._accumulation_exc = 0
        
    def needs_roll_back(self):
        return self._roll_back
    
    def roll_back_beginning(self):
        return self._begin_roll_back
    
    def roll_back_ending(self):
        return self._end_roll_back
    
    def roll_back_average(self):
        return self._accumulation_exc / (self._end_roll_back - self._begin_roll_back)
    
    def reset_roll_back(self, pos):
        self._roll_back = False
        self._begin_roll_back = pos
        self._end_roll_back = pos
        self._accumulation_exc = 0
    
    def generate_next_state(self, new_time, new_accel):
        
        time_diff = new_time - self._curr_time
        
        #Acceleration
        if(self.max_collection.get_max_accel() < abs(new_accel)):
            new_accel = (new_accel / abs(new_accel)) * self.max_collection.get_max_accel()
            
        #Acceleration Onset
        if(self.max_collection.get_max_accel_diff() < abs(new_accel - self._curr_accel)):
            new_accel = (new_accel / abs(new_accel)) * ((self.max_collection.get_max_accel_diff() * time_diff + self._curr_accel))
        
        new_vel = self.determine_next_velocity(time_diff, new_accel)
        
        #Velocity (positive and negative)
        if(self.max_collection.get_max_vel() < abs(new_vel)):
            new_vel = (new_vel / abs(new_vel)) * self.max_collection.get_max_vel()
            new_accel = self.determine_next_acceleration(time_diff, new_vel)
        
        new_pos = self.determine_next_position(time_diff, new_accel)
        potential_exc = new_pos - self._curr_pos
        
        #Excursion (negative)
        if(self.max_collection.get_max_neg_exc() > potential_exc):
            new_pos = self._curr_pos - self.max_collection.get_max_neg_exc()
            new_accel = self.determine_next_acceleration_by_pos(time_diff, new_pos)
            new_vel = self.determine_next_velocity(time_diff, new_accel)
        
        #Excursion (positive)
        if(self.max_collection.get_max_pos_exc() < potential_exc):
            new_pos = self.curr_pos + self.max_collection.get_max_pos_exc()
            new_accel = self.determine_next_acceleration_by_pos(time_diff, new_pos)
            new_vel = self.determine_next_velocity(time_diff, new_accel)
        
        self._curr_exc = potential_exc
        self._curr_vel = new_vel
        self._curr_accel = new_accel
        self._curr_time = new_time
        self._curr_pos = new_pos
    
    def get_excursion(self):
        return self._curr_exc

    def set_excursion(self, exc):
        self._curr_exc = exc
    
    def get_velocity(self):
        return self._curr_vel
    
    def set_velocity(self, vel):
        self._curr_vel = vel
    
    def get_acceleration(self):
        return self._curr_accel
    
    def set_acceleration(self, accel):
        self._curr_accel
    
    def get_position(self):
        return self._curr_pos
    
    def set_position(self, pos):
        return self._curr_pos
    
    def get_time(self):
        return self._curr_time
    
    def set_time(self, time):
        self._curr_time = time
    
    def determine_next_acceleration_by_pos(self, time_diff, new_pos):
        return ((6 * (new_pos - self._curr_pos - (self._curr_vel * time_diff) - ((1 / 2) * (self._curr_accel * (time_diff ** 2))))) / (time_diff ** 2)) + self._curr_accel
    
    def determine_next_acceleration_by_vel(self, time_diff, new_vel):
        return ((2 * (new_vel - self._curr_vel - (self._curr_accel * time_diff)))/(time_diff ** 2)) + self._curr_accel
    
    def determine_next_position(self, time_diff, new_accel):
        return self._curr_pos + self._curr_vel * time_diff + (1/2) * self._curr_accel * (time_diff ** 2) + (1/6) * ((new_accel - self._curr_accel) / time_diff) * (time_diff ** 3)
    
    def determine_next_velocity(self, time_diff, new_accel):
        return self._curr_vel + self._curr_accel * time_diff + (1/2) * ((new_accel - self._curr_accel) / time_diff) * (time_diff ** 2)